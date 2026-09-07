# -*- coding: utf-8 -*-
"""Uygulama fabrikasi (app factory).

Site statik sayfa sablonlariyla calisir: veritabani, goc ya da tohum
adimi yoktur. `python run.py` yeterlidir.
"""

from __future__ import annotations

from flask import Flask

from .config import ROOT, Config


def create_app(config_object=Config) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(ROOT / "static"),
        template_folder=str(ROOT / "templates"),
    )
    app.config.from_object(config_object)

    # Jinja i18n -- sablonlardaki {{ _('...') }} metinleri
    from . import i18n
    i18n.install(app)

    # Sozluk aramasinin sunucu tarafi: sablon, aranacak metni Turkce
    # karakterlerden arindirilmis halde data- ozniteligine basiyor.
    from . import metin
    app.jinja_env.filters["sadelestir"] = metin.sadelestir

    # --- rotalar ---
    from .blueprints.public import bp as public_bp
    app.register_blueprint(public_bp)

    # Ters proxy arkasindaysa gercek sema ve host okunsun.
    if app.config.get("TRUST_PROXY"):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    return app
