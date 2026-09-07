# -*- coding: utf-8 -*-
"""Tum ayarlar tek yerde. Degerler .env dosyasindan okunur.

Kodda hicbir sifre/anahtar sabit degildir; eksikse uygulama uyarir.
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

# .env yoksa sessizce gec (ilk kurulum, CI vb.)
load_dotenv(ROOT / ".env")

# Sadece gelistirmede kullanilan sahte anahtar. Yayinda .env'den
# gercek bir anahtar gelmezse Config.dogrula() hata verir.
GELISTIRME_ANAHTARI = "gelistirme-icin-gecici-anahtar-yayinda-kullanma"


def _bool(ad: str, varsayilan: bool = False) -> bool:
    ham = os.environ.get(ad)
    if not ham:
        return varsayilan
    return ham.strip().lower() in {"1", "true", "yes", "evet", "on"}


def _int(ad: str, varsayilan: int) -> int:
    try:
        return int((os.environ.get(ad) or "").strip())
    except (TypeError, ValueError):
        return varsayilan


def _admin_path() -> str:
    """Basinda / olan, sonunda / olmayan bir yol dondur."""
    ham = (os.environ.get("ADMIN_PATH") or "/admin").strip()
    if not ham.startswith("/"):
        ham = "/" + ham
    return ham.rstrip("/") or "/admin"


class Config:
    # --- yollar ---
    ROOT_DIR = ROOT
    UPLOAD_DIR = ROOT / "static" / "uploads"
    STATIC_DIR = ROOT / "static"

    # --- Flask ---
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or GELISTIRME_ANAHTARI
    # Sablon degisince otomatik yenile (gelistirme kolayligi)
    TEMPLATES_AUTO_RELOAD = True

    # --- veritabani ---
    # Goreli sqlite yolu Flask'in instance/ klasorune yazilir.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///toyota.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLITE_WAL = _bool("SQLITE_WAL", False)

    # --- dil ---
    # legacy_app.py'den birebir tasindi
    LANGUAGES = {
        "tr": "Türkçe",
        "en": "English",
    }
    DEFAULT_LANG = "tr"
    SOURCE_LANG = "tr"

    # --- panel / guvenlik ---
    ADMIN_PATH = _admin_path()
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH") or ""
    ADMIN_SESSION_MINUTES = _int("ADMIN_SESSION_MINUTES", 60)
    ADMIN_MAX_ATTEMPTS = _int("ADMIN_MAX_ATTEMPTS", 5)
    ADMIN_LOCK_MINUTES = _int("ADMIN_LOCK_MINUTES", 15)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=_int("ADMIN_SESSION_MINUTES", 60))
    TRUST_PROXY = _bool("TRUST_PROXY", False)

    # --- gorsel yukleme ---
    UPLOAD_MAX_MB = _int("UPLOAD_MAX_MB", 4)
    MAX_CONTENT_LENGTH = _int("UPLOAD_MAX_MB", 4) * 1024 * 1024
    ALLOWED_IMAGE_MIMES = ("image/jpeg", "image/png", "image/webp", "image/gif")

    # --- davranis anahtarlari ---
    # Harita tesis metinleri cevrilsin mi? Bugunku site cevirmiyor.
    MAP_MARKERS_TRANSLATABLE = _bool("MAP_MARKERS_TRANSLATABLE", False)
    # Gizli panel adresi robots.txt'ye yazilsin mi? (Onerilen: hayir)
    ROBOTS_DISCLOSE_ADMIN = _bool("ROBOTS_DISCLOSE_ADMIN", False)

    @classmethod
    def eksikler(cls) -> list[str]:
        """Yayina alinmadan once doldurulmasi gerekenler."""
        sorunlar = []
        if cls.SECRET_KEY == GELISTIRME_ANAHTARI:
            sorunlar.append("FLASK_SECRET_KEY .env'de tanimli degil")
        if not cls.ADMIN_PASSWORD_HASH:
            sorunlar.append("ADMIN_PASSWORD_HASH .env'de tanimli degil "
                            "(uretmek icin: python tools/hash_password.py)")
        if cls.ADMIN_PATH == "/admin":
            sorunlar.append("ADMIN_PATH varsayilan /admin -- gizli bir adres ver")
        return sorunlar
