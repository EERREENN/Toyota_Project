# -*- coding: utf-8 -*-
"""TMMT sayfasina IKINCI grup bolumleri ekler -- veritabanini sifirlamadan.

    python tools/tmmt_bolumleri2.py           # ekle
    python tools/tmmt_bolumleri2.py --rapor   # yazma, ne yapilacagini goster
    python tools/tmmt_bolumleri2.py --geri    # eklenenleri kaldir

EKLENEN BOLUMLER
----------------
    Vizyon ve Misyon              (stat_grid, card varyanti, iki sutun)
    Kurumsal bilgiler             (fact_table -- yeni tip)
    Ihracat pazarlari             (map -- global sayfasindaki blogun aynisi)
    Toplumla birlikte             (card_grid, dort sutun)
    Kariyer                       (card_grid + kart baglantilari)
    Sertifikalar ve oduller       (badge_strip -- yeni tip)
    Haberler ve basin bultenleri  (news_list -- yeni tip, bilerek bos)

Ayrica zaman tunelinin giris cumlesinden tartismali "30'dan fazla ulke"
ifadesi cikariliyor (bkz. tools/seed.py icindeki not).

tools/tmmt_bolumleri.py ile ayni mantik: iki kez calistirilirsa ikinci
seferde hicbir sey yapmaz, icerik seed.py'deki BOLUM_* sabitlerinden
okunur -- ayni metnin iki kopyasi olmasin diye.

Yazma/siralama/ceviri-kilitleme yardimcilari tools/_bolum_yazici.py
icinde; ayni yardimcilari tools/global_bolumleri.py de kullaniyor.
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
from app.models import Block, Page                    # noqa: E402
from tools._bolum_yazici import (                     # noqa: E402
    blok_yaz,
    bul,
    cevirileri_kilitle,
    cevirileri_tamamla,
    hedef_sira,
    sirala,
)
from tools.seed import (                              # noqa: E402
    BOLUM_HABERLER,
    BOLUM_IHRACAT,
    BOLUM_KARIYER,
    BOLUM_KILOMETRE,
    BOLUM_KUNYE,
    BOLUM_SERTIFIKA,
    BOLUM_TOPLUM,
    BOLUM_VIZYON,
    SAYFA_TMMT,
)

# Eklenecek bolumler: (sabit, panelde gorunecek kisa ad)
YENI_BOLUMLER = [
    (BOLUM_VIZYON, "Vizyon ve Misyon"),
    (BOLUM_KUNYE, "Kurumsal bilgiler"),
    (BOLUM_IHRACAT, "Ihracat pazarlari haritasi"),
    (BOLUM_TOPLUM, "Toplumla birlikte"),
    (BOLUM_KARIYER, "Kariyer"),
    (BOLUM_SERTIFIKA, "Sertifikalar ve oduller"),
    (BOLUM_HABERLER, "Haberler ve basin bultenleri"),
]

# Zaman tunelinin ESKI giris cumlesi. Yalnizca metin HALA BUYSA
# degistiriliyor -- editor panelden elle degistirdiyse dokunulmaz.
ESKI_ZAMAN_TUNELI_INTRO = (
    "Üretimin büyük bölümü, ağırlıklı olarak Avrupa'ya, ayrıca Orta Doğu ve "
    "Afrika'ya olmak üzere 30'dan fazla ülkeye ihraç ediliyor. Fabrika, 2021 "
    "yılında 3 milyonuncu aracını üretti ve Türkiye'nin en büyük ihracatçı "
    "sanayi kuruluşlarından biri."
)


# ============================================================
#  Uygulama
# ============================================================
def uygula(rapor_modu: bool) -> int:
    sayfa = db.session.query(Page).filter_by(slug="tmmt").first()
    if sayfa is None:
        print("! 'tmmt' sayfasi bulunamadi. Once: python tools/seed.py")
        return 1

    print("MEVCUT DURUM")
    for b in sayfa.blocks:
        print(f"  {b.position:2d}. {b.type:14s} {(b.heading or '-')[:45]}")
    print()

    eksikler = [
        (veri, ad) for veri, ad in YENI_BOLUMLER
        if bul(sayfa, veri["type"], veri.get("heading") or "") is None
    ]

    zaman_tuneli = bul(sayfa, "timeline", BOLUM_KILOMETRE["heading"])
    intro_duzeltilecek = (
        zaman_tuneli is not None
        and (zaman_tuneli.intro or "") == ESKI_ZAMAN_TUNELI_INTRO
    )

    if not eksikler and not intro_duzeltilecek:
        # Bloklar duruyor ama elle ceviri kilitleri eksik olabilir
        # (ornek: liste sonradan genisletildi). Ucuz bir gecis.
        if rapor_modu:
            print("Yapilacak bir sey yok -- bolumler zaten ekli.")
            return 0
        kilitli = cevirileri_kilitle(list(sayfa.blocks))
        if kilitli:
            db.session.commit()
            print(f"{kilitli} metnin Ingilizcesi elle yazilip kilitlendi.")
        # Onceki calistirmada ag/hiz siniri yuzunden Turkce kalmis
        # ceviri varsa burada yeniden denenir.
        duzelen = cevirileri_tamamla(list(sayfa.blocks))
        if duzelen:
            print(f"{duzelen} metnin Ingilizcesi tamamlandi.")
        elif not kilitli:
            print("Yapilacak bir sey yok -- bolumler zaten ekli.")
        return 0

    print("YAPILACAKLAR")
    for veri, ad in eksikler:
        print(f"  EKLE      {veri['type']:12s} {ad}")
    if intro_duzeltilecek:
        print("  DUZELT    timeline     giris cumlesinden \"30'dan fazla ulke\" "
              "ifadesi cikariliyor")
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler: list[Block] = []
    for veri, _ad in eksikler:
        yeniler.append(blok_yaz(sayfa, veri))

    if intro_duzeltilecek:
        zaman_tuneli.intro = BOLUM_KILOMETRE["intro"]
        yeniler.append(zaman_tuneli)

    sirala(sayfa, hedef_sira(sayfa, SAYFA_TMMT))
    db.session.commit()

    print("Ingilizce ceviriler uretiliyor...")
    for blok in yeniler:
        translation_sync.blogu_senkronize(blok)

    kilitli = cevirileri_kilitle(list(sayfa.blocks))
    if kilitli:
        db.session.commit()
        print(f"  {kilitli} metnin Ingilizcesi elle yazilip kilitlendi")

    # Google cok sayida metni pespese cevirirken hiz sinirina takilip
    # kaynak metni geri dondurebiliyor; o satirlar burada yeniden denenir.
    duzelen = cevirileri_tamamla(list(sayfa.blocks))
    if duzelen:
        print(f"  {duzelen} metnin Ingilizcesi tamamlandi")

    print()
    print("YENI DURUM")
    for b in sayfa.blocks:
        print(f"  {b.position:2d}. {b.type:14s} {len(b.all_items):2d} oge  "
              f"{(b.heading or '-')[:45]}")
    return 0


def geri_al() -> int:
    """Bu betigin ekledigi bolumleri kaldirir, zaman tuneli girisini geri alir."""
    sayfa = db.session.query(Page).filter_by(slug="tmmt").first()
    if sayfa is None:
        return 1

    for veri, ad in YENI_BOLUMLER:
        blok = bul(sayfa, veri["type"], veri.get("heading") or "")
        if blok is not None:
            print(f"  siliniyor: {veri['type']} — {ad}")
            db.session.delete(blok)
    db.session.flush()
    db.session.expire(sayfa, ["blocks"])

    zaman_tuneli = bul(sayfa, "timeline", BOLUM_KILOMETRE["heading"])
    if zaman_tuneli is not None and (zaman_tuneli.intro or "") == BOLUM_KILOMETRE["intro"]:
        zaman_tuneli.intro = ESKI_ZAMAN_TUNELI_INTRO
        print("  geri alindi: zaman tuneli giris cumlesi")

    sirala(sayfa, sorted(sayfa.blocks, key=lambda b: b.position))
    db.session.commit()

    if zaman_tuneli is not None:
        translation_sync.blogu_senkronize(zaman_tuneli)
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
