# -*- coding: utf-8 -*-
"""HABERLERI OKUYAN TEK MODUL.

Rotalar ve sablonlar veritabanini DOGRUDAN gormez; her sey buradan
gecer. Disari verdigi sey model nesnesi degil, sade sozluklerdir --
icindeki metinler ISTENEN DILDE cozulmus haldedir, sablonun ceviri
yapmasi gerekmez.

Sozlugun anahtarlari sablonlarin bekledigi adlardir:

    id · slug · date · image · category · title · summary · content

`content` bir PARAGRAF LISTESIDIR: veritabanindaki duz metin bos
satirlardan bolunur. Paragraf icindeki tek satir sonlari korunur ve
tarayicida `white-space: pre-line` ile satir sonu olarak gorunur --
metin sablona HTML olarak degil duz metin olarak gider, yani icerikte
etiket calismaz.

Yalnizca YAYINDAKI haberler doner (`is_published = True`); taslaklar
ne listede ne de kendi adresinde gorunur.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import and_, select

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


# ------------------------------------------------------------
#  Genel API  --  disaridan kullanilan tek yuzey
# ------------------------------------------------------------
def sayfa_getir(locale: str = VARSAYILAN_DIL, sayfa=1,
                boyut: int = SAYFA_BOYUTU) -> Sayfalama | None:
    """Bir sayfalik haber, yeniden eskiye.

    Istenen sayfa yoksa None doner (rota 404 verir). Hic haber
    yoksa bos ama gecerli bir 1. sayfa doner -- liste sablonu bos
    durum mesajini gosterir.
    """
    no = _sayfa_no(sayfa)

    toplam = db.session.scalar(
        select(db.func.count(News.id)).where(News.is_published.is_(True))
    ) or 0
    toplam_sayfa = max(1, -(-toplam // boyut))     # yukari yuvarlama
    if no > toplam_sayfa:
        return None

    kayitlar = db.session.scalars(
        select(News)
        .where(News.is_published.is_(True))
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
    )


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
