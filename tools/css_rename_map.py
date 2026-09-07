# -*- coding: utf-8 -*-
"""Asama 2b: eski CSS sinif adi -> yeni (blok adiyla oneklenmis) ad.

Bu sozluk TEK DOGRULUK KAYNAGIDIR: hem dogrulama araci (css_check.py)
hem de degisiklikleri gozden gecirirken bakilacak tablo budur.

ONEK KURALI
-----------
  tk-<blok>__<parca>     bloga ait parca      (tk-timeline__year)
  tk-<blok>--<varyant>   ayni blogun varyanti (tk-grid--2)
  tk-<paylasilan>        birden fazla blogun kullandigi yuzey/araclar
                         (tk-card, tk-grid, tk-note, tk-subnote)

ONEKLENMEYENLER
---------------
Kabuk ve durum siniflari bir bloga ait degil, oldugu gibi kaliyor:
  navbar / nav-inner / nav-menu / nav-links / nav-toggle* / brand
  lang-switch / lang-opt / lang-pill
  page / page-tmmt / page-global / page-uretim / page-cevre
  js / reveal / reveal-in / is-open / active / nav-open / table-wrap
  leaflet-* (ucuncu parti)
"""

from __future__ import annotations

RENAME = {
    # --- paylasilan yuzeyler (blocks/card.css, base.css) ---
    "icerik-blok": "tk-block",
    "grid": "tk-grid",
    "grid-2": "tk-grid--2",
    "kart": "tk-card",
    "kaynak-not": "tk-note",
    # .milestone-sub iki yerde kullaniliyordu: stat_badge'in alt notu ve
    # chip_groups'un soluk kapanis paragrafi. Bir bloga ait olmadigi icin
    # paylasilan araca donusturuldu -- boylece chip_groups'un stat_badge'e
    # bagimli olmasi gerekmiyor.
    "milestone-sub": "tk-subnote",

    # --- hero ---
    "hero": "tk-hero",
    "lede": "tk-hero__lede",

    # --- stat_grid ---
    "stat": "tk-stat-grid__value",
    "ilerleme-grid": "tk-stat-grid--progress",
    "ilerleme-kart": "tk-stat-grid__progress-card",
    "ilerleme-sayi": "tk-stat-grid__progress-value",
    "sayac": "tk-stat-grid__count",
    "sayac-sonek": "tk-stat-grid__count-suffix",

    # --- stat_badge ---
    "milestone-badge": "tk-stat-badge",
    "milestone-num": "tk-stat-badge__value",
    "milestone-label": "tk-stat-badge__label",

    # --- card_grid ---
    "odul-grid": "tk-card-grid--award",
    "odul-kart": "tk-card-grid__award-card",
    "odul-yil": "tk-card-grid__year",
    "hat-alani": "tk-card-grid--station",
    "hat-baslik": "tk-card-grid__station-title",
    "hat-aciklama": "tk-card-grid__station-intro",
    "istasyon": "tk-card-grid__station",
    "istasyon-no": "tk-card-grid__station-no",

    # --- chip_groups ---
    "marka-agaci": "tk-chip-groups",
    "marka-grup": "tk-chip-groups__group",
    "marka-cips": "tk-chip-groups__list",
    "cip": "tk-chip-groups__chip",

    # --- timeline ---
    "zaman-tuneli": "tk-timeline",
    "zt-durak": "tk-timeline__stop",
    "zt-nokta": "tk-timeline__button",
    "zt-detay": "tk-timeline__detail",
    "zt-yil": "tk-timeline__year",
    "zt-baslik": "tk-timeline__title",
    "acik": "is-open",          # durum sinifi

    # --- map ---
    "map-urun": "tk-map__product",
    "map-not": "tk-map__legend",
    "dot": "tk-map__dot",
    "dot-red": "tk-map__dot--red",
    "dot-gold": "tk-map__dot--gold",

    # --- co2_calculator ---
    "hesap-form": "tk-calc__form",
    "hesap-alan": "tk-calc__field",
    "hesap-sonuc": "tk-calc__result",
    "sonuc-ust": "tk-calc__summary",
    "sonuc-kart": "tk-calc__summary-item",
    "sonuc-etiket": "tk-calc__label",
    "sonuc-deger": "tk-calc__value",
    "sonuc-bar": "tk-calc__chart",
    "bar-baslik": "tk-calc__chart-title",
    "bar-satir": "tk-calc__row",
    "bar-etiket": "tk-calc__row-label",
    "bar-yol": "tk-calc__track",
    "bar-dolu": "tk-calc__fill",
    "bar-mevcut": "tk-calc__fill--current",
    "bar-toyota": "tk-calc__fill--toyota",
    "bar-sayi": "tk-calc__row-value",

    # --- source_list ---
    "kaynaklar": "tk-source-list",

    # --- media_split ---
    "vitrin-grid": "tk-media-split",
    "vitrin-metin": "tk-media-split__text",
    "vitrin-gorsel": "tk-media-split__figure",
    "gorsel-yer": "tk-media-split__frame",

    # --- divider ---
    "hat-serit": "tk-divider--conveyor",

    # --- sayfa arka planlari (tema dosyalari) ---
    "tmmt-bg": "tk-bg--tmmt",
    "global-bg": "tk-bg--global",
    "uretim-bg": "tk-bg--uretim",
    "cevre-bg": "tk-bg--cevre",
}

# @keyframes adlari
KEYFRAME_RENAME = {
    "hat-kay": "tk-conveyor-belt",
    "hat-parca": "tk-conveyor-part",
}

# Bilerek DEGISMEYEN siniflar (dogrulama bunlari "eksik" saymasin)
KORUNAN = {
    "navbar", "nav-inner", "nav-menu", "nav-links", "nav-toggle",
    "nav-toggle-box", "nav-toggle-bar", "nav-open", "brand",
    "lang-switch", "lang-opt", "lang-pill",
    "page", "page-tmmt", "page-global", "page-uretim", "page-cevre",
    "js", "reveal", "reveal-in", "is-open", "active", "table-wrap",
    "leaflet-tile-pane", "leaflet-popup-content",
}

# Eski CSS'te tanimliydi ama HICBIR sablonda kullanilmiyordu.
# Tasima sirasinda bilerek atildi (olu kural).
ATILAN = {
    "hedef-liste": "hicbir sablonda kullanilmiyordu (olu kural)",
}

# HTML'de kullanilan ama BILEREK stilsiz olan siniflar.
# Bunlar gorsel degil islevsel: JS'in elemani bulmasi ya da bir durumu
# isaretlemesi icin varlar. Eski CSS'te de stilleri yoktu.
STILSIZ_KABUL = {
    # JS'in yazi yazdigi sayac kutusu (eski adi .sayac). Gorunum
    # ust ogesi .tk-stat-grid__progress-value'dan geliyor.
    "tk-stat-grid__count": "JS tutamagi -- eski .sayac da stilsizdi",
    # Calisma aninda JS tarafindan eklenen durum siniflari
    "reveal-in": "JS ekliyor (kaydirdikca belirme)",
    "is-open": "JS ekliyor (menu / zaman tuneli acik durumu)",
    "nav-open": "JS ekliyor (mobil menu acikken govde kilidi)",
    # Leaflet'in kendi urettigi siniflar
    "leaflet-tile-pane": "Leaflet uretiyor",
    "leaflet-popup-content": "Leaflet uretiyor",
    # Popup HTML'i JS icinde uretiliyor, sablonda gorunmez
    "tk-map__product": "JS'in urettigi popup icinde",
    # value_columns'un yapisal tutamaklari: gorunumleri ust ogeden
    # (.tk-value-columns izgarasi) ve .tk-card yuzeyinden geliyor,
    # kendi kurallari yok.
    "tk-value-columns__column": "izgara cocugu -- stili ust ogeden",
    "tk-value-columns__value": ".tk-card ile birlikte kullaniliyor",
    # JS'in TPS Evi'ni bulmak icin kullandigi kapsam sinifi; gorunumu
    # .tk-block'tan geliyor, kendi kurali yok.
    "tk-house": "JS kapsam tutamagi (house.js)",
    "tk-hybrid": "JS kapsam tutamagi (hybrid.js)",
    # Not satirinin gorunumu hucrelerinden geliyor
    # (.tk-compare__cell--note); satirin kendi kurali yok.
    "tk-compare__note-row": "yapisal tutamak -- stili hucrelerden",
}

# CSS'te tanimli ama sayfalarda HENUZ gorunmeyen siniflar.
# Bunlar editor panelden gorsel sectiginde devreye giriyor; su an
# hicbir bloga gorsel atanmadigi icin HTML'de yoklar. Eksik degiller.
EDITORE_BAGLI = {
    "tk-hero__image": "kapak gorseli secilirse",
    "tk-card__image": "kart gorseli secilirse",
    "tk-steps__image": "adim gorseli secilirse",
    "tk-timeline__image": "zaman tuneli duragina gorsel secilirse",
    "tk-badge-strip__logo": "rozete logo secilirse",
}

# #id -> .class donusumu.
# Harita kabinin id'si artik ayarlanabilir (block.settings.map_id);
# stil bir id'ye baglanamaz, bu yuzden sinifa tasindi.
ID_TO_CLASS = {
    "toyota-map": "tk-map__canvas",
}


def yeni_ad(eski: str) -> str:
    """Bir sinif adinin yeni karsiligi (degismeyenler aynen doner)."""
    return RENAME.get(eski, eski)
