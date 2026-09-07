# -*- coding: utf-8 -*-
"""Yonetim paneli blueprint'i.

Adres .env'deki ADMIN_PATH'ten gelir (ornek: /panel-8f3a2c9d). Sitede
buraya giden HICBIR link, buton ya da ipucu yoktur -- adresi yalnizca
sen bilirsin.

Her yanit `X-Robots-Tag: noindex` basligi tasir; sablon tarafinda da
<meta name="robots" content="noindex, nofollow"> var. Ikisi birlikte,
adres bir sekilde sizsa bile arama motorlarina girmesini engeller.
"""

from __future__ import annotations

from flask import Blueprint

# template_folder BILEREK verilmiyor: sablonlar "admin/..." yoluyla
# cagriliyor. Aksi halde templates/admin/base.html ile sitenin
# templates/base.html'i ayni adi tasir ve uygulama klasoru oncelikli
# oldugu icin panel, SITENIN kabugunun icine render olur.
bp = Blueprint("admin", __name__)


@bp.after_request
def robotlara_kapat(yanit):
    yanit.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    # Panel sayfalari onbelleklenmesin: cikis yaptiktan sonra geri
    # tusuyla icerik gorunmesin.
    yanit.headers["Cache-Control"] = "no-store, max-age=0"
    return yanit


def blueprint_hazirla():
    """Alt modulleri yukleyip rotalari kaydeder.

    Import'lar fonksiyon icinde: modul yuklenirken dairesel import
    olusmasin diye (auth -> security -> models -> extensions).
    """
    from . import auth, blocks, media, pages, translations  # noqa: F401

    return bp
