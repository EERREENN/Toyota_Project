# -*- coding: utf-8 -*-
"""Mevcut bir sayfaya bolum ekleyen betiklerin paylastigi yardimcilar.

Kullananlar:
    tools/tmmt_bolumleri2.py    TMMT sayfasi, 2. grup bolumler
    tools/global_bolumleri.py   Global Toyota sayfasi

Ne yapar: seed.py'deki BOLUM_* sozluklerini MEVCUT veritabanina yazar,
blok sirasini seed.py'deki sayfa tanimindan uretir ve cevrilmemesi
gereken metinleri kilitler. Ne yapmaz: veritabanini sifirlamak
(o `tools/seed.py --reset`in isi).

BURASI ARAYUZ URETMEZ. Panel formlari her tip icin elle yazilidir
(templates/admin/fields/<tip>.html); buradaki kod yalnizca seed
sozluklerini modellere cevirir.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import auto_translate                                # noqa: E402
from app import translation_sync                     # noqa: E402
from app.extensions import db                        # noqa: E402
from app.models import Block, BlockItem, Page        # noqa: E402
from tools.seed import KILITLI_CEVIRI                # noqa: E402


# ============================================================
#  Yazma
# ============================================================
def oge_yaz(blok: Block, veri: dict, sira: int,
            ust: BlockItem | None = None) -> BlockItem:
    """Bir ogeyi (ve varsa alt ogelerini) yazar."""
    oge = BlockItem(
        block=blok,
        parent=ust,
        position=sira,
        kind=veri.get("kind", "item"),
        variant=veri.get("variant"),
        slug=veri.get("slug"),
        eyebrow=veri.get("eyebrow"),
        title=veri.get("title"),
        subtitle=veri.get("subtitle"),
        value=veri.get("value"),
        text=veri.get("text"),
        note=veri.get("note"),
        url=veri.get("url"),
        link_label=veri.get("link_label"),
        lat=veri.get("lat"),
        lon=veri.get("lon"),
        count_to=veri.get("count_to"),
        count_from=veri.get("count_from", 0),
        count_prefix=veri.get("count_prefix"),
        count_suffix=veri.get("count_suffix"),
        count_group=veri.get("count_group", False),
        count_format=veri.get("count_format", "group"),
        settings=veri.get("settings", {}) or {},
    )
    db.session.add(oge)
    db.session.flush()                      # alt ogelerin ust id'si gereksin
    for alt_sira, alt in enumerate(veri.get("children", [])):
        oge_yaz(blok, alt, alt_sira, ust=oge)
    return oge


def blok_yaz(sayfa: Page, veri: dict) -> Block:
    """Blogu sayfanin SONUNA ekler; sirayi `sirala` duzeltir."""
    blok = Block(
        page=sayfa,
        position=len(sayfa.blocks),
        type=veri["type"],
        anchor=veri.get("anchor"),
        heading=veri.get("heading"),
        heading_level=veri.get("heading_level", 2),
        intro=veri.get("intro"),
        note=veri.get("note"),
        reveal=veri.get("reveal"),
        settings=veri.get("settings", {}) or {},
    )
    db.session.add(blok)
    db.session.flush()
    for sira, oge in enumerate(veri.get("items", [])):
        oge_yaz(blok, oge, sira)
    db.session.flush()
    return blok


# ============================================================
#  Bulma ve siralama
# ============================================================
def bul(sayfa: Page, tip: str, baslik: str, haric=()) -> Block | None:
    """Sayfadaki ilk (tip, baslik) eslesmesi. Basligi bos blok icin ''.

    `haric`: atlanacak bloklar. Ayni (tip, baslik) ciftinden birden
    fazla olabilir -- TPS sayfasindaki iki dekoratif `divider` gibi --
    ve o zaman her seed blogu AYRI bir sayfa blogana eslenmeli; yoksa
    ikisi de birinciyi bulur, ikincisi eslesmemis sayilip sona duser.
    """
    for b in sayfa.blocks:
        if b in haric:
            continue
        if b.type == tip and (b.heading or "") == (baslik or ""):
            return b
    return None


def sirala(sayfa: Page, istenen: list[Block]) -> None:
    for sira, blok in enumerate(istenen):
        blok.position = sira


def hedef_sira(sayfa: Page, sayfa_verisi: dict) -> list[Block]:
    """Istenen blok sirasi -- seed.py'deki sayfa tanimindan uretilir.

    Tek dogruluk kaynagi orasi: bolumlerin sayfadaki yeri iki dosyada
    ayri ayri tarif edilmesin. Eslesmeyen (editorun sonradan ekledigi)
    bloklar sirayi bozmamak icin sona alinir.
    """
    sirali: list[Block] = []
    for veri in sayfa_verisi["blocks"]:
        blok = bul(sayfa, veri["type"], veri.get("heading") or "", haric=sirali)
        if blok is not None:
            sirali.append(blok)
    kalanlar = sorted(
        (b for b in sayfa.blocks if b not in sirali), key=lambda b: b.position
    )
    return sirali + kalanlar


# ============================================================
#  Cevrilmemesi gereken metinler
# ============================================================
def cevirileri_kilitle(bloklar: list[Block]) -> int:
    """Otomatik cevirinin bozdugu kisa metinleri elle yazip kilitler.

    Iki durum var (bkz. seed.py -> KILITLI_CEVIRI):
      1. Ingilizce/Japonca ozel terimler: kaynak sutunu Turkce ama metin
         cevrilmemeli ("Kaizen", "Global Excellence in Manufacturing").
      2. Baglamsiz kisa metinler: "Mısır" ulke degil tahil, "Toplumla
         birlikte" ise "with society" gibi bozuk cikiyor.

    Ikisi de is_manual=True yazilir; panelde "elle duzenlendi" gorunur
    ve bir daha otomatik uretilmez. Zaten dogru ve kilitli olana
    dokunulmaz -- betik tekrar tekrar calistirilabilsin diye.

    Degisen satir sayisini dondurur.
    """
    def _uygula(nesne, entity_type: str, alan: str) -> int:
        kaynak = getattr(nesne, alan, None) or ""
        karsilik = KILITLI_CEVIRI.get(kaynak)
        if not karsilik:
            return 0
        mevcut = translation_sync.ceviri_degeri(nesne, entity_type, alan)
        if mevcut == karsilik and translation_sync.durum(
            nesne, entity_type, alan
        ) == translation_sync.DURUM_ELLE:
            return 0
        translation_sync.elle_kaydet(nesne, entity_type, alan, karsilik)
        return 1

    sayi = 0
    for blok in bloklar:
        sayi += _uygula(blok, "block", "heading")
        for oge in blok.all_items:
            sayi += _uygula(oge, "block_item", "title")
            # Deger kartlarinin alt basligi da terim olabilir
            # (sutun basliklarindaki "Continuous Improvement" gibi).
            sayi += _uygula(oge, "block_item", "subtitle")
            # Kisa govde metinleri de takilabiliyor (tablo hucresindeki
            # "Yok." gibi). Eslesme TAM METIN uzerinden oldugu icin uzun
            # paragraflarin yanlislikla yakalanma ihtimali yok.
            sayi += _uygula(oge, "block_item", "text")
    return sayi


# ============================================================
#  Ceviri onarimi
# ============================================================
def _turkce_kalanlar(bloklar: list[Block], locale: str) -> list[tuple]:
    """(nesne, entity_type, alan, kaynak) -- Ingilizcesi Turkce kalmis olanlar.

    Cok sayida metni pespese cevirirken Google bazen hiz sinirina takilip
    "ceviri bulunamadi" donuyor; deep-translator bunu "cevrilemez" sayip
    KAYNAK METNI donduruyor ve auto_translate onu onbellege oyle yaziyor.
    Sonuc: Ingilizce sayfada Turkce metin, ustelik bir daha denenmiyor
    (ne onbellek ne de `source_hash` bayat gorunuyor).

    Burada o satirlar toplaniyor. "Prius", "Kaizen" gibi gercekten
    cevrilmeyen ozel isimler elenmis olsun diye olcut warm_cache.py ile
    ayni: en az iki kelimeli ve kucuk harf iceren metinler.
    """
    adaylar = []
    for blok in bloklar:
        for nesne, tur, alanlar in (
            [(blok, "block", Block.TRANSLATABLE)]
            + [(o, "block_item", o.translatable_fields) for o in blok.all_items]
        ):
            for alan in alanlar:
                kaynak = getattr(nesne, alan, None)
                if not kaynak or not str(kaynak).strip():
                    continue
                metin = str(kaynak)
                if " " not in metin or len(metin) <= 3:
                    continue          # tek kelime -> ozel isim olabilir
                if not any(c.islower() for c in metin):
                    continue
                if translation_sync.durum(nesne, tur, alan, locale) ==                         translation_sync.DURUM_ELLE:
                    continue          # editorun / kilit listesinin karari
                mevcut = translation_sync.ceviri_degeri(nesne, tur, alan, locale)
                if mevcut and mevcut != metin:
                    continue          # zaten cevrilmis
                adaylar.append((nesne, tur, alan, metin))
    return adaylar


def cevirileri_tamamla(bloklar: list[Block], locale: str = "en",
                       deneme: int = 3, bekleme: float = 1.2) -> int:
    """Turkce kalmis cevirileri yavaslatilmis hizda yeniden dener.

    Google'in ucretsiz ucu, pespese cok istek gelince arada bir
    "ceviri bulunamadi" donuyor ve deep-translator bunu KAYNAK METIN
    olarak veriyor -- yani hata sessiz. Tek bir deneme yeterli degil:
    ayni metin biraz sonra sorunsuz cevriliyor. Bu yuzden her metin
    icin `deneme` kadar hak var ve denemeler arasi bekleme artiyor.

    Duzeltilen satir sayisini dondurur; sifir donmesi "artik yapacak
    bir sey yok" demek degildir, kalanlar icin betigi tekrar calistir.
    """
    adaylar = _turkce_kalanlar(bloklar, locale)
    if not adaylar:
        return 0

    print(f"  {len(adaylar)} metin Turkce kalmis, yeniden deneniyor...")
    duzelen = 0
    for sira, (nesne, tur, alan, metin) in enumerate(adaylar, 1):
        for tur_no in range(deneme):
            kalan = auto_translate.pause_remaining()
            if kalan > 0:
                print(f"    ... hiz siniri, {int(kalan) + 1} sn bekleniyor")
                time.sleep(kalan + 1)
            yeni_metin = auto_translate.translate_fresh(metin, locale)
            if yeni_metin and yeni_metin != metin:
                # Onbellek duzeldi; ceviri satirini zorla yeniden uret.
                translation_sync.alani_senkronize(nesne, tur, alan, locale,
                                                  zorla=True)
                duzelen += 1
                break
            time.sleep(bekleme * (tur_no + 1))
        print(f"    [{sira}/{len(adaylar)}] {duzelen} duzeldi", end="\r")
    print(" " * 60, end="\r")
    db.session.commit()
    return duzelen


# ============================================================
#  Capalar (bolum menusu icin)
# ============================================================
def capalari_uygula(sayfa: Page, sayfa_verisi: dict) -> int:
    """seed.py'deki `anchor` degerlerini MEVCUT bloklara yazar.

    Bolum menusu (section_nav) sayfayi tarayip `anchor` alani dolu ve
    basligi olan bloklari listeliyor; taze seed'de capalar yerinde ama
    daha once kurulmus veritabanlarinda yok. ELLE DEGISTIRILMIS capaya
    dokunulmaz -- yalnizca bos olan doldurulur.

    Yazilan capa sayisini dondurur.
    """
    sayi = 0
    for veri in sayfa_verisi["blocks"]:
        capa = veri.get("anchor")
        if not capa:
            continue
        blok = bul(sayfa, veri["type"], veri.get("heading") or "")
        if blok is not None and not blok.anchor:
            blok.anchor = capa
            sayi += 1
    return sayi
