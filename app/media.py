# -*- coding: utf-8 -*-
"""Gorsel yukleme ve kutuphane.

GUVENLIK NOTLARI
----------------
* Dosya adina GUVENILMEZ. Yuklenen ad yalnizca kayitta gosterilmek uzere
  saklanir; diske rastgele bir adla yazilir. Boylece "../../" gibi yol
  oyunlari ve ayni adi tekrar yukleyip ustune yazma imkansiz olur.
* Uzanti da yeterli degil: dosya Pillow ile GERCEKTEN acilip resim
  oldugu dogrulanir. .jpg adi verilmis bir betik boylece elenir.
* Boyut siniri Flask'in MAX_CONTENT_LENGTH ayariyla istek duzeyinde
  uygulanir (.env -> UPLOAD_MAX_MB).
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app

from .extensions import db
from .models import MediaAsset

# Kabul edilen turler ve diske yazilacak uzantilari
UZANTILAR = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


class YuklemeHatasi(Exception):
    """Editore gosterilecek, anlasilir hata."""


def _hedef_klasor() -> tuple[Path, str]:
    """uploads/YIL/AY -- tek klasorde binlerce dosya birikmesin."""
    simdi = datetime.now(timezone.utc)
    goreli = f"uploads/{simdi:%Y}/{simdi:%m}"
    mutlak = Path(current_app.config["STATIC_DIR"]) / goreli
    mutlak.mkdir(parents=True, exist_ok=True)
    return mutlak, goreli


def _dogrula(dosya) -> tuple[str, int, int]:
    """Gercekten resim mi? (mime, genislik, yukseklik) dondurur."""
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:  # pragma: no cover
        raise YuklemeHatasi("Pillow kurulu değil: pip install -r requirements.txt")

    dosya.stream.seek(0)
    try:
        with Image.open(dosya.stream) as resim:
            resim.verify()                 # bozuk / sahte dosyayi ele
    except (UnidentifiedImageError, OSError, ValueError):
        raise YuklemeHatasi(
            "Bu dosya bir resim değil ya da bozuk. "
            "JPG, PNG, WebP veya GIF yükle."
        )

    # verify() akisi tuketir; olculer icin yeniden ac
    dosya.stream.seek(0)
    with Image.open(dosya.stream) as resim:
        bicim = (resim.format or "").upper()
        genislik, yukseklik = resim.size

    mime = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
        "GIF": "image/gif",
    }.get(bicim)

    if mime not in UZANTILAR:
        raise YuklemeHatasi(
            f"'{bicim or 'bilinmeyen'}' biçimi desteklenmiyor. "
            "JPG, PNG, WebP veya GIF yükle."
        )
    return mime, genislik, yukseklik


def yukle(dosya, alt: str | None = None) -> MediaAsset:
    """Yuklenen dosyayi diske yazar ve kaydini olusturur."""
    if dosya is None or not getattr(dosya, "filename", ""):
        raise YuklemeHatasi("Dosya seçilmedi.")

    mime, genislik, yukseklik = _dogrula(dosya)

    klasor, goreli_klasor = _hedef_klasor()
    ad = secrets.token_hex(8) + UZANTILAR[mime]
    hedef = klasor / ad

    dosya.stream.seek(0)
    veri = dosya.stream.read()
    hedef.write_bytes(veri)

    varlik = MediaAsset(
        path=f"{goreli_klasor}/{ad}",
        original_name=(dosya.filename or "")[:255],
        mime=mime,
        width=genislik,
        height=yukseklik,
        size_bytes=len(veri),
        alt=(alt or "").strip() or None,
        is_builtin=False,
    )
    db.session.add(varlik)
    db.session.commit()
    return varlik


def sil(varlik: MediaAsset) -> None:
    """Kaydi ve dosyayi siler. Projeyle gelen gorseller silinemez."""
    if varlik.is_builtin:
        raise YuklemeHatasi(
            "Bu görsel projeyle birlikte geliyor, panelden silinemez."
        )

    yol = Path(current_app.config["STATIC_DIR"]) / varlik.path
    try:
        yol.unlink(missing_ok=True)
    except OSError:
        pass                      # dosya gitmisse kayit yine de silinsin

    db.session.delete(varlik)
    db.session.commit()


def listele() -> list[MediaAsset]:
    """Once yeni yuklenenler, sonra projeyle gelenler."""
    return list(
        db.session.query(MediaAsset)
        .order_by(MediaAsset.is_builtin, MediaAsset.uploaded_at.desc())
    )


def kullanim_sayisi(varlik: MediaAsset) -> int:
    """Bu gorsel kac yerde kullaniliyor? (silmeden once uyarmak icin)"""
    from .models import Block, BlockItem, Page

    sayi = db.session.query(Page).filter_by(background_image_id=varlik.id).count()
    sayi += db.session.query(BlockItem).filter_by(image_id=varlik.id).count()
    for blok in db.session.query(Block).all():
        if (blok.settings or {}).get("image_id") == varlik.id:
            sayi += 1
    return sayi


def boyut_metni(bayt: int) -> str:
    if bayt < 1024:
        return f"{bayt} B"
    if bayt < 1024 * 1024:
        return f"{bayt / 1024:.0f} KB"
    return f"{bayt / (1024 * 1024):.1f} MB"
