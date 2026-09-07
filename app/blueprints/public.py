# -*- coding: utf-8 -*-
"""Sitenin rotalari.

Her sayfa dogrudan kendi sablonunu basar; arada veritabani, icerik
sorgusu ya da blok cozumleme yok:

    /                 -> pages/tmmt.html   (ana sayfa)
    /tmmt             -> pages/tmmt.html
    /global-toyota    -> pages/global.html
    /uretim-sistemi   -> pages/tps.html
    /cevre            -> pages/cevre.html

Sayfanin basligi, stil dosyalari ve icerigi sablonun kendi icinde
tanimli; buraya yalnizca adres bilgisi dusuyor.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    Response,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..i18n import get_locale

bp = Blueprint("public", __name__)


# ------------------------------------------------------------
#  Her sablonun gordugu ortak degerler
# ------------------------------------------------------------
@bp.app_context_processor
def ortak_degerler():
    return {
        "AKTIF_DIL": get_locale(),
    }


# ------------------------------------------------------------
#  Sayfalar
# ------------------------------------------------------------
@bp.route("/tmmt")
def tmmt():
    return render_template("pages/tmmt.html")


@bp.route("/")
def ana_sayfa():
    # Ana sayfa TMMT'nin kendisi -- iki adres, tek sayfa.
    return tmmt()


@bp.route("/global-toyota")
def global_toyota():
    return render_template("pages/global.html")


@bp.route("/uretim-sistemi")
def uretim_sistemi():
    return render_template("pages/tps.html")


@bp.route("/cevre")
def cevre():
    return render_template("pages/cevre.html")


# ------------------------------------------------------------
#  Dil degistirme
# ------------------------------------------------------------
@bp.route("/dil/<lang>")
def dil_degistir(lang: str):
    diller = current_app.config["LANGUAGES"]
    if lang not in diller:
        lang = current_app.config["DEFAULT_LANG"]
    session["lang"] = lang
    # Kullanici hangi sayfadaydiysa oraya geri don
    hedef = request.referrer or url_for("public.tmmt")
    yanit = make_response(redirect(hedef))
    yanit.set_cookie("lang", lang, max_age=60 * 60 * 24 * 365)  # 1 yil
    return yanit


# ------------------------------------------------------------
#  robots.txt
#
#  /dil/ disarida: arama motoru ayni sayfayi iki dilde iki kez
#  taramasin, yonlendirme adresleri dizine girmesin diye.
# ------------------------------------------------------------
@bp.route("/robots.txt")
def robots() -> Response:
    govde = "\n".join(["User-agent: *", "Disallow: /dil/"]) + "\n"
    yanit = make_response(govde)
    yanit.mimetype = "text/plain"
    return yanit


# ------------------------------------------------------------
#  404
# ------------------------------------------------------------
@bp.app_errorhandler(404)
def bulunamadi(_hata):
    return render_template("404.html"), 404
