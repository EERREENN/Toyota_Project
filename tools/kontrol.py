# -*- coding: utf-8 -*-
"""Tum otomatik dogrulamalari sirayla calistirir.

    python tools/kontrol.py

Her adim bagimsiz bir soruyu yanitlar. Hepsi yesilse tasima sirasinda
hicbir sey kaybolmamis demektir.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

ADIMLAR = [
    ("Icerik butunlugu",
     "Tasima oncesi sablonlardaki her metin veritabaninda var mi?",
     ["tools/verify_seed.py"]),

    ("Site ciktisi",
     "Sayfalarda gorunen metin, tasimadan onceki haliyle ayni mi?",
     ["tools/snapshot.py", "diff", "--text"]),

    ("CSS bolunmesi",
     "1162 satirlik eski CSS'in her kurali yeni dosyalarda duruyor mu?",
     ["tools/css_check.py"]),

    ("Panel gidis-donus",
     "Panelden kaydetmek veriyi bozuyor mu?",
     ["tools/panel_roundtrip.py"]),
]


def calistir(betik: list[str]) -> tuple[int, str]:
    sonuc = subprocess.run(
        [PY] + betik,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return sonuc.returncode, (sonuc.stdout or "") + (sonuc.stderr or "")


def main() -> int:
    print()
    print("=" * 64)
    print("  TOYOTA CMS -- OTOMATIK DOGRULAMA")
    print("=" * 64)

    # Once guncel anlik goruntuyu al (site ciktisi karsilastirmasi icin)
    print("\n[hazirlik] sayfalarin anlik goruntusu aliniyor...")
    kod, _ = calistir(["tools/snapshot.py", "after"])
    if kod != 0:
        print("  ! anlik goruntu alinamadi")
        return 2

    basarisiz = []
    for i, (ad, soru, betik) in enumerate(ADIMLAR, 1):
        print()
        print(f"[{i}/{len(ADIMLAR)}] {ad}")
        print(f"        {soru}")
        kod, cikti = calistir(betik)
        if kod == 0:
            ozet = [s for s in cikti.splitlines() if "SONUC" in s or "farki olan" in s]
            for s in ozet[-2:]:
                print(f"        {s.strip()}")
            print("        >> GECTI")
        else:
            basarisiz.append(ad)
            print("        >> BASARISIZ")
            for s in cikti.splitlines()[-25:]:
                print(f"        | {s}")

    print()
    print("=" * 64)
    if basarisiz:
        print(f"  {len(basarisiz)} ADIM BASARISIZ: {', '.join(basarisiz)}")
        print("=" * 64)
        return 1
    print("  TUM KONTROLLER GECTI")
    print("=" * 64)
    print()
    print("  Geriye elle bakilmasi gerekenler:")
    print("   - sayfalarin gorunumu (arka planlar, renkler, animasyonlar)")
    print("   - panelde suruk-birak siralama")
    print("   - mobil goruntu (dar pencere)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
