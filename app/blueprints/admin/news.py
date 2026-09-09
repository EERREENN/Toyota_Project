# -*- coding: utf-8 -*-
"""Haber ekleme, duzenleme, silme.

GORSEL SAYISI
-------------
Bir haberde en fazla Config.MAX_NEWS_IMAGES gorsel olabilir ve bu
sinir UC katmanda birden zorlanir:

  1. tarayici  -- sayac + pasif "Ekle" dugmesi
                  (templates/admin/news_form.html)
  2. SUNUCU    -- _kaydet() asagida, yukleme.dogrula() uzerinden
  3. istek     -- Config.MAX_CONTENT_LENGTH, govde tavani

Ikinci katman belirleyici olandir: birincisi atlanabilir (curl,
devtools). Ve kontrol "kac dosya yuklendi" degil, MEVCUT + YENI
TOPLAMI uzerinden yapilir -- 4 gorselli habere 2 gorsel eklenmek
istendiginde ikisi de tek basina limitin altindadir, toplam degil.
"""

from __future__ import annotations

from datetime import date, datetime

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select

from ... import haberler, kategoriler, security, yukleme
from ...extensions import db
from ...metin import benzersiz_slug, slugify, tarih_metni
from ...models import News, NewsImage
from . import bp


def _form(kayit: News | None) -> dict:
    if kayit is None:
        return {
            "title_tr": "",
            "title_en": "",
            "slug": "",
            # Kategori artik serbest metin degil, katalog anahtari
            # (bkz. app/kategoriler.py). Bos = kategorisiz haber.
            "kategori": "",
            "date": date.today().isoformat(),
            "summary_tr": "",
            "summary_en": "",
            "content_tr": "",
            "content_en": "",
            "is_published": "1",
            # Kayitli galeri (yeni haberde bos). Sablon sayaci ve
            # kapak secimini bunun uzerinden kuruyor.
            "gorseller": [],
            "kapak_id": None,
        }
    return {
        "title_tr": kayit.title_tr,
        "title_en": kayit.title_en or "",
        "slug": kayit.slug,
        # Veritabaninda anahtar degil TR etiket duruyor; secim kutusunu
        # doldurmak icin ters cevirim. Katalogda olmayan eski bir deger
        # "" doner -- form o zaman uyari basar, sessizce silmez
        # (bkz. templates/admin/news_form.html).
        "kategori": kategoriler.anahtar_bul(kayit.category_tr) or "",
        "date": kayit.date.isoformat() if kayit.date else date.today().isoformat(),
        "summary_tr": kayit.summary_tr or "",
        "summary_en": kayit.summary_en or "",
        "content_tr": kayit.content_tr or "",
        "content_en": kayit.content_en or "",
        "is_published": "1" if kayit.is_published else "0",
        "gorseller": [
            {"id": g.id, "path": g.path, "alt_tr": g.alt_tr, "alt_en": g.alt_en}
            for g in kayit.images
        ],
        # Kapak, galerideki gorsellerden birinin YOLUNA esit
        # (bkz. app/models.py -> News.image). Radyo dugmesini
        # isaretlemek icin o gorselin id'sine cevriliyor.
        "kapak_id": next(
            (g.id for g in kayit.images if g.path == kayit.image), None
        ),
    }


def _posta() -> dict:
    form = request.form
    return {
        "title_tr": (form.get("title_tr") or "").strip(),
        "title_en": (form.get("title_en") or "").strip(),
        "slug": (form.get("slug") or "").strip(),
        "kategori": (form.get("kategori") or "").strip(),
        "date": (form.get("date") or "").strip(),
        "summary_tr": (form.get("summary_tr") or "").strip(),
        "summary_en": (form.get("summary_en") or "").strip(),
        "content_tr": form.get("content_tr") or "",
        "content_en": form.get("content_en") or "",
        "is_published": "1" if form.get("is_published") == "1" else "0",
        # Silinmesi istenen KAYITLI gorsellerin id'leri. Sayi
        # olmayan degerler sessizce elenir: adres/istek kurcalansa
        # bile eslesmeyen id kimseyi silmez.
        "silinecek": {int(d) for d in form.getlist("sil_gorsel") if d.isdigit()},
        # Kapak olarak isaretlenen kayitli gorselin id'si.
        "kapak_id": int(form.get("kapak")) if (form.get("kapak") or "").isdigit()
                    else None,
    }


def _tarih_oku(deger: str) -> date | None:
    try:
        return datetime.strptime(deger, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _kapak_yaz(kayit: News, secilen_id: int | None) -> None:
    """News.image sutununa kapak gorselinin yolunu yazar.

    Kapak, galerideki gorsellerden BIRIDIR; ayri bir dosya degil
    (bkz. app/models.py -> News.image). Secim gecersizse -- hic
    isaretlenmemisse, ya da isaretli gorsel bu kaydetmede
    silindiyse -- galerinin ilkine duser. Galeri bossa kapak da
    bosalir ve kart yer tutucuyu gosterir.

    Yeni yuklenen gorsellerin id'si bu asamada henuz yok (flush
    olmadi), o yuzden secim yalnizca KAYITLI gorseller arasindan
    yapilabiliyor: editor once yukluyor, sonra kapagi seciyor.
    """
    galeri = sorted(kayit.images, key=lambda g: (g.position, g.id or 0))
    if not galeri:
        kayit.image = ""
        return
    secilen = next((g for g in galeri if g.id == secilen_id), None)
    kayit.image = (secilen or galeri[0]).path


def _kaydet(kayit: News | None, deger: dict) -> str | None:
    """Basariliysa None, hata varsa mesaj doner. kayit None ise yeni satır."""
    if not deger["title_tr"]:
        return "Başlık zorunludur."

    gun = _tarih_oku(deger["date"])
    if gun is None:
        return "Tarih geçersiz. Yıl-ay-gün biçiminde yaz (örnek: 2026-09-07)."

    # Kategori istege bagli: bos deger gecerlidir (kategorisiz haber).
    # Dolu ama katalogda yoksa kaydetme -- secim kutusu disindan
    # gonderilmis bir degerdir.
    kategori = kategoriler.bul(deger["kategori"])
    if deger["kategori"] and kategori is None:
        return "Geçersiz kategori."

    haric = kayit.id if kayit is not None else None
    if deger["slug"]:
        slug = slugify(deger["slug"])
        if haberler.slug_var_mi(slug, haric):
            return "Bu adres parçası başka bir haberde kullanılıyor."
    else:
        slug = benzersiz_slug(
            deger["title_tr"],
            lambda s: haberler.slug_var_mi(s, haric),
        )

    # --- gorseller ---
    # Once SAYI, sonra dosya. Kalan = kayitli olup silinmeyecekler;
    # limit bunun uzerine yeni yuklenenler eklenerek olculuyor.
    mevcut = list(kayit.images) if kayit is not None else []
    kalan = [g for g in mevcut if g.id not in deger["silinecek"]]

    try:
        # Diske YAZMADAN once dogrular; limit asilirsa uploads/
        # klasorune tek dosya bile dusmez.
        yeni_yollar = yukleme.kaydet_coklu(
            request.files.getlist("gorseller"), slug, len(kalan)
        )
    except yukleme.YuklemeHatasi as hata:
        return str(hata)

    if kayit is None:
        kayit = News()
        db.session.add(kayit)

    # Silinecekler: once diskten dosya, sonra listeden satir.
    # Satirin kendisini delete-orphan siliyor (bkz. app/models.py).
    for gorsel in mevcut:
        if gorsel.id in deger["silinecek"]:
            yukleme.sil_dosya(gorsel.path)
            kayit.images.remove(gorsel)

    sonraki = max((g.position for g in kalan), default=-1) + 1
    for sira, yol in enumerate(yeni_yollar):
        kayit.images.append(NewsImage(path=yol, position=sonraki + sira))

    kayit.slug = slug
    kayit.date = gun
    kayit.is_published = deger["is_published"] == "1"
    kayit.title_tr = deger["title_tr"]
    kayit.title_en = deger["title_en"]
    # Katalogdaki karsiliklar sutunlara yazilir; secim bossa ikisi de
    # bosalir. Sema degismedigi icin site tarafi bu iki sutunu
    # okumaya devam ediyor.
    kayit.category_tr = kategori.tr if kategori else ""
    kayit.category_en = kategori.en if kategori else ""
    kayit.summary_tr = deger["summary_tr"]
    kayit.summary_en = deger["summary_en"]
    kayit.content_tr = deger["content_tr"]
    kayit.content_en = deger["content_en"]
    _kapak_yaz(kayit, deger["kapak_id"])
    db.session.commit()
    return None


@bp.route("/news")
@security.admin_gerekli
def news_list():
    kayitlar = list(db.session.scalars(
        select(News).order_by(News.date.desc(), News.id.desc())
    ))
    return render_template(
        "admin/news_list.html",
        haberler=kayitlar,
        tarih=lambda iso: tarih_metni(iso, "tr"),
        aktif="haberler",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/news/new", methods=["GET", "POST"])
@security.admin_gerekli
def news_new():
    deger = _form(None)
    if request.method == "POST":
        security.csrf_dogrula()
        deger = _posta()
        hata = _kaydet(None, deger)
        if hata:
            flash(hata, "hata")
        else:
            flash("Haber eklendi.", "ok")
            return redirect(url_for("admin.news_list"))

    return render_template(
        "admin/news_form.html",
        deger=deger,
        kayit=None,
        kategoriler=kategoriler.hepsi(),
        # Sayac ve pasif "Ekle" dugmesi icin. Sablon limiti kendi
        # bilmiyor, tek kaynaktan aliyor (app/yukleme.py).
        azami_gorsel=yukleme.azami_gorsel(),
        aktif="haberler",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/news/edit/<int:haber_id>", methods=["GET", "POST"])
@security.admin_gerekli
def news_edit(haber_id: int):
    kayit = db.session.get(News, haber_id)
    if kayit is None:
        flash("Haber bulunamadı.", "hata")
        return redirect(url_for("admin.news_list"))

    deger = _form(kayit)
    if request.method == "POST":
        security.csrf_dogrula()
        deger = _posta()
        hata = _kaydet(kayit, deger)
        if hata:
            flash(hata, "hata")
        else:
            flash("Haber güncellendi.", "ok")
            return redirect(url_for("admin.news_list"))

    return render_template(
        "admin/news_form.html",
        deger=deger,
        kayit=kayit,
        kategoriler=kategoriler.hepsi(),
        # Sayac ve pasif "Ekle" dugmesi icin. Sablon limiti kendi
        # bilmiyor, tek kaynaktan aliyor (app/yukleme.py).
        azami_gorsel=yukleme.azami_gorsel(),
        aktif="haberler",
        oturum_acik=True,
        csrf=security.csrf_token(),
    )


@bp.route("/news/delete/<int:haber_id>", methods=["POST"])
@security.admin_gerekli
def news_delete(haber_id: int):
    security.csrf_dogrula()
    kayit = db.session.get(News, haber_id)
    if kayit is None:
        flash("Haber bulunamadı.", "hata")
        return redirect(url_for("admin.news_list"))

    ad = kayit.title_tr
    # Satirlari CASCADE siliyor; dosyalari kimse silmez, burada
    # tek tek kaldiriliyor. Kapak galerinin bir uyesi oldugu icin
    # ayrica silinmesine gerek yok.
    for gorsel in list(kayit.images):
        yukleme.sil_dosya(gorsel.path)
    db.session.delete(kayit)
    db.session.commit()
    flash(f"“{ad}” silindi.", "ok")
    return redirect(url_for("admin.news_list"))
