# -*- coding: utf-8 -*-
"""TMMT sayfasina uc yeni bolum ekler -- MEVCUT veritabanini sifirlamadan.

    python tools/tmmt_bolumleri.py           # ekle
    python tools/tmmt_bolumleri.py --rapor   # yazma, ne yapilacagini goster
    python tools/tmmt_bolumleri.py --geri    # eklenenleri kaldir, eskiyi geri getir

NEDEN AYRI BIR BETIK
--------------------
`tools/seed.py --reset` her seyi siler; panelden yapilmis duzenlemeler de
gider. Bu betik yalnizca eksik olani ekler ve iki kez calistirilirsa
ikinci seferde hicbir sey yapmaz.

Icerigin kendisi seed.py icindeki BOLUM_* sabitlerinden okunur -- ayni
metnin iki kopyasi olmasin diye.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app, translation_sync          # noqa: E402
from app.extensions import db                         # noqa: E402
from app.models import Block, BlockItem, Page         # noqa: E402
from tools.seed import (                              # noqa: E402
    BOLUM_KILOMETRE,
    BOLUM_PHEV,
    BOLUM_YOLCULUK,
)

# Yeri degistirilen eski blok: duz metin "Ihracat ve kilometre taslari".
# Metni zaman tunelinin giris paragrafina tasindigi icin siliniyor.
ESKI_IHRACAT_BASLIGI = "İhracat ve kilometre taşları"


def _oge_yaz(blok: Block, veri: dict, sira: int) -> BlockItem:
    oge = BlockItem(
        block=blok,
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
    return oge


def _blok_yaz(sayfa: Page, veri: dict) -> Block:
    blok = Block(
        page=sayfa,
        position=len(sayfa.blocks),      # sona ekle, sirayi sonra duzeltiyoruz
        type=veri["type"],
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
        _oge_yaz(blok, oge, sira)
    db.session.flush()
    return blok


def _bul(sayfa: Page, tip: str, baslik: str) -> Block | None:
    for b in sayfa.blocks:
        if b.type == tip and (b.heading or "") == baslik:
            return b
    return None


def _sirala(sayfa: Page, istenen: list[Block]) -> None:
    """Verilen sirayi uygula; listede olmayanlar sonda kalir."""
    for sira, blok in enumerate(istenen):
        blok.position = sira


def uygula(rapor_modu: bool) -> int:
    sayfa = db.session.query(Page).filter_by(slug="tmmt").first()
    if sayfa is None:
        print("! 'tmmt' sayfasi bulunamadi. Once: python tools/seed.py")
        return 1

    print("MEVCUT DURUM")
    for b in sayfa.blocks:
        print(f"  {b.position}. {b.type:15s} {(b.heading or '-')[:45]}")
    print()

    yolculuk = _bul(sayfa, "process_steps", BOLUM_YOLCULUK["heading"])
    kilometre = _bul(sayfa, "timeline", BOLUM_KILOMETRE["heading"])
    phev = _bul(sayfa, "stat_grid", BOLUM_PHEV["heading"])
    eski = _bul(sayfa, "rich_text", ESKI_IHRACAT_BASLIGI)

    yapilacak = []
    if yolculuk is None:
        yapilacak.append(f"EKLE   process_steps  {BOLUM_YOLCULUK['heading']}")
    if kilometre is None:
        yapilacak.append(f"EKLE   timeline       {BOLUM_KILOMETRE['heading']}")
    if phev is None:
        yapilacak.append(f"EKLE   stat_grid      {BOLUM_PHEV['heading']}")
    if eski is not None:
        yapilacak.append(f"SIL    rich_text      {ESKI_IHRACAT_BASLIGI}"
                         f"  (metni zaman tunelinin girisine tasindi)")

    if not yapilacak:
        print("Yapilacak bir sey yok -- bolumler zaten ekli.")
        return 0

    print("YAPILACAKLAR")
    for satir in yapilacak:
        print("  " + satir)
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler = []
    if yolculuk is None:
        yolculuk = _blok_yaz(sayfa, BOLUM_YOLCULUK)
        yeniler.append(yolculuk)
    if kilometre is None:
        kilometre = _blok_yaz(sayfa, BOLUM_KILOMETRE)
        yeniler.append(kilometre)
    if phev is None:
        phev = _blok_yaz(sayfa, BOLUM_PHEV)
        yeniler.append(phev)

    if eski is not None:
        db.session.delete(eski)
        db.session.flush()
        # Silinen blok koleksiyonda kalmasin: yoksa sira sayarken
        # hesaba katilir ve pozisyonlarda bosluk olusur.
        db.session.expire(sayfa, ["blocks"])

    # --- istenen sira ---
    modeller = _bul(sayfa, "rich_text", "Üretilen modeller")
    yaklasim = _bul(sayfa, "rich_text", "Üretim yaklaşımı ve çevre")
    kaynaklar = _bul(sayfa, "source_list", "Kaynaklar")

    kalanlar = [
        b for b in sayfa.blocks
        if b not in (yolculuk, kilometre, phev, modeller, yaklasim, kaynaklar)
    ]
    kalanlar.sort(key=lambda b: b.position)

    sira = kalanlar + [
        b for b in (modeller, yolculuk, kilometre, phev, yaklasim, kaynaklar)
        if b is not None
    ]
    _sirala(sayfa, sira)
    db.session.commit()

    # --- Ingilizce ceviriler ---
    print("Ingilizce ceviriler uretiliyor...")
    for blok in yeniler:
        translation_sync.blogu_senkronize(blok)
    db.session.commit()

    print()
    print("YENI DURUM")
    for b in sayfa.blocks:
        print(f"  {b.position}. {b.type:15s} {len(b.all_items):2d} oge  "
              f"{(b.heading or '-')[:45]}")
    return 0


def geri_al() -> int:
    """Eklenen uc bolumu kaldirir ve eski duz metin bolumunu geri getirir."""
    sayfa = db.session.query(Page).filter_by(slug="tmmt").first()
    if sayfa is None:
        return 1

    for tip, baslik in (
        ("process_steps", BOLUM_YOLCULUK["heading"]),
        ("timeline", BOLUM_KILOMETRE["heading"]),
        ("stat_grid", BOLUM_PHEV["heading"]),
    ):
        blok = _bul(sayfa, tip, baslik)
        if blok is not None:
            print(f"  siliniyor: {tip} — {baslik}")
            db.session.delete(blok)
    db.session.flush()

    if _bul(sayfa, "rich_text", ESKI_IHRACAT_BASLIGI) is None:
        eski = _blok_yaz(sayfa, {
            "type": "rich_text",
            "heading": ESKI_IHRACAT_BASLIGI,
            "items": [{"kind": "paragraph", "text": BOLUM_KILOMETRE["intro"]}],
        })
        translation_sync.blogu_senkronize(eski)
        print(f"  geri getirildi: rich_text — {ESKI_IHRACAT_BASLIGI}")

    modeller = _bul(sayfa, "rich_text", "Üretilen modeller")
    yaklasim = _bul(sayfa, "rich_text", "Üretim yaklaşımı ve çevre")
    kaynaklar = _bul(sayfa, "source_list", "Kaynaklar")
    eski = _bul(sayfa, "rich_text", ESKI_IHRACAT_BASLIGI)
    kalanlar = [b for b in sayfa.blocks
                if b not in (modeller, yaklasim, kaynaklar, eski)]
    kalanlar.sort(key=lambda b: b.position)
    _sirala(sayfa, kalanlar + [b for b in (modeller, eski, yaklasim, kaynaklar) if b])
    db.session.commit()
    print("geri alindi.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rapor", action="store_true", help="yazma, sadece goster")
    p.add_argument("--geri", action="store_true", help="eklenenleri kaldir")
    a = p.parse_args()

    app = create_app()
    with app.app_context():
        if a.geri:
            return geri_al()
        return uygula(a.rapor)


if __name__ == "__main__":
    sys.exit(main())
