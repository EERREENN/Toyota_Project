# -*- coding: utf-8 -*-
"""HABERLERI OKUYAN TEK MODUL.

Rotalar ve sablonlar veritabanini DOGRUDAN gormez; her sey buradan
gecer. Disari verdigi sey model nesnesi degil, sade sozluklerdir --
icindeki metinler ISTENEN DILDE cozulmus haldedir, sablonun ceviri
yapmasi gerekmez.

Sozlugun anahtarlari sablonlarin bekledigi adlardir:

    id · slug · date · image · gallery · category · title · summary
    · content

`image` KAPAK gorselidir, `gallery` ise ayni haberin KAPAK DISINDAKI
gorselleri (bkz. app/models.py -> NewsImage). Ikisi ayrilmis durumda
cunku kart yalnizca kapagi basiyor, detay sayfasi ikisini iki ayri
yerde gosteriyor: kapak basligin altinda buyuk, digerleri metnin
altinda serit halinde.

`content` bir PARAGRAF LISTESIDIR: veritabanindaki duz metin bos
satirlardan bolunur. Paragraf icindeki tek satir sonlari korunur ve
tarayicida `white-space: pre-line` ile satir sonu olarak gorunur --
metin sablona HTML olarak degil duz metin olarak gider, yani icerikte
etiket calismaz.

Yalnizca YAYINDAKI haberler doner (`is_published = True`); taslaklar
ne listede ne de kendi adresinde gorunur.

KATEGORI FILTRESI
-----------------
Kategoriler sabit bir katalogdan geliyor (app/kategoriler.py). Adres
cubugundaki `?kategori=<anahtar>` burada TR etikete cevrilip sorguya
kosul olarak ekleniyor; veritabaninda anahtar degil o etiket duruyor.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import and_, select

from . import kategoriler
from .extensions import db
from .models import News

VARSAYILAN_DIL = "tr"

# Sayfa basina haber. Izgara iki sutunlu oldugu icin CIFT sayi:
# son satir yarim kalmasin.
SAYFA_BOYUTU = 6


# ------------------------------------------------------------
#  Cozme
# ------------------------------------------------------------
def _metin(tr: str, en: str, locale: str) -> str:
    """Istenen dildeki metin; o dil bossa Turkcesine duser."""
    if locale == "en":
        return (en or "").strip() or (tr or "")
    return tr or ""


def _paragraflar(metin: str) -> list[str]:
    """Duz metni paragraflara boler: BOS SATIR = yeni paragraf."""
    if not metin:
        return []
    parcalar = (metin or "").replace("\r\n", "\n").split("\n\n")
    return [p.strip("\n").strip() for p in parcalar if p.strip()]


def _coz(kayit: News, locale: str) -> dict:
    """Bir haber kaydini sablonun bekledigi sade sozluge cevirir."""
    return {
        "id": kayit.id,
        "slug": kayit.slug,
        # Sablon hem datetime ozniteligine hem de tarih() suzgecine
        # veriyor; ikisi de ISO metin bekliyor.
        "date": kayit.date.isoformat() if kayit.date else "",
        "image": kayit.image or "",
        # Kapak galeriden ELENIYOR: yoksa detay sayfasinda ayni
        # fotograf hem basta buyuk hem seritte ikinci kez cikardi.
        "gallery": [
            {
                "path": gorsel.path,
                "alt": _metin(gorsel.alt_tr, gorsel.alt_en, locale),
            }
            for gorsel in kayit.images
            if gorsel.path and gorsel.path != (kayit.image or "")
        ],
        "category": _metin(kayit.category_tr, kayit.category_en, locale),
        "title": _metin(kayit.title_tr, kayit.title_en, locale),
        "summary": _metin(kayit.summary_tr, kayit.summary_en, locale),
        "content": _paragraflar(_metin(kayit.content_tr, kayit.content_en, locale)),
    }


# ------------------------------------------------------------
#  Sayfalama
# ------------------------------------------------------------
@dataclass
class Sayfalama:
    """Bir sayfalik haber + sayfa cubugunun ihtiyaci olan sayilar."""

    haberler: list[dict] = field(default_factory=list)
    sayfa: int = 1
    toplam_sayfa: int = 1
    toplam: int = 0
    # Yururlukteki kategori filtresinin ANAHTARI (filtre yoksa None).
    # Dogrulanmis hali: bilinmeyen bir anahtar buraya None olarak
    # duser. Sablon sayfa baglantilarini bununla kuruyor, yoksa
    # 2. sayfaya gecen ziyaretci filtreyi kaybederdi.
    kategori: str | None = None

    @property
    def gerekli(self) -> bool:
        """Tek sayfa varsa sayfa cubugu hic basilmaz."""
        return self.toplam_sayfa > 1

    @property
    def onceki(self) -> int | None:
        return self.sayfa - 1 if self.sayfa > 1 else None

    @property
    def sonraki(self) -> int | None:
        return self.sayfa + 1 if self.sayfa < self.toplam_sayfa else None

    @property
    def numaralar(self) -> list[int]:
        return list(range(1, self.toplam_sayfa + 1))


def _sayfa_no(deger) -> int:
    """?page=... degerini guvenli bir sayfa numarasina cevirir.

    Sayi olmayan ya da 1'den kucuk her sey ilk sayfadir; adres
    kurcalandiginda hata degil ilk sayfa gorunsun.
    """
    try:
        no = int(deger)
    except (TypeError, ValueError):
        return 1
    return no if no >= 1 else 1


def _kosullar(kategori: kategoriler.Kategori | None) -> list:
    """Listenin ve sayimin ORTAK where kosullari.

    Ikisi ayni yerden gelmezse sayfa sayisi filtreyle uyusmaz:
    sayim filtresiz kalirsa sayfa cubugu olmayan sayfalari gosterir
    ve ziyaretci bos listelere tiklar.
    """
    kosul = [News.is_published.is_(True)]
    if kategori is not None:
        # Veritabaninda anahtar degil TR etiket duruyor
        # (bkz. app/kategoriler.py).
        kosul.append(News.category_tr == kategori.tr)
    return kosul


# ------------------------------------------------------------
#  Genel API  --  disaridan kullanilan tek yuzey
# ------------------------------------------------------------
def sayfa_getir(locale: str = VARSAYILAN_DIL, sayfa=1,
                kategori: str | None = None,
                boyut: int = SAYFA_BOYUTU) -> Sayfalama | None:
    """Bir sayfalik haber, yeniden eskiye.

    `kategori` bir katalog ANAHTARIDIR ("uretim" gibi). Bos ya da
    katalogda olmayan bir deger geldiginde filtre UYGULANMAZ ve tam
    liste doner -- _sayfa_no() ile ayni tutum: adres kurcalandiginda
    hata degil makul olan gorunsun.

    Istenen sayfa yoksa None doner (rota 404 verir). Hic haber
    yoksa bos ama gecerli bir 1. sayfa doner -- liste sablonu bos
    durum mesajini gosterir.
    """
    no = _sayfa_no(sayfa)
    secili = kategoriler.bul(kategori)
    kosul = _kosullar(secili)

    toplam = db.session.scalar(
        select(db.func.count(News.id)).where(*kosul)
    ) or 0
    toplam_sayfa = max(1, -(-toplam // boyut))     # yukari yuvarlama
    if no > toplam_sayfa:
        return None

    kayitlar = db.session.scalars(
        select(News)
        .where(*kosul)
        # Ayni gune dusen haberlerde sira sabit kalsin diye ikinci
        # olcut: sonra eklenen ustte.
        .order_by(News.date.desc(), News.id.desc())
        .offset((no - 1) * boyut)
        .limit(boyut)
    ).all()

    return Sayfalama(
        haberler=[_coz(k, locale) for k in kayitlar],
        sayfa=no,
        toplam_sayfa=toplam_sayfa,
        toplam=toplam,
        kategori=secili.anahtar if secili else None,
    )


def kategori_sayilari(locale: str = VARSAYILAN_DIL) -> list[dict]:
    """Filtre cubugunun gosterecegi kategoriler, katalog sirasiyla.

    Her oge: anahtar · etiket (istenen dilde) · sayi.

    YAYINDAKI haberi olmayan kategori listeye HIC girmez: tiklaninca
    bos liste veren bir dugme kotu bir deneyim. Sayim, filtrenin
    kullandigi TAM eslemenin aynisini kullanir (`category_tr` degeri
    katalogdaki TR etikete birebir esit olmali); boylece cubukta
    gorunen sayi ile filtrenin dondurdugu haber sayisi ayrismaz.
    """
    satirlar = db.session.execute(
        select(News.category_tr, db.func.count(News.id))
        .where(News.is_published.is_(True))
        .group_by(News.category_tr)
    ).all()
    sayim = {(ad or ""): adet for ad, adet in satirlar}

    liste = []
    for oge in kategoriler.hepsi():
        adet = sayim.get(oge.tr, 0)
        if adet:
            liste.append({
                "anahtar": oge.anahtar,
                "etiket": kategoriler.etiket(oge.anahtar, locale),
                "sayi": adet,
            })
    return liste


def bul(slug: str, locale: str = VARSAYILAN_DIL) -> dict | None:
    """Adres parcasina gore tek haber.

    Taslak haber YOK sayilir: adresi dogrudan yazan da 404 alir.
    """
    kayit = db.session.scalars(
        select(News).where(News.slug == slug, News.is_published.is_(True))
    ).first()
    return _coz(kayit, locale) if kayit else None


def slug_var_mi(slug: str, haric_id: int | None = None) -> bool:
    """Bu adres parcasi kullanimda mi? (taslaklar dahil)

    app/metin.py -> benzersiz_slug() bunu kullanir.
    Duzenlemede kendi kaydini cakisma saymamak icin `haric_id` verilir.
    """
    kosul = News.slug == slug
    if haric_id is not None:
        kosul = and_(kosul, News.id != haric_id)
    return (db.session.scalar(select(db.func.count(News.id)).where(kosul)) or 0) > 0
