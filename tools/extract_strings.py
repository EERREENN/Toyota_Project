# -*- coding: utf-8 -*-
"""Sablonlardaki cevrilebilir metinleri Jinja'nin kendi ayristiricisiyla cikarir.

Bu, `{{ _('...') }}` ve `{% trans %}` icindeki metinlerin -- trimmed politikasi
uygulanmis, yani coklu satirin tek satira indirgenmis -- BIREBIR halini verir.
Ceviri onbelleginin (translations/auto_cache.json) anahtarlari da tam olarak
bu metinlerdir.

Kullanim:
    python tools/extract_strings.py                # sablon -> metin listesi
    python tools/extract_strings.py --json out.json
    python tools/extract_strings.py --check-cache  # hangileri onbellekte var
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jinja2 import Environment
from jinja2.ext import extract_from_ast

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
CACHE = ROOT / "translations" / "auto_cache.json"


def env_kur() -> Environment:
    """app.py ile AYNI politikalar -- yoksa trimmed farkli calisir."""
    env = Environment(extensions=["jinja2.ext.i18n"])
    env.policies["ext.i18n.trimmed"] = True
    return env


def sablondan_cikar(env: Environment, yol: Path) -> list[str]:
    kaynak = yol.read_text(encoding="utf-8")
    ast = env.parse(kaynak)
    cikan = []
    for _lineno, _func, mesaj in extract_from_ast(ast):
        if isinstance(mesaj, tuple):          # ngettext
            cikan.extend(m for m in mesaj if m)
        elif mesaj:
            cikan.append(mesaj)
    return cikan


def topla() -> dict[str, list[str]]:
    env = env_kur()
    sonuc = {}
    for yol in sorted(TEMPLATES.glob("*.html")):
        sonuc[yol.name] = sablondan_cikar(env, yol)
    return sonuc


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", metavar="DOSYA")
    p.add_argument("--check-cache", action="store_true")
    a = p.parse_args()

    veri = topla()
    toplam = sum(len(v) for v in veri.values())

    if a.json:
        Path(a.json).write_text(
            json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"{toplam} metin -> {a.json}")

    if a.check_cache:
        onbellek = json.loads(CACHE.read_text(encoding="utf-8")).get("en", {})
        eksik = []
        for dosya, metinler in veri.items():
            for m in metinler:
                if m not in onbellek:
                    eksik.append((dosya, m))
        print(f"toplam metin      : {toplam}")
        print(f"onbellekte var    : {toplam - len(eksik)}")
        print(f"onbellekte YOK    : {len(eksik)}")
        for dosya, m in eksik:
            print(f"  [{dosya}] {m[:80]!r}")
        return 0

    if not a.json:
        for dosya, metinler in veri.items():
            print(f"\n=== {dosya}  ({len(metinler)} metin) ===")
            for m in metinler:
                print(f"  {m[:100]!r}")
    print(f"\nTOPLAM: {toplam}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
