# -*- coding: utf-8 -*-
"""TPS sayfasina 2. grup bolumleri ekler -- veritabanini sifirlamadan.

    python tools/tps_bolumleri2.py           # ekle
    python tools/tps_bolumleri2.py --rapor   # yazma, ne yapilacagini goster
    python tools/tps_bolumleri2.py --geri    # eklenenleri kaldir

YAPTIKLARI
----------
    EKLE  section_nav   Bu sayfada             (girisin altina)
    EKLE  andon         Yerinde kalite ve andon
    EKLE  cycle_steps   Kaizen dongusu
    EKLE  glossary      TPS kavram sozlugu
    EKLE  card_grid     TPS bugun nerede
    EKLE  mission       TMMT yonlendirme bandi (basliksiz)
    CAPA  mevcut TPS bloklarina `anchor` yazar (menu bunlardan uretiliyor)
    CAPA  TMMT'deki "Fabrikada bir aracin yolculugu" bloguna `yolculuk`
          capasini yazar -- yonlendirme butonunun hedefi orasi

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
    capalari_uygula,
    cevirileri_kilitle,
    cevirileri_tamamla,
    hedef_sira,
    sirala,
)
from tools.seed import (                              # noqa: E402
    BOLUM_ANDON,
    BOLUM_KAIZEN,
    BOLUM_SOZLUK,
    BOLUM_TMMT_KOPRU,
    BOLUM_TPS_BUGUN,
    BOLUM_TPS_MENU,
    BOLUM_YOLCULUK,
    SAYFA_TMMT,
    SAYFA_URETIM,
)

SAYFA_SLUG = "uretim-sistemi"

YENI_BOLUMLER = [
    (BOLUM_TPS_MENU, "Bolum menusu (sayfa ici baglantilar)"),
    (BOLUM_ANDON, "Yerinde kalite ve andon"),
    (BOLUM_KAIZEN, "Kaizen dongusu"),
    (BOLUM_SOZLUK, "TPS kavram sozlugu"),
    (BOLUM_TPS_BUGUN, "TPS bugun nerede"),
    (BOLUM_TMMT_KOPRU, "TMMT yonlendirme bandi"),
]


def _tmmt_capasi() -> int:
    """Yonlendirme butonunun hedefi olan capayi TMMT sayfasina yazar.

    Buton /tmmt#yolculuk adresine gidiyor; capa yoksa tarayici
    sayfanin basinda kalir -- yani bozuk bir link olur.
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
        print(f"  {b.position:2d}. {b.type:14s} {(b.heading or '-')[:45]}")
    print()

    eksikler = [
        (veri, ad) for veri, ad in YENI_BOLUMLER
        if bul(sayfa, veri["type"], veri.get("heading") or "") is None
    ]
    capa_sayisi = sum(
        1 for veri in SAYFA_URETIM["blocks"]
        if veri.get("anchor")
        and (b := bul(sayfa, veri["type"], veri.get("heading") or "")) is not None
        and not b.anchor
    )
    tmmt = db.session.query(Page).filter_by(slug="tmmt").first()
    tmmt_capa = bool(
        tmmt is not None
        and (b := bul(tmmt, "process_steps", BOLUM_YOLCULUK["heading"])) is not None
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
        print(f"  EKLE      {veri['type']:14s} {ad}")
    if capa_sayisi:
        print(f"  CAPA      {capa_sayisi} TPS bloguna bolum menusu capasi")
    if tmmt_capa:
        print("  CAPA      TMMT 'Fabrikada bir aracin yolculugu' -> #yolculuk")
    print()

    if rapor_modu:
        print("(--rapor: hicbir sey yazilmadi)")
        return 0

    yeniler: list[Block] = [blok_yaz(sayfa, veri) for veri, _ad in eksikler]

    yazilan = capalari_uygula(sayfa, SAYFA_URETIM) + _tmmt_capasi()
    sirala(sayfa, hedef_sira(sayfa, SAYFA_URETIM))
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
        print(f"  {b.position:2d}. {b.type:14s} {len(b.all_items):2d} oge  "
              f"{(b.anchor or '-'):11s} {(b.heading or '-')[:40]}")
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
