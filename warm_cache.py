# -*- coding: utf-8 -*-
"""Ceviri onbellegini doldur.  [ESKI ARAC]

DIKKAT: Icerik veritabanina tasindiktan sonra bu betigin isi kalmadi.
Sayfalari gezerek onbellegi doldurmaya calisir, ama ceviriler artik
`translation` tablosundan geliyor. Bunun yerine:

    python tools/ceviri_yenile.py

Bu dosya, auto_cache.json uzerinde dogrudan calismak gerekirse diye
duruyor (ornek: --refresh ile cevrilememis girdileri yeniden denemek).


Tum sayfalari Ingilizce olarak isler; her metin `translations/auto_cache.json`
dosyasina yazilir. Yeni icerik ekledikten sonra bir kez calistir:

    python warm_cache.py            # eksik cevirileri tamamla
    python warm_cache.py --refresh  # ayrica cevrilememis girdileri yeniden dene

Calistirmasan da olur; ilk ziyarette metinler kendiliginden cevrilir.
Bu betik sadece ilk yuklemeyi hizlandirir ve internetsiz ortamda
Ingilizce'nin hazir olmasini saglar.
"""

import sys
import time

import auto_translate
from app import create_app
from app.config import Config

app = create_app()
LANGUAGES = Config.LANGUAGES

PAGES = ["/", "/global-toyota", "/uretim-sistemi", "/cevre"]
DILLER = [d for d in LANGUAGES if d != auto_translate.SOURCE_LANG]


def _bekle_devre_kesici():
    kalan = auto_translate.pause_remaining()
    if kalan > 0:
        print(f"  ... devre kesici acik, {int(kalan) + 1} sn bekleniyor")
        time.sleep(kalan + 1)


def doldur(client) -> None:
    onceki = -1
    ayni = 0
    for tur in range(1, 12):
        for dil in DILLER:
            for yol in PAGES:
                r = client.get(f"{yol}?lang={dil}")
                if r.status_code != 200:
                    print(f"  ! {yol} ({dil}) -> HTTP {r.status_code}")
            _bekle_devre_kesici()

        toplam = sum(auto_translate.cache_stats().values())
        print(f"tur {tur}: onbellekte {toplam} metin")
        ayni = ayni + 1 if toplam == onceki else 0
        if ayni >= 1:
            break
        onceki = toplam


def yenile(client) -> None:
    """Kaynak metinle ayni kalmis (cevrilememis) girdileri yeniden dene."""
    for dil in DILLER:
        bucket = auto_translate._cache.get(dil, {})
        adaylar = [
            k for k, v in bucket.items()
            if k == v and len(k) > 3 and any(c.islower() for c in k) and " " in k
        ]
        print(f"[{dil}] yeniden denenecek {len(adaylar)} girdi")
        for i, k in enumerate(adaylar, 1):
            _bekle_devre_kesici()
            yeni = auto_translate.translate_fresh(k, dil)
            if yeni and yeni != k:
                print(f"  + {k[:45]!r} -> {yeni[:45]!r}")
            time.sleep(0.3)


def main() -> int:
    client = app.test_client()
    doldur(client)
    if "--refresh" in sys.argv:
        yenile(client)
        doldur(client)
    print("\nOnbellek durumu:", auto_translate.cache_stats())
    print(f"Dosya: {auto_translate.CACHE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
