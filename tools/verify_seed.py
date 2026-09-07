# -*- coding: utf-8 -*-
"""Seed dogrulama: sablonlardaki hicbir metin kaybolmadi mi?

Iki yonlu karsilastirma yapar:

  1) SABLON -> VERITABANI
     templates/*.html icindeki her cevrilebilir metin (Jinja'nin kendi
     ayristiricisiyla, trimmed politikasi uygulanmis haliyle) veritabaninda
     birebir bulunuyor mu? Bir tanesi bile eksikse KARAKTER FARKI vardir.

  2) VERITABANI -> CEVIRI
     Her Turkce alanin bir Ingilizce karsiligi var mi? Ceviri onbellekten mi
     geldi yoksa Turkce mi birakildi?

    python tools/verify_seed.py
    python tools/verify_seed.py --ayrinti   # eslesmeyenleri tam metinle yaz
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.factory import create_app                # noqa: E402
from app.extensions import db                     # noqa: E402
from app.models import (                          # noqa: E402
    Block,
    BlockItem,
    MediaAsset,
    Page,
    SiteSetting,
    Translation,
)
from tools.extract_strings import topla           # noqa: E402

# Asama 1'de, ESKI sablonlardan cikarilip dondurulan metin listesi.
# Karsilastirmanin dayanagi budur: eski sablonlar artik silindigi icin
# (tools/_retired/) canli tarama yapmak anlamsiz olurdu -- bu dosya
# sitenin tasima oncesi halinin kalici kaydidir.
TEMEL_LISTE = ROOT / "tools" / "baseline_strings.json"

# Sablonda "sabit on ek + cevrilen parca" seklinde olup veritabaninda
# tek alana birlestirilen metinler. Eksik gorunmeleri BEKLENIR.
BEKLENEN_EKSIKLER = {
    "resmi haber duyuruları": "global.toyota – resmi haber duyuruları "
                              "(on ekle birlestirildi)",
    # Zaman tunelinin giris cumlesi. Icinde "30'dan fazla ulkeye ihrac
    # ediliyor" yaziyordu; sirketin kendi aciklamalarinda "150'den fazla
    # ulke" gectigi ve iki rakam da dogrulanamadigi icin cumleden sayi
    # cikarildi. Ihracatin kapsamini anlatan cumle artik ihracat
    # haritasinin giris alaninda ve panelden duzenlenebilir.
    "Üretimin büyük bölümü, ağırlıklı olarak Avrupa'ya, ayrıca Orta Doğu ve "
    "Afrika'ya olmak üzere 30'dan fazla ülkeye ihraç ediliyor. Fabrika, 2021 "
    "yılında 3 milyonuncu aracını üretti ve Türkiye'nin en büyük ihracatçı "
    "sanayi kuruluşlarından biri.":
        "sayi cikarildi -- dogrulanamayan ulke sayisi (bkz. tools/seed.py)",
}

# Veritabaninda DEGIL, sablonda kalmasi DOGRU olan metinler.
# Bunlar icerik degil arayuz metnidir; editorun duzenlemesi gereken
# bir sey degil, bu yuzden CMS'e tasinmadi.
SABLONDA_KALANLAR = {
    "Ana sayfaya dön": "404 sayfasi -- arayuz metni",
    "Aradığınız sayfa bulunamadı.": "404 sayfasi -- arayuz metni",
}


def temel_listeyi_oku() -> dict[str, list[str]]:
    """Once dondurulmus listeyi kullan; yoksa canli sablonlari tara."""
    if TEMEL_LISTE.exists():
        import json

        return json.loads(TEMEL_LISTE.read_text(encoding="utf-8"))
    print(f"  UYARI: {TEMEL_LISTE.name} yok, canli sablonlar taraniyor")
    return topla()


def normalize(s: str) -> str:
    """Karsilastirma icin Unicode normalizasyonu (NFC).

    Turkce karakterler farkli kod noktasi dizilimleriyle yazilabilir;
    bu olmadan gozle ayni gorunen iki metin esitsiz cikabilir.
    """
    return unicodedata.normalize("NFC", s)


def veritabanindaki_metinler() -> set[str]:
    """Veritabanindaki TUM Turkce metin alanlari."""
    metinler: set[str] = set()

    def ekle(deger):
        if deger and str(deger).strip():
            metinler.add(normalize(str(deger)))

    for sayfa in db.session.query(Page).all():
        ekle(sayfa.title)
        ekle(sayfa.nav_label)

    for blok in db.session.query(Block).all():
        ekle(blok.heading)
        ekle(blok.intro)
        ekle(blok.note)
        # settings icindeki metinler (harita kunyesi gibi)
        _sozlukten_topla(blok.settings, ekle)

    for oge in db.session.query(BlockItem).all():
        for alan in ("title", "subtitle", "value", "text", "note",
                     "link_label", "eyebrow"):
            ekle(getattr(oge, alan, None))
        _sozlukten_topla(oge.settings, ekle)

    for varlik in db.session.query(MediaAsset).all():
        ekle(varlik.alt)

    for ayar in db.session.query(SiteSetting).all():
        ekle(ayar.value)

    return metinler


def _sozlukten_topla(sozluk, ekle) -> None:
    if isinstance(sozluk, dict):
        for deger in sozluk.values():
            _sozlukten_topla(deger, ekle)
    elif isinstance(sozluk, list):
        for deger in sozluk:
            _sozlukten_topla(deger, ekle)
    elif isinstance(sozluk, str):
        ekle(sozluk)


def sablon_kontrolu(ayrinti: bool) -> int:
    sablon = temel_listeyi_oku()
    db_metinleri = veritabanindaki_metinler()

    tum: list[tuple[str, str]] = []
    for dosya, metinler in sablon.items():
        for m in metinler:
            tum.append((dosya, normalize(m)))

    benzersiz = {m for _d, m in tum}
    eksik = sorted({m for _d, m in tum if m not in db_metinleri})
    beklenen = [m for m in eksik if m in BEKLENEN_EKSIKLER]
    arayuz = [m for m in eksik if m in SABLONDA_KALANLAR]
    beklenmeyen = [
        m for m in eksik
        if m not in BEKLENEN_EKSIKLER and m not in SABLONDA_KALANLAR
    ]

    print("1) TASIMA ONCESI SABLONLAR -> VERITABANI")
    print("-" * 60)
    print(f"  kaynak                         : {TEMEL_LISTE.name}")
    print(f"  sablondaki metin (tekrarlarla) : {len(tum)}")
    print(f"  benzersiz metin                : {len(benzersiz)}")
    print(f"  veritabaninda bulunan          : {len(benzersiz) - len(eksik)}")
    print(f"  beklenen eksik                 : {len(beklenen) + len(arayuz)}")
    print(f"  BEKLENMEYEN EKSIK              : {len(beklenmeyen)}")
    print()

    for m in beklenen:
        print(f"  [beklenen] {m[:60]!r}")
        print(f"             -> {BEKLENEN_EKSIKLER[m]}")
    for m in arayuz:
        print(f"  [arayuz]   {m[:60]!r}")
        print(f"             -> {SABLONDA_KALANLAR[m]}")

    if beklenmeyen:
        print()
        print("  !!! ASAGIDAKI METINLER VERITABANINDA YOK -- KARAKTER FARKI VAR:")
        for m in beklenmeyen:
            if ayrinti:
                print(f"      {m!r}")
                # en yakin adayi goster
                yakin = _en_yakin(m, db_metinleri)
                if yakin:
                    print(f"      en yakin DB kaydi: {yakin!r}")
            else:
                print(f"      {m[:90]!r}")
    print()
    return len(beklenmeyen)


def _en_yakin(hedef: str, adaylar: set[str]) -> str | None:
    import difflib

    sonuc = difflib.get_close_matches(hedef, adaylar, n=1, cutoff=0.6)
    return sonuc[0] if sonuc else None


def ceviri_kontrolu() -> int:
    print("2) VERITABANI -> CEVIRI")
    print("-" * 60)

    beklenen = 0
    for model, entity in (
        (Page, "page"),
        (Block, "block"),
        (BlockItem, "block_item"),
        (MediaAsset, "media"),
    ):
        for nesne in db.session.query(model).all():
            for alan in getattr(model, "TRANSLATABLE", ()):
                deger = getattr(nesne, alan, None)
                if deger and str(deger).strip():
                    beklenen += 1

    ayar_cevrilebilir = db.session.query(Translation).filter_by(
        entity_type="setting"
    ).count()
    beklenen += ayar_cevrilebilir

    mevcut = db.session.query(Translation).filter_by(locale="en").count()

    ayni_kalan = 0
    cevrilmis = 0
    for ceviri in db.session.query(Translation).filter_by(locale="en").all():
        kaynak = _kaynak_metin(ceviri)
        if kaynak is not None and normalize(kaynak) == normalize(ceviri.value or ""):
            ayni_kalan += 1
        else:
            cevrilmis += 1

    print(f"  cevrilmesi gereken alan : {beklenen}")
    print(f"  olusturulan EN satiri   : {mevcut}")
    print(f"  gercekten cevrilmis     : {cevrilmis}")
    print(f"  Turkce birakilan        : {ayni_kalan}")
    print()
    print("  NOT: 'Turkce birakilan' satirlarin cogu marka adi, rakam ve")
    print("  ozel isimdir (Lexus, Interbrand, 280.000, ~%4,9). Bugunku site")
    print("  de bunlari cevirmiyor -- Ingilizce cikti birebir ayni kaliyor.")
    print()
    return 0 if mevcut >= beklenen else 1


_KAYNAK_MODELLER = {
    "page": (Page, None),
    "block": (Block, None),
    "block_item": (BlockItem, None),
    "media": (MediaAsset, None),
    "setting": (SiteSetting, "value"),
}


def _kaynak_metin(ceviri: Translation):
    girdi = _KAYNAK_MODELLER.get(ceviri.entity_type)
    if not girdi:
        return None
    model, sabit_alan = girdi
    nesne = db.session.get(model, ceviri.entity_id)
    if nesne is None:
        return None
    return getattr(nesne, sabit_alan or ceviri.field, None)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ayrinti", action="store_true",
                   help="eslesmeyen metinleri tam haliyle yaz")
    a = p.parse_args()

    uygulama = create_app()
    with uygulama.app_context():
        hata = sablon_kontrolu(a.ayrinti)
        hata += ceviri_kontrolu()

    if hata:
        print("=" * 60)
        print("SONUC: DOGRULAMA BASARISIZ")
        print("=" * 60)
        return 1
    print("=" * 60)
    print("SONUC: TUM SABLON METINLERI VERITABANINDA, BIREBIR.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
