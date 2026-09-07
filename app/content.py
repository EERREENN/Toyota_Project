# -*- coding: utf-8 -*-
"""ICERIGI OKUYAN TEK MODUL.

Sablonlar ve rotalar veritabanini DOGRUDAN gormez; her sey buradan gecer.
Ileride depolama degisirse (baska bir veritabani, bir API, dosya sistemi)
degisecek tek yer burasidir.

Disari verdigi sey model nesneleri degil, sade "gorunum" nesneleridir
(PageView / BlockView / ItemView). Bunlarin icindeki metinler ISTENEN
DILDE cozulmus haldedir; sablonun ceviri yapmasi gerekmez.

Ceviri cozumleme sirasi:
    1) locale == "tr"            -> kaynak sutunun kendisi
    2) translation tablosunda EN -> oradaki deger
    3) hicbiri yoksa            -> auto_translate (calisma zamani, onbellekli)

3. adim normalde hic calismaz: seed her cevrilebilir alan icin satir
uretir. Yalnizca panelden yeni icerik eklenip cevirisi henuz uretilmemisse
devreye girer -- yani hicbir sey Turkce kalmis gorunmez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

import auto_translate

from .block_types import BASE_CSS, BLOCK_TYPES, THEMES, css_for, vendor_for
from .extensions import db
from .models import Block, BlockItem, MediaAsset, Page, SiteSetting, Translation


# ============================================================
#  Gorunum nesneleri
# ============================================================
@dataclass
class ImageView:
    id: int
    path: str                     # static/ altina gore: "img/tmmt-bg.jpg"
    alt: str = ""
    width: int | None = None
    height: int | None = None


@dataclass
class ItemView:
    id: int
    kind: str
    variant: str | None = None
    slug: str | None = None
    eyebrow: str | None = None
    title: str | None = None
    subtitle: str | None = None
    value: str | None = None
    text: str | None = None
    note: str | None = None
    url: str | None = None
    link_label: str | None = None
    image: ImageView | None = None
    lat: float | None = None
    lon: float | None = None
    count_to: float | None = None
    count_from: float = 0.0
    count_prefix: str | None = None
    count_suffix: str | None = None
    count_group: bool = False
    count_format: str = "group"
    settings: dict = field(default_factory=dict)
    children: list["ItemView"] = field(default_factory=list)

    @property
    def has_count(self) -> bool:
        return self.count_to is not None

    def children_of(self, kind: str) -> list["ItemView"]:
        return [c for c in self.children if c.kind == kind]

    @property
    def alt_baslik_farkli(self) -> bool:
        """Alt baslik, basligin AYNISI degil mi?

        Turkce kaynakta "Redesign / Yeniden tasarla" gibi bir cift,
        Ingilizce'ye cevrilince "Redesign / redesign" haline geliyor --
        ayni seyi iki kez yazmis oluyoruz. Bu kural o tekrari
        kendiliginden tekile indiriyor; iki blok tipi (card_grid ve
        value_columns) ayni kurali kullandigi icin burada duruyor.

        ICERME de sayilir: "Reuse / Remanufacture" basliginin altina
        "reuse" yazmanin bir anlami yok. Baslik alt basligi zaten
        soyluyorsa satir basilmaz.
        """
        alt = (self.subtitle or "").lower().strip()
        if not alt:
            return False
        return alt not in (self.title or "").lower().strip()


@dataclass
class BlockView:
    id: int
    type: str
    anchor: str | None = None
    heading: str | None = None
    heading_level: int = 2
    intro: str | None = None
    note: str | None = None
    reveal: bool = False
    settings: dict = field(default_factory=dict)
    items: list[ItemView] = field(default_factory=list)
    # settings.image_id ile secilen gorsel (su an yalnizca hero kullaniyor)
    image: ImageView | None = None

    def items_of(self, kind: str) -> list[ItemView]:
        return [i for i in self.items if i.kind == kind]

    def first_of(self, kind: str) -> ItemView | None:
        bulunan = self.items_of(kind)
        return bulunan[0] if bulunan else None

    def by_slug(self, slug: str) -> ItemView | None:
        for i in self.items:
            if i.slug == slug:
                return i
        return None

    @property
    def variant(self) -> str | None:
        return self.settings.get("variant")

    @property
    def columns(self) -> str:
        return str(self.settings.get("columns", "auto"))

    @property
    def has_header(self) -> bool:
        """Ortak baslik/giris/dipnot sarmalayicisi gerekiyor mu?"""
        return bool(self.heading or self.intro or self.note)

    @property
    def renders(self) -> bool:
        """Bu blok sayfada gorunur bir sey basacak mi?

        Bazi bloklar KENDINI GIZLIYOR: icerigi doldurulmamis bir bolum
        basligiyla birlikte hic basilmasin diye (bkz. ilgili
        templates/blocks/*.html). Kural burada tek yerde duruyor,
        cunku iki yer birden bilmek zorunda:

          1. blogun kendi sablonu  -> basayim mi?
          2. bolum menusu          -> bu bolume link vereyim mi?

        Ikisi ayrisirsa menude hicbir yere gitmeyen bir link kalir.
        """
        if self.type == "card_grid":
            return any(i.title for i in self.items_of("card"))
        if self.type == "news_list":
            return bool(news_items(self))
        if self.type == "mission":
            cumle = self.first_of("statement")
            buton = self.first_of("link")
            return bool(
                (cumle and cumle.text)
                or self.items_of("paragraph")
                or (buton and buton.url and buton.title)
            )
        return True


@dataclass
class PageView:
    id: int
    slug: str
    url: str
    title: str
    nav_label: str
    theme: str
    is_home: bool = False
    background: ImageView | None = None
    blocks: list[BlockView] = field(default_factory=list)

    @property
    def body_class(self) -> str:
        return f"page-{self.theme}"

    @property
    def background_class(self) -> str:
        """Arka plan katmani: .tk-bg--tmmt / --global / --uretim / --cevre

        Gorselin kendisi tema CSS'inde tanimli. Panelden degistirilebilir
        hale getirmek Asama 4'un isi (gorsel yukleme ile birlikte).
        """
        return f"tk-bg--{self.theme}"

    @property
    def block_types(self) -> list[str]:
        gorulen: list[str] = []
        for b in self.blocks:
            if b.type not in gorulen:
                gorulen.append(b.type)
        return gorulen

    @property
    def css_files(self) -> list[str]:
        dosyalar = css_for(self.block_types)
        tema = THEMES.get(self.theme, {}).get("css")
        if tema and tema not in dosyalar:
            dosyalar.append(tema)
        return dosyalar

    @property
    def vendor(self) -> dict:
        return vendor_for(self.block_types)


@dataclass
class NavItem:
    url: str
    label: str
    slug: str
    is_active: bool = False


# ============================================================
#  Ceviri cozumleyici
# ============================================================
class _Cevirmen:
    """Bir istek boyunca ceviri satirlarini tek seferde yukleyip dagitir.

    N+1 sorgu olmasin diye: sayfanin tum bloklari/ogeleri icin ceviriler
    3 sorguda alinir, sonra sozlukten okunur.
    """

    def __init__(self, locale: str):
        self.locale = locale
        self.kaynak_dil = locale == "tr"
        self._satirlar: dict[tuple[str, int, str], str] = {}

    def yukle(self, entity_type: str, kimlikler) -> None:
        if self.kaynak_dil:
            return
        kimlikler = [k for k in kimlikler if k is not None]
        if not kimlikler:
            return
        sorgu = select(Translation).where(
            Translation.entity_type == entity_type,
            Translation.locale == self.locale,
            Translation.entity_id.in_(kimlikler),
        )
        for satir in db.session.scalars(sorgu):
            self._satirlar[(satir.entity_type, satir.entity_id, satir.field)] = satir.value

    def __call__(self, entity_type: str, entity_id: int, alan: str, kaynak):
        if self.kaynak_dil or not kaynak:
            return kaynak
        deger = self._satirlar.get((entity_type, entity_id, alan))
        if deger:
            return deger
        # Ceviri satiri yoksa calisma zamaninda cevir (onbellekli, ag
        # yoksa Turkce doner -- uygulama asla hata vermez).
        return auto_translate.translate(kaynak, self.locale)


# ============================================================
#  Donusturme
# ============================================================
def _gorsel(varlik: MediaAsset | None, cevir: _Cevirmen) -> ImageView | None:
    if varlik is None:
        return None
    return ImageView(
        id=varlik.id,
        path=varlik.path,
        alt=cevir("media", varlik.id, "alt", varlik.alt) or "",
        width=varlik.width,
        height=varlik.height,
    )


def _oge(model: BlockItem, cevir: _Cevirmen) -> ItemView:
    return ItemView(
        id=model.id,
        kind=model.kind,
        variant=model.variant,
        slug=model.slug,
        eyebrow=model.eyebrow,
        title=cevir("block_item", model.id, "title", model.title),
        subtitle=cevir("block_item", model.id, "subtitle", model.subtitle),
        # `value` yalnizca ekranda gorunen turlerde cevrilir; secenek
        # kodlari ("benzin", "hev") oldugu gibi kalmali.
        value=(
            cevir("block_item", model.id, "value", model.value)
            if "value" in model.translatable_fields
            else model.value
        ),
        text=cevir("block_item", model.id, "text", model.text),
        note=cevir("block_item", model.id, "note", model.note),
        url=model.url,
        link_label=cevir("block_item", model.id, "link_label", model.link_label),
        image=_gorsel(model.image, cevir),
        lat=model.lat,
        lon=model.lon,
        count_to=model.count_to,
        count_from=model.count_from,
        count_prefix=model.count_prefix,
        count_suffix=model.count_suffix,
        count_group=model.count_group,
        count_format=model.count_format,
        settings=dict(model.settings or {}),
        children=[_oge(c, cevir) for c in model.children if c.is_visible],
    )


def _blok(model: Block, sayfa: Page, cevir: _Cevirmen) -> BlockView:
    # reveal: blokta acikca belirtilmemisse sayfanin varsayilani
    goster = model.reveal if model.reveal is not None else sayfa.reveal_default

    # settings.image_id -> gorsel (hero)
    gorsel_id = (model.settings or {}).get("image_id")
    gorsel = db.session.get(MediaAsset, gorsel_id) if gorsel_id else None

    return BlockView(
        id=model.id,
        type=model.type,
        anchor=model.anchor,
        heading=cevir("block", model.id, "heading", model.heading),
        heading_level=model.heading_level,
        intro=cevir("block", model.id, "intro", model.intro),
        note=cevir("block", model.id, "note", model.note),
        reveal=bool(goster),
        settings=dict(model.settings or {}),
        image=_gorsel(gorsel, cevir),
        items=[_oge(i, cevir) for i in model.items if i.is_visible],
    )


# ============================================================
#  Genel API  --  disaridan kullanilan tek yuzey
# ============================================================
def get_site(locale: str) -> dict[str, str]:
    """Marka adi ve kabuk metinleri."""
    cevir = _Cevirmen(locale)
    ayarlar = list(db.session.scalars(select(SiteSetting)))
    cevir.yukle("setting", [a.id for a in ayarlar])
    return {
        a.key: cevir("setting", a.id, "value", a.value) or ""
        for a in ayarlar
    }


def get_nav(locale: str, aktif_slug: str | None = None) -> list[NavItem]:
    """Ust menu -- yayindaki sayfalar, nav_order sirasiyla."""
    cevir = _Cevirmen(locale)
    sayfalar = list(
        db.session.scalars(
            select(Page).where(Page.is_published.is_(True)).order_by(Page.nav_order)
        )
    )
    cevir.yukle("page", [s.id for s in sayfalar])
    return [
        NavItem(
            url=s.url,
            label=cevir("page", s.id, "nav_label", s.nav_label) or s.nav_label,
            slug=s.slug,
            is_active=(s.slug == aktif_slug),
        )
        for s in sayfalar
    ]


def _sayfa_sorgusu():
    return select(Page).options(
        selectinload(Page.blocks).selectinload(Block.all_items),
        selectinload(Page.background_image),
    )


def _dolu_sayfa(model: Page | None, locale: str) -> PageView | None:
    if model is None or not model.is_published:
        return None

    cevir = _Cevirmen(locale)
    bloklar = [b for b in model.blocks if b.is_visible]
    oge_kimlikleri = [i.id for b in bloklar for i in b.all_items]
    gorsel_kimlikleri = [i.image_id for b in bloklar for i in b.all_items]
    if model.background_image_id:
        gorsel_kimlikleri.append(model.background_image_id)

    cevir.yukle("page", [model.id])
    cevir.yukle("block", [b.id for b in bloklar])
    cevir.yukle("block_item", oge_kimlikleri)
    cevir.yukle("media", gorsel_kimlikleri)

    return PageView(
        id=model.id,
        slug=model.slug,
        url=model.url,
        title=cevir("page", model.id, "title", model.title) or model.title,
        nav_label=cevir("page", model.id, "nav_label", model.nav_label) or model.nav_label,
        theme=model.theme,
        is_home=model.is_home,
        background=_gorsel(model.background_image, cevir),
        blocks=[_blok(b, model, cevir) for b in bloklar],
    )


def get_page_by_url(url: str, locale: str) -> PageView | None:
    model = db.session.scalars(_sayfa_sorgusu().where(Page.url == url)).first()
    return _dolu_sayfa(model, locale)


def get_page_by_slug(slug: str, locale: str) -> PageView | None:
    model = db.session.scalars(_sayfa_sorgusu().where(Page.slug == slug)).first()
    return _dolu_sayfa(model, locale)


def get_home(locale: str) -> PageView | None:
    model = db.session.scalars(
        _sayfa_sorgusu().where(Page.is_home.is_(True)).order_by(Page.nav_order)
    ).first()
    if model is None:
        model = db.session.scalars(_sayfa_sorgusu().order_by(Page.nav_order)).first()
    return _dolu_sayfa(model, locale)


def get_home_url() -> str:
    """Markanin ve 404 sayfasinin baglanacagi adres."""
    url = db.session.scalar(select(Page.url).where(Page.is_home.is_(True)))
    return url or "/"


def shell_css_files() -> list[str]:
    """Sayfa baglami olmadan (404 gibi) yuklenecek CSS dosyalari."""
    return list(BASE_CSS)


def block_template(tip: str) -> str:
    """Blok tipinin sablon yolu. Bilinmeyen tip icin bos parca."""
    veri = BLOCK_TYPES.get(tip)
    return veri["template"] if veri else "blocks/_unknown.html"


def all_page_urls() -> list[str]:
    return list(db.session.scalars(select(Page.url).order_by(Page.nav_order)))


# ============================================================
#  Etkilesimli bloklarin JS'e verdigi veri
#
#  Harita ve hesaplayici HTML olarak degil VERI olarak saklaniyor.
#  Sablon bu sozlukleri <script type="application/json"> icine basar,
#  ilgili JS modulu okur. Boylece editor koordinat ve katsayi
#  duzenleyebilir, HTML'e hic dokunmadan.
# ============================================================
def map_payload(blok: BlockView) -> dict:
    ayar = blok.settings or {}
    doseme = ayar.get("tile", {}) or {}
    noktalar = []
    for oge in blok.items_of("marker"):
        if oge.lat is None or oge.lon is None:
            continue
        noktalar.append(
            {
                "lat": oge.lat,
                "lon": oge.lon,
                "title": oge.title or "",
                "subtitle": oge.subtitle or "",
                "text": oge.text or "",
                "kind": oge.variant or "plant",
                "url": oge.url or "",
                "linkLabel": oge.link_label or "",
                "open": bool(oge.settings.get("open")),
            }
        )
    return {
        "mapId": ayar.get("map_id", "toyota-map"),
        "center": ayar.get("center", [20, 20]),
        "zoom": ayar.get("zoom", 2),
        "minZoom": ayar.get("min_zoom", 2),
        "maxZoom": ayar.get("max_zoom", 8),
        "worldCopyJump": bool(ayar.get("world_copy_jump", True)),
        "tile": {
            "url": doseme.get("url", ""),
            "maxZoom": doseme.get("max_zoom", 18),
            "attribution": doseme.get("attribution", ""),
        },
        "markers": noktalar,
    }


def news_items(blok: BlockView, limit: int | None = None) -> list[ItemView]:
    """Haber listesinin sayfada gosterilecek bultenleri.

    Siralama ve kirpma sablonda degil BURADA: tarih ISO metin olarak
    (`slug` = "2026-03-12") saklandigi icin karsilastirma kurali tek
    yerde dursun. Basligi olmayan bulten atlanir; tarihi girilmemis
    olan en sona duser.
    """
    ayar = blok.settings or {}
    if limit is None:
        try:
            limit = int(ayar.get("limit", 5))
        except (TypeError, ValueError):
            limit = 5
    # Panelde alan bosaltilirsa 0 gelir; blogun tamamen kaybolmasi
    # yerine varsayilana donsun. Blogu gizlemenin yolu "Gorunum"
    # sekmesindeki gorunurluk kutusu.
    if limit < 1:
        limit = 5

    bultenler = [o for o in blok.items_of("news") if (o.title or "").strip()]
    # ISO tarih sozlukte de dogru siralanir; tarihsizler "" ile sona gider.
    bultenler.sort(key=lambda o: (o.slug or ""), reverse=True)
    return bultenler[:limit]


# Ay adlari: tarih `slug` alaninda ISO olarak duruyor, ekranda dilin
# kendi yazimiyla gosteriliyor. Ceviri tablosuna girmiyor -- icerik
# degil arayuz metni; ayrica her bultende tekrar etmesi anlamsiz olurdu.
_AYLAR = {
    "tr": ("Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
           "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"),
    "en": ("January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"),
}


def tarih_metni(iso: str | None, locale: str = "tr") -> str:
    """'2026-03-12' -> '12 Mart 2026' / '12 March 2026'.

    Tanimadigi bicimi oldugu gibi dondurur: editor elle bir sey
    yazdiysa sayfa yine de bir sey gosterir.
    """
    if not iso:
        return ""
    parcalar = str(iso).strip().split("-")
    if len(parcalar) != 3:
        return str(iso)
    try:
        yil, ay, gun = int(parcalar[0]), int(parcalar[1]), int(parcalar[2])
    except ValueError:
        return str(iso)
    if not 1 <= ay <= 12:
        return str(iso)
    adlar = _AYLAR.get(locale, _AYLAR["tr"])
    return f"{gun} {adlar[ay - 1]} {yil}"


def calc_payload(blok: BlockView) -> dict:
    ayar = blok.settings or {}
    oranlar = ayar.get("rates", {}) or {}
    return {
        # static/js/cevre.js icindeki TUKETIM / ELEKTRIK / CO2 / FIYAT
        "fuelPer100km": oranlar.get("fuel_per_100km", {}),
        "kwhPer100km": oranlar.get("kwh_per_100km", {}),
        "co2PerUnit": oranlar.get("co2_per_unit", {}),
        "pricePerUnit": oranlar.get("price_per_unit", {}),
        "numberLocale": ayar.get("number_locale", "tr-TR"),
    }


# Turkce harfleri ASCII karsiliklarina indirger. Sozluk aramasi
# "sogut" yazinca "söğüt"u de bulsun diye; ayni donusum tarayici
# tarafinda da var (static/js/modules/glossary.js) -- ikisi ayrisirsa
# arama sessizce eksik sonuc dondurur, o yuzden birlikte degistirin.
#
# NOT: once translate(), sonra lower(). Ters sirada "İ".lower() ayri
# bir birlestirici nokta uretir ("i̇") ve eslesme bozulur.
_SADE_HARFLER = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g",
    "ı": "i", "I": "i", "İ": "i",
    "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
    "â": "a", "Â": "a", "î": "i", "Î": "i", "û": "u", "Û": "u",
})


def sadelestir(metin: Any) -> str:
    """'Genchi Genbutsu' / 'İsraf' -> aramada karsilastirilabilir hal."""
    if not metin:
        return ""
    return str(metin).translate(_SADE_HARFLER).lower()


# Sablonlarin ihtiyac duydugu yardimcilar
def sayi_metni(deger: Any) -> str:
    """2035.0 -> "2035",  7.4 -> "7.4".  data-* ozniteliklerinde kullanilir."""
    if deger is None:
        return ""
    if isinstance(deger, float) and deger.is_integer():
        return str(int(deger))
    return str(deger)
