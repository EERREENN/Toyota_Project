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
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

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

    # static/ klasorune gore gorsel yolu ("img/tmmt_img/corolla.jpg").
    # Bos birakilabilir; kart ve detay sayfasi gorselsiz de calisir.
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

    def __repr__(self) -> str:
        return f"<News {self.slug}>"


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
