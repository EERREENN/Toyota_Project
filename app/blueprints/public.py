# -*- coding: utf-8 -*-
"""Herkese acik sayfalar.

legacy_app.py'deki 4 ayri rota (tmmt / global_toyota / uretim_sistemi /
cevre) tek bir dinamik rotaya indirildi: adresler artik veritabanindaki
`page.url` sutunundan geliyor. Ana sayfa hem "/" hem kendi adresinden
servis ediliyor -- bugunku davranisin aynisi.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .. import content
from ..i18n import get_locale

bp = Blueprint("public", __name__)


# ------------------------------------------------------------
#  Her sablonun gordugu ortak degerler
# ------------------------------------------------------------
@bp.app_context_processor
def ortak_degerler():
    dil = get_locale()
    return {
        "AKTIF_DIL": dil,
        "LANGUAGES": current_app.config["LANGUAGES"],
        "site": content.get_site(dil),
        "ana_sayfa_url": content.get_home_url(),
        "block_template": content.block_template,
        "sayi": content.sayi_metni,
        "map_payload": content.map_payload,
        "calc_payload": content.calc_payload,
        "news_items": content.news_items,
        # Tarih, aktif dilin yazimiyla basilir (bkz. content.tarih_metni).
        "tarih": lambda iso: content.tarih_metni(iso, dil),
    }


def _goster(sayfa):
    if sayfa is None:
        abort(404)
    return render_template(
        "page.html",
        sayfa=sayfa,
        nav=content.get_nav(get_locale(), sayfa.slug),
        css_files=sayfa.css_files,
    )


# ------------------------------------------------------------
#  Sayfalar
# ------------------------------------------------------------
@bp.route("/")
def home():
    return _goster(content.get_home(get_locale()))


@bp.route("/<slug>")
def page(slug: str):
    # Adres veritabaninda "/tmmt" seklinde tutuluyor.
    return _goster(content.get_page_by_url(f"/{slug}", get_locale()))


# ------------------------------------------------------------
#  Dil degistirme  (legacy_app.py'den birebir)
# ------------------------------------------------------------
@bp.route("/dil/<lang>")
def dil_degistir(lang: str):
    diller = current_app.config["LANGUAGES"]
    if lang not in diller:
        lang = current_app.config["DEFAULT_LANG"]
    session["lang"] = lang
    # Kullanici hangi sayfadaydiysa oraya geri don
    hedef = request.referrer or content.get_home_url()
    yanit = make_response(redirect(hedef))
    yanit.set_cookie("lang", lang, max_age=60 * 60 * 24 * 365)  # 1 yil
    return yanit


# ------------------------------------------------------------
#  robots.txt
#
#  Gizli panel adresi BILEREK yazilmiyor: robots.txt herkese acik bir
#  dosyadir, adresi oraya koymak onu ilan etmek olur. Panel zaten her
#  yanitinda X-Robots-Tag basligi ve <meta robots noindex> ile
#  kapatiliyor (Asama 3). .env'de ROBOTS_DISCLOSE_ADMIN=true yaparsan
#  yine de yazilir.
# ------------------------------------------------------------
@bp.route("/robots.txt")
def robots() -> Response:
    satirlar = ["User-agent: *", "Disallow: /admin/", "Disallow: /dil/"]
    if current_app.config.get("ROBOTS_DISCLOSE_ADMIN"):
        satirlar.append(f"Disallow: {current_app.config['ADMIN_PATH']}/")
    govde = "\n".join(satirlar) + "\n"
    yanit = make_response(govde)
    yanit.mimetype = "text/plain"
    return yanit


# ------------------------------------------------------------
#  404
# ------------------------------------------------------------
@bp.app_errorhandler(404)
def bulunamadi(_hata):
    return (
        render_template(
            "404.html",
            nav=content.get_nav(get_locale()),
            css_files=content.shell_css_files(),
        ),
        404,
    )
