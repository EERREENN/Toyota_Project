# -*- coding: utf-8 -*-
"""Uygulama fabrikasi (app factory).

Asama 2'den itibaren siteyi bu fabrika servis ediyor; legacy_app.py
kaldirildi. Admin blueprint'i Asama 3'te eklenecek.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask

from .config import ROOT, Config
from .extensions import db, wal_ayarla


def create_app(config_object=Config) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(ROOT / "static"),
        template_folder=str(ROOT / "templates"),
        instance_path=str(ROOT / "instance"),
    )
    app.config.from_object(config_object)

    # instance/ klasoru yoksa olustur (sqlite dosyasi buraya yazilir)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # SQLite PRAGMA'lari icin (bkz. extensions.py)
    wal_ayarla(app.config.get("SQLITE_WAL", False))

    db.init_app(app)

    # Modeller import edilmezse db.create_all() tablolari bilmez.
    from . import models  # noqa: F401

    # Jinja i18n (legacy_app.py'deki kurulumun aynisi)
    from . import i18n
    i18n.install(app)

    # Sozluk aramasinin sunucu tarafi: sablon, aranacak metni Turkce
    # karakterlerden arindirilmis halde data- ozniteligine basiyor.
    from . import content
    app.jinja_env.filters["sadelestir"] = content.sadelestir

    # --- rotalar ---
    from .blueprints.public import bp as public_bp
    app.register_blueprint(public_bp)

    # --- panel ---
    # Adres .env'deki ADMIN_PATH'ten geliyor; kodda sabit degil.
    from .blueprints.admin import blueprint_hazirla
    app.register_blueprint(blueprint_hazirla(), url_prefix=app.config["ADMIN_PATH"])

    # Ters proxy arkasindaysa gercek istemci IP'si ve sema okunsun.
    # Bu olmadan hem IP kilidi tum ziyaretcileri tek IP sanar hem de
    # Flask kendini HTTP zanneder.
    if app.config.get("TRUST_PROXY"):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    return app
