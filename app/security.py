# -*- coding: utf-8 -*-
"""Panel guvenligi: sifre, oturum, IP kilidi, CSRF.

Flask-Login KULLANILMIYOR (istenmedi). Oturum dogrudan Flask session
uzerinde tutuluyor; kullanici hesabi yok, tek ortak sifre var.

TASARIM NOTLARI
---------------
* Sifre hicbir yerde duz metin durmaz. .env yalnizca HASH tasir; panelden
  degistirilince yeni hash veritabanina yazilir ve oradaki kazanir.
* Yanlis sifre "hatali sifre" demez, 404 dondurur: panelin varligi
  sizmasin diye. Kilitliyken de ayni sey olur.
* Oturumun yasi ayrica session icinde tutulur. Sadece cerez omrune
  guvenmek yetmez: tarayici cerezi tasiyip durur, biz yasa bakip
  suresi dolduysa temizleriz.
"""

from __future__ import annotations

import hmac
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import abort, current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .models import Block, LoginAttempt, SiteSetting, utcnow

OTURUM_ANAHTARI = "admin"
OTURUM_ZAMANI = "admin_since"
CSRF_ANAHTARI = "csrf"
HASH_AYARI = "admin_password_hash"


# ============================================================
#  Sifre
# ============================================================
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
        # bozuk / taninmayan hash bicimi
        return False


def sifre_degistir(yeni: str) -> None:
    """Yeni sifrenin hash'ini veritabanina yazar."""
    ozet = generate_password_hash(yeni, method="scrypt")
    ayar = db.session.query(SiteSetting).filter_by(key=HASH_AYARI).first()
    if ayar is None:
        ayar = SiteSetting(key=HASH_AYARI)
        db.session.add(ayar)
    ayar.value = ozet
    db.session.commit()


# ============================================================
#  Oturum
# ============================================================
def giris_yap() -> None:
    session.clear()                       # oturum sabitlemesine karsi
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
        session.clear()                   # suresi doldu
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


# ============================================================
#  CSRF
#
#  Flask-WTF kullanilmadigi icin elle. Token oturumda durur, her
#  formda gizli alan olarak gider, POST'ta sabit zamanli karsilastirma
#  ile dogrulanir.
# ============================================================
def csrf_token() -> str:
    if CSRF_ANAHTARI not in session:
        session[CSRF_ANAHTARI] = secrets.token_urlsafe(32)
    return session[CSRF_ANAHTARI]


def csrf_dogrula() -> None:
    """Gecersizse 400 ile keser."""
    beklenen = session.get(CSRF_ANAHTARI)
    gelen = request.form.get("_csrf", "")
    if not beklenen or not hmac.compare_digest(str(beklenen), str(gelen)):
        abort(400, "Form dogrulamasi basarisiz. Sayfayi yenileyip tekrar dene.")


# ============================================================
#  BLOK KILIDI
#
#  Panel 25 blok tipini de duzenlemeye aciyordu; bu genis bir hata
#  yuzeyiydi. Artik yalnizca `is_locked = False` olan bloklar
#  yazilabilir (bugun: haber bloklari).
#
#  BU FONKSIYON GERCEK KAPIDIR. Sablon tarafinda dugmeyi gizlemek
#  yalnizca gorseldir -- gecerli oturum ve gecerli CSRF token'i ile
#  elle POST atan biri onu asar, burayi asamaz. Bu yuzden kontrol
#  HER YAZMA ROTASININ ICINDE olmali.
#
#  Kilit kotu niyete degil KAZAYA karsi: sifreyi bilen zaten
#  veritabanina da erisebilir.
# ============================================================
def kilit_kontrol(blok: Block) -> None:
    """Kilitli bloga yazma girisimini 403 ile reddeder."""
    if blok.is_locked:
        abort(403)


# ============================================================
#  IP basina gecici kilit
# ============================================================
def istemci_ip() -> str:
    """Gercek istemci IP'si.

    Ters proxy arkasindaysak ProxyFix (factory.py) request.remote_addr'i
    zaten duzeltmis olur; TRUST_PROXY kapaliyken basligi DIKKATE ALMAYIZ
    -- yoksa herkes kendi IP'sini uydurup kilidi asardi.
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
        kayit.fail_count = 0              # kilit bitince sifirdan baslasin
    db.session.commit()


def basarili_deneme(ip: str) -> None:
    kayit = db.session.query(LoginAttempt).filter_by(ip=ip).first()
    if kayit is not None:
        db.session.delete(kayit)
        db.session.commit()


def kalan_kilit_dakika(ip: str) -> int:
    kayit = db.session.query(LoginAttempt).filter_by(ip=ip).first()
    if not kayit or not kayit.locked_until:
        return 0
    bitis = kayit.locked_until
    if bitis.tzinfo is None:
        bitis = bitis.replace(tzinfo=timezone.utc)
    kalan = (bitis - utcnow()).total_seconds()
    return max(0, int(kalan // 60) + 1)
