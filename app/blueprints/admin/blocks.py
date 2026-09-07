# -*- coding: utf-8 -*-
"""Blok duzenleme, ekleme, silme, siralama.

Formlar her tip icin ELLE yazilmis (templates/admin/fields/<tip>.html).
Buradaki KAYIT sozlugu yalnizca "o formdan gelen POST hangi sutuna
yazilacak" esleşmesidir -- arayuz uretmez.
"""

from __future__ import annotations

from flask import abort, flash, redirect, render_template, request, url_for

from ... import media, security, translation_sync
from ...block_types import BLOCK_TYPES, defaults_for, is_valid_type
from ...extensions import db
from ...models import Block, Page
from . import bp
from ._form import (
    EVET_HAYIR,
    GORSEL,
    METIN,
    METIN_BOSLUKLU,
    SAYI,
    TAMSAYI,
    UZUN,
    OgeYazici,
    ayarlari_kaydet,
    ortak_alanlari_kaydet,
)

# Sayac alanlari cok yerde tekrar ediyor
SAYAC = [
    ("count_to", SAYI),
    ("count_from", SAYI, 0),
    # bastaki bosluk anlamli: " km"
    ("count_prefix", METIN_BOSLUKLU),
    ("count_suffix", METIN_BOSLUKLU),
    ("count_group", EVET_HAYIR),
    ("count_format", METIN, "group"),
]

# ------------------------------------------------------------
#  Tip -> (settings alanlari, oge gruplari)
#  Grup: (tur, alanlar) veya (tur, alanlar, [alt gruplar])
# ------------------------------------------------------------
KAYIT: dict[str, dict] = {
    "hero": {"ayarlar": [("image_id", GORSEL)], "gruplar": []},
    "rich_text": {
        "ayarlar": [],
        "gruplar": [("paragraph", [("text", UZUN)])],
    },
    "stat_grid": {
        "ayarlar": [("variant", METIN), ("columns", METIN)],
        "gruplar": [
            ("stat", [("value", METIN), ("title", METIN),
                      # hedefin resmi adi -- kartin en ustundeki etiket
                      ("subtitle", METIN),
                      ("text", UZUN), ("note", METIN)] + SAYAC),
            # izgaranin altindaki kompakt liste
            ("fact", [("title", METIN), ("text", UZUN)]),
            # bolumun altindaki tek baglanti
            ("link", [("title", METIN), ("url", METIN)]),
        ],
    },
    "stat_badge": {
        "ayarlar": [],
        "gruplar": [
            ("stat", [("value", METIN), ("title", METIN),
                      ("text", UZUN)] + SAYAC),
        ],
    },
    "card_grid": {
        "ayarlar": [("variant", METIN), ("columns", METIN)],
        "gruplar": [
            ("card",
             [("eyebrow", METIN), ("title", METIN),
              # konum / unvan -- cevrilebilir oldugu icin eyebrow degil
              ("subtitle", METIN), ("note", METIN),
              ("image_id", GORSEL),
              # kartin altindaki tek baglanti (kariyer kartlari)
              ("url", METIN), ("link_label", METIN)],
             [("paragraph", [("text", UZUN)]),
              ("bullet", [("text", UZUN)])]),
            # baslik ustu gecis cumlesi ve izgara alti aciklama kutusu
            ("lead", [("text", UZUN)]),
            ("outro", [("title", METIN), ("text", UZUN)]),
        ],
    },
    "chip_groups": {
        "ayarlar": [],
        "gruplar": [
            ("chip_group", [("title", METIN)],
             [("chip", [("title", METIN), ("note", METIN),
                        ("text", UZUN), ("url", METIN)])]),
            ("outro", [("text", UZUN), ("variant", METIN)]),
        ],
    },
    "process_steps": {
        "ayarlar": [],
        "gruplar": [
            ("step", [("eyebrow", METIN), ("title", METIN),
                      # donem / tarih -- cevrilebilir oldugu icin eyebrow degil
                      ("subtitle", METIN),
                      ("text", UZUN), ("image_id", GORSEL)]),
        ],
    },
    "timeline": {
        "ayarlar": [],
        "gruplar": [
            ("stop", [("slug", METIN), ("eyebrow", METIN),
                      ("title", METIN), ("text", UZUN),
                      ("image_id", GORSEL)]),
        ],
    },
    "map": {
        "ayarlar": [
            ("map_id", METIN),
            ("zoom", TAMSAYI), ("min_zoom", TAMSAYI), ("max_zoom", TAMSAYI),
            ("tile.url", METIN), ("tile.max_zoom", TAMSAYI),
            ("tile.attribution", METIN),
        ],
        "gruplar": [
            ("marker", [("lat", SAYI), ("lon", SAYI), ("title", METIN),
                        ("subtitle", METIN), ("text", UZUN),
                        ("variant", METIN), ("url", METIN),
                        ("link_label", METIN)]),
            ("legend", [("variant", METIN), ("title", METIN)]),
        ],
    },
    "co2_calculator": {
        "ayarlar": [
            ("number_locale", METIN),
            ("rates.fuel_per_100km.benzin", SAYI),
            ("rates.fuel_per_100km.dizel", SAYI),
            ("rates.fuel_per_100km.hev", SAYI),
            ("rates.fuel_per_100km.phev", SAYI),
            ("rates.fuel_per_100km.bev", SAYI),
            ("rates.kwh_per_100km.phev", SAYI),
            ("rates.kwh_per_100km.bev", SAYI),
            ("rates.co2_per_unit.benzin", SAYI),
            ("rates.co2_per_unit.dizel", SAYI),
            ("rates.co2_per_unit.elektrik", SAYI),
            ("rates.price_per_unit.benzin", SAYI),
            ("rates.price_per_unit.dizel", SAYI),
            ("rates.price_per_unit.elektrik", SAYI),
        ],
        "gruplar": [
            ("field", [("slug", METIN), ("title", METIN)],
             [("option", [("value", METIN), ("title", METIN)])]),
            ("label", [("slug", METIN), ("title", METIN),
                       ("subtitle", METIN), ("value", METIN)]),
        ],
    },
    "source_list": {
        "ayarlar": [],
        "gruplar": [
            ("link", [("title", METIN), ("url", METIN), ("variant", METIN)]),
        ],
    },
    "media_split": {
        "ayarlar": [("media_position", METIN)],
        "gruplar": [
            ("paragraph", [("text", UZUN)]),
            ("bullet", [("text", UZUN)]),
            ("media", [("slug", METIN), ("title", METIN), ("text", UZUN),
                       ("image_id", GORSEL)]),
        ],
    },
    "compare_table": {
        "ayarlar": [],
        "gruplar": [
            ("row", [("title", METIN)]),
            ("column",
             [("title", METIN), ("subtitle", METIN), ("note", METIN),
              ("url", METIN), ("link_label", METIN)],
             [("cell", [("text", UZUN)])]),
            ("outro", [("text", UZUN)]),
        ],
    },
    "hybrid_flow": {
        "ayarlar": [],
        "gruplar": [
            # diyagramin yazili karsiligi
            ("paragraph", [("text", UZUN)]),
            ("step", [("slug", METIN), ("eyebrow", METIN),
                      ("title", METIN), ("text", UZUN)]),
            ("outro", [("text", UZUN)]),
        ],
    },
    "tps_house": {
        "ayarlar": [],
        "gruplar": [
            # diyagramin yazili karsiligi -- tek paragraf
            ("paragraph", [("text", UZUN)]),
            ("part", [("slug", METIN), ("title", METIN),
                      ("subtitle", UZUN), ("text", UZUN)]),
        ],
    },
    "section_nav": {"ayarlar": [], "gruplar": []},
    "mission": {
        "ayarlar": [("variant", METIN)],
        "gruplar": [
            ("statement", [("text", UZUN)]),
            ("paragraph", [("text", UZUN)]),
            # bandin altindaki yonlendirme butonu
            ("link", [("title", METIN), ("url", METIN)]),
        ],
    },
    "andon": {
        "ayarlar": [],
        "gruplar": [
            ("paragraph", [("text", UZUN)]),
            ("light", [("variant", METIN), ("title", METIN), ("text", UZUN)]),
        ],
    },
    "cycle_steps": {
        "ayarlar": [("variant", METIN)],
        "gruplar": [
            ("step", [("eyebrow", METIN), ("title", METIN), ("text", UZUN)]),
            ("outro", [("title", METIN), ("text", UZUN)]),
            # akisin altindaki tek baglanti
            ("link", [("title", METIN), ("url", METIN)]),
        ],
    },
    "glossary": {
        "ayarlar": [("search_label", METIN), ("empty_label", METIN)],
        "gruplar": [
            ("term", [("slug", METIN), ("title", METIN),
                      ("subtitle", METIN), ("text", UZUN)]),
        ],
    },
    "value_columns": {
        "ayarlar": [],
        "gruplar": [
            ("column", [("title", METIN), ("subtitle", METIN)],
             [("value", [("title", METIN), ("subtitle", METIN),
                         ("text", UZUN)])]),
            ("link", [("title", METIN), ("url", METIN)]),
        ],
    },
    "fact_table": {
        "ayarlar": [],
        "gruplar": [
            ("fact", [("title", METIN), ("text", UZUN)]),
        ],
    },
    "badge_strip": {
        "ayarlar": [],
        "gruplar": [
            ("badge", [("slug", METIN), ("title", METIN), ("text", METIN),
                       ("image_id", GORSEL)]),
        ],
    },
    "news_list": {
        "ayarlar": [("limit", TAMSAYI)],
        "gruplar": [
            # slug = ISO tarih ("2026-03-12"); siralama buna gore.
            ("news", [("slug", METIN), ("title", METIN), ("text", UZUN),
                      ("url", METIN)]),
            ("link", [("title", METIN), ("url", METIN)]),
        ],
    },
    "divider": {"ayarlar": [("variant", METIN)], "gruplar": []},
}


def _blok_veya_404(blok_id: int) -> Block:
    blok = db.session.get(Block, blok_id)
    if blok is None:
        abort(404)
    return blok


def _ekran(blok: Block, **ekstra):
    return render_template(
        "admin/block_edit.html",
        blok=blok,
        sayfa=blok.page,
        tip=BLOCK_TYPES[blok.type],
        gorseller=media.listele(),
        # Kilitli blok GORUNUR ama YAZILAMAZ: editor icerigin ne
        # oldugunu gorebilsin, degistiremesin. Sablon bu bayrakla
        # formu <fieldset disabled> icine alip Kaydet'i gizler --
        # ama asil kapi security.kilit_kontrol().
        salt_okunur=blok.is_locked,
        aktif="haberler" if blok.type == "news_list" else "sayfalar",
        oturum_acik=True,
        csrf=security.csrf_token(),
        **ekstra,
    )


# ============================================================
#  Duzenleme
# ============================================================
@bp.route("/blok/<int:blok_id>", methods=["GET", "POST"])
@security.admin_gerekli
def block_edit(blok_id: int):
    blok = _blok_veya_404(blok_id)

    if request.method == "POST":
        security.csrf_dogrula()
        # Kilitli bloga yazilamaz. Kontrol BURADA, cunku sablondaki
        # gizleme elle POST atan birini durdurmaz.
        security.kilit_kontrol(blok)
        kayit = KAYIT.get(blok.type, {"ayarlar": [], "gruplar": []})

        ortak_alanlari_kaydet(blok, request.form)
        if kayit["ayarlar"]:
            ayarlari_kaydet(blok, request.form, kayit["ayarlar"])

        yazici = OgeYazici(blok, request.form)
        for grup in kayit["gruplar"]:
            tur, alanlar = grup[0], grup[1]
            alt_gruplar = grup[2] if len(grup) > 2 else []
            ustler = yazici.grup(tur, alanlar)
            if alt_gruplar:
                db.session.flush()          # yeni ustlerin id'si gereksin
                for ust in ustler:
                    anahtar = getattr(ust, "_form_anahtari", str(ust.id))
                    for alt_tur, alt_alanlar in alt_gruplar:
                        yazici.grup(alt_tur, alt_alanlar,
                                    ust=ust, ust_anahtar=anahtar)
        yazici.temizle()

        db.session.commit()

        # Turkce degistiyse Ingilizcesini uret. Elle duzeltilmis
        # ceviriler KORUNUR (bkz. translation_sync).
        translation_sync.blogu_senkronize(blok)

        flash("Blok kaydedildi. Site güncellendi.", "ok")
        return redirect(url_for("admin.block_edit", blok_id=blok.id))

    return _ekran(blok)


# ============================================================
#  Ekleme
# ============================================================
@bp.route("/sayfa/<int:sayfa_id>/blok-ekle", methods=["GET", "POST"])
@security.admin_gerekli
def block_new(sayfa_id: int):
    # KAPALI. Editor artik yeni blok EKLEYEMEZ: sayfa duzeni sabit,
    # duzenlenen tek sey haber bloklarinin icerigi.
    # Asagidaki kod BILEREK duruyor -- yeniden acmak bu satiri
    # silmekten ibaret olsun diye.
    abort(403)

    sayfa = db.session.get(Page, sayfa_id)
    if sayfa is None:
        abort(404)

    if request.method == "POST":
        security.csrf_dogrula()
        tip = (request.form.get("tip") or "").strip()
        if not is_valid_type(tip):
            flash("Geçersiz blok tipi.", "hata")
            return redirect(url_for("admin.block_new", sayfa_id=sayfa.id))

        blok = Block(
            page=sayfa,
            type=tip,
            position=len(sayfa.blocks),
            settings=defaults_for(tip),
            heading=None,
        )
        db.session.add(blok)
        db.session.commit()
        flash(f"“{BLOCK_TYPES[tip]['label']}” eklendi. Şimdi içeriğini gir.", "ok")
        return redirect(url_for("admin.block_edit", blok_id=blok.id))

    return render_template(
        "admin/block_new.html",
        sayfa=sayfa,
        tipler=[(t, v["label"], v["description"]) for t, v in BLOCK_TYPES.items()],
        aktif="sayfalar",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


# ============================================================
#  Silme
# ============================================================
@bp.route("/blok/<int:blok_id>/sil", methods=["POST"])
@security.admin_gerekli
def block_delete(blok_id: int):
    security.csrf_dogrula()
    blok = _blok_veya_404(blok_id)
    security.kilit_kontrol(blok)
    sayfa_id = blok.page_id
    etiket = BLOCK_TYPES.get(blok.type, {}).get("label", blok.type)

    db.session.delete(blok)
    db.session.flush()
    # sirayi sikistir
    kalan = db.session.get(Page, sayfa_id).blocks
    for i, b in enumerate(kalan):
        b.position = i
    db.session.commit()

    flash(f"“{etiket}” bloğu silindi.", "ok")
    return redirect(url_for("admin.page_edit", sayfa_id=sayfa_id))


# ============================================================
#  Siralama
# ============================================================
@bp.route("/sayfa/<int:sayfa_id>/sirala", methods=["POST"])
@security.admin_gerekli
def block_reorder(sayfa_id: int):
    # KAPALI. Siralama sitenin duzenini degistirir; kilidin amaci tam
    # olarak bunu engellemek. Kod BILEREK duruyor (bkz. block_new).
    abort(403)

    security.csrf_dogrula()
    sayfa = db.session.get(Page, sayfa_id)
    if sayfa is None:
        abort(404)

    ham = request.form.get("sira") or ""
    istenen = [int(p) for p in ham.split(",") if p.strip().isdigit()]
    bloklar = {b.id: b for b in sayfa.blocks}

    sira_no = 0
    for blok_id in istenen:
        blok = bloklar.pop(blok_id, None)
        if blok is not None:
            blok.position = sira_no
            sira_no += 1
    # listede olmayanlar (olmamali) sona
    for blok in bloklar.values():
        blok.position = sira_no
        sira_no += 1

    db.session.commit()
    flash("Blok sırası kaydedildi.", "ok")
    return redirect(url_for("admin.page_edit", sayfa_id=sayfa.id))


# ============================================================
#  Haberler kisayolu
#
#  Panel menusundeki "Haberler" girisi buraya gelir. Editorun sayfa
#  agacinda gezinip haber blogunu aramasi gerekmesin diye dogrudan
#  duzenlenebilir haber bloguna atar.
#
#  Birden fazla varsa menudeki sayfa sirasina, sonra blok sirasina
#  gore ilki secilir.
# ============================================================
@bp.route("/haberler")
@security.admin_gerekli
def news():
    blok = (
        db.session.query(Block)
        .join(Page)
        .filter(Block.type == "news_list", Block.is_locked.is_(False))
        .order_by(Page.nav_order, Block.position)
        .first()
    )
    if blok is None:
        flash("Düzenlenebilir bir haber bloğu bulunamadı.", "hata")
        return redirect(url_for("admin.pages"))
    return redirect(url_for("admin.block_edit", blok_id=blok.id))
