# -*- coding: utf-8 -*-
"""block tablosuna `is_locked` sutununu ekler (tek seferlik goc).

Projede Alembic/Flask-Migrate YOK. Sema degisikligi elle yapiliyor;
bu betik o degisikligi guvenle uygulayan tek yerdir.

    python tools/kilit_ekle.py            # sutunu ekle ve haberleri ac
    python tools/kilit_ekle.py --rapor    # yazma, sadece ne yapacagini goster

IKI KEZ CALISTIRILABILIR. Ikinci seferde sutunun zaten var oldugunu
gorup atlar, guncellenecek satir bulamaz ve hicbir sey yapmadan cikar.

NEDEN HAM SQL?
--------------
`app.models` artik `is_locked` alanini BILDIRIYOR ama veritabaninda
sutun HENUZ YOK. Bu betigi ORM uzerinden yazmak, ORM'in var olmayan bir
sutunu SELECT etmesine ve daha ilk sorguda patlamasina yol acardi.
Bu yuzden dogrudan sqlite3 ile calisiyoruz.

NE YAPAR
--------
1. `PRAGMA table_info(block)` -> sutun zaten var mi?
2. Yoksa: ALTER TABLE block ADD COLUMN is_locked BOOLEAN NOT NULL DEFAULT 1
   (yani MEVCUT TUM BLOKLAR KILITLENIR)
3. UPDATE block SET is_locked = 0 WHERE type = 'news_list'
   (yalnizca haber bloklari acilir)
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import Config                       # noqa: E402

SUTUN = "is_locked"
TABLO = "block"
# Panelden duzenlenmeye ACIK kalacak tek blok tipi.
# Baska bir tipi de acmak icin bu listeye eklemek yeterli.
ACIK_TIPLER = ("news_list",)


def veritabani_yolu() -> Path:
    """Config'teki sqlite adresini gercek dosya yoluna cevirir.

    Goreli sqlite yolu (varsayilan "sqlite:///toyota.db") Flask'in
    instance/ klasorune yazilir -- factory.py orayi ROOT/instance
    olarak sabitliyor.
    """
    uri = Config.SQLALCHEMY_DATABASE_URI
    if not uri.startswith("sqlite"):
        raise SystemExit(
            f"Bu betik yalnizca SQLite ile calisir. Bulunan adres: {uri}"
        )
    ham = uri.split("///", 1)[-1]
    yol = Path(ham)
    if not yol.is_absolute():
        yol = ROOT / "instance" / ham
    return yol


def sutun_var_mi(baglanti: sqlite3.Connection) -> bool:
    satirlar = baglanti.execute(f"PRAGMA table_info({TABLO})").fetchall()
    if not satirlar:
        raise SystemExit(
            f"'{TABLO}' tablosu bulunamadi. Once 'python tools/seed.py' calistir."
        )
    return any(s[1] == SUTUN for s in satirlar)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rapor", action="store_true",
                   help="yazma, sadece ne yapacagini goster")
    a = p.parse_args()

    yol = veritabani_yolu()
    if not yol.exists():
        raise SystemExit(
            f"Veritabani bulunamadi: {yol}\n"
            "Once 'python tools/seed.py' calistir."
        )

    print()
    print("=" * 58)
    print("  BLOK KILIDI -- sema gocu")
    print("=" * 58)
    print(f"  veritabani : {yol}")

    baglanti = sqlite3.connect(yol)
    try:
        var = sutun_var_mi(baglanti)
        toplam = baglanti.execute(f"SELECT COUNT(*) FROM {TABLO}").fetchone()[0]
        yer_tutucu = ", ".join("?" for _ in ACIK_TIPLER)
        acilacak = baglanti.execute(
            f"SELECT COUNT(*) FROM {TABLO} WHERE type IN ({yer_tutucu})",
            ACIK_TIPLER,
        ).fetchone()[0]

        print(f"  toplam blok: {toplam}")
        print()

        # --- 1. adim: sutun ---
        if var:
            print(f"  [atlandi] '{SUTUN}' sutunu zaten var.")
        elif a.rapor:
            print(f"  [yapilacak] ALTER TABLE {TABLO} ADD COLUMN {SUTUN} "
                  f"BOOLEAN NOT NULL DEFAULT 1")
            print(f"              -> {toplam} blogun tamami KILITLENIR")
        else:
            baglanti.execute(
                f"ALTER TABLE {TABLO} ADD COLUMN {SUTUN} "
                f"BOOLEAN NOT NULL DEFAULT 1"
            )
            print(f"  [eklendi] '{SUTUN}' sutunu -- {toplam} blok kilitlendi.")

        # --- 2. adim: haber bloklarini ac ---
        tipler = ", ".join(ACIK_TIPLER)
        if a.rapor:
            if not var:
                print(f"  [yapilacak] UPDATE ... SET {SUTUN} = 0 "
                      f"WHERE type IN ({tipler})")
                print(f"              -> {acilacak} blok acilir")
            else:
                kalan = baglanti.execute(
                    f"SELECT COUNT(*) FROM {TABLO} "
                    f"WHERE type IN ({yer_tutucu}) AND {SUTUN} != 0",
                    ACIK_TIPLER,
                ).fetchone()[0]
                print(f"  [yapilacak] {kalan} '{tipler}' blogu acilir"
                      if kalan else
                      f"  [atlandi] '{tipler}' bloklari zaten acik.")
            print()
            print("  --rapor verildi, HICBIR SEY YAZILMADI.")
            return 0

        imlec = baglanti.execute(
            f"UPDATE {TABLO} SET {SUTUN} = 0 "
            f"WHERE type IN ({yer_tutucu}) AND {SUTUN} != 0",
            ACIK_TIPLER,
        )
        acilan = imlec.rowcount
        baglanti.commit()

        if acilan:
            print(f"  [acildi]  {acilan} '{tipler}' blogu duzenlemeye acildi.")
        else:
            print(f"  [atlandi] '{tipler}' bloklari zaten acikti.")

        # --- ozet ---
        kilitli = baglanti.execute(
            f"SELECT COUNT(*) FROM {TABLO} WHERE {SUTUN} = 1"
        ).fetchone()[0]
        acik = toplam - kilitli
        print()
        print(f"  SONUC: {kilitli} blok kilitli, {acik} blok duzenlenebilir.")
        print("=" * 58)
        print()
        print("  Baska bir blogu acmak icin:")
        print("    UPDATE block SET is_locked = 0 WHERE id = <blok_id>;")
        print()
    finally:
        baglanti.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
