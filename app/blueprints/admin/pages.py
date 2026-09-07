# -*- coding: utf-8 -*-
"""Sayfa listesi ve sayfa ayarlari.

Editor YENI SAYFA ACAMAZ, SILEMEZ (istendigi gibi): burada yalnizca
mevcut 4 sayfanin ayarlari ve blok listesi var.
"""

from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select

from ... import media, security, translation_sync
from ...block_types import BLOCK_TYPES
from ...extensions import db
from ...models import Page
from . import bp
from ._form import METIN, TAMSAYI, EVET_HAYIR, GORSEL, _oku


def _sayfalar():
    return list(db.session.scalars(select(Page).order_by(Page.nav_order)))


@bp.route("/sayfalar")
@security.admin_gerekli
def pages():
    return render_template(
        "admin/pages.html",
        sayfalar=_sayfalar(),
        tip_adi={t: v["label"] for t, v in BLOCK_TYPES.items()},
        aktif="sayfalar",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/sayfa/<int:sayfa_id>", methods=["GET", "POST"])
@security.admin_gerekli
def page_edit(sayfa_id: int):
    sayfa = db.session.get(Page, sayfa_id)
    if sayfa is None:
        flash("Sayfa bulunamadı.", "hata")
        return redirect(url_for("admin.pages"))

    if request.method == "POST":
        security.csrf_dogrula()
        baslik = _oku(request.form, "title", METIN)
        menu = _oku(request.form, "nav_label", METIN)

        if not baslik or not menu:
            flash("Sayfa başlığı ve menü adı boş bırakılamaz.", "hata")
        else:
            sayfa.title = baslik
            sayfa.nav_label = menu
            sira = _oku(request.form, "nav_order", TAMSAYI)
            if sira is not None:
                sayfa.nav_order = sira
            sayfa.is_published = _oku(request.form, "is_published", EVET_HAYIR)
            sayfa.background_image_id = _oku(
                request.form, "background_image_id", GORSEL
            )
            db.session.commit()
            translation_sync.sayfayi_senkronize(sayfa)
            flash("Sayfa ayarları kaydedildi.", "ok")
            return redirect(url_for("admin.page_edit", sayfa_id=sayfa.id))

    return render_template(
        "admin/page_edit.html",
        sayfa=sayfa,
        gorseller=media.listele(),
        tip_adi={t: v["label"] for t, v in BLOCK_TYPES.items()},
        aktif="sayfalar",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )
