# -*- coding: utf-8 -*-
"""Cevre sayfasina 2. grup bolumleri ekler -- veritabanini sifirlamadan.

    python tools/cevre_bolumleri2.py           # ekle
    python tools/cevre_bolumleri2.py --rapor   # yazma, ne yapilacagini goster
    python tools/cevre_bolumleri2.py --geri    # eklenenleri kaldir

YAPTIKLARI
----------
    EKLE  section_nav   Bu sayfada              (girisin altina)
    EKLE  card_grid     Dongusel ekonomi: 4R
    EKLE  cycle_steps   Bataryanin ikinci hayati (duz akis)
    EKLE  stat_grid     TMMT'de cevre
    EKLE  timeline      Karbon notr fabrikaya giden yol
    EKLE  mission       Surdurulebilirlik Raporu bandi
    CAPA  mevcut Cevre bloklarina `anchor` yazar (menu bunlardan uretilir)
    CAPA  TMMT'deki "PHEV Batarya Hatti" bloguna `phev` capasini yazar --
          batarya akisindaki baglantinin hedefi orasi

tools/cevre_bolumleri.py ile ayni mantik ve ayni yardimcilar
(tools/_bolum_yazici.py): iki kez calistirilirsa ikinci seferde hicbir
sey yapmaz, icerik seed.py'deki BOLUM_* sabitlerinden okunur.
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
    capalari_uygula,
    cevirileri_kilitle,
    cevirileri_tamamla,
    hedef_sira,
    sirala,
)
from tools.seed import (                              # noqa: E402
    BOLUM_4R,
    BOLUM_BATARYA,
    BOLUM_CEVRE_MENU,
    BOLUM_KARBON_YOL,
    BOLUM_PHEV,
    BOLUM_RAPOR,
    BOLUM_TMMT_CEVRE,
    SAYFA_CEVRE,
    SAYFA_TMMT,
)

SAYFA_SLUG = "cevre"

YENI_BOLUMLER = [
    (BOLUM_CEVRE_MENU, "Bolum menusu (sayfa ici baglantilar)"),
    (BOLUM_4R, "Dongusel ekonomi: 4R"),
    (BOLUM_BATARYA, "Bataryanin ikinci hayati"),
    (BOLUM_TMMT_CEVRE, "TMMT'de cevre"),
    (BOLUM_KARBON_YOL, "Karbon notr fabrikaya giden yol"),
    (BOLUM_RAPOR, "Surdurulebilirlik Raporu bandi"),
]


def _tmmt_capasi() -> int:
    """Batarya akisindaki baglantinin hedefini TMMT sayfasina yazar.

    Link /tmmt#phev adresine gidiyor; capa yoksa tarayici sayfanin
    basinda kalir -- yani bozuk bir baglanti olur.
    """
    tmmt = db.session.query(Page).filter_by(slug="tmmt").first()
    if tmmt is None:
        return 0
    return capalari_uygula(tmmt, SAYFA_TMMT)


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
        print(f"  {b.position:2d}. {b.type:15s} {(b.heading or '-')[:45]}")
    print()

    eksikler = [
        (veri, ad) for veri, ad in YENI_BOLUMLER
        if bul(sayfa, veri["type"], veri.get("heading") or "") is None
    ]
    capa_sayisi = sum(
        1 for veri in SAYFA_CEVRE["blocks"]
        if veri.get("anchor")
        and (b := bul(sayfa, veri["type"], veri.get("heading") or "")) is not None
        and not b.anchor
    )
    tmmt = db.session.query(Page).filter_by(slug="tmmt").first()
    tmmt_capa = bool(
        tmmt is not None
        and (b := bul(tmmt, "stat_grid", BOLUM_PHEV["heading"])) is not None
        and not b.anchor
    )

    if not eksikler and not capa_sayisi and not tmmt_capa:
        if rapor_modu:
            print("Yapilacak bir sey yok -- bolumler zaten ekli.")
            return 0
        kilitli = cevirileri_kilitle(list(sayfa.blocks))
        if kilitli:
            db.session.commit()
            print(f"{kilitli} metnin Ingilizcesi elle yazilip kilitlendi.")
        duzelen = cevirileri_tamamla(list(sayfa.blocks))
        if duzelen:
            print(f"{duzelen} metnin Ingilizcesi tamamlandi.")
        elif not kilitli:
            print("Yapilacak bir sey yok -- bolumler zaten ekli.")
        return 0

    print("YAPILACAKLAR")
    for veri, ad in eksikler:
        print(f"  EKLE      {veri['type']:15s} {ad}")
    if capa_sayisi:
        print(f"  CAPA      {capa_sayisi} Cevre bloguna bolum menusu capasi")
    if tmmt_capa:
        print("  CAPA      TMMT 'PHEV Batarya Hatti' -> #phev")
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler: list[Block] = [blok_yaz(sayfa, veri) for veri, _ad in eksikler]

    yazilan = capalari_uygula(sayfa, SAYFA_CEVRE) + _tmmt_capasi()
    sirala(sayfa, hedef_sira(sayfa, SAYFA_CEVRE))
    db.session.commit()
    if yazilan:
        print(f"  {yazilan} bloga capa yazildi")

    print("Ingilizce ceviriler uretiliyor...")
    for blok in yeniler:
        translation_sync.blogu_senkronize(blok)

    kilitli = cevirileri_kilitle(list(sayfa.blocks))
    if kilitli:
        db.session.commit()
        print(f"  {kilitli} metnin Ingilizcesi elle yazilip kilitlendi")

    duzelen = cevirileri_tamamla(list(sayfa.blocks))
    if duzelen:
        print(f"  {duzelen} metnin Ingilizcesi tamamlandi")

    print()
    print("YENI DURUM")
    for b in sayfa.blocks:
        print(f"  {b.position:2d}. {b.type:15s} {len(b.all_items):2d} oge  "
              f"{(b.anchor or '-'):12s} {(b.heading or '-')[:38]}")
    return 0


def geri_al() -> int:
    """Bu betigin ekledigi bolumleri kaldirir (capalar zararsiz, kalir)."""
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
    print("geri alindi. (capalar korundu -- zararsiz)")
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
