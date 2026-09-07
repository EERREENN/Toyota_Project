# -*- coding: utf-8 -*-
"""Tum sayfalarin cevirilerini toplu gozden gecirir.

Panelde her blogun kendi "Hepsini yeniden cevir" dugmesi var; bu betik
ayni isi 27 blogun tamami icin tek seferde yapar.

    python tools/ceviri_yenile.py            # eksik ve bayat olanlari tamamla
    python tools/ceviri_yenile.py --hepsi    # ELLE DUZELTILENLER DAHIL hepsini yenile
    python tools/ceviri_yenile.py --rapor    # yazma, sadece durumu goster

VARSAYILAN DAVRANIS ELLE DUZELTILENLERE DOKUNMAZ. `--hepsi` bunu ezer;
editorun yazdigi Ingilizce metinler kaybolur, o yuzden onay ister.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app, translation_sync as ts   # noqa: E402
from app.extensions import db                        # noqa: E402
from app.models import Block, Page                   # noqa: E402


def durumlari_topla() -> Counter:
    sayac: Counter = Counter()
    for sayfa in db.session.query(Page).all():
        for alan in Page.TRANSLATABLE:
            if getattr(sayfa, alan, None):
                sayac[ts.durum(sayfa, "page", alan)] += 1
    for blok in db.session.query(Block).all():
        for satir in ts.blok_alanlari(blok):
            sayac[satir["durum"]] += 1
    return sayac


def yaz_durum(baslik: str, sayac: Counter) -> None:
    print(f"  {baslik}")
    for anahtar in ("otomatik", "elle", "bayat", "yok"):
        if sayac.get(anahtar):
            print(f"    {ts.DURUM_ETIKET[anahtar]:20s} {sayac[anahtar]}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--hepsi", action="store_true",
                   help="elle duzeltilenler dahil hepsini yeniden cevir")
    p.add_argument("--rapor", action="store_true", help="yazma, sadece goster")
    a = p.parse_args()

    app = create_app()
    with app.app_context():
        print()
        yaz_durum("BASLANGIC DURUMU", durumlari_topla())

        if a.rapor:
            return 0

        if a.hepsi:
            print()
            print("  UYARI: --hepsi, editorun ELLE yazdigi cevirileri de siler.")
            onay = input("  Devam etmek icin 'evet' yaz: ").strip().lower()
            if onay != "evet":
                print("  Vazgecildi.")
                return 1

        print()
        print("  ceviriler gozden geciriliyor...")
        sayfalar = db.session.query(Page).all()
        for sayfa in sayfalar:
            ts.sayfayi_senkronize(sayfa, zorla=a.hepsi)

        bloklar = db.session.query(Block).order_by(Block.id).all()
        for i, blok in enumerate(bloklar, 1):
            ts.blogu_senkronize(blok, zorla=a.hepsi)
            print(f"    [{i}/{len(bloklar)}] {blok.type}", end="\r")
        print(" " * 50, end="\r")

        print()
        yaz_durum("SON DURUM", durumlari_topla())
        print()
        print("  Not: 'kaynak degisti' kalan alanlar, Turkcesi degismis ama")
        print("  Ingilizcesi ELLE yazilmis alanlardir -- bilerek korunuyorlar.")
        print("  Panelden tek tek gozden gecir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
