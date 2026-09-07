# -*- coding: utf-8 -*-
"""TPS sayfasina uc yeni bolum ekler -- veritabanini sifirlamadan.

    python tools/tps_bolumleri.py           # ekle
    python tools/tps_bolumleri.py --rapor   # yazma, ne yapilacagini goster
    python tools/tps_bolumleri.py --geri    # eklenenleri kaldir

YAPTIKLARI
----------
    EKLE     tps_house      TPS Evi              (girisin altina)
    EKLE     process_steps  TPS nasil dogdu      (evin altina)
    EKLE     card_grid      Yedi israf (muda)    (sayfanin sonuna)
    GENISLET card_grid      "Hattin iki sutunu" basliginin USTUNE
                            gecis cumlesi ekler

tools/global_bolumleri2.py ile ayni mantik ve ayni yardimcilar
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
    cevirileri_kilitle,
    cevirileri_tamamla,
    hedef_sira,
    oge_yaz,
    sirala,
)
from tools.seed import (                              # noqa: E402
    BOLUM_MUDA,
    BOLUM_TPS_DOGUS,
    BOLUM_TPS_EVI,
    GECIS_IKI_SUTUN,
    SAYFA_URETIM,
)

SAYFA_SLUG = "uretim-sistemi"

YENI_BOLUMLER = [
    (BOLUM_TPS_EVI, "TPS Evi (SVG diyagram)"),
    (BOLUM_TPS_DOGUS, "TPS nasil dogdu (uc adimli anlati)"),
    (BOLUM_MUDA, "Yedi israf (muda)"),
]

IKI_SUTUN_BASLIGI = "Hattın iki sütunu"


def _gecis_eksik(sayfa: Page) -> Block | None:
    """Gecis cumlesi henuz yoksa "Hattin iki sutunu" blogunu dondurur."""
    blok = bul(sayfa, "card_grid", IKI_SUTUN_BASLIGI)
    if blok is None:
        return None
    for oge in blok.items:
        if oge.kind == "lead":
            return None
    return blok


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
    iki_sutun = _gecis_eksik(sayfa)

    if not eksikler and iki_sutun is None:
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
        print(f"  EKLE      {veri['type']:14s} {ad}")
    if iki_sutun is not None:
        print(f"  GENISLET  card_grid       \"{IKI_SUTUN_BASLIGI}\""
              f" -> baslik ustu gecis cumlesi")
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler: list[Block] = [blok_yaz(sayfa, veri) for veri, _ad in eksikler]

    if iki_sutun is not None:
        # Gecis cumlesi kartlardan ONCE gelmeli: OgeYazici sirayi
        # `position`'a gore yaziyor, sablon da `first_of('lead')`
        # ile ariyor. Kartlarin sirasi bozulmasin diye hepsini bir
        # kaydiriyoruz.
        for oge in iki_sutun.items:
            oge.position += 1
        oge_yaz(iki_sutun, GECIS_IKI_SUTUN, 0)
        db.session.flush()
        yeniler.append(iki_sutun)

    sirala(sayfa, hedef_sira(sayfa, SAYFA_URETIM))
    db.session.commit()

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
        print(f"  {b.position:2d}. {b.type:14s} {len(b.all_items):2d} oge  "
              f"{(b.heading or '-')[:45]}")
    return 0


def geri_al() -> int:
    """Eklenen uc bolumu ve gecis cumlesini kaldirir."""
    sayfa = db.session.query(Page).filter_by(slug=SAYFA_SLUG).first()
    if sayfa is None:
        return 1

    for veri, ad in YENI_BOLUMLER:
        blok = bul(sayfa, veri["type"], veri.get("heading") or "")
        if blok is not None:
            print(f"  siliniyor: {veri['type']} — {ad}")
            db.session.delete(blok)

    iki_sutun = bul(sayfa, "card_grid", IKI_SUTUN_BASLIGI)
    if iki_sutun is not None:
        for oge in list(iki_sutun.items):
            if oge.kind == "lead":
                print("  siliniyor: lead — baslik ustu gecis cumlesi")
                db.session.delete(oge)

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
