# -*- coding: utf-8 -*-
"""Global Toyota sayfasina 2. grup bolumleri ekler -- veritabanini sifirlamadan.

    python tools/global_bolumleri2.py           # ekle
    python tools/global_bolumleri2.py --rapor   # yazma, ne yapilacagini goster
    python tools/global_bolumleri2.py --geri    # eklenenleri kaldir

YAPTIKLARI
----------
    EKLE    section_nav  Bu sayfada          (bolum menusu, en uste)
    EKLE    stat_grid    Avrupa'da Toyota    (haritanin altina)
    EKLE    card_grid    Platform ve teknoloji
    EKLE    card_grid    Ar-Ge ve tasarim
    EKLE    card_grid    Yonetim             (bos, en alta)
    GENISLET chip_groups Marka Ailesi -> ucuncu kutu "Markalar ve hizmetler"
    CAPA    mevcut bolumlere `anchor` yazar  (menu bunlardan uretiliyor)

tools/global_bolumleri.py ile ayni mantik ve ayni yardimcilar
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
    oge_yaz,
    sirala,
)
from tools.seed import (                              # noqa: E402
    BOLUM_ARGE,
    BOLUM_AVRUPA,
    BOLUM_MENU,
    BOLUM_PLATFORM,
    BOLUM_YONETIM,
    SAYFA_GLOBAL,
)

SAYFA_SLUG = "global-toyota"

YENI_BOLUMLER = [
    (BOLUM_MENU, "Bolum menusu (sayfa ici baglantilar)"),
    (BOLUM_AVRUPA, "Avrupa'da Toyota"),
    (BOLUM_PLATFORM, "Platform ve teknoloji"),
    (BOLUM_ARGE, "Ar-Ge ve tasarim"),
    (BOLUM_YONETIM, "Yonetim (bos, panelden doldurulacak)"),
]

# Marka ailesi bloguna eklenecek ucuncu kutu
MARKA_BLOGU_BASLIGI = "Toyota Grubu Marka Ailesi"
UCUNCU_KUTU_BASLIGI = "Markalar ve hizmetler"


def _ucuncu_kutu_verisi() -> dict:
    """seed.py'deki SAYFA_GLOBAL tanimindan ucuncu kutuyu cikarir.

    Ayri bir sabit yapmak yerine buradan okunuyor: metnin tek
    dogruluk kaynagi seed.py kalsin.
    """
    for veri in SAYFA_GLOBAL["blocks"]:
        if veri.get("heading") != MARKA_BLOGU_BASLIGI:
            continue
        for oge in veri["items"]:
            if oge.get("title") == UCUNCU_KUTU_BASLIGI:
                return oge
    raise SystemExit(f"! seed.py icinde '{UCUNCU_KUTU_BASLIGI}' kutusu yok")


def _marka_kutusu_eksik(sayfa: Page) -> Block | None:
    """Ucuncu kutu henuz yoksa marka ailesi blogunu dondurur."""
    blok = bul(sayfa, "chip_groups", MARKA_BLOGU_BASLIGI)
    if blok is None:
        return None
    for oge in blok.items:
        if oge.kind == "chip_group" and (oge.title or "") == UCUNCU_KUTU_BASLIGI:
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
    marka_blogu = _marka_kutusu_eksik(sayfa)
    capa_sayisi = sum(
        1 for veri in SAYFA_GLOBAL["blocks"]
        if veri.get("anchor")
        and (b := bul(sayfa, veri["type"], veri.get("heading") or "")) is not None
        and not b.anchor
    )

    if not eksikler and marka_blogu is None and not capa_sayisi:
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
    if marka_blogu is not None:
        print(f"  GENISLET  chip_groups     {MARKA_BLOGU_BASLIGI}"
              f" -> \"{UCUNCU_KUTU_BASLIGI}\" kutusu")
    if capa_sayisi:
        print(f"  CAPA      {capa_sayisi} bloga bolum menusu capasi yaziliyor")
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler: list[Block] = [blok_yaz(sayfa, veri) for veri, _ad in eksikler]

    if marka_blogu is not None:
        oge_yaz(marka_blogu, _ucuncu_kutu_verisi(), len(marka_blogu.items))
        db.session.flush()
        yeniler.append(marka_blogu)

    yazilan_capa = capalari_uygula(sayfa, SAYFA_GLOBAL)
    sirala(sayfa, hedef_sira(sayfa, SAYFA_GLOBAL))
    db.session.commit()
    if yazilan_capa:
        print(f"  {yazilan_capa} bloga capa yazildi")

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
              f"{(b.anchor or '-'):14s} {(b.heading or '-')[:40]}")
    return 0


def geri_al() -> int:
    """Bu betigin ekledigi bolumleri ve ucuncu kutuyu kaldirir."""
    sayfa = db.session.query(Page).filter_by(slug=SAYFA_SLUG).first()
    if sayfa is None:
        return 1

    for veri, ad in YENI_BOLUMLER:
        blok = bul(sayfa, veri["type"], veri.get("heading") or "")
        if blok is not None:
            print(f"  siliniyor: {veri['type']} — {ad}")
            db.session.delete(blok)

    marka = bul(sayfa, "chip_groups", MARKA_BLOGU_BASLIGI)
    if marka is not None:
        for oge in list(marka.items):
            if oge.kind == "chip_group" and (oge.title or "") == UCUNCU_KUTU_BASLIGI:
                print(f"  siliniyor: chip_group — {UCUNCU_KUTU_BASLIGI}")
                db.session.delete(oge)

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
