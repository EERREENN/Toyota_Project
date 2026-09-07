# -*- coding: utf-8 -*-
"""Blok tipi kaydi -- 25 tip.

Burada her blok tipinin KIMLIGI durur: Turkce adi, hangi sablonla
render edilecegi, hangi CSS/JS dosyasina ihtiyac duydugu, hangi tur
ogeler icerdigi ve yeni eklendiginde hangi varsayilan ayarlarla
baslayacagi.

Burada OLMAYAN sey: panel formlari. Kullanicilar kod bilmedigi icin
formlar sema'dan otomatik uretilmiyor; her tip icin
templates/admin/fields/<tip>.html altinda ELLE yaziliyor.
"""

from __future__ import annotations

# ------------------------------------------------------------
#  Oge turleri (block_item.kind) -- panelde gorunen Turkce adlar
# ------------------------------------------------------------
ITEM_KIND_LABELS = {
    "paragraph": "Paragraf",
    "bullet": "Madde",
    "stat": "Rakam kutusu",
    "card": "Kart",
    "chip_group": "Etiket grubu",
    "chip": "Etiket",
    "stop": "Zaman tuneli duragi",
    "marker": "Harita noktasi",
    "legend": "Harita gostergesi",
    "link": "Kaynak baglantisi",
    "outro": "Kapanis paragrafi",
    "field": "Form alani",
    "option": "Secenek",
    "label": "Sonuc etiketi",
    "media": "Gorsel",
    "step": "Adim",
    "fact": "Kunye satiri",
    "badge": "Rozet",
    "news": "Bulten",
    "statement": "Ana cumle",
    "column": "Sutun",
    "value": "Deger",
    "part": "Diyagram parcasi",
    "lead": "Baslik ustu cumle",
    "light": "Andon isigi",
    "term": "Sozluk terimi",
    "row": "Tablo satiri",
    "cell": "Tablo hucresi",
}

# NOT (tasarim karari):
# Cevrilebilir HICBIR metin `settings` JSON'unda tutulmaz; hepsi
# block / block_item sutunlarindadir. Sebep: ceviri tablosu
# (entity_type, entity_id, field) uclusuyle calisiyor; JSON icindeki
# bir metni adresleyebilmek icin "settings.form.distance.label" gibi
# noktali yollar gerekirdi. Bunun yerine hesaplayicinin etiketleri
# `field` / `option` / `label` turunde ogeler, media_split'in alt ve
# altyazi metinleri ise `media` turunde bir oge olarak saklanir.
# `settings` icinde yalnizca SAYI ve YAPISAL ayar bulunur.

# ------------------------------------------------------------
#  Blok tipleri
#
#  label        : panelde gorunen Turkce ad
#  description  : editore "bu ne ise yarar" aciklamasi
#  template     : templates/blocks/<...>
#  css          : static/css/blocks/<...>   (sadece bu tip sayfadaysa yuklenir)
#  js           : static/js/modules/<...>   (main.js icinden, DOM varsa calisir)
#  vendor       : harici kutuphaneler (Leaflet gibi)
#  item_kinds   : bu tipin kullandigi oge turleri (ust seviye)
#  child_kinds  : oge altindaki alt oge turleri
#  uses_heading : ortak baslik/giris/dipnot alanlari gosterilsin mi
#  defaults     : yeni blok eklenince baslangic ayarlari
#  unique       : sayfada en fazla bir tane olmali mi
# ------------------------------------------------------------
BLOCK_TYPES: dict[str, dict] = {
    "hero": {
        "label": "Kapak (baslik + spot yazi)",
        "description": "Sayfanin en ustundeki buyuk baslik ve giris cumlesi.",
        "template": "blocks/hero.html",
        "css": "hero.css",
        "js": [],
        "vendor": [],
        "item_kinds": [],
        "child_kinds": [],
        "uses_heading": True,
        "unique": True,
        "defaults": {"image_id": None},
    },
    "rich_text": {
        "label": "Metin blogu",
        "description": "Bir veya birden fazla paragraf. Her paragraf ayri satirdir.",
        "template": "blocks/rich_text.html",
        "css": "rich-text.css",
        "js": [],
        "vendor": [],
        "item_kinds": ["paragraph"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "stat_grid": {
        "label": "Rakam izgarasi",
        "description": "Buyuk rakam + etiket + aciklama kutulari. "
                       "Rakamlar ekrana girince sayarak dolabilir.",
        "template": "blocks/stat_grid.html",
        "css": "stat-grid.css",
        "js": ["counters.js", "progress-counters.js"],
        "vendor": [],
        # `link` : bolumun altindaki baglanti
        # `fact` : izgaranin altindaki kompakt liste (rakamsiz maddeler)
        "item_kinds": ["stat", "fact", "link"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        # variant: card (beyaz kart) | progress (cevre sayfasindaki ilerleme kutulari)
        "defaults": {"variant": "card", "columns": "auto"},
    },
    "stat_badge": {
        "label": "Buyuk rakam rozeti",
        "description": "Tek, tam genislikte one cikan rakam "
                       "(ornek: 300.000.000+ uretilen arac).",
        "template": "blocks/stat_badge.html",
        "css": "stat-badge.css",
        "js": ["counters.js"],
        "vendor": [],
        "item_kinds": ["stat"],
        "child_kinds": [],
        "uses_heading": False,
        "unique": False,
        "defaults": {},
    },
    "card_grid": {
        "label": "Kart listesi",
        "description": "Baslikli kartlar. Odul kartlari ve numarali "
                       "istasyon kartlari da bu tiptir.",
        "template": "blocks/card_grid.html",
        "css": "card-grid.css",
        "js": [],
        "vendor": [],
        # `lead`  : basligin USTUNDE duran kisa gecis cumlesi
        # `outro` : izgaranin ALTINDA duran kucuk aciklama kutusu
        "item_kinds": ["lead", "card", "outro"],
        "child_kinds": ["paragraph", "bullet"],
        "uses_heading": True,
        "unique": False,
        # variant: plain (sade) | award (odul) | station (numarali istasyon)
        "defaults": {"variant": "plain", "columns": "auto"},
    },
    "chip_groups": {
        "label": "Etiket gruplari",
        "description": "Baslikli gruplar altinda kucuk etiketler "
                       "(ornek: marka ailesi).",
        "template": "blocks/chip_groups.html",
        "css": "chip-groups.css",
        "js": [],
        "vendor": [],
        "item_kinds": ["chip_group", "outro"],
        "child_kinds": ["chip"],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "process_steps": {
        "label": "Adim adim (surec)",
        "description": "Numarali adimlar tek sirada; tiklayinca aciklamasi "
                       "acilir. Dar ekranda dikey akordeona doner.",
        "template": "blocks/process_steps.html",
        "css": "process-steps.css",
        "js": ["steps.js"],
        "vendor": [],
        "item_kinds": ["step"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "timeline": {
        "label": "Zaman tuneli",
        "description": "Yil + baslik duraklari; tiklayinca aciklama acilir.",
        "template": "blocks/timeline.html",
        "css": "timeline.css",
        "js": ["timeline.js"],
        "vendor": [],
        "item_kinds": ["stop"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "map": {
        "label": "Harita (tesis noktalari)",
        "description": "Leaflet haritasi. Noktalar koordinat olarak "
                       "duzenlenir, HTML olarak degil.",
        "template": "blocks/map.html",
        "css": "map.css",
        "js": ["map.js"],
        "vendor": ["leaflet"],
        "item_kinds": ["marker", "legend"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": True,
        "defaults": {
            "map_id": "toyota-map",
            "center": [20, 20],
            "zoom": 2,
            "min_zoom": 2,
            "max_zoom": 8,
            "world_copy_jump": True,
            "tile": {
                "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "max_zoom": 18,
            },
        },
    },
    "co2_calculator": {
        "label": "CO2 hesaplayici",
        "description": "Etkilesimli hesaplayici. Katsayilar ve fiyatlar "
                       "panelden duzenlenir.",
        "template": "blocks/co2_calculator.html",
        "css": "co2-calculator.css",
        "js": ["co2-calculator.js"],
        "vendor": [],
        # Etiketler ve secenekler oge olarak saklanir (cevrilebilir olduklari
        # icin); settings'te yalnizca sayilar durur.
        "item_kinds": ["field", "label"],
        "child_kinds": ["option"],
        "uses_heading": True,
        "unique": True,
        "defaults": {
            "rates": {
                "fuel_per_100km": {},
                "kwh_per_100km": {},
                "co2_per_unit": {},
                "price_per_unit": {},
            },
            "number_locale": "tr-TR",
        },
    },
    "source_list": {
        "label": "Kaynak listesi",
        "description": "Alt alta kaynak baglantilari.",
        "template": "blocks/source_list.html",
        "css": "source-list.css",
        "js": [],
        "vendor": [],
        "item_kinds": ["link"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "media_split": {
        "label": "Metin + gorsel",
        "description": "Solda metin, sagda gorsel/cizim. Gorsel panelden "
                       "yuklenebilir.",
        "template": "blocks/media_split.html",
        "css": "media-split.css",
        "js": [],
        "vendor": [],
        # `media` turundeki oge gorselin alt metnini ve altyazisini tutar
        # (ikisi de cevrilebilir); settings'te yalnizca konum bilgisi durur.
        "item_kinds": ["paragraph", "bullet", "media"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {"media_position": "end"},
    },
    "andon": {
        "label": "Andon bandi (metin + uc durum isigi)",
        "description": "Solda metin, sagda uc durum isigi (yesil/sari/kirmizi). "
                       "Isiklar sirayla yanar; hareket azaltma tercihi acikken "
                       "animasyon durur. Dar ekranda alt alta gecer.",
        "template": "blocks/andon.html",
        "css": "andon.css",
        "js": [],
        "vendor": [],
        "item_kinds": ["paragraph", "light"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "cycle_steps": {
        "label": "Adim akisi (dongusel ya da duz)",
        "description": "Adimlar oklarla birbirine baglanir. Dongusel "
                       "secilirse sonda 'basa doner' seridi cikar, duz "
                       "secilirse cikmaz. Masaustunde yan yana, dar ekranda "
                       "alt alta. Aciklamalar hep gorunur.",
        "template": "blocks/cycle_steps.html",
        "css": "cycle-steps.css",
        "js": [],
        "vendor": [],
        # `outro`: akisin altindaki kucuk aciklama kutusu
        # `link` : akisin altindaki tek baglanti
        "item_kinds": ["step", "outro", "link"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        # variant: cycle (sonda "basa doner" seridi) | linear (duz akis)
        "defaults": {"variant": "cycle"},
    },
    "glossary": {
        "label": "Sozluk (arama kutulu akordeon)",
        "description": "Terim listesi. Ziyaretci yazdikca hem terim adinda "
                       "hem aciklamada filtreleme yapilir (Turkce karakter "
                       "duyarsiz). Basta hepsi kapali, tiklaninca acilir.",
        "template": "blocks/glossary.html",
        "css": "glossary.css",
        "js": ["glossary.js"],
        "vendor": [],
        "item_kinds": ["term"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "compare_table": {
        "label": "Karsilastirma tablosu",
        "description": "Sutunlar bir secenegi (teknoloji, paket...), satirlar "
                       "bir ozelligi anlatir. Dar ekranda tablo yatay kayar, "
                       "satir etiketleri solda sabit kalir. HUCRELER SUTUNUN "
                       "ICINDE durur: yeni sutun eklemek mevcut tabloyu "
                       "bozmaz.",
        "template": "blocks/compare_table.html",
        "css": "compare-table.css",
        "js": [],
        "vendor": [],
        # `row`   : satir etiketleri (soldaki sutun)
        # `column`: bir teknoloji + hucreleri
        # `outro` : tablonun altindaki baglam cumlesi
        "item_kinds": ["row", "column", "outro"],
        "child_kinds": ["cell"],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "hybrid_flow": {
        "label": "Hibrit akis diyagrami (asamali)",
        "description": "Ustten arac semasi uzerinde her asamada hangi "
                       "bilesenin calistigi vurgulanir. Asamaya tiklaninca "
                       "aciklamasi acilir; dar ekranda dikey akordeona "
                       "doner. SEMANIN YAPISI SABIT -- metinler buradan.",
        "template": "blocks/hybrid_flow.html",
        "css": "hybrid-flow.css",
        "js": ["hybrid.js"],
        "vendor": [],
        # `paragraph`: diyagramin yazili karsiligi (ekran okuyucu icin)
        # `step`     : asamalar
        # `outro`    : diyagramin altindaki not
        "item_kinds": ["paragraph", "step", "outro"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "tps_house": {
        "label": "TPS Evi diyagrami",
        "description": "Klasik 'TPS Evi' semasi: cati (hedefler), iki sutun "
                       "(JIT / Jidoka), merkez (insan) ve temel. Bir parcaya "
                       "tiklayinca aciklamasi diyagramin altinda acilir. "
                       "SEMANIN YAPISI SABIT -- yalnizca icindeki metinler "
                       "buradan duzenlenir.",
        "template": "blocks/tps_house.html",
        "css": "tps-house.css",
        "js": ["house.js"],
        "vendor": [],
        # `paragraph`: diyagramin yazili karsiligi (ekran okuyucu icin).
        # settings'te DEGIL, cunku cevrilmesi gerekiyor.
        "item_kinds": ["paragraph", "part"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": True,
        "defaults": {},
    },
    "section_nav": {
        "label": "Bolum menusu (sayfa ici baglantilar)",
        "description": "Uzun sayfalarda en uste konulan hizli gecis serdi. "
                       "Icerigi ELLE GIRILMEZ: sayfadaki bloklardan, "
                       "'Baglanti adresi (#)' alani doldurulmus ve basligi "
                       "olanlari kendiliginden listeler.",
        "template": "blocks/section_nav.html",
        "css": "section-nav.css",
        "js": [],
        "vendor": [],
        "item_kinds": [],
        "child_kinds": [],
        "uses_heading": True,
        "unique": True,
        "defaults": {},
    },
    "mission": {
        "label": "Vurgu bandi (ortalanmis cumle + buton)",
        "description": "Sayfa genisliginde, zemini hafif farkli sade bir band: "
                       "ortada buyuk puntolu tek cumle, altinda kisa "
                       "paragraflar, istege bagli bir yonlendirme butonu. "
                       "Kart degildir, kutu icine alinmaz.",
        "template": "blocks/mission.html",
        "css": "mission.css",
        "js": [],
        "vendor": [],
        # `link` turundeki tek oge banttaki yonlendirme butonudur.
        "item_kinds": ["statement", "paragraph", "link"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        # variant: center (ortalanmis) | split (solda metin, sagda buton)
        "defaults": {"variant": "center"},
    },
    "value_columns": {
        "label": "Deger sutunlari (iki grup + kartlar)",
        "description": "Iki sutun basligi ve her sutunun altinda deger "
                       "kartlari. Masaustunde yan yana, mobilde alt alta. "
                       "En altta istege bagli tek baglanti.",
        "template": "blocks/value_columns.html",
        "css": "value-columns.css",
        "js": [],
        "vendor": [],
        # `link` turundeki tek oge en alttaki baglantidir (news_list ile ayni).
        "item_kinds": ["column", "link"],
        "child_kinds": ["value"],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "fact_table": {
        "label": "Kunye tablosu (etiket - deger)",
        "description": "Iki sutunlu etiket-deger listesi (konum, kurulus yili, "
                       "kapasite...). Degeri bos birakilan satir sitede "
                       "gorunmez; dar ekranda tek sutuna doner.",
        "template": "blocks/fact_table.html",
        "css": "fact-table.css",
        "js": [],
        "vendor": [],
        "item_kinds": ["fact"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "badge_strip": {
        "label": "Rozet seridi (sertifika / odul)",
        "description": "Yan yana dizilen kucuk rozetler. Her rozette baslik, "
                       "istege bagli kisa aciklama ve istege bagli logo var.",
        "template": "blocks/badge_strip.html",
        "css": "badge-strip.css",
        "js": [],
        "vendor": [],
        "item_kinds": ["badge"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {},
    },
    "news_list": {
        "label": "Haber / basin bulteni listesi",
        "description": "Tarih + baslik listesi. Yalnizca en yeni birkac bulten "
                       "gosterilir (sayisi ayarlanabilir), siralama tarihe gore "
                       "azalandir. Hic bulten yoksa blok sitede hic gorunmez.",
        "template": "blocks/news_list.html",
        "css": "news-list.css",
        "js": [],
        "vendor": [],
        # `link` turundeki tek oge alttaki "Tum bultenler" baglantisidir.
        "item_kinds": ["news", "link"],
        "child_kinds": [],
        "uses_heading": True,
        "unique": False,
        "defaults": {"limit": 5},
    },
    "divider": {
        "label": "Ayrac serit",
        "description": "Dekoratif konveyor bandi (uretim sistemi sayfasi).",
        "template": "blocks/divider.html",
        "css": "divider.css",
        "js": [],
        "vendor": [],
        "item_kinds": [],
        "child_kinds": [],
        "uses_heading": False,
        "unique": False,
        "defaults": {"variant": "conveyor"},
    },
}

# ------------------------------------------------------------
#  Harici kutuphaneler
# ------------------------------------------------------------
VENDOR_ASSETS = {
    "leaflet": {
        "css": ["https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"],
        "js": ["https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"],
    },
}

# ------------------------------------------------------------
#  Her sayfada yuklenen CSS (blok tipinden bagimsiz)
# ------------------------------------------------------------
BASE_CSS = ["tokens.css", "base.css", "layout.css", "blocks/card.css"]

# ------------------------------------------------------------
#  Sayfa temalari -> <body class="page-...">  ve tema CSS dosyasi
# ------------------------------------------------------------
THEMES = {
    "tmmt": {"label": "TMMT (mavi-gri)", "css": "themes/tmmt.css"},
    "global": {"label": "Global (altin)", "css": "themes/global.css"},
    "uretim": {"label": "Uretim sistemi (celik)", "css": "themes/uretim.css"},
    "cevre": {"label": "Cevre (yesil)", "css": "themes/cevre.css"},
}

# ------------------------------------------------------------
#  Site ayarlari -- panelde "Site ayarlari" ekraninda gorunur
#  (admin_password_hash burada YOK: gizli, ayri ekranda yonetilir)
# ------------------------------------------------------------
SETTING_FIELDS = [
    {
        "key": "brand",
        "label": "Ust bardaki site adi",
        "translatable": False,
        "default": "TOYOTA",
    },
    {
        "key": "nav_toggle_label",
        "label": "Mobil menu dugmesi (ekran okuyucu metni)",
        "translatable": True,
        "default": "Menü",
    },
    {
        "key": "lang_group_label",
        "label": "Dil secici (ekran okuyucu metni)",
        "translatable": True,
        "default": "Dil seçimi",
    },
    {
        "key": "lang_short_tr",
        "label": "Dil dugmesi -- Turkce kisaltmasi",
        "translatable": False,
        "default": "TR",
    },
    {
        "key": "lang_short_en",
        "label": "Dil dugmesi -- Ingilizce kisaltmasi",
        "translatable": False,
        "default": "ENG",
    },
]

# Panelde gosterilmeyen, sistem tarafindan kullanilan ayar anahtarlari
SYSTEM_SETTING_KEYS = ("admin_password_hash",)


# ------------------------------------------------------------
#  Yardimcilar
# ------------------------------------------------------------
def is_valid_type(tip: str) -> bool:
    return tip in BLOCK_TYPES


def spec(tip: str) -> dict:
    try:
        return BLOCK_TYPES[tip]
    except KeyError:
        raise KeyError(
            f"Bilinmeyen blok tipi: {tip!r}. "
            f"Gecerli tipler: {', '.join(sorted(BLOCK_TYPES))}"
        ) from None


def label(tip: str) -> str:
    return BLOCK_TYPES.get(tip, {}).get("label", tip)


def template_of(tip: str) -> str:
    return spec(tip)["template"]


def defaults_for(tip: str) -> dict:
    """Yeni blok eklenirken kullanilacak baslangic ayarlari (kopya)."""
    import copy

    return copy.deepcopy(spec(tip).get("defaults", {}))


def css_for(tipler) -> list[str]:
    """Sayfada kullanilan blok tiplerine gore CSS dosya listesi.

    Sira onemli: once tokens/base/layout, sonra bloklar. Tema CSS'i
    en sona sayfa render'i sirasinda eklenir.
    """
    dosyalar = list(BASE_CSS)
    for tip in tipler:
        ad = BLOCK_TYPES.get(tip, {}).get("css")
        if ad:
            yol = f"blocks/{ad}"
            if yol not in dosyalar:
                dosyalar.append(yol)
    return dosyalar


def vendor_for(tipler) -> dict[str, list[str]]:
    """Sayfada kullanilan blok tiplerinin gerektirdigi harici dosyalar."""
    css: list[str] = []
    js: list[str] = []
    for tip in tipler:
        for ad in BLOCK_TYPES.get(tip, {}).get("vendor", []):
            varlik = VENDOR_ASSETS.get(ad, {})
            for u in varlik.get("css", []):
                if u not in css:
                    css.append(u)
            for u in varlik.get("js", []):
                if u not in js:
                    js.append(u)
    return {"css": css, "js": js}


def kind_label(kind: str) -> str:
    return ITEM_KIND_LABELS.get(kind, kind)


def secilebilir_tipler() -> list[tuple[str, str, str]]:
    """Panelde 'blok ekle' listesinde gosterilecek (tip, ad, aciklama)."""
    return [
        (tip, veri["label"], veri["description"])
        for tip, veri in BLOCK_TYPES.items()
    ]
