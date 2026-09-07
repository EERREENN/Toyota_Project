# -*- coding: utf-8 -*-
"""Panel gidis-donus testi.

En sert dogrulama: her blogun duzenleme formunu ACIP, HICBIR SEYI
DEGISTIRMEDEN kaydeder. Sonrasinda sitenin ciktisi bit bit ayni
kalmalidir.

Bir alan formda hic gosterilmiyorsa, yanlis isimle gonderiliyorsa ya
da kaydederken tur donusumu bozuluyorsa, kaydetme o veriyi siler ya da
bozar -- ve bu test onu yakalar.

    python tools/panel_roundtrip.py            # tum bloklar
    python tools/panel_roundtrip.py --tip map  # sadece bir tip
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup                      # noqa: E402
from werkzeug.datastructures import MultiDict       # noqa: E402

from app import create_app                         # noqa: E402
from app.extensions import db                      # noqa: E402
from app.models import Block, LoginAttempt         # noqa: E402

SAYFALAR = ["/", "/global-toyota", "/uretim-sistemi", "/cevre"]


def form_verisi(html: str, form_id: str) -> list[tuple[str, str]]:
    """Bir formdaki tum alanlari tarayicinin gonderecegi gibi topla.

    - isaretsiz checkbox GONDERILMEZ (tarayici da gondermez)
    - <template> icindeki bos satir kalibi ATLANIR (gercek satir degil)
    - select'te secili secenek alinir
    """
    corba = BeautifulSoup(html, "html.parser")
    form = corba.find(id=form_id)
    if form is None:
        raise SystemExit(f"'{form_id}' formu bulunamadi")

    # kalip satirlari gercek veri degil
    for kalip in form.find_all("template"):
        kalip.decompose()

    veri: list[tuple[str, str]] = []

    for el in form.find_all(["input", "textarea", "select"]):
        ad = el.get("name")
        if not ad:
            continue
        etiket = el.name
        if etiket == "input":
            tur = (el.get("type") or "text").lower()
            if tur in ("checkbox", "radio"):
                if el.has_attr("checked"):
                    veri.append((ad, el.get("value", "on")))
                continue
            if tur == "submit":
                continue
            veri.append((ad, el.get("value", "")))
        elif etiket == "textarea":
            veri.append((ad, el.get_text()))
        else:  # select
            secili = el.find("option", selected=True) or el.find("option")
            veri.append((ad, secili.get("value", "") if secili else ""))
    return veri


def sayfa_ciktilari(client) -> dict[str, str]:
    cikti = {}
    for yol in SAYFALAR:
        for dil in ("tr", "en"):
            cikti[f"{yol}?{dil}"] = client.get(f"{yol}?lang={dil}").get_data(
                as_text=True
            )
    return cikti


def main() -> int:
    ayrist = argparse.ArgumentParser()
    ayrist.add_argument("--tip", help="sadece bu blok tipini dene")
    ayrist.add_argument("--parola", default="grjqo-wsxwn-hmhjs-60")
    a = ayrist.parse_args()

    app = create_app()
    yol_onek = app.config["ADMIN_PATH"]

    # ceviri icin aga cikma -- deterministik olsun
    import auto_translate
    auto_translate._remote_translate = lambda text, target: None

    with app.app_context():
        db.session.query(LoginAttempt).delete()
        db.session.commit()
        bloklar = [
            (b.id, b.type)
            for b in db.session.query(Block).order_by(Block.id).all()
            if not a.tip or b.type == a.tip
        ]

    client = app.test_client()

    def csrf(yol):
        h = client.get(yol).get_data(as_text=True)
        m = re.search(r'name="_csrf" value="([^"]+)"', h)
        return m.group(1) if m else ""

    giris = client.post(
        yol_onek + "/", data={"parola": a.parola, "_csrf": csrf(yol_onek + "/")}
    )
    if giris.status_code != 302:
        print("! Panele giris yapilamadi. --parola dogru mu?")
        return 2

    print(f"{len(bloklar)} blok denenecek\n")
    onceki = sayfa_ciktilari(client)

    bozulan = []
    for blok_id, tip in bloklar:
        adres = f"{yol_onek}/blok/{blok_id}"
        html = client.get(adres).get_data(as_text=True)
        veri = form_verisi(html, "blok-form")

        # ayni ad birden fazla kez gecebilir -> MultiDict
        r = client.post(adres, data=MultiDict(veri))
        if r.status_code not in (200, 302):
            print(f"  ! {tip:16s} #{blok_id:<3} kaydetme HTTP {r.status_code}")
            bozulan.append((blok_id, tip, f"HTTP {r.status_code}"))
            continue

        sonraki = sayfa_ciktilari(client)
        farkli = [k for k in onceki if onceki[k] != sonraki[k]]
        if farkli:
            print(f"  ! {tip:16s} #{blok_id:<3} SAYFA DEGISTI: {', '.join(farkli)}")
            bozulan.append((blok_id, tip, ", ".join(farkli)))
            _fark_goster(onceki, sonraki, farkli[0])
            onceki = sonraki           # sonrakileri de kacirmayalim
        else:
            print(f"    {tip:16s} #{blok_id:<3} degismedi  ({len(veri)} alan)")

    print()
    print("=" * 58)
    if bozulan:
        print(f"SONUC: {len(bozulan)} blok gidis-donuste BOZULDU")
        print("=" * 58)
        return 1
    print("SONUC: TUM BLOKLAR KAYIPSIZ -- kaydetmek ciktiyi degistirmiyor")
    print("=" * 58)
    return 0


def _fark_goster(onceki, sonraki, anahtar, en_fazla=6):
    import difflib

    fark = list(
        difflib.unified_diff(
            onceki[anahtar].splitlines(),
            sonraki[anahtar].splitlines(),
            "once", "sonra", lineterm="", n=0,
        )
    )
    for satir in fark[:en_fazla + 3]:
        print("        " + satir[:120])
    if len(fark) > en_fazla + 3:
        print(f"        ... ({len(fark)} satir fark)")


if __name__ == "__main__":
    sys.exit(main())
