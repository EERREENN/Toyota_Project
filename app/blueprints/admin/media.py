# -*- coding: utf-8 -*-
"""Gorsel kutuphanesi ekrani."""

from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ... import media, security, translation_sync
from ...extensions import db
from ...models import MediaAsset
from . import bp


@bp.route("/gorseller", methods=["GET", "POST"])
@security.admin_gerekli
def media_library():
    if request.method == "POST":
        security.csrf_dogrula()
        try:
            varlik = media.yukle(
                request.files.get("dosya"),
                alt=request.form.get("alt"),
            )
        except media.YuklemeHatasi as hata:
            flash(str(hata), "hata")
        else:
            # alt metninin Ingilizcesini de uret
            translation_sync.nesneyi_senkronize(varlik)
            db.session.commit()
            flash(f"“{varlik.original_name}” yüklendi.", "ok")
        return redirect(url_for("admin.media_library"))

    gorseller = media.listele()
    return render_template(
        "admin/media.html",
        gorseller=gorseller,
        kullanim={g.id: media.kullanim_sayisi(g) for g in gorseller},
        boyut=media.boyut_metni,
        aktif="gorseller",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/gorsel/<int:gorsel_id>/sil", methods=["POST"])
@security.admin_gerekli
def media_delete(gorsel_id: int):
    security.csrf_dogrula()
    varlik = db.session.get(MediaAsset, gorsel_id)
    if varlik is None:
        flash("Görsel bulunamadı.", "hata")
        return redirect(url_for("admin.media_library"))

    ad = varlik.original_name or varlik.path
    try:
        media.sil(varlik)
    except media.YuklemeHatasi as hata:
        flash(str(hata), "hata")
    else:
        flash(f"“{ad}” silindi.", "ok")
    return redirect(url_for("admin.media_library"))


@bp.route("/gorsel/<int:gorsel_id>/alt", methods=["POST"])
@security.admin_gerekli
def media_alt(gorsel_id: int):
    """Gorsel aciklamasini (alt metni) guncelle."""
    security.csrf_dogrula()
    varlik = db.session.get(MediaAsset, gorsel_id)
    if varlik is None:
        flash("Görsel bulunamadı.", "hata")
        return redirect(url_for("admin.media_library"))

    varlik.alt = (request.form.get("alt") or "").strip() or None
    db.session.commit()
    translation_sync.nesneyi_senkronize(varlik)
    db.session.commit()
    flash("Görsel açıklaması kaydedildi.", "ok")
    return redirect(url_for("admin.media_library"))
