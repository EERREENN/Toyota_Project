# -*- coding: utf-8 -*-
"""Yonetim paneli blueprint'i.

Adres .env'deki ADMIN_PATH'ten gelir (varsayilan /admin). Sitede
buraya giden HICBIR link yoktur.

Her yanit `X-Robots-Tag: noindex` basligi tasir; sablon tarafinda da
<meta name="robots" content="noindex, nofollow"> var.
"""

from __future__ import annotations

from flask import Blueprint

# template_folder BILEREK verilmiyor: sablonlar "admin/..." yoluyla
# cagriliyor. Aksi halde templates/admin/base.html ile sitenin
# templates/base.html'i ayni adi tasir.
bp = Blueprint("admin", __name__)


@bp.after_request
def robotlara_kapat(yanit):
    yanit.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    yanit.headers["Cache-Control"] = "no-store, max-age=0"
    return yanit


def blueprint_hazirla():
    """Alt modulleri yukleyip rotalari kaydeder."""
    from . import auth, news  # noqa: F401

    return bp
