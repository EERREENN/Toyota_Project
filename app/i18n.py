# -*- coding: utf-8 -*-
"""Dil secimi ve Jinja ceviri kurulumu.

get_locale() legacy_app.py'den BIREBIR tasindi -- sira ayni:
URL parametresi -> session -> cookie -> tarayici basligi -> varsayilan.

Icerik metinleri artik content.py tarafindan cozuluyor; buradaki
`_()` / `{% trans %}` altyapisi yalnizca sablonlarda kalan az sayidaki
sabit metin ve ileride eklenecek panel arayuzu icin duruyor.
"""

from __future__ import annotations

from flask import current_app, request, session

import auto_translate


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


def install(app) -> None:
    """Jinja i18n eklentisini legacy_app.py ile ayni politikalarla kurar."""
    app.jinja_env.add_extension("jinja2.ext.i18n")
    # {% trans %} bloklarindaki girinti/satir sonlarini kirp
    app.jinja_env.policies["ext.i18n.trimmed"] = True
    # newstyle=False -> jinja metni "%" ile bicimlemez, yani icerikte
    # "%30" gibi ifadeler sorunsuz kullanilabilir.
    app.jinja_env.install_gettext_callables(
        gettext=lambda s: auto_translate.translate(s, get_locale()),
        ngettext=lambda s, p, n: auto_translate.translate(s if n == 1 else p, get_locale()),
        newstyle=False,
    )
