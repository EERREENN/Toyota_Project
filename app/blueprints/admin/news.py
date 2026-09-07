# -*- coding: utf-8 -*-
"""Haber ekleme, duzenleme, silme."""

from __future__ import annotations

from datetime import date, datetime

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select

from ... import haberler, security, yukleme
from ...extensions import db
from ...metin import benzersiz_slug, slugify, tarih_metni
from ...models import News
from . import bp


def _form(kayit: News | None) -> dict:
    if kayit is None:
        return {
            "title_tr": "",
            "title_en": "",
            "slug": "",
            "category_tr": "",
            "category_en": "",
            "date": date.today().isoformat(),
            "summary_tr": "",
            "summary_en": "",
            "content_tr": "",
            "content_en": "",
            "is_published": "1",
            "image": "",
        }
    return {
        "title_tr": kayit.title_tr,
        "title_en": kayit.title_en or "",
        "slug": kayit.slug,
        "category_tr": kayit.category_tr or "",
        "category_en": kayit.category_en or "",
        "date": kayit.date.isoformat() if kayit.date else date.today().isoformat(),
        "summary_tr": kayit.summary_tr or "",
        "summary_en": kayit.summary_en or "",
        "content_tr": kayit.content_tr or "",
        "content_en": kayit.content_en or "",
        "is_published": "1" if kayit.is_published else "0",
        "image": kayit.image or "",
    }


def _posta() -> dict:
    form = request.form
    return {
        "title_tr": (form.get("title_tr") or "").strip(),
        "title_en": (form.get("title_en") or "").strip(),
        "slug": (form.get("slug") or "").strip(),
        "category_tr": (form.get("category_tr") or "").strip(),
        "category_en": (form.get("category_en") or "").strip(),
        "date": (form.get("date") or "").strip(),
        "summary_tr": (form.get("summary_tr") or "").strip(),
        "summary_en": (form.get("summary_en") or "").strip(),
        "content_tr": form.get("content_tr") or "",
        "content_en": form.get("content_en") or "",
        "is_published": "1" if form.get("is_published") == "1" else "0",
        "image": (form.get("mevcut_gorsel") or "").strip(),
    }


def _tarih_oku(deger: str) -> date | None:
    try:
        return datetime.strptime(deger, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _kaydet(kayit: News | None, deger: dict) -> str | None:
    """Basariliysa None, hata varsa mesaj doner. kayit None ise yeni satır."""
    if not deger["title_tr"]:
        return "Başlık zorunludur."

    gun = _tarih_oku(deger["date"])
    if gun is None:
        return "Tarih geçersiz. Yıl-ay-gün biçiminde yaz (örnek: 2026-09-07)."

    haric = kayit.id if kayit is not None else None
    if deger["slug"]:
        slug = slugify(deger["slug"])
        if haberler.slug_var_mi(slug, haric):
            return "Bu adres parçası başka bir haberde kullanılıyor."
    else:
        slug = benzersiz_slug(
            deger["title_tr"],
            lambda s: haberler.slug_var_mi(s, haric),
        )

    try:
        yeni_gorsel = yukleme.kaydet(request.files.get("gorsel"))
    except yukleme.YuklemeHatasi as hata:
        return str(hata)

    gorsel = deger["image"]
    if yeni_gorsel:
        if kayit is not None:
            yukleme.sil_dosya(kayit.image or "")
        gorsel = yeni_gorsel

    if kayit is None:
        kayit = News()
        db.session.add(kayit)

    kayit.slug = slug
    kayit.date = gun
    kayit.image = gorsel
    kayit.is_published = deger["is_published"] == "1"
    kayit.title_tr = deger["title_tr"]
    kayit.title_en = deger["title_en"]
    kayit.category_tr = deger["category_tr"]
    kayit.category_en = deger["category_en"]
    kayit.summary_tr = deger["summary_tr"]
    kayit.summary_en = deger["summary_en"]
    kayit.content_tr = deger["content_tr"]
    kayit.content_en = deger["content_en"]
    db.session.commit()
    return None


@bp.route("/news")
@security.admin_gerekli
def news_list():
    kayitlar = list(db.session.scalars(
        select(News).order_by(News.date.desc(), News.id.desc())
    ))
    return render_template(
        "admin/news_list.html",
        haberler=kayitlar,
        tarih=lambda iso: tarih_metni(iso, "tr"),
        aktif="haberler",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/news/new", methods=["GET", "POST"])
@security.admin_gerekli
def news_new():
    deger = _form(None)
    if request.method == "POST":
        security.csrf_dogrula()
        deger = _posta()
        hata = _kaydet(None, deger)
        if hata:
            flash(hata, "hata")
        else:
            flash("Haber eklendi.", "ok")
            return redirect(url_for("admin.news_list"))

    return render_template(
        "admin/news_form.html",
        deger=deger,
        kayit=None,
        aktif="haberler",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/news/edit/<int:haber_id>", methods=["GET", "POST"])
@security.admin_gerekli
def news_edit(haber_id: int):
    kayit = db.session.get(News, haber_id)
    if kayit is None:
        flash("Haber bulunamadı.", "hata")
        return redirect(url_for("admin.news_list"))

    deger = _form(kayit)
    if request.method == "POST":
        security.csrf_dogrula()
        deger = _posta()
        hata = _kaydet(kayit, deger)
        if hata:
            flash(hata, "hata")
        else:
            flash("Haber güncellendi.", "ok")
            return redirect(url_for("admin.news_list"))

    return render_template(
        "admin/news_form.html",
        deger=deger,
        kayit=kayit,
        aktif="haberler",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/news/delete/<int:haber_id>", methods=["POST"])
@security.admin_gerekli
def news_delete(haber_id: int):
    security.csrf_dogrula()
    kayit = db.session.get(News, haber_id)
    if kayit is None:
        flash("Haber bulunamadı.", "hata")
        return redirect(url_for("admin.news_list"))

    ad = kayit.title_tr
    yukleme.sil_dosya(kayit.image or "")
    db.session.delete(kayit)
    db.session.commit()
    flash(f"“{ad}” silindi.", "ok")
    return redirect(url_for("admin.news_list"))
