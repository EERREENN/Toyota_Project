# -*- coding: utf-8 -*-
"""Cevre sayfasini gunceller ve iki yeni bolum ekler -- sifirlamadan.

    python tools/cevre_bolumleri.py           # uygula
    python tools/cevre_bolumleri.py --rapor   # yazma, ne yapilacagini goster
    python tools/cevre_bolumleri.py --geri    # eklenenleri kaldir

YAPTIKLARI
----------
    GUNCELLE stat_grid  "Alti hedef" -- 6 karta hedef ADI yazar
                        (bos olanlara; editorun degistirdigine dokunmaz)
    EKLE     stat_grid  ayni bloga izgara alti kompakt liste (3 hedef)
    EKLE     compare_table  Hangi teknoloji size uygun?
    EKLE     hybrid_flow    Hibrit nasil calisir?

tools/tps_bolumleri2.py ile ayni mantik ve ayni yardimcilar
(tools/_bolum_yazici.py): iki kez calistirilirsa ikinci seferde hicbir
sey yapmaz, icerik seed.py'deki sabitlerden okunur.
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
    BOLUM_HIBRIT,
    BOLUM_TEKNOLOJI,
    KALAN_HEDEFLER,
    SAYFA_CEVRE,
)

SAYFA_SLUG = "cevre"
HEDEF_BLOGU_BASLIGI = "Altı hedef, güncel ilerleme"

YENI_BOLUMLER = [
    (BOLUM_TEKNOLOJI, "Hangi teknoloji size uygun? (karsilastirma tablosu)"),
    (BOLUM_HIBRIT, "Hibrit nasil calisir? (asamali diyagram)"),
]


def _hedef_adlari() -> dict[str, str]:
    """{kartin `value` degeri: hedef adi} -- seed.py'deki tanimdan.

    Kartlar `value` ile eslestiriliyor ("32", "2035"...): sira degisse
    de dogru karta yaziyoruz.
    """
    for veri in SAYFA_CEVRE["blocks"]:
        if veri.get("heading") != HEDEF_BLOGU_BASLIGI:
            continue
        return {
            oge["value"]: oge["subtitle"]
            for oge in veri["items"]
            if oge.get("kind") == "stat" and oge.get("subtitle")
        }
    return {}


def _hedef_blogu(sayfa: Page) -> Block | None:
    return bul(sayfa, "stat_grid", HEDEF_BLOGU_BASLIGI)


def _eksik_adlar(blok: Block | None) -> list:
    """Hedef adi HENUZ BOS olan kartlar. Dolu olana dokunulmaz."""
    if blok is None:
        return []
    adlar = _hedef_adlari()
    return [
        oge for oge in blok.items_of("stat")
        if adlar.get(oge.value) and not oge.subtitle
    ]


def _liste_eksik(blok: Block | None) -> bool:
    return blok is not None and not blok.items_of("fact")


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

    hedef_blogu = _hedef_blogu(sayfa)
    eksik_adlar = _eksik_adlar(hedef_blogu)
    liste_eksik = _liste_eksik(hedef_blogu)
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

    if not eksikler and not eksik_adlar and not liste_eksik and not capa_sayisi:
        if rapor_modu:
            print("Yapilacak bir sey yok -- her sey guncel.")
            return 0
        kilitli = cevirileri_kilitle(list(sayfa.blocks))
        if kilitli:
            db.session.commit()
            print(f"{kilitli} metnin Ingilizcesi elle yazilip kilitlendi.")
        duzelen = cevirileri_tamamla(list(sayfa.blocks))
        if duzelen:
            print(f"{duzelen} metnin Ingilizcesi tamamlandi.")
        elif not kilitli:
            print("Yapilacak bir sey yok -- her sey guncel.")
        return 0

    print("YAPILACAKLAR")
    if eksik_adlar:
        print(f"  GUNCELLE  stat_grid       {len(eksik_adlar)} karta hedef adi")
    if liste_eksik:
        print(f"  EKLE      stat_grid       izgara alti liste "
              f"({len(KALAN_HEDEFLER)} hedef)")
    for veri, ad in eksikler:
        print(f"  EKLE      {veri['type']:15s} {ad}")
    if capa_sayisi:
        print(f"  CAPA      {capa_sayisi} bloga capa")
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler: list[Block] = []

    if eksik_adlar or liste_eksik:
        adlar = _hedef_adlari()
        for oge in eksik_adlar:
            oge.subtitle = adlar[oge.value]
        if liste_eksik:
            for sira, veri in enumerate(KALAN_HEDEFLER):
                oge_yaz(hedef_blogu, veri, len(hedef_blogu.items) + sira)
        db.session.flush()
        yeniler.append(hedef_blogu)

    yeniler += [blok_yaz(sayfa, veri) for veri, _ad in eksikler]

    yazilan = capalari_uygula(sayfa, SAYFA_CEVRE)
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
              f"{(b.heading or '-')[:42]}")
    return 0


def geri_al() -> int:
    """Iki yeni bolumu, izgara alti listeyi ve hedef adlarini kaldirir."""
    sayfa = db.session.query(Page).filter_by(slug=SAYFA_SLUG).first()
    if sayfa is None:
        return 1

    for veri, ad in YENI_BOLUMLER:
        blok = bul(sayfa, veri["type"], veri.get("heading") or "")
        if blok is not None:
            print(f"  siliniyor: {veri['type']} — {ad}")
            db.session.delete(blok)

    hedef_blogu = _hedef_blogu(sayfa)
    if hedef_blogu is not None:
        adlar = _hedef_adlari()
        for oge in hedef_blogu.items_of("fact"):
            print(f"  siliniyor: fact — {oge.title}")
            db.session.delete(oge)
        for oge in hedef_blogu.items_of("stat"):
            # Yalnizca BIZIM yazdigimizi geri al; editor degistirdiyse dur.
            if oge.subtitle and oge.subtitle == adlar.get(oge.value):
                oge.subtitle = None

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
