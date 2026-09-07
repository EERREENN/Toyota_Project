# -*- coding: utf-8 -*-
"""Dil secimi ve sablon cevirisi.

get_locale() sirasi:
    URL parametresi -> session -> cookie -> tarayici basligi -> varsayilan.

Sablonlardaki her {{ _('...') }} cagrisi app/ceviri.py -> EN sozlugune
bakar. Ag uzerinden calisma zamani cevirisi YOK; karsiligi yazilmamis
metin Turkce haliyle gosterilir.
"""

from __future__ import annotations

from flask import current_app, request, session

from .ceviri import EN


def get_locale() -> str:
    diller = current_app.config["LANGUAGES"]
    varsayilan = current_app.config["DEFAULT_LANG"]

    # 1) ?lang=en gibi bir URL parametresi (tek seferlik onizleme icin)
    url_dili = request.args.get("lang")
    if url_dili in diller:
        return url_dili
    # 2) Kullanicinin daha once sectigi dil (session)
    if session.get("lang") in diller:
        return session["lang"]
    # 3) Kalici cookie
    cerez = request.cookies.get("lang")
    if cerez in diller:
        return cerez
    # 4) Tarayicinin Accept-Language basligina en iyi eslesme
    return request.accept_languages.best_match(list(diller.keys())) or varsayilan


def cevir(metin: str) -> str:
    """Metnin aktif dildeki karsiligi. Karsiligi yoksa Turkcesi doner."""
    return EN.get(metin, metin) if get_locale() == "en" else metin


def install(app) -> None:
    """Jinja i18n eklentisi -- {{ _('...') }} ve {% trans %}."""
    app.jinja_env.add_extension("jinja2.ext.i18n")
    # {% trans %} bloklarindaki girinti/satir sonlarini kirp
    app.jinja_env.policies["ext.i18n.trimmed"] = True
    # newstyle=False -> jinja metni "%" ile bicimlemez, yani icerikte
    # "%30" gibi ifadeler sorunsuz kullanilabilir.
    app.jinja_env.install_gettext_callables(
        gettext=cevir,
        ngettext=lambda s, p, n: cevir(s if n == 1 else p),
        newstyle=False,
    )
