# -*- coding: utf-8 -*-
"""Veritabani modelleri.

Haberler `news` tablosunda. Dort tanitim sayfasinin icerigi
veritabaninda DEGIL, sayfa sablonlarinda duruyor -- oralara
dokunulmuyor.

Panel icin iki kucuk tablo daha var: sifre hash'i (`site_setting`)
ve giris kilidi (`login_attempt`). Bunlar haber modelini
degistirmez.

IKI DILLILIK
------------
Cevrilebilir alanlar `_tr` / `_en` olarak yan yana iki sutunda:

    title_tr / title_en, summary_tr / summary_en,
    content_tr / content_en, category_tr / category_en

Neden ayri bir `translation` tablosu degil: site iki dilli ve bu iki
dil sabit. Ayri tablo, her haber icin 4 ek satir ve her listede bir
JOIN demek olurdu; kazanci ise ancak dil sayisi degisken oldugunda
ortaya cikardi. Yan yana sutunlar ayrica ileride yazilacak yonetim
formunu tek ekranda tutuyor: editor Turkce ve Ingilizce alani ayni
sayfada doldurur.

Ingilizcesi bos birakilan alan sitede Turkcesine duser
(bkz. app/haberler.py -> _metin); eksik ceviri sayfayi bozmaz.

GORSELLER
---------
Bir haberde birden fazla gorsel olabilir; bunlar ayri bir
`news_image` tablosunda durur (asagida). `News.image` sutunu
KALDIRILMADI: artik KAPAK gorselini tasiyor ve galerideki
gorsellerden birine esittir. Sebebi iki tarafli:

  * kart ve panel listesi tek bir gorsel istiyor (galeriyi
    dolasmalari gereksiz), o yuzden kapak dogrudan `news`
    satirinda duruyor;
  * elde duran instance/news.db bozulmasin diye `news` tablosuna
    YENI SUTUN eklenmedi -- projede migration araci yok,
    app/factory.py yalnizca db.create_all() cagiriyor ve o da var
    olan bir tabloya sutun EKLEMEZ. Eksik TABLO ise olusturur;
    `news_image` bu yuzden ayri bir tablo.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (Boolean, Date, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db


def utcnow() -> datetime:
    """Her yerde UTC. Yerel saat / yaz saati karmasasi yasanmasin."""
    return datetime.now(timezone.utc)


class News(db.Model):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Adres parcasi: /news/<slug>. Basliktan uretilir
    # (app/metin.py -> slugify) ama sonradan elle degistirilebilir.
    # BENZERSIZ: iki haber ayni adresi paylasamaz.
    slug: Mapped[str] = mapped_column(String(200), unique=True,
                                      nullable=False, index=True)

    # Yayin tarihi. Siralama ve ekranda gosterim buna gore
    # (created_at'e gore DEGIL: haber geriye donuk tarihlenebilir).
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # KAPAK gorseli: static/ klasorune gore yol
    # ("uploads/news/toyota-corolla-2026-1.jpg").
    #
    # Galerideki gorsellerden BIRINE esittir; panelde hangisinin
    # kapak olacagi secilir (bkz. app/blueprints/admin/news.py ->
    # _kapak_yaz). Bos birakilabilir; kart ve detay sayfasi
    # gorselsiz de calisir.
    image: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # False -> taslak. Sitede hic gorunmez: ne listede ne de kendi
    # adresinde (adresi dogrudan yazan 404 alir).
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                               default=True, index=True)

    # --- cevrilebilir alanlar ---
    title_tr: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    category_tr: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    category_en: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    summary_tr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary_en: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Duz metin. BOS SATIR yeni paragraf demektir; paragraf icindeki
    # tek satir sonlari oldugu gibi korunur (bkz. app/haberler.py ->
    # _paragraflar ve news-detail.css -> white-space: pre-line).
    # HTML DEGIL: icerik sablonda kacislanarak basiliyor.
    content_tr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_en: Mapped[str] = mapped_column(Text, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    # Galeri. `sira` sutununa gore siralanir; sira esitse id
    # bozar (ekleme sirasi). delete-orphan: listeden cikarilan
    # NewsImage satiri veritabanindan da silinir -- DOSYAYI silmek
    # ayri is, onu app/yukleme.py -> sil_dosya yapiyor.
    #
    # lazy="selectin": haber listesi 6 haber basar ve her biri
    # kapagini kendi satirindan okur, ama detay sayfasi galeriyi
    # istiyor. selectin, N+1 sorgu yerine tek ek sorgu demek.
    images: Mapped[list["NewsImage"]] = relationship(
        back_populates="news",
        cascade="all, delete-orphan",
        order_by="NewsImage.position, NewsImage.id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<News {self.slug}>"


# ============================================================
#  Haber galerisi  --  haber basina en fazla MAX_NEWS_IMAGES gorsel
# ============================================================
class NewsImage(db.Model):
    """Bir haberin tek gorseli.

    SAYI SINIRI BURADA DEGIL: kac gorsel eklenebilecegi
    Config.MAX_NEWS_IMAGES'te tanimli ve app/yukleme.py ->
    azami_gorsel() uzerinden okunuyor. Veritabani seviyesinde
    zorlanmiyor cunku SQLite'ta satir sayisi kisiti yazmak
    trigger gerektirirdi; kontrol tek noktada, kaydetme yolunda.
    """

    __tablename__ = "news_image"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # ondelete CASCADE: haber silinince gorsel satirlari da gider.
    # SQLite'ta yabanci anahtarlar varsayilan olarak KAPALI; onlari
    # acan PRAGMA app/extensions.py icinde.
    news_id: Mapped[int] = mapped_column(
        ForeignKey("news.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # static/ klasorune gore yol ("uploads/news/...jpg") --
    # News.image ile AYNI bicim, ikisi karsilastirilabilsin diye
    # (kapak esleme bunun uzerinden yapiliyor).
    path: Mapped[str] = mapped_column(String(255), nullable=False)

    # Galeri sirasi. Panelde gorseller bu sirayla listelenir.
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Alternatif metin. Bos birakilabilir: gorsel suslemeyse bos alt
    # dogru olandir, ekran okuyucu atlar.
    alt_tr: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    alt_en: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    news: Mapped["News"] = relationship(back_populates="images")

    def __repr__(self) -> str:
        return f"<NewsImage {self.path}>"


# ============================================================
#  Panel ayarlari  --  su an yalnizca sifre hash'i
# ============================================================
class SiteSetting(db.Model):
    __tablename__ = "site_setting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    value: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<SiteSetting {self.key}>"


# ============================================================
#  Giris denemesi  --  IP basina gecici kilit
# ============================================================
class LoginAttempt(db.Model):
    __tablename__ = "login_attempt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_fail_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_fail_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def is_locked(self) -> bool:
        if not self.locked_until:
            return False
        bitis = self.locked_until
        if bitis.tzinfo is None:
            bitis = bitis.replace(tzinfo=timezone.utc)
        return bitis > utcnow()

    def __repr__(self) -> str:
        return f"<LoginAttempt {self.ip} x{self.fail_count}>"
