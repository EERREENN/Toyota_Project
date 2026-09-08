# -*- coding: utf-8 -*-
"""HABER KATEGORILERI  --  tek dogruluk kaynagi.

Kategori serbest metin DEGIL, asagidaki sabit katalogdur. Panelde
editor bu listeden secer, sitede ziyaretci bu listeye gore filtreler.

VERITABANINDA NE DURUYOR
------------------------
Ayri bir `category_key` sutunu YOK: kategori, News modelinin var olan
`category_tr` / `category_en` sutunlarinda durmaya devam ediyor
(bkz. app/models.py). Sebebi sema: projede migration araci yok,
app/factory.py yalnizca db.create_all() cagiriyor ve o da var olan
bir tabloya yeni sutun EKLEMEZ -- yeni sutun, elde duran
instance/news.db dosyasini kullanilamaz hale getirirdi.

Bu yuzden anahtar yalnizca KOD tarafinda yasiyor:

    kaydederken   anahtar -> (tr, en)   ikilisi sutunlara yazilir
    okurken       category_tr -> anahtar   ters cevirimle bulunur
                  (bkz. anahtar_bul)

`anahtar` adres parcasinda gorunur (/news?kategori=uretim), o yuzden
ascii ve kucuk harf: Turkce karakter adreste kacislanip okunmaz hale
gelirdi.

YENI KATEGORI EKLEMEK
---------------------
Asagidaki KATALOG demetine bir satir eklemek yeterlidir; panelin
secim kutusu da sitenin filtre cubugu da bu listeden uretiliyor.
Kategori adi baska HICBIR dosyada sabit yazili degil.

Bir kategoriyi KALDIRMAK, o kategoriyle kaydedilmis eski haberleri
silmez: haberin `category_tr` degeri yerinde kalir, yalnizca filtre
cubugunda ve panelin secim kutusunda gorunmez olur (panel bu durumda
uyari basar, bkz. templates/admin/news_form.html).
"""

from __future__ import annotations

from dataclasses import dataclass

VARSAYILAN_DIL = "tr"


@dataclass(frozen=True)
class Kategori:
    """Tek kategori: adres parcasi + iki dildeki etiketi."""

    anahtar: str      # ascii slug -- /news?kategori=<anahtar>
    tr: str           # News.category_tr'ye yazilan deger
    en: str           # News.category_en'e yazilan deger


# Sira onemli: filtre cubugu ve panelin secim kutusu bu siradadir.
KATALOG: tuple[Kategori, ...] = (
    Kategori("uretim", "Üretim", "Production"),
    Kategori("kalite", "Kalite", "Quality"),
    Kategori("cevre", "Çevre", "Environment"),
    Kategori("kurumsal", "Kurumsal", "Corporate"),
)


def hepsi() -> tuple[Kategori, ...]:
    """Katalogun tamami, tanimlandigi sirayla."""
    return KATALOG


def bul(anahtar: str | None) -> Kategori | None:
    """Anahtara gore kategori; bilinmeyen anahtar icin None.

    Deger adres cubugundan da gelebildigi icin None ve bosluk
    hos gorulur -- cagiran taraf hata degil "filtre yok" anlar.
    """
    aranan = (anahtar or "").strip()
    if not aranan:
        return None
    for oge in KATALOG:
        if oge.anahtar == aranan:
            return oge
    return None


def anahtar_bul(tr_metin: str | None) -> str | None:
    """Turkce etiketten anahtara ters cevirim; yoksa None.

    Veritabaninda anahtar degil TR etiket duruyor; panelin secim
    kutusunu doldurmak ve filtre baglantisi uretmek icin bu ters
    yon gerekiyor.

    Esleme TAM: elle girilmis "üretim" gibi eski bir deger katalogda
    SAYILMAZ. Boylesi bir kayit panelde uyari alir; sessizce yanlis
    kategoriye baglanmaktansa listede yokmus gibi davranmak dogru --
    site tarafindaki filtre sorgusu da ayni tam eslemeyi kullaniyor,
    ikisi ayni sonucu vermeli.
    """
    aranan = (tr_metin or "").strip()
    if not aranan:
        return None
    for oge in KATALOG:
        if oge.tr == aranan:
            return oge.anahtar
    return None


def etiket(anahtar: str | None, locale: str = VARSAYILAN_DIL) -> str:
    """Kategorinin istenen dildeki adi; bilinmeyen anahtar icin "".

    Dusme mantigi app/haberler.py -> _metin() ile ayni: Ingilizcesi
    bossa Turkcesi gorunur, eksik ceviri sayfayi bozmaz.
    """
    oge = bul(anahtar)
    if oge is None:
        return ""
    if locale == "en":
        return (oge.en or "").strip() or oge.tr
    return oge.tr
