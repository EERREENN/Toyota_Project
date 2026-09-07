# -*- coding: utf-8 -*-
"""Haber gorseli yukleme.

CMS gorsel kutuphanesi bu asamada yok; haber formunun kendi
dosya alani static/uploads/news/ altina yazar. Kayit, News.image
sutununda static/ klasorune gore yol olarak durur
(ornek: "uploads/news/a1b2c3.jpg").
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

IZINLI_UZANTILAR = {".jpg", ".jpeg", ".png", ".webp"}
HABER_KLASORU = Path("uploads") / "news"


class YuklemeHatasi(Exception):
    """Kullaniciya gosterilecek, beklenen bir yukleme hatasi."""


def _kok() -> Path:
    return Path(current_app.config["STATIC_DIR"])


def haber_klasoru() -> Path:
    yol = _kok() / HABER_KLASORU
    yol.mkdir(parents=True, exist_ok=True)
    return yol


def uzanti_uygun_mu(ad: str) -> bool:
    return Path(ad).suffix.lower() in IZINLI_UZANTILAR


def panel_yuklenen_mi(gorsel_yolu: str) -> bool:
    """Bu dosya panelden mi geldi? (ornek gorselleri silme)"""
    if not gorsel_yolu:
        return False
    parca = Path(gorsel_yolu.replace("\\", "/"))
    try:
        return parca.parts[:2] == ("uploads", "news")
    except Exception:  # noqa: BLE001
        return False


def kaydet(dosya: FileStorage | None) -> str:
    """Yuklenen dosyayi yazar, static'e gore yolu dondurur.

    Dosya yoksa veya adi bossa bos metin doner (placeholder).
    """
    if dosya is None or not dosya.filename:
        return ""

    ham_ad = secure_filename(dosya.filename)
    if not ham_ad or not uzanti_uygun_mu(ham_ad):
        raise YuklemeHatasi(
            "Görsel jpg, jpeg, png veya webp olmalı."
        )

    azami = current_app.config.get("UPLOAD_MAX_MB", 4) * 1024 * 1024
    dosya.stream.seek(0, 2)
    boyut = dosya.stream.tell()
    dosya.stream.seek(0)
    if boyut > azami:
        raise YuklemeHatasi(
            f"Görsel en fazla {current_app.config.get('UPLOAD_MAX_MB', 4)} MB olabilir."
        )
    if boyut == 0:
        raise YuklemeHatasi("Yüklenen görsel boş.")

    uzanti = Path(ham_ad).suffix.lower()
    ad = f"{uuid4().hex}{uzanti}"
    hedef = haber_klasoru() / ad
    dosya.save(hedef)
    return str(HABER_KLASORU / ad).replace("\\", "/")


def sil_dosya(gorsel_yolu: str) -> None:
    """Yalnizca panelin yukledigi haber gorselini siler."""
    if not panel_yuklenen_mi(gorsel_yolu):
        return
    yol = (_kok() / gorsel_yolu).resolve()
    kok = haber_klasoru().resolve()
    if kok not in yol.parents and yol != kok:
        return
    if yol.is_file():
        yol.unlink()
