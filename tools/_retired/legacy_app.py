from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    make_response,
)

from auto_translate import translate

app = Flask(__name__)
app.secret_key = "dev-secret-key-degistir"  # session imzalamak icin gerekli

# --- Dil ayarlari ---
LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
}
DEFAULT_LANG = "tr"


def get_locale():
    """Dil tercihini sirayla: URL parametresi -> session -> cookie -> tarayici."""
    # 1) ?lang=en gibi bir URL parametresi (tek seferlik onizleme icin)
    url_lang = request.args.get("lang")
    if url_lang in LANGUAGES:
        return url_lang
    # 2) Kullanicinin daha once sectigi dil (session)
    if session.get("lang") in LANGUAGES:
        return session["lang"]
    # 3) Kalici cookie
    cookie_lang = request.cookies.get("lang")
    if cookie_lang in LANGUAGES:
        return cookie_lang
    # 4) Tarayicinin Accept-Language basligina en iyi eslesme
    return request.accept_languages.best_match(list(LANGUAGES.keys())) or DEFAULT_LANG


# --- i18n ---
# Sablon metinleri Turkce yazilir; { _('...') } ve {% trans %} bloklari
# istege gore otomatik olarak Ingilizce'ye cevrilir (auto_translate).
# newstyle=False -> jinja metni "%" ile bicimlemez, yani icerikte "%30"
# gibi ifadeler sorunsuz kullanilabilir.
app.jinja_env.add_extension("jinja2.ext.i18n")
app.jinja_env.policies["ext.i18n.trimmed"] = True  # {% trans %} girinti/satir sonu kirp
app.jinja_env.install_gettext_callables(
    gettext=lambda s: translate(s, get_locale()),
    ngettext=lambda s, p, n: translate(s if n == 1 else p, get_locale()),
    newstyle=False,
)


@app.context_processor
def inject_conf():
    """Sablonlarin aktif dili ve dil listesini gormesi icin."""
    return {
        "LANGUAGES": LANGUAGES,
        "AKTIF_DIL": get_locale(),
    }


# --- Dil degistirme endpoint'i ---
@app.route("/dil/<lang>")
def dil_degistir(lang):
    if lang not in LANGUAGES:
        lang = DEFAULT_LANG
    session["lang"] = lang
    # Kullanici hangi sayfadaydiysa oraya geri don
    hedef = request.referrer or url_for("tmmt")
    resp = make_response(redirect(hedef))
    resp.set_cookie("lang", lang, max_age=60 * 60 * 24 * 365)  # 1 yil
    return resp


# --- 1. SAYFA (acilis): TMMT ---
@app.route("/")
@app.route("/tmmt")
def tmmt():
    return render_template("tmmt.html", aktif_sayfa="tmmt")


# --- 2. SAYFA: Global Toyota ---
@app.route("/global-toyota")
def global_toyota():
    return render_template("global_toyota.html", aktif_sayfa="global")


# --- 3. SAYFA: Toyota Production System ---
@app.route("/uretim-sistemi")
def uretim_sistemi():
    return render_template("uretim_sistemi.html", aktif_sayfa="uretim")


# --- 4. SAYFA: Toyota ve Çevre ---
@app.route("/cevre")
def cevre():
    return render_template("cevre.html", aktif_sayfa="cevre")


if __name__ == "__main__":
    app.run(debug=True)
