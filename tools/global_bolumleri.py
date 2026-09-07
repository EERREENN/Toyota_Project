# -*- coding: utf-8 -*-
"""Global Toyota sayfasina uc yeni bolum ekler -- veritabanini sifirlamadan.

    python tools/global_bolumleri.py           # ekle
    python tools/global_bolumleri.py --rapor   # yazma, ne yapilacagini goster
    python tools/global_bolumleri.py --geri    # eklenenleri kaldir

EKLENEN BOLUMLER
----------------
    Mobility for All              (mission -- yeni tip, misyon bandi)
    Toyota'nin hikayesi           (timeline -- cevre/TMMT ile ayni bilesen)
    Toyota Way: iki sutun, bes deger  (value_columns -- yeni tip)

tools/tmmt_bolumleri2.py ile ayni mantik ve ayni yardimcilar
(tools/_bolum_yazici.py): iki kez calistirilirsa ikinci seferde hicbir
sey yapmaz, icerik seed.py'deki BOLUM_* sabitlerinden okunur -- ayni
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
    BOLUM_HIKAYE,
    BOLUM_MOBILITY,
    BOLUM_TOYOTA_WAY,
    SAYFA_GLOBAL,
)

SAYFA_SLUG = "global-toyota"

# Eklenecek bolumler: (sabit, panelde gorunecek kisa ad)
YENI_BOLUMLER = [
    (BOLUM_MOBILITY, "Mobility for All (misyon bandi)"),
    (BOLUM_HIKAYE, "Toyota'nin hikayesi (zaman tuneli)"),
    (BOLUM_TOYOTA_WAY, "Toyota Way: iki sutun, bes deger"),
]


# ============================================================
#  Uygulama
# ============================================================
def uygula(rapor_modu: bool) -> int:
    sayfa = db.session.query(Page).filter_by(slug=SAYFA_SLUG).first()
    if sayfa is None:
        print(f"! '{SAYFA_SLUG}' sayfasi bulunamadi. Once: python tools/seed.py")
        return 1

    print("MEVCUT DURUM")
    for b in sayfa.blocks:
        print(f"  {b.position:2d}. {b.type:14s} {(b.heading or '-')[:45]}")
    print()

    eksikler = [
        (veri, ad) for veri, ad in YENI_BOLUMLER
        if bul(sayfa, veri["type"], veri.get("heading") or "") is None
    ]

    if not eksikler:
        # Bloklar duruyor ama elle ceviri kilitleri eksik olabilir
        # (ornek: KILITLI_CEVIRI listesi sonradan genisletildi).
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
        print(f"  EKLE      {veri['type']:14s} {ad}")
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler: list[Block] = [blok_yaz(sayfa, veri) for veri, _ad in eksikler]

    sirala(sayfa, hedef_sira(sayfa, SAYFA_GLOBAL))
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
    """Bu betigin ekledigi uc bolumu kaldirir."""
    sayfa = db.session.query(Page).filter_by(slug=SAYFA_SLUG).first()
    if sayfa is None:
        return 1

    for veri, ad in YENI_BOLUMLER:
        blok = bul(sayfa, veri["type"], veri.get("heading") or "")
        if blok is not None:
            print(f"  siliniyor: {veri['type']} — {ad}")
            db.session.delete(blok)
    db.session.flush()
    db.session.expire(sayfa, ["blocks"])

    sirala(sayfa, sorted(sayfa.blocks, key=lambda b: b.position))
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
