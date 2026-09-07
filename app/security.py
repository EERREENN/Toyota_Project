# -*- coding: utf-8 -*-
"""Panel guvenligi: sifre, oturum, IP kilidi, CSRF.

Flask-Login KULLANILMIYOR. Oturum dogrudan Flask session uzerinde
tutuluyor; kullanici hesabi yok, tek ortak sifre var.

* Sifre hicbir yerde duz metin durmaz. .env yalnizca HASH tasir;
  panelden degistirilince yeni hash veritabanina yazilir ve oradaki
  kazanir.
* Yanlis sifre "hatali sifre" demez, 404 dondurur: panelin varligi
  sizmasin diye. Kilitliyken de ayni sey olur.
* Oturumun yasi session icinde tutulur. Cerez omrune tek basina
  guvenilmez.
"""

from __future__ import annotations

import hmac
import secrets
from datetime import timedelta, timezone
from functools import wraps

from flask import abort, current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .models import LoginAttempt, SiteSetting, utcnow

OTURUM_ANAHTARI = "admin"
OTURUM_ZAMANI = "admin_since"
CSRF_ANAHTARI = "csrf"
HASH_AYARI = "admin_password_hash"


def aktif_hash() -> str:
    """Gecerli sifre hash'i.

    Once veritabanina bakar (panelden degistirilmis olabilir), yoksa
    .env'den gelen baslangic degerini kullanir.
    """
    ayar = db.session.query(SiteSetting).filter_by(key=HASH_AYARI).first()
    if ayar and ayar.value:
        return ayar.value
    return current_app.config.get("ADMIN_PASSWORD_HASH") or ""


def sifre_dogru(parola: str) -> bool:
    ozet = aktif_hash()
    if not ozet or not parola:
        return False
    try:
        return check_password_hash(ozet, parola)
    except (ValueError, TypeError):
        return False


def sifre_degistir(yeni: str) -> None:
    ozet = generate_password_hash(yeni, method="scrypt")
    ayar = db.session.query(SiteSetting).filter_by(key=HASH_AYARI).first()
    if ayar is None:
        ayar = SiteSetting(key=HASH_AYARI)
        db.session.add(ayar)
    ayar.value = ozet
    db.session.commit()


def giris_yap() -> None:
    session.clear()
    session[OTURUM_ANAHTARI] = True
    session[OTURUM_ZAMANI] = utcnow().timestamp()
    session[CSRF_ANAHTARI] = secrets.token_urlsafe(32)
    session.permanent = True


def cikis_yap() -> None:
    session.clear()


def oturum_gecerli() -> bool:
    if not session.get(OTURUM_ANAHTARI):
        return False
    baslangic = session.get(OTURUM_ZAMANI)
    if not baslangic:
        return False
    omur = current_app.config.get("ADMIN_SESSION_MINUTES", 60)
    yas = utcnow().timestamp() - float(baslangic)
    if yas > omur * 60:
        session.clear()
        return False
    return True


def admin_gerekli(gorunum):
    """Giris yapilmamissa giris ekranina yollar."""

    @wraps(gorunum)
    def sarmalayici(*args, **kwargs):
        if not oturum_gecerli():
            return redirect(url_for("admin.login", next=request.path))
        return gorunum(*args, **kwargs)

    return sarmalayici


def csrf_token() -> str:
    if CSRF_ANAHTARI not in session:
        session[CSRF_ANAHTARI] = secrets.token_urlsafe(32)
    return session[CSRF_ANAHTARI]


def csrf_dogrula() -> None:
    beklenen = session.get(CSRF_ANAHTARI)
    gelen = request.form.get("_csrf", "")
    if not beklenen or not hmac.compare_digest(str(beklenen), str(gelen)):
        abort(400, "Form dogrulamasi basarisiz. Sayfayi yenileyip tekrar dene.")


def istemci_ip() -> str:
    """Gercek istemci IP'si.

    Ters proxy arkasindaysak ProxyFix request.remote_addr'i duzeltmis
    olur; TRUST_PROXY kapaliyken X-Forwarded-For dikkate alinmaz.
    """
    return request.remote_addr or "bilinmeyen"


def _kayit(ip: str) -> LoginAttempt:
    kayit = db.session.query(LoginAttempt).filter_by(ip=ip).first()
    if kayit is None:
        kayit = LoginAttempt(ip=ip, fail_count=0)
        db.session.add(kayit)
    return kayit


def kilitli_mi(ip: str) -> bool:
    kayit = db.session.query(LoginAttempt).filter_by(ip=ip).first()
    return bool(kayit and kayit.is_locked())


def basarisiz_deneme(ip: str) -> None:
    kayit = _kayit(ip)
    simdi = utcnow()
    if kayit.first_fail_at is None:
        kayit.first_fail_at = simdi
    kayit.last_fail_at = simdi
    kayit.fail_count += 1

    ust_sinir = current_app.config.get("ADMIN_MAX_ATTEMPTS", 5)
    if kayit.fail_count >= ust_sinir:
        dakika = current_app.config.get("ADMIN_LOCK_MINUTES", 15)
        kayit.locked_until = simdi + timedelta(minutes=dakika)
        kayit.fail_count = 0
    db.session.commit()


def basarili_deneme(ip: str) -> None:
    kayit = db.session.query(LoginAttempt).filter_by(ip=ip).first()
    if kayit is not None:
        db.session.delete(kayit)
        db.session.commit()
