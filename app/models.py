# -*- coding: utf-8 -*-
"""Veritabani modelleri -- 7 tablo.

Tasarimin iki temel karari:

1) CEVRILEBILIR METIN GERCEK SUTUNDA, YAPISAL AYAR JSON'DA.
   Turkce metin varligin kendi sutununda durur (kaynak dogru). Ingilizce
   karsiligi ayri `translation` tablosunda durur; boylece "editorun elle
   duzelttigi EN alani otomatik ceviri tarafindan ezilmesin" kurali tum
   tipler icin tek yerde cozulur.

2) TEKRARLAYAN OGELER `block_item` TABLOSUNDA, KENDINE REFERANSLI.
   Kart maddeleri ve marka gruplari iki seviye derinlikte; `parent_id`
   ile cozuluyor, ayri tablo gerekmiyor.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db

# JSON sutunlarinda yerinde degisikligin (settings["x"] = 1) da
# algilanmasi icin. Bu olmadan panelde yapilan kismi degisiklikler
# kaydedilmez -- sessiz ve bulmasi zor bir hata olurdu.
JSONDict = MutableDict.as_mutable(JSON)


def utcnow() -> datetime:
    """Her yerde UTC. Yerel saat / yaz saati karmasasi yasanmasin."""
    return datetime.now(timezone.utc)


def text_hash(deger) -> str:
    """Bir kaynak metnin parmak izi.

    Ceviriyle birlikte saklanir; kaynak Turkce metin sonradan degisirse
    bu esitlik bozulur ve panel "ceviri bayatladi" uyarisi gosterir.
    """
    return hashlib.sha256((deger or "").encode("utf-8")).hexdigest()


# ============================================================
#  Site ayarlari
#  (marka adi, menu metinleri, panel sifresinin hash'i...)
# ============================================================
class SiteSetting(db.Model):
    __tablename__ = "site_setting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    value: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    # Hangi anahtarin cevrilecegi ve panelde hangi Turkce etiketle
    # gorunecegi kodda (app/block_types.py -> SETTING_FIELDS) tanimli.
    # DB'de tutulmuyor: editorun degistirmesi gereken bir sey degil.

    def __repr__(self) -> str:
        return f"<SiteSetting {self.key}>"


# ============================================================
#  Gorsel kutuphanesi
# ============================================================
class MediaAsset(db.Model):
    __tablename__ = "media_asset"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # static/ klasorune gore yol:
    #   "img/tmmt-bg.jpg"             (projeyle gelen)
    #   "uploads/2026/09/a1b2c3.jpg"  (panelden yuklenen)
    path: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    mime: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    alt: Mapped[str | None] = mapped_column(String(255))
    # True = projeyle gelen dosya; panelden silinemez.
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    TRANSLATABLE = ("alt",)

    def __repr__(self) -> str:
        return f"<MediaAsset {self.path}>"


# ============================================================
#  Sayfa  --  4 satir. Editor YENI SAYFA ACAMAZ, SILEMEZ.
# ============================================================
class Page(db.Model):
    __tablename__ = "page"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    # is_home olan sayfa hem "/" hem kendi url'inden servis edilir.
    # (legacy_app.py'deki @app.route("/") + @app.route("/tmmt") davranisi)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    nav_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # <body class="page-{theme}">  ->  tmmt | global | uretim | cevre
    theme: Mapped[str] = mapped_column(String(32), nullable=False, default="tmmt")
    # Sayfa geneli .reveal animasyonu (global ve uretim'de acik)
    reveal_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # --- cevrilebilir metinler (TR kaynak) ---
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    nav_label: Mapped[str] = mapped_column(String(64), nullable=False)

    background_image_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_asset.id", ondelete="SET NULL")
    )
    background_image: Mapped["MediaAsset | None"] = relationship(
        foreign_keys=[background_image_id]
    )

    blocks: Mapped[list["Block"]] = relationship(
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="Block.position",
    )

    TRANSLATABLE = ("title", "nav_label")

    @property
    def visible_blocks(self) -> list["Block"]:
        return [b for b in self.blocks if b.is_visible]

    def __repr__(self) -> str:
        return f"<Page {self.slug}>"


# ============================================================
#  Blok  --  sayfadaki sirali parca
# ============================================================
class Block(db.Model):
    __tablename__ = "block"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_id: Mapped[int] = mapped_column(
        ForeignKey("page.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 25 tipten biri; gecerli degerler app/block_types.py icinde.
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # --- her blokta ortak alanlar ---
    anchor: Mapped[str | None] = mapped_column(String(64))
    heading: Mapped[str | None] = mapped_column(String(255))
    heading_level: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    intro: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(String(500))
    # None -> sayfanin reveal_default degeri kullanilir
    reveal: Mapped[bool | None] = mapped_column(Boolean)

    # Tipe ozel, CEVRILMEYEN yapisal ayarlar. Ornekler:
    #   stat_grid      -> {"variant": "card", "columns": "auto"}
    #   map            -> {"center": [20, 20], "zoom": 2, "tile": {...}}
    #   co2_calculator -> {"rates": {...}, "form": {...}, "results": {...}}
    settings: Mapped[dict] = mapped_column(JSONDict, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    page: Mapped["Page"] = relationship(back_populates="blocks")

    # Blogun TUM ogeleri (alt ogeler dahil). Yasam dongusunun tek sahibi
    # budur: blok silinince hepsi silinir.
    all_items: Mapped[list["BlockItem"]] = relationship(
        back_populates="block",
        cascade="all, delete-orphan",
        order_by="BlockItem.position",
        foreign_keys="BlockItem.block_id",
    )

    TRANSLATABLE = ("heading", "intro", "note")

    @property
    def items(self) -> list["BlockItem"]:
        """Sadece ust seviye ogeler (alt ogeler parent.children altinda)."""
        return [i for i in self.all_items if i.parent_id is None]

    def items_of(self, kind: str) -> list["BlockItem"]:
        return [i for i in self.items if i.kind == kind]

    def first_item(self):
        ust = self.items
        return ust[0] if ust else None

    def __repr__(self) -> str:
        return f"<Block {self.type} #{self.position}>"


# ============================================================
#  Blok ogesi
#  kart / istatistik / durak / harita noktasi / paragraf / etiket...
# ============================================================
class BlockItem(db.Model):
    __tablename__ = "block_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    block_id: Mapped[int] = mapped_column(
        ForeignKey("block.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("block_item.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # NE oldugu:
    #   paragraph | bullet | stat | card | chip_group | chip
    #   stop | marker | legend | link | outro
    kind: Mapped[str] = mapped_column(String(24), nullable=False, default="item")
    # NASIL gorundugu:
    #   award | station | plain | highlight | red | gold | muted | external
    variant: Mapped[str | None] = mapped_column(String(24))
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Sabit HTML id gereken yerler icin (zaman tuneli: id="zt-1992")
    slug: Mapped[str | None] = mapped_column(String(64))

    # --- metin alanlari ---
    eyebrow: Mapped[str | None] = mapped_column(String(64))      # yil / istasyon no
    title: Mapped[str | None] = mapped_column(String(255))
    subtitle: Mapped[str | None] = mapped_column(String(255))    # harita: ulke
    value: Mapped[str | None] = mapped_column(String(64))        # "280.000"
    text: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(500))
    link_label: Mapped[str | None] = mapped_column(String(255))

    image_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_asset.id", ondelete="SET NULL")
    )
    image: Mapped["MediaAsset | None"] = relationship(foreign_keys=[image_id])

    # --- harita noktasi ---
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # --- sayac animasyonu (stat_grid / stat_badge) ---
    count_to: Mapped[float | None] = mapped_column(Float)
    count_from: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    count_prefix: Mapped[str | None] = mapped_column(String(16))
    count_suffix: Mapped[str | None] = mapped_column(String(16))
    count_group: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    count_format: Mapped[str] = mapped_column(String(8), nullable=False, default="group")

    settings: Mapped[dict] = mapped_column(JSONDict, nullable=False, default=dict)

    block: Mapped["Block"] = relationship(
        back_populates="all_items", foreign_keys=[block_id]
    )
    # Alt ogeler. Yasam dongusunun sahibi Block.all_items'tir; buradaki
    # cascade yalnizca "save-update" -- ayni nesneye iki delete-orphan
    # sahibi vermek SQLAlchemy'de hataya yol acar. Ust oge dogrudan
    # silinirse alt ogeleri veritabani temizler
    # (ON DELETE CASCADE + PRAGMA foreign_keys=ON).
    children: Mapped[list["BlockItem"]] = relationship(
        back_populates="parent",
        cascade="save-update, merge",
        order_by="BlockItem.position",
        foreign_keys=[parent_id],
    )
    parent: Mapped["BlockItem | None"] = relationship(
        back_populates="children", remote_side=[id], foreign_keys=[parent_id]
    )

    TRANSLATABLE = ("title", "subtitle", "text", "note", "link_label")

    # `value` sutunu ogenin turune gore ya GORUNEN METIN ya da MAKINE
    # KODU tasir; bu yuzden sabit listede degil, asagidaki kurala bagli:
    #   kind="stat"   -> "300.000.000+"  ekranda gorunur, CEVRILIR
    #   kind="option" -> "benzin"/"hev"  hesaplayicinin anahtari, CEVRILMEZ
    #   kind="label"  -> "₺"             para birimi, CEVRILMEZ
    # Bu ayrimi kaybetmek hesaplayiciyi sessizce bozardi: secenek kodu
    # "gasoline" olarak cevrilirse JS tarafi eslesmeyi bulamaz.
    VALUE_TRANSLATABLE_KINDS = ("stat",)

    @property
    def translatable_fields(self) -> tuple[str, ...]:
        if self.kind in self.VALUE_TRANSLATABLE_KINDS:
            return self.TRANSLATABLE + ("value",)
        return self.TRANSLATABLE

    def children_of(self, kind: str) -> list["BlockItem"]:
        return [c for c in self.children if c.kind == kind]

    def __repr__(self) -> str:
        return f"<BlockItem {self.kind} #{self.position}>"


# ============================================================
#  Ceviri  --  Turkce disindaki diller
# ============================================================
class Translation(db.Model):
    __tablename__ = "translation"
    __table_args__ = (
        UniqueConstraint(
            "entity_type", "entity_id", "field", "locale", name="uq_translation_target"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # page | block | block_item | media | setting
    entity_type: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    field: Mapped[str] = mapped_column(String(32), nullable=False)
    locale: Mapped[str] = mapped_column(String(8), nullable=False)

    value: Mapped[str | None] = mapped_column(Text)
    # True -> editor panelden ELLE yazdi. Otomatik ceviri BUNU EZMEZ.
    is_manual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Bu cevirinin uretildigi Turkce metnin parmak izi.
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    def is_stale(self, source_value) -> bool:
        """Kaynak Turkce metin, bu ceviri uretildikten sonra degisti mi?"""
        return self.source_hash != text_hash(source_value)

    def __repr__(self) -> str:
        return (
            f"<Translation {self.entity_type}#{self.entity_id}"
            f".{self.field} [{self.locale}]>"
        )


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
        if bitis.tzinfo is None:            # sqlite naive dondurebilir
            bitis = bitis.replace(tzinfo=timezone.utc)
        return bitis > utcnow()

    def __repr__(self) -> str:
        return f"<LoginAttempt {self.ip} x{self.fail_count}>"


# ============================================================
#  Ceviri tablosunda kullanilan entity_type degerleri -- tek yerden.
# ============================================================
ENTITY_PAGE = "page"
ENTITY_BLOCK = "block"
ENTITY_ITEM = "block_item"
ENTITY_MEDIA = "media"
ENTITY_SETTING = "setting"

ENTITY_MODELS = {
    ENTITY_PAGE: Page,
    ENTITY_BLOCK: Block,
    ENTITY_ITEM: BlockItem,
    ENTITY_MEDIA: MediaAsset,
    ENTITY_SETTING: SiteSetting,
}


def entity_type_of(nesne) -> str:
    """Bir model nesnesinin ceviri tablosundaki entity_type karsiligi."""
    for ad, sinif in ENTITY_MODELS.items():
        if isinstance(nesne, sinif):
            return ad
    raise TypeError(f"Ceviri desteklenmeyen tur: {type(nesne).__name__}")
