# -*- coding: utf-8 -*-
"""Giris, cikis, sifre degistirme."""

from __future__ import annotations

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ... import security
from . import bp


@bp.route("/", methods=["GET", "POST"])
def login():
    """Giris ekrani.

    Yanlis sifrede BILEREK 404 donuyoruz: "hatali sifre" mesaji, adresi
    tesadufen bulan birine burada bir panel oldugunu soylerdi.
    """
    if security.oturum_gecerli():
        return redirect(url_for("admin.news_list"))

    if request.method == "POST":
        security.csrf_dogrula()
        ip = security.istemci_ip()

        if security.kilitli_mi(ip):
            abort(404)

        if security.sifre_dogru(request.form.get("parola", "")):
            security.basarili_deneme(ip)
            security.giris_yap()
            hedef = request.args.get("next") or url_for("admin.news_list")
            if not hedef.startswith(current_app.config["ADMIN_PATH"]):
                hedef = url_for("admin.news_list")
            return redirect(hedef)

        security.basarisiz_deneme(ip)
        abort(404)

    return render_template(
        "admin/login.html", csrf=security.csrf_token())


@bp.route("/cikis", methods=["POST"])
@security.admin_gerekli
def logout():
    security.csrf_dogrula()
    security.cikis_yap()
    return redirect(url_for("admin.login"))


@bp.route("/sifre", methods=["GET", "POST"])
@security.admin_gerekli
def change_password():
    if request.method == "POST":
        security.csrf_dogrula()
        mevcut = request.form.get("mevcut", "")
        yeni = request.form.get("yeni", "")
        tekrar = request.form.get("tekrar", "")

        if not security.sifre_dogru(mevcut):
            flash("Mevcut şifre yanlış.", "hata")
        elif len(yeni) < 8:
            flash("Yeni şifre en az 8 karakter olmalı.", "hata")
        elif yeni != tekrar:
            flash("Yeni şifreler birbirini tutmuyor.", "hata")
        else:
            security.sifre_degistir(yeni)
            flash("Şifre değiştirildi. Bir sonraki girişte yenisini kullan.", "ok")
            return redirect(url_for("admin.change_password"))

    return render_template(
        "admin/change_password.html",
        csrf=security.csrf_token(),
        oturum_acik=True,
        aktif="sifre",
    )
