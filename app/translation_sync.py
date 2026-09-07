# -*- coding: utf-8 -*-
"""Ceviri akisi: TR degisince EN uret, ELLE DUZELTILENI EZME.

KURAL (istenen davranis)
------------------------
    Ceviri satiri yok            -> otomatik uret
    Var, is_manual = False       -> yeniden uret, uzerine yaz
    Var, is_manual = True        -> DOKUNMA. Kaynak degistiyse
                                    "bayat" olarak isaretle, editor
                                    gorup karar versin.

`source_hash`, cevirinin uretildigi Turkce metnin parmak izidir. Turkce
sonradan degisirse esitlik bozulur ve panel "kaynak değişti" rozeti
gosterir.

AG KULLANIMI
------------
auto_translate zaten onbellekli ve devre kesicili: onbellekte olan metin
aninda doner, ag yoksa kisa surede vazgecer ve Turkce'yi dondurur. Bu
yuzden kaydetme islemi ag olmadan da calisir; ceviri uretilemezse satir
"bayat" kalir, veri kaybi olmaz.
"""

from __future__ import annotations

import auto_translate

from .extensions import db
from .models import (
    Block,
    BlockItem,
    MediaAsset,
    Page,
    Translation,
    text_hash,
)

# Durumlar (panelde rozet olarak gosterilir)
DURUM_YOK = "yok"
DURUM_OTOMATIK = "otomatik"
DURUM_ELLE = "elle"
DURUM_BAYAT = "bayat"

DURUM_ETIKET = {
    DURUM_YOK: "çeviri yok",
    DURUM_OTOMATIK: "otomatik",
    DURUM_ELLE: "elle düzenlendi",
    DURUM_BAYAT: "kaynak değişti",
}


def _satir(entity_type: str, entity_id: int, alan: str, locale: str):
    return (
        db.session.query(Translation)
        .filter_by(
            entity_type=entity_type,
            entity_id=entity_id,
            field=alan,
            locale=locale,
        )
        .first()
    )


def durum(nesne, entity_type: str, alan: str, locale: str = "en") -> str:
    kaynak = getattr(nesne, alan, None)
    satir = _satir(entity_type, nesne.id, alan, locale)
    if satir is None or not satir.value:
        return DURUM_YOK
    if satir.is_stale(kaynak):
        return DURUM_BAYAT
    return DURUM_ELLE if satir.is_manual else DURUM_OTOMATIK


def ceviri_degeri(nesne, entity_type: str, alan: str, locale: str = "en"):
    satir = _satir(entity_type, nesne.id, alan, locale)
    return satir.value if satir else None


# ============================================================
#  Otomatik uretim
# ============================================================
def alani_senkronize(nesne, entity_type: str, alan: str,
                     locale: str = "en", zorla: bool = False) -> str:
    """Tek bir alanin cevirisini gozden gecirir. Durum dondurur."""
    kaynak = getattr(nesne, alan, None)
    satir = _satir(entity_type, nesne.id, alan, locale)

    # Kaynak bosaldiysa ceviri de anlamsiz
    if not kaynak or not str(kaynak).strip():
        if satir is not None:
            db.session.delete(satir)
        return DURUM_YOK

    if satir is not None and satir.is_manual and not zorla:
        # Editorun yazdigi ceviriye DOKUNMA; sadece bayat mi diye bak.
        return DURUM_BAYAT if satir.is_stale(kaynak) else DURUM_ELLE

    if satir is not None and not satir.is_stale(kaynak) and satir.value and not zorla:
        return DURUM_OTOMATIK          # zaten guncel, agi yorma

    cevrilen = auto_translate.translate(str(kaynak), locale)

    if satir is None:
        satir = Translation(
            entity_type=entity_type,
            entity_id=nesne.id,
            field=alan,
            locale=locale,
        )
        db.session.add(satir)

    satir.value = cevrilen
    satir.source_hash = text_hash(kaynak)
    satir.is_manual = False
    return DURUM_OTOMATIK


def _nesne_alanlari(nesne) -> tuple[str, tuple[str, ...]]:
    if isinstance(nesne, Page):
        return "page", Page.TRANSLATABLE
    if isinstance(nesne, Block):
        return "block", Block.TRANSLATABLE
    if isinstance(nesne, BlockItem):
        return "block_item", nesne.translatable_fields
    if isinstance(nesne, MediaAsset):
        return "media", MediaAsset.TRANSLATABLE
    raise TypeError(f"Ceviri desteklenmeyen tur: {type(nesne).__name__}")


def nesneyi_senkronize(nesne, locale: str = "en", zorla: bool = False) -> None:
    entity_type, alanlar = _nesne_alanlari(nesne)
    for alan in alanlar:
        alani_senkronize(nesne, entity_type, alan, locale, zorla)


def blogu_senkronize(blok: Block, locale: str = "en", zorla: bool = False) -> None:
    """Blogun ve tum ogelerinin cevirilerini gozden gecirir."""
    nesneyi_senkronize(blok, locale, zorla)
    for oge in blok.all_items:
        nesneyi_senkronize(oge, locale, zorla)
    db.session.commit()


def sayfayi_senkronize(sayfa: Page, locale: str = "en", zorla: bool = False) -> None:
    nesneyi_senkronize(sayfa, locale, zorla)
    db.session.commit()


# ============================================================
#  Elle duzeltme
# ============================================================
def elle_kaydet(nesne, entity_type: str, alan: str, deger: str | None,
                locale: str = "en") -> None:
    """Editorun yazdigi ceviriyi kaydeder ve KILITLER."""
    kaynak = getattr(nesne, alan, None)
    satir = _satir(entity_type, nesne.id, alan, locale)
    temiz = (deger or "").strip()

    if not temiz:
        # Bosaltmak = "otomatige don" demek
        if satir is not None:
            satir.is_manual = False
            satir.value = None
            satir.source_hash = ""
        return

    if satir is None:
        satir = Translation(
            entity_type=entity_type,
            entity_id=nesne.id,
            field=alan,
            locale=locale,
        )
        db.session.add(satir)

    satir.value = temiz
    satir.is_manual = True
    satir.source_hash = text_hash(kaynak)


def otomatige_don(nesne, entity_type: str, alan: str, locale: str = "en") -> None:
    """Elle kilidi kaldirir ve yeniden otomatik uretir."""
    satir = _satir(entity_type, nesne.id, alan, locale)
    if satir is not None:
        satir.is_manual = False
    alani_senkronize(nesne, entity_type, alan, locale, zorla=True)


# ============================================================
#  Panelde gosterilecek liste
# ============================================================
def blok_alanlari(blok: Block, locale: str = "en") -> list[dict]:
    """Blogun tum cevrilebilir alanlari, durumlariyla birlikte.

    Panel bu listeyi dolasarak TR (salt okunur) + EN (duzenlenebilir)
    ciftlerini basar.
    """
    satirlar: list[dict] = []

    def ekle(nesne, entity_type, alanlar, baslik):
        for alan in alanlar:
            kaynak = getattr(nesne, alan, None)
            if not kaynak or not str(kaynak).strip():
                continue
            satirlar.append({
                "anahtar": f"{entity_type}:{nesne.id}:{alan}",
                "grup": baslik,
                "alan": alan,
                "alan_adi": ALAN_ADLARI.get(alan, alan),
                "tr": str(kaynak),
                "en": ceviri_degeri(nesne, entity_type, alan, locale) or "",
                "durum": durum(nesne, entity_type, alan, locale),
                "uzun": len(str(kaynak)) > 90,
            })

    ekle(blok, "block", Block.TRANSLATABLE, "Blok")
    for oge in blok.items:
        baslik = (oge.title or oge.value or oge.text or "")[:40] or "Öğe"
        ekle(oge, "block_item", oge.translatable_fields, baslik)
        for alt in oge.children:
            alt_baslik = f"{baslik} › {(alt.title or alt.text or '')[:30]}"
            ekle(alt, "block_item", alt.translatable_fields, alt_baslik)
    return satirlar


ALAN_ADLARI = {
    "heading": "Başlık",
    "intro": "Giriş paragrafı",
    "note": "Kaynak dipnotu",
    "title": "Başlık / etiket",
    "subtitle": "Alt başlık",
    "text": "Metin",
    "value": "Rakam",
    "link_label": "Bağlantı yazısı",
    "alt": "Görsel açıklaması",
}


def nesne_coz(anahtar: str):
    """'block_item:42:title' -> (nesne, entity_type, alan)"""
    try:
        entity_type, ham_id, alan = anahtar.split(":", 2)
        nesne_id = int(ham_id)
    except (ValueError, TypeError):
        return None, None, None

    model = {
        "page": Page,
        "block": Block,
        "block_item": BlockItem,
        "media": MediaAsset,
    }.get(entity_type)
    if model is None:
        return None, None, None

    nesne = db.session.get(model, nesne_id)
    if nesne is None:
        return None, None, None

    _tur, izinli = _nesne_alanlari(nesne)
    if alan not in izinli:
        return None, None, None       # uydurma alan adiyla yazma girisimi
    return nesne, entity_type, alan
