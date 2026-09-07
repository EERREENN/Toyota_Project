# -*- coding: utf-8 -*-
"""Gorunum regresyonu icin HTML anlik goruntusu.

Amac: yeniden yapilandirma sirasinda sayfalarin ciktisinin degismedigini
kanitlamak. Once mevcut (eski) uygulamadan "before" alinir, her asamadan
sonra yeni uygulamadan "after" alinip ikisi karsilastirilir.

    python tools/snapshot.py before      # mevcut durumu kaydet
    python tools/snapshot.py after       # yeni durumu kaydet
    python tools/snapshot.py diff        # ikisini karsilastir
    python tools/snapshot.py diff --text # sadece METIN farki (etiketler haric)

Ceviri icin agi kullanmaz (--online demedikce): onbellekte olmayan metin
Turkce kalir. Boylece anlik goruntu her calistirmada ayni cikar.
"""

from __future__ import annotations

import argparse
import difflib
import html
import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SNAP_DIR = Path(__file__).resolve().parent / "_snapshots"

# (dosya adi, yol) -- "/" ana sayfa (tmmt)
PAGES = [
    ("tmmt", "/"),
    ("global", "/global-toyota"),
    ("uretim", "/uretim-sistemi"),
    ("cevre", "/cevre"),
]
LANGS = ["tr", "en"]


def load_app():
    """Once yeni yapiyi (app paketi + create_app), yoksa eskisini yukle."""
    try:
        mod = importlib.import_module("app")
        if hasattr(mod, "create_app"):
            return mod.create_app(), "app.create_app()"
        if hasattr(mod, "app"):
            return mod.app, "app.app (eski)"
    except ImportError:
        pass
    mod = importlib.import_module("legacy_app")
    return mod.app, "legacy_app.app (eski)"


def force_offline() -> str:
    """Ceviri icin agi kapat -- anlik goruntu deterministik olsun."""
    for name in ("app.auto_translate", "auto_translate"):
        try:
            mod = importlib.import_module(name)
        except ImportError:
            continue
        mod._remote_translate = lambda text, target: None
        return name
    return "(auto_translate bulunamadi)"


def capture(tag: str, online: bool) -> Path:
    if not online:
        force_offline()
    flask_app, kaynak = load_app()
    flask_app.config["SERVER_NAME"] = None
    out = SNAP_DIR / tag
    out.mkdir(parents=True, exist_ok=True)

    client = flask_app.test_client()
    print(f"kaynak: {kaynak}")
    for ad, yol in PAGES:
        for dil in LANGS:
            r = client.get(f"{yol}?lang={dil}")
            hedef = out / f"{ad}.{dil}.html"
            body = r.get_data(as_text=True)
            hedef.write_text(body, encoding="utf-8")
            durum = "ok " if r.status_code == 200 else f"!! {r.status_code}"
            print(f"  {durum} {ad}.{dil}.html  ({len(body)} karakter)")
    print(f"\nyazildi: {out}")
    return out


# --- metin cikarma (etiketleri atip sadece gorunen yaziyi birakir) ---
_SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t\r\f\v]+")


def gorunen_metin(kaynak: str) -> list[str]:
    govde = _SCRIPT_STYLE.sub(" ", kaynak)
    govde = _TAG.sub("\n", govde)
    govde = html.unescape(govde)
    satirlar = []
    for satir in govde.split("\n"):
        satir = _WS.sub(" ", satir).strip()
        if satir:
            satirlar.append(satir)
    return satirlar


def dom_normalize(kaynak: str) -> list[str]:
    """HTML'i bosluktan bagimsiz, karsilastirilabilir satirlara cevirir.

    Her etiket kendi satirinda, oznitelikleri sirali; metin dugumleri
    sadelestirilmis. Boylece girinti/satir sonu farklari gorunmez ama
    DEGISEN BIR SINIF, EKSIK BIR DIV ya da farkli bir oznitelik
    aninda goze carpar.
    """
    from bs4 import BeautifulSoup, NavigableString, Tag

    corba = BeautifulSoup(kaynak, "html.parser")
    satirlar: list[str] = []

    def yaz(dugum, derinlik: int) -> None:
        if isinstance(dugum, NavigableString):
            metin = _WS.sub(" ", str(dugum)).strip()
            if metin:
                satirlar.append(f"{'  ' * derinlik}#text {metin}")
            return
        if not isinstance(dugum, Tag):
            return

        oznitelikler = []
        for ad in sorted(dugum.attrs):
            deger = dugum.attrs[ad]
            if isinstance(deger, list):
                deger = " ".join(deger)
            if deger == "":
                oznitelikler.append(ad)
            else:
                oznitelikler.append(f'{ad}="{deger}"')
        bas = f"{'  ' * derinlik}<{dugum.name}"
        if oznitelikler:
            bas += " " + " ".join(oznitelikler)
        satirlar.append(bas + ">")

        if dugum.name in ("script", "style"):
            govde = _WS.sub(" ", dugum.get_text()).strip()
            if govde:
                kisa = govde[:70] + ("..." if len(govde) > 70 else "")
                satirlar.append(f"{'  ' * (derinlik + 1)}#kod {kisa}")
            return

        for cocuk in dugum.children:
            yaz(cocuk, derinlik + 1)

    for kok in corba.children:
        yaz(kok, 0)
    return satirlar


def yazdirilabilir(metin: str) -> str:
    """Konsolun kaldiramadigi karakterleri temizler.

    Windows konsolu cp1254 ile aciliyor; sayfa metninde ise ok
    isareti (U+2192) gibi karakterler var. Farki dogrudan print
    etmek UnicodeEncodeError veriyordu -- yani FARK BULUNAN her
    calistirmada betik, farki gostermek yerine cokuyordu. Rapor
    okunabilir kalsin diye konsolun kodlamasina indirgiyoruz.
    """
    kodlama = sys.stdout.encoding or "utf-8"
    return metin.encode(kodlama, errors="replace").decode(
        kodlama, errors="replace"
    )


def diff(sadece_metin: bool, dom: bool = False) -> int:
    onceki, sonraki = SNAP_DIR / "before", SNAP_DIR / "after"
    if not onceki.exists() or not sonraki.exists():
        print("Once 'before' ve 'after' anlik goruntulerini al.")
        return 2

    toplam_fark = 0
    for ad, _yol in PAGES:
        for dil in LANGS:
            dosya = f"{ad}.{dil}.html"
            a_yol, b_yol = onceki / dosya, sonraki / dosya
            if not a_yol.exists() or not b_yol.exists():
                print(f"[atlandi] {dosya} (bir tarafta yok)")
                continue
            a_ham = a_yol.read_text(encoding="utf-8")
            b_ham = b_yol.read_text(encoding="utf-8")

            if sadece_metin:
                a, b = gorunen_metin(a_ham), gorunen_metin(b_ham)
            elif dom:
                a, b = dom_normalize(a_ham), dom_normalize(b_ham)
            else:
                a, b = a_ham.splitlines(), b_ham.splitlines()

            fark = list(difflib.unified_diff(a, b, f"before/{dosya}", f"after/{dosya}", lineterm=""))
            if fark:
                toplam_fark += 1
                print(yazdirilabilir("\n".join(fark)))
                print()
            else:
                print(f"[ayni] {dosya}")

    baslik = "METIN" if sadece_metin else ("DOM YAPISI" if dom else "HAM HTML")
    print(f"\n=== {baslik} farki olan dosya: {toplam_fark} ===")
    return 1 if toplam_fark else 0


def main() -> int:
    p = argparse.ArgumentParser(description="Gorunum regresyon anlik goruntusu")
    p.add_argument("komut", choices=["before", "after", "diff"])
    p.add_argument("--online", action="store_true", help="cevirt icin agi kullan")
    p.add_argument("--text", action="store_true",
                   help="diff: sadece gorunen metni karsilastir")
    p.add_argument("--dom", action="store_true",
                   help="diff: etiket/oznitelik yapisini karsilastir (bosluk yoksayilir)")
    a = p.parse_args()

    if a.komut == "diff":
        return diff(a.text, a.dom)
    capture(a.komut, a.online)
    return 0


if __name__ == "__main__":
    sys.exit(main())
