# -*- coding: utf-8 -*-
"""Blok bazinda ceviri ekrani.

Neden ayri ekran: her alanin yanina bir de Ingilizce kutusu koymak
12 formu iki katina cikarirdi ve editorun asil isi olan Turkce yazimi
zorlastirirdi. Bunun yerine "once Turkce'yi yaz, sonra Ingilizce'yi
gozden gecir" akisi kuruldu.
"""

from __future__ import annotations

from flask import abort, flash, redirect, render_template, request, url_for

from ... import security, translation_sync
from ...block_types import BLOCK_TYPES
from ...extensions import db
from ...models import Block
from . import bp


@bp.route("/blok/<int:blok_id>/ceviri", methods=["GET", "POST"])
@security.admin_gerekli
def block_translations(blok_id: int):
    blok = db.session.get(Block, blok_id)
    if blok is None:
        abort(404)

    if request.method == "POST":
        security.csrf_dogrula()
        eylem = request.form.get("eylem") or "kaydet"

        if eylem == "hepsini_yenile":
            # Elle duzeltilenler dahil HEPSINI yeniden uret
            translation_sync.blogu_senkronize(blok, zorla=True)
            flash("Tüm çeviriler yeniden üretildi.", "ok")
            return redirect(url_for("admin.block_translations", blok_id=blok.id))

        if eylem.startswith("otomatige_don:"):
            anahtar = eylem.split(":", 1)[1]
            nesne, tur, alan = translation_sync.nesne_coz(anahtar)
            if nesne is not None:
                translation_sync.otomatige_don(nesne, tur, alan)
                db.session.commit()
                flash("Bu alan otomatik çeviriye döndürüldü.", "ok")
            return redirect(url_for("admin.block_translations", blok_id=blok.id))

        if eylem.startswith("yeniden_cevir:"):
            anahtar = eylem.split(":", 1)[1]
            nesne, tur, alan = translation_sync.nesne_coz(anahtar)
            if nesne is not None:
                translation_sync.alani_senkronize(nesne, tur, alan, zorla=True)
                db.session.commit()
                flash("Alan yeniden çevrildi.", "ok")
            return redirect(url_for("admin.block_translations", blok_id=blok.id))

        # --- normal kaydetme: elle yazilan cevirileri isle ---
        degisen = 0
        for ad, deger in request.form.items():
            if not ad.startswith("en__"):
                continue
            anahtar = ad[4:]
            nesne, tur, alan = translation_sync.nesne_coz(anahtar)
            if nesne is None:
                continue
            mevcut = translation_sync.ceviri_degeri(nesne, tur, alan) or ""
            if (deger or "").strip() == mevcut.strip():
                continue                      # dokunulmamis alani kilitleme
            translation_sync.elle_kaydet(nesne, tur, alan, deger)
            degisen += 1

        db.session.commit()
        if degisen:
            flash(f"{degisen} çeviri elle kaydedildi ve kilitlendi.", "ok")
        else:
            flash("Değişiklik yok.", "ok")
        return redirect(url_for("admin.block_translations", blok_id=blok.id))

    return render_template(
        "admin/block_translations.html",
        blok=blok,
        sayfa=blok.page,
        tip=BLOCK_TYPES.get(blok.type, {"label": blok.type}),
        alanlar=translation_sync.blok_alanlari(blok),
        etiket=translation_sync.DURUM_ETIKET,
        aktif="sayfalar",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )
