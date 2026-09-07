# -*- coding: utf-8 -*-
"""Uygulama fabrikasi (app factory).

Dort tanitim sayfasi tamamen sablonlardan gelir. Haberler icin bir
SQLite dosyasi kullanilir; dosya yoksa ilk acilista kendiliginden
olusur, ayri bir kurulum adimi yoktur. `python run.py` yeterlidir.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask

from .config import ROOT, Config
from .extensions import db


def create_app(config_object=Config) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(ROOT / "static"),
        template_folder=str(ROOT / "templates"),
        # Goreli sqlite yolu buraya yazilir. Acikca veriliyor: Flask'in
        # varsayilani paketin (app/) yani basi olurdu.
        instance_path=str(ROOT / "instance"),
    )
    app.config.from_object(config_object)

    # --- veritabani (yalnizca haberler) ---
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    from . import models  # noqa: F401  -- tablolari db'ye tanitir
    with app.app_context():
        try:
            db.create_all()
        except Exception as hata:                       # noqa: BLE001
            # Tablo olusturulamasa bile (salt okunur disk vb.) dort
            # tanitim sayfasi calismaya devam etsin; onlar veritabanina
            # hic dokunmuyor. Yalnizca /news hata verir.
            app.logger.warning("Haber veritabani hazirlanamadi: %s", hata)

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

    from .blueprints.admin import blueprint_hazirla
    app.register_blueprint(
        blueprint_hazirla(), url_prefix=app.config["ADMIN_PATH"]
    )

    Path(app.config["UPLOAD_DIR"] / "news").mkdir(parents=True, exist_ok=True)

    # Ters proxy arkasindaysa gercek sema ve host okunsun.
    if app.config.get("TRUST_PROXY"):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    return app
