# -*- coding: utf-8 -*-
"""Tum ayarlar tek yerde. Degerler .env dosyasindan okunur.

Site .env dosyasi olmadan da calisir; hicbir deger zorunlu degil.

VERITABANI YALNIZCA HABERLER ICIN: dort tanitim sayfasinin icerigi
sablonlarda duruyor ve veritabanina hic dokunmuyor. Dosya yoksa
uygulama ilk acilista kendisi olusturur (bkz. factory.create_app).
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

# .env yoksa sessizce gec (ilk kurulum, CI vb.)
load_dotenv(ROOT / ".env")

# Sadece gelistirmede kullanilan sahte anahtar. Yayinda .env'ye
# gercek bir anahtar yaz (bkz. DEPLOY.md).
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
    ham = (os.environ.get("ADMIN_PATH") or "/admin").strip()
    if not ham.startswith("/"):
        ham = "/" + ham
    return ham.rstrip("/") or "/admin"


class Config:
    # --- yollar ---
    ROOT_DIR = ROOT
    STATIC_DIR = ROOT / "static"
    UPLOAD_DIR = ROOT / "static" / "uploads"

    # --- Flask ---
    # Oturum dil tercihini VE panel girisini tasir.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or GELISTIRME_ANAHTARI
    # Sablon degisince otomatik yenile (gelistirme kolayligi)
    TEMPLATES_AUTO_RELOAD = True

    # --- veritabani (yalnizca haberler) ---
    # Goreli sqlite yolu instance/ klasorune yazilir.
    #
    # Degisken adi bilerek NEWS_DATABASE_URL: kaldirilan CMS'ten kalma
    # .env dosyalarinda DATABASE_URL=sqlite:///toyota.db satiri olabilir
    # ve o adres ARSIV dosyasini gosterir. Ayri ad, haber tablosunun
    # yanlislikla arsivin icine yazilmasini engelliyor.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("NEWS_DATABASE_URL") or "sqlite:///news.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- dil ---
    LANGUAGES = {
        "tr": "Türkçe",
        "en": "English",
    }
    DEFAULT_LANG = "tr"

    # --- panel / guvenlik ---
    ADMIN_PATH = _admin_path()
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH") or ""
    ADMIN_SESSION_MINUTES = _int("ADMIN_SESSION_MINUTES", 60)
    ADMIN_MAX_ATTEMPTS = _int("ADMIN_MAX_ATTEMPTS", 5)
    ADMIN_LOCK_MINUTES = _int("ADMIN_LOCK_MINUTES", 15)

    # --- cerez ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=_int("ADMIN_SESSION_MINUTES", 60)
    )

    # Ters proxy arkasindaysa gercek istemci semasi okunsun; yoksa Flask
    # HTTPS'i goremez ve guvenli cerez calismaz.
    TRUST_PROXY = _bool("TRUST_PROXY", False)

    # --- haber gorseli ---
    UPLOAD_MAX_MB = _int("UPLOAD_MAX_MB", 4)
    MAX_CONTENT_LENGTH = _int("UPLOAD_MAX_MB", 4) * 1024 * 1024
