# -*- coding: utf-8 -*-
"""Sitenin rotalari.

Her sayfa dogrudan kendi sablonunu basar; arada veritabani, icerik
sorgusu ya da blok cozumleme yok:

    /                 -> pages/tmmt.html   (ana sayfa)
    /tmmt             -> pages/tmmt.html
    /global-toyota    -> pages/global.html
    /uretim-sistemi   -> pages/tps.html
    /cevre            -> pages/cevre.html
    /news             -> pages/news.html          (haber listesi,
                                                   ?page=N, ?kategori=K)
    /news/<slug>      -> pages/news_detail.html   (haber detayi)

Sayfanin basligi, stil dosyalari ve icerigi sablonun kendi icinde
tanimli; buraya yalnizca adres bilgisi dusuyor.
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

from .. import haberler
from ..i18n import get_locale
from ..metin import tarih_metni

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
#  Haberler
#
#  Dort tanitim sayfasindan farkli olarak icerik sablonda degil
#  veritabaninda; cunku haber listesi degisken uzunlukta ve
#  editorden geliyor. Sorgular app/haberler.py icinde; buradaki
#  rotalar veritabanini dogrudan gormez.
# ------------------------------------------------------------
@bp.route("/news")
def news():
    dil = get_locale()
    # Olmayan bir sayfa numarasi istendiginde bos liste yerine 404:
    # /news?page=99 gecerli bir adres degil.
    #
    # ?kategori=... icin ayni sertlik YOK: bilinmeyen anahtar 404
    # degil filtresiz tam liste verir (bkz. haberler.sayfa_getir).
    sayfalama = haberler.sayfa_getir(
        dil, request.args.get("page"), request.args.get("kategori")
    )
    if sayfalama is None:
        abort(404)
    return render_template(
        "pages/news.html",
        sayfalama=sayfalama,
        haberler=sayfalama.haberler,
        # Filtre cubugu: yalnizca haberi olan kategoriler.
        kategoriler=haberler.kategori_sayilari(dil),
        # Dogrulanmis anahtar: bilinmeyen bir deger burada None'dir,
        # cubukta "Tumu" isaretli kalir.
        secili_kategori=sayfalama.kategori,
        tarih=lambda iso: tarih_metni(iso, dil),
    )


@bp.route("/news/<slug>")
def news_detail(slug: str):
    dil = get_locale()
    haber = haberler.bul(slug, dil)
    if haber is None:
        abort(404)
    return render_template(
        "pages/news_detail.html",
        haber=haber,
        tarih=lambda iso: tarih_metni(iso, dil),
    )


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
