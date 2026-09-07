# -*- coding: utf-8 -*-
"""Tum ayarlar tek yerde. Degerler .env dosyasindan okunur.

Site statik icerikle calisir; veritabani, oturum acma veya gizli
anahtar gerektiren bir yonetim paneli yoktur. .env dosyasi olmadan da
calisir -- tek kullanimi dil cerezini imzalayan FLASK_SECRET_KEY.
"""

from __future__ import annotations

import os
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


class Config:
    # --- yollar ---
    ROOT_DIR = ROOT
    STATIC_DIR = ROOT / "static"

    # --- Flask ---
    # Oturum yalnizca secilen dili tasir; baska hicbir sey saklanmaz.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or GELISTIRME_ANAHTARI
    # Sablon degisince otomatik yenile (gelistirme kolayligi)
    TEMPLATES_AUTO_RELOAD = True

    # --- dil ---
    LANGUAGES = {
        "tr": "Türkçe",
        "en": "English",
    }
    DEFAULT_LANG = "tr"

    # --- cerez ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)

    # Ters proxy arkasindaysa gercek istemci semasi okunsun; yoksa Flask
    # HTTPS'i goremez ve guvenli cerez calismaz.
    TRUST_PROXY = _bool("TRUST_PROXY", False)
