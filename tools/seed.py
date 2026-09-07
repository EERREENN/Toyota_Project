# -*- coding: utf-8 -*-
"""Mevcut 4 sayfanin icerigini veritabanina aktarir.

NEREDEN NEREYE:
  templates/tmmt.html            -> Page "tmmt"            + 6 blok
  templates/global_toyota.html   -> Page "global-toyota"   + 9 blok
  templates/uretim_sistemi.html  -> Page "uretim-sistemi"  + 5 blok
  templates/cevre.html           -> Page "cevre"           + 7 blok
  static/js/toyota-map.js        -> map blogunun 37 noktasi
  static/js/cevre.js             -> co2_calculator blogunun katsayilari
  templates/base.html            -> SiteSetting (marka, menu metinleri)
  static/img/*.jpg               -> MediaAsset (is_builtin=True)

TURKCE METINLER BIREBIR TASINDI. Sablonlardaki {% trans %} bloklari
"trimmed" politikasiyla tek satira indirgenmis haliyle yaziliyor -- yani
translations/auto_cache.json icindeki anahtarlarla KARAKTER KARAKTER ayni.
Bu sayede mevcut 150 ceviri yeniden cevrilmeden kullanilir.

INGILIZCE CEVIRILER: seed sirasinda AG KULLANILMAZ. Her cevrilebilir alan
icin auto_cache.json'a bakilir; varsa oradaki karsilik yazilir, yoksa
Turkce metnin kendisi yazilir. Bu, bugunku sitenin urettigi ciktinin
tamamen aynisidir (cunku bugun de cevrilmeyen metin Turkce gorunuyor).

    python tools/seed.py            # bos veritabanini doldur
    python tools/seed.py --reset    # her seyi sil ve yeniden doldur
    python tools/seed.py --rapor    # sadece mevcut durumu ozetle
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.factory import create_app                      # noqa: E402
from app.extensions import db                           # noqa: E402
from app.models import (                                # noqa: E402
    Block,
    BlockItem,
    MediaAsset,
    Page,
    SiteSetting,
    Translation,
    text_hash,
)
from app.block_types import BLOCK_TYPES, SETTING_FIELDS  # noqa: E402

CACHE_PATH = ROOT / "translations" / "auto_cache.json"
HEDEF_DILLER = ["en"]


# ============================================================
#  SITE AYARLARI  (templates/base.html)
# ============================================================
SITE_AYARLARI = {
    "brand": "TOYOTA",
    "nav_toggle_label": "Menü",
    "lang_group_label": "Dil seçimi",
    "lang_short_tr": "TR",
    "lang_short_en": "ENG",
}


# ============================================================
#  PANELDEN DUZENLENEBILIR BLOK TIPLERI
#
#  Buranin disindaki her tip `is_locked=True` ile kurulur ve panelde
#  salt okunur gorunur. Yeni bir tipi acmak = bu listeye eklemek.
#  Ayni liste tools/kilit_ekle.py icinde de var (ACIK_TIPLER); mevcut
#  bir veritabanini gocuren betik odur.
# ============================================================
ACIK_BLOK_TIPLERI = ("news_list",)


# ============================================================
#  GORSELLER  (static/img/ -- projeyle gelen, panelden silinemez)
# ============================================================
GORSELLER = [
    {"path": "img/tmmt-bg.jpg", "alt": "TMMT fabrika arka planı"},
    {"path": "img/global-bg.jpg", "alt": "Global Toyota arka planı"},
    {"path": "img/tps-bg.jpg", "alt": "Toyota Production System arka planı"},
    {"path": "img/cevre-bg.jpg", "alt": "Toyota ve Çevre arka planı"},
]


# ============================================================
#  HARITA NOKTALARI  (static/js/toyota-map.js icindeki dizi)
# ============================================================
FABRIKALAR = [
    (35.0833, 137.1561, "Toyota City, Aichi", "Japonya",
     "Ana üretim kümesi: Honsha, Motomachi, Tsutsumi, Tahara ve daha fazlası"),
    (33.7660, 130.7690, "Miyawaka, Fukuoka", "Japonya",
     "Lexus ES / RX / NX / UX, motor"),
    (42.6337, 141.6044, "Tomakomai, Hokkaido", "Japonya",
     "Şanzıman ve aktarma organları"),
    (39.2306, 141.1464, "Kanegasaki, Iwate", "Japonya",
     "Yaris, Yaris Cross, Aqua"),
    (38.2098, -84.5588, "Georgetown, Kentucky", "ABD",
     "Camry, RAV4, motor"),
    (38.3559, -87.5661, "Princeton, Indiana", "ABD",
     "Highlander, Grand Highlander, Sienna"),
    (34.7304, -86.5861, "Huntsville, Alabama", "ABD",
     "Motor, Corolla Cross (Mazda ortak girişimi)"),
    (34.4078, -88.8945, "Blue Springs, Mississippi", "ABD",
     "Corolla"),
    (29.4241, -98.4936, "San Antonio, Teksas", "ABD",
     "Tundra, Sequoia"),
    (38.6151, -81.9887, "Buffalo, Batı Virginia", "ABD",
     "Motor, şanzıman"),
    (38.9792, -90.9807, "Troy, Missouri", "ABD",
     "Alüminyum silindir kapağı"),
    (35.8493, -79.5687, "Liberty, Kuzey Karolina", "ABD",
     "Batarya paketleri (2025)"),
    (43.36, -80.31, "Cambridge / Woodstock, Ontario", "Kanada",
     "RAV4, Lexus RX / NX"),
    (32.5149, -117.0382, "Tijuana, Baja California", "Meksika",
     "Tacoma kasası"),
    (20.5667, -100.6167, "Apaseo el Grande, Guanajuato", "Meksika",
     "Tacoma"),
    (-34.0967, -59.0272, "Zárate, Buenos Aires", "Arjantin",
     "Hilux, SW4 (Fortuner), HiAce"),
    (-23.5015, -47.4526, "Sorocaba, São Paulo", "Brezilya",
     "Corolla Cross, Yaris"),
    (-29.9633, 30.9581, "Prospecton, Durban", "Güney Afrika",
     "Corolla, Corolla Cross, Fortuner, Hilux"),
    (40.8613, -8.6291, "Ovar", "Portekiz",
     "Dyna, Land Cruiser, Toyota Sora otobüsü"),
    (52.8408, -1.6683, "Burnaston, Derbyshire", "Birleşik Krallık",
     "Corolla hatchback / estate"),
    (53.2205, -3.0505, "Deeside, Galler", "Birleşik Krallık",
     "Motor"),
    (50.3833, 3.5333, "Onnaing", "Fransa",
     "Yaris"),
    (50.0281, 15.1998, "Kolín", "Çekya",
     "Aygo X, Yaris"),
    (50.7716, 16.2845, "Wałbrzych", "Polonya",
     "Motor"),
    (39.3434, 117.3616, "Tianjin (FAW Toyota)", "Çin",
     "bZ3, Corolla, Crown Kluger"),
    (30.5728, 104.0668, "Chengdu (FAW Toyota)", "Çin",
     "Land Cruiser Prado, Coaster"),
    (43.8171, 125.3235, "Changchun (FAW Toyota)", "Çin",
     "RAV4"),
    (23.1291, 113.2644, "Guangzhou (GAC Toyota)", "Çin",
     "Camry, Highlander, bZ4X"),
    (12.7980, 77.3903, "Bidadi, Karnataka", "Hindistan",
     "Innova, Fortuner, Camry"),
    (24.8607, 67.0011, "Karaçi", "Pakistan",
     "Corolla Altis, Fortuner"),
    (24.9670, 121.2360, "Zhongli, Taoyuan", "Tayvan",
     "Corolla Altis, Yaris Cross"),
    (-6.3227, 107.3376, "Karawang, Batı Java", "Endonezya",
     "Fortuner, Innova, bZ4X"),
    (13.6904, 101.0770, "Chachoengsao", "Tayland",
     "Camry, Corolla, Yaris"),
    (21.2333, 105.7333, "Phúc Yên", "Vietnam",
     "Fortuner, Innova, Veloz"),
    (3.0738, 101.5183, "Shah Alam / Bukit Raja, Selangor", "Malezya",
     "Corolla Cross, Vios"),
    (14.3122, 121.0997, "Santa Rosa, Laguna", "Filipinler",
     "Vios, Innova, Hilux"),
]


def harita_ogeleri() -> list[dict]:
    """36 uretim tesisi + 1 one cikan TMMT noktasi + 2 gosterge satiri."""
    ogeler = [
        {
            "kind": "marker",
            "variant": "plant",
            "lat": lat,
            "lon": lon,
            "title": sehir,
            "subtitle": ulke,
            "text": urun,
        }
        for lat, lon, sehir, ulke, urun in FABRIKALAR
    ]
    # toyota-map.js'te bu nokta digerlerinden SONRA ekleniyor ve
    # popup'i acik basliyor. Popup icerigi de farkli (ulke satiri yok).
    ogeler.append(
        {
            "kind": "marker",
            "variant": "highlight",
            "lat": 40.6971,
            "lon": 30.3564,
            "title": "TMMT — Sakarya, Türkiye",
            "subtitle": None,
            "text": "C-HR, Corolla Sedan",
            "url": "/tmmt",
            "link_label": "Detaylı bilgi için tıkla →",
            "settings": {"open": True},
        }
    )
    ogeler.append({"kind": "legend", "variant": "red", "title": "Üretim tesisi"})
    ogeler.append({"kind": "legend", "variant": "gold", "title": "Türkiye (TMMT)"})
    return ogeler


# ============================================================
#  SAYFALAR
# ============================================================

# ============================================================
#  TMMT sayfasina sonradan eklenen bolumler
#
#  Ayri sabitler halinde: tools/tmmt_bolumleri.py (1. grup) ve
#  tools/tmmt_bolumleri2.py (2. grup) bunlari MEVCUT veritabanina da
#  ekleyebilsin diye. Tek dogruluk kaynagi burasi -- iki dosyada ayni
#  metnin iki kopyasi olmasin.
#
#  1. grup: BOLUM_YOLCULUK, BOLUM_KILOMETRE, BOLUM_PHEV
#  2. grup: BOLUM_VIZYON, BOLUM_KUNYE, BOLUM_IHRACAT, BOLUM_TOPLUM,
#           BOLUM_KARIYER, BOLUM_SERTIFIKA, BOLUM_HABERLER
# ============================================================

# --- 1) Fabrikada bir aracin yolculugu (adim adim) ---
BOLUM_YOLCULUK = {
    "type": "process_steps",
    # TPS sayfasinin en altindaki yonlendirme butonu buraya baglaniyor
    # (/tmmt#yolculuk). Capa silinirse o buton sayfanin basina duser.
    "anchor": "yolculuk",
    "heading": "Fabrikada bir aracın yolculuğu",
    "intro": "Bir aracın çelik rulodan yola çıkıp fabrikadan tamamlanmış "
             "olarak ayrılmasına kadar geçtiği altı durak. Bir adıma "
             "dokunarak o bölümde ne yapıldığını görebilirsiniz.",
    "items": [
        {"kind": "step", "eyebrow": "1", "title": "Pres Fabrikası",
         "text": "Çelik rulolar düz plakalara dönüştürülür ve pres hatlarında "
                 "aracın kaput, kapı, tavan gibi gövde panellerine şekillendirilir."},
        {"kind": "step", "eyebrow": "2", "title": "Kaynak Fabrikası",
         "text": "Preste şekillenen paneller, yüksek hassasiyetli robotlar ve "
                 "deneyimli ekiplerle birleştirilerek aracın gövdesi oluşturulur."},
        {"kind": "step", "eyebrow": "3", "title": "Boya Fabrikası",
         "text": "Gövde yalnızca renklendirilmez; korozyona karşı korunur ve ses "
                 "yalıtımı sağlanır. Çok katmanlı bir süreçtir."},
        {"kind": "step", "eyebrow": "4", "title": "Montaj Fabrikası",
         "text": "Boyalı gövde hatta girer; motor, iç döşeme, cam ve elektronik "
                 "parçalar \"tam zamanında\" prensibiyle istasyonlara ulaştırılarak "
                 "monte edilir."},
        {"kind": "step", "eyebrow": "5", "title": "Kalite",
         "text": "Temel prensip \"yerinde kalite\": hata tespit edildiği anda "
                 "çözülür, bir sonraki sürece asla geçmez."},
        {"kind": "step", "eyebrow": "6", "title": "Üretim Kontrol",
         "text": "Günlük üretim planının takibi ve binlerce parçanın "
                 "tedarikçilerden hatta kadar senkronizasyonu bu grup tarafından "
                 "yürütülür."},
    ],
}

# --- 2) Kilometre taslari (zaman tuneli) ---
#     Eskiden burada duz metin bir "Ihracat ve kilometre taslari" bolumu
#     vardi; o paragraf zaman tunelinin ustunde giris metni olarak duruyor.
BOLUM_KILOMETRE = {
    "type": "timeline",
    "heading": "İhracat ve kilometre taşları",
    # NOT (icerik): burada eskiden "30'dan fazla ulkeye" yaziyordu.
    # Sirketin kendi aciklamalarinda "150'den fazla ulke" geciyor;
    # iki rakam da dogrulanmadigi icin cumleden sayi cikarildi.
    # Ihracatin kapsamini anlatan cumle artik ihracat haritasinin
    # giris alaninda (BOLUM_IHRACAT["intro"]) ve panelden duzenlenebilir.
    "intro": "Üretimin büyük bölümü, ağırlıklı olarak Avrupa'ya, ayrıca Orta Doğu ve "
             "Afrika'ya ihraç ediliyor. Fabrika, 2021 "
             "yılında 3 milyonuncu aracını üretti ve Türkiye'nin en büyük ihracatçı "
             "sanayi kuruluşlarından biri.",
    "items": [
        {"kind": "stop", "slug": "1990", "eyebrow": "1990",
         "title": "Şirketin \"Toyotasa\" adıyla kuruluşu"},
        {"kind": "stop", "slug": "1994", "eyebrow": "1994",
         "title": "Corolla Sedan ile üretimin başlaması"},
        {"kind": "stop", "slug": "2016", "eyebrow": "2016",
         "title": "Toyota C-HR üretiminin başlaması"},
        {"kind": "stop", "slug": "2021", "eyebrow": "2021",
         "title": "3 milyonuncu aracın üretimi"},
        {"kind": "stop", "slug": "2023", "eyebrow": "2023",
         "title": "Yeni nesil C-HR ve Avrupa'daki ilk PHEV batarya hattı"},
        {"kind": "stop", "slug": "2024", "eyebrow": "2024",
         "title": "215.645 araç üretimi"},
    ],
}

# --- 3) PHEV Batarya Hatti (rakam izgarasi, split varyanti) ---
BOLUM_PHEV = {
    "type": "stat_grid",
    # Cevre sayfasindaki batarya akisinin baglantisi buraya geliyor
    # (/tmmt#phev). Capa silinirse o link sayfanin basina duser.
    "anchor": "phev",
    "heading": "PHEV Batarya Hattı",
    "intro": "Kasım 2023'ten bu yana TMMT, C-HR'ın şarj edilebilir hibrit (PHEV) "
             "versiyonunun bataryasını da üretiyor. Bu, Toyota'nın Avrupa'daki "
             "tesisleri arasında bir ilk: Sakarya fabrikası hem şarj edilebilir "
             "otomobil hem de bataryasını üreten ilk Toyota Avrupa fabrikası. "
             "Üretim, Toyota'nın TNGA-2 platformu üzerinde yapılıyor ve fabrika, "
             "Toyota'nın Avrupa'daki elektrifikasyon dönüşümünde merkezi bir rol "
             "üstleniyor.",
    "settings": {"variant": "split", "columns": "auto"},
    "items": [
        # NOT: Bu kartlarda sayac animasyonu YOK -- TMMT sayfasindaki
        # mevcut uc rakam karti da (280.000 / ~5.000-5.400 / 215.645)
        # animasyonsuz. Ayrica birimi sayac son ekine koymak dil sorunu
        # yaratirdi: `count_suffix` cevrilmeyen bir alan (%, +, km gibi
        # dilden bagimsiz olsun diye), o yuzden " milyon €" son eki
        # Ingilizce sayfada da Turkce kalirdi. Birim `value` icinde
        # duruyor ve `value` cevriliyor.
        {"kind": "stat", "value": "308 milyon €",
         "title": "Yeni nesil C-HR ve batarya hattı için yapılan ek yatırım"},
        {"kind": "stat", "value": "75.000",
         "title": "Yıllık batarya üretim kapasitesi (adet)"},
        {"kind": "stat", "value": "60",
         "title": "Hat için istihdam edilen ek uzman çalışan"},
    ],
}


# ============================================================
#  TMMT -- 2. grup bolumler
# ============================================================

# --- 4) Vizyon ve Misyon (iki kutu, buyuk punto) ---
#     Yeni bir kart tipi acilmadi: mevcut "rakam izgarasi"nin card
#     varyanti kullaniliyor. O varyantta `value` alani zaten buyuk
#     puntolu kirmizi display yazidir -- istenen "iki kisa kutu,
#     buyuk punto" gorunumu icin yeni CSS gerekmedi.
#
#     Ingilizce sloganlar `title` alaninda TURKCE KAYNAK olarak
#     duruyor. Otomatik ceviri bunlari bozmasin diye tmmt_bolumleri2.py
#     ayni metni ELLE ceviri olarak kilitliyor (bkz. SLOGAN_EN).
BOLUM_VIZYON = {
    "type": "stat_grid",
    "heading": "Vizyon ve Misyon",
    "settings": {"variant": "card", "columns": "2"},
    "items": [
        {"kind": "stat", "value": "Vizyon",
         "title": "Global Excellence in Manufacturing",
         "text": "Üretimde küresel mükemmellik."},
        {"kind": "stat", "value": "Misyon",
         "title": "Produce Admired Products with Premium Quality",
         "text": "Üstün kaliteyle beğeni toplayan ürünler üretmek."},
    ],
}

# Yukaridaki iki slogan Ingilizce sayfada AYNEN kalmali.
SLOGAN_EN = {
    "Global Excellence in Manufacturing": "Global Excellence in Manufacturing",
    "Produce Admired Products with Premium Quality":
        "Produce Admired Products with Premium Quality",
}

# Otomatik cevirmenin yanlis cevirdigi kisa metinler.
# ("Misir" hem ulke hem tahil; "Toplumla birlikte" tek basina baglamsiz
#  kaliyor ve "with society" gibi bozuk bir karsilik uretiyor.)
ELLE_EN = {
    "Mısır": "Egypt",
    "Çekya": "Czechia",
    "Hollanda": "Netherlands",
    "Toplumla birlikte": "Together with the community",
    # Toyota Way terimleri: Japonca/Ingilizce ozel terim, cevrilmez.
    "Continuous Improvement": "Continuous Improvement",
    "Respect for People": "Respect for People",
    # Sutun basliklari: Ingilizcesi terimin KENDISI olmali. Otomatik
    # ceviri "Respect for Humanity" gibi yakin ama yanlis bir karsilik
    # uretiyordu; boyle olunca alt baslikla da eslesmiyor ve sablon
    # ikisini birden basiyordu.
    "Sürekli İyileştirme": "Continuous Improvement",
    "İnsana Saygı": "Respect for People",
    # Tek kelimelik deger karsiliklari: baglamsiz cevrilemiyor.
    "Saygı": "Respect",
    "Yönetim": "Management",
    # --- TPS Evi ---
    # Tek kelimelik parca basliklari: baglamsiz cevrilemiyor.
    "Hedefler": "Goals",
    "Temel": "Foundation",
    # Terimin Turkce karsiligi Ingilizce'de gereksiz tekrar olurdu
    # ("Just-in-Time (just-in-time production)").
    "Just-in-Time (tam zamanında üretim)": "Just-in-Time",
    # Otomatik ceviri "autonomy" diyordu; dogru terim "autonomation".
    "Jidoka (otonomasyon)": "Jidoka (autonomation)",
    # Otomatik ceviri "·" ayraclarini dusuruyordu.
    "Otomatik durdurma · andon · poka-yoke · yerinde kalite":
        "Automatic stop · andon · poka-yoke · quality at the source",
    # --- Yedi israf ---
    # Tek kelimelik basliklar cevrilemiyor; ayrica bunlarin yalin
    # uretim yazinindaki YERLESIK Ingilizce karsiliklari var.
    "Bekleme": "Waiting",
    "Taşıma": "Transport",
    "Stok": "Inventory",
    # --- Cevre: dongusel ekonomi (4R) ---
    # Yerlesik Ingilizce terimler; otomatik ceviri kucuk harfe
    # dusuruyordu ("reduce", "recycle").
    "Redesign": "Redesign",
    "Reduce": "Reduce",
    "Reuse / Remanufacture": "Reuse / Remanufacture",
    "Recycle": "Recycle",
    # --- Cevre: TMMT'de cevre ---
    # Otomatik ceviri kucuk harfe dusuruyordu.
    "Atık azaltımı": "Waste reduction",
    # --- Cevre: teknoloji tablosu ve hibrit diyagram ---
    # Tek kelimelik hucre/baslik; baglamsiz cevrilemiyordu.
    "Yok.": "None.",
    "Hızlanma": "Acceleration",
    # --- TPS bugun nerede ---
    # Tek kelimelik kart basliklari; "Saglik" burada saglik SEKTORU.
    "Sağlık": "Healthcare",
    "Yazılım": "Software",
    # --- Kaizen dongusu ---
    # PDCA'nin yerlesik Ingilizce adlari; otomatik ceviri "Apply",
    # "Take Precautions" gibi yakin ama yanlis karsiliklar uretiyordu.
    "Planla": "Plan",
    "Uygula": "Do",
    "Kontrol Et": "Check",
    "Önlem Al": "Act",
    # --- TPS'in dogusu: donemler ---
    "1920'ler": "1920s",
    "1930'lar": "1930s",
    # Zaman tunelinde otomatik cevirinin bozdugu iki baslik.
    "Otomatik dokuma tezgâhı": "Automatic loom",
    "Toyota Motor Co. Ltd.'in kuruluşu": "Founding of Toyota Motor Co., Ltd.",
    "Challenge": "Challenge",
    "Kaizen": "Kaizen",
    "Genchi Genbutsu": "Genchi Genbutsu",
    "Respect": "Respect",
    "Teamwork": "Teamwork",
}

# Otomatik cevirinin ASLA uzerine yazmamasi gereken kaynak metinler ve
# Ingilizce karsiliklari. Bu satirlar is_manual=True yazilir -- panelde
# "elle duzenlendi" gorunur, yeniden uretilmez.
KILITLI_CEVIRI = {**SLOGAN_EN, **ELLE_EN}

# --- 5) Kurumsal bilgiler (kunye tablosu) ---
BOLUM_KUNYE = {
    "type": "fact_table",
    "heading": "Kurumsal bilgiler",
    "items": [
        {"kind": "fact", "title": "Konum",
         "text": "Arifiye / Sakarya, Türkiye"},
        {"kind": "fact", "title": "Kuruluş", "text": "1990"},
        {"kind": "fact", "title": "Üretimin başlangıcı", "text": "1994"},
        {"kind": "fact", "title": "Ortaklık yapısı",
         "text": "Toyota Motor Europe NV/SA (%90), Mitsui &amp; Co. Ltd. (%10)"},
        {"kind": "fact", "title": "Toplam yatırım",
         "text": "yaklaşık 2,5 milyar €"},
        {"kind": "fact", "title": "Yıllık üretim kapasitesi",
         "text": "280.000 araç"},
        {"kind": "fact", "title": "Çalışan sayısı",
         "text": "yaklaşık 5.000–5.400"},
        {"kind": "fact", "title": "Üretilen modeller",
         "text": "Toyota Corolla Sedan, Toyota C-HR (HEV / PHEV)"},
        # DOGRULANACAK: alan var, degeri bos. Degeri bos oldugu icin
        # satir sitede basilmaz; panelde durur, editor doldurunca cikar.
        {"kind": "fact", "title": "Arazi alanı / kapalı alan", "text": None},
    ],
}

# --- 6) Ihracat pazarlari haritasi ---
#     Global sayfasindaki Leaflet blogunun AYNISI, farkli veri kumesiyle.
#     Ikinci bir harita kutuphanesi yok: map.js sayfadaki her
#     .tk-map__canvas icin ayri harita kuruyor.
#
#     NOT (icerik): ihracat yapilan ulke sayisi kaynaklara gore
#     degisiyor (sayfada "30'dan fazla", sirket aciklamalarinda
#     "150'den fazla"). Bu yuzden asagidaki giris cumlesinde SAYI YOK;
#     cumle panelden duzenlenebilir bir alandir.
IHRACAT_PAZARLARI = [
    (52.5200, 13.4050, "Almanya", "Batı Avrupa",
     "Avrupa'nın en büyük otomobil pazarı."),
    (51.5074, -0.1278, "Birleşik Krallık", "Batı Avrupa",
     "Başlıca ihracat pazarlarından biri."),
    (48.8566, 2.3522, "Fransa", "Batı Avrupa",
     "Başlıca ihracat pazarlarından biri."),
    (50.8503, 4.3517, "Belçika", "Batı Avrupa",
     "Toyota Motor Europe'un merkezi Brüksel'de."),
    (52.3676, 4.9041, "Hollanda", "Batı Avrupa",
     "Başlıca ihracat pazarlarından biri."),
    (41.9028, 12.4964, "İtalya", "Güney Avrupa",
     "Başlıca ihracat pazarlarından biri."),
    (40.4168, -3.7038, "İspanya", "Güney Avrupa",
     "Başlıca ihracat pazarlarından biri."),
    (52.2297, 21.0122, "Polonya", "Orta Avrupa",
     "Başlıca ihracat pazarlarından biri."),
    (50.0755, 14.4378, "Çekya", "Orta Avrupa",
     "Başlıca ihracat pazarlarından biri."),
    (32.0853, 34.7818, "İsrail", "Orta Doğu",
     "Başlıca ihracat pazarlarından biri."),
    (25.2048, 55.2708, "Birleşik Arap Emirlikleri", "Orta Doğu",
     "Başlıca ihracat pazarlarından biri."),
    (24.7136, 46.6753, "Suudi Arabistan", "Orta Doğu",
     "Başlıca ihracat pazarlarından biri."),
    (30.0444, 31.2357, "Mısır", "Kuzey Afrika",
     "Başlıca ihracat pazarlarından biri."),
    (33.9716, -6.8498, "Fas", "Kuzey Afrika",
     "Başlıca ihracat pazarlarından biri."),
    (-25.7479, 28.2293, "Güney Afrika", "Güney Afrika",
     "Başlıca ihracat pazarlarından biri."),
]


def ihracat_ogeleri() -> list[dict]:
    """1 uretim tesisi + 15 ihracat pazari + 2 gosterge satiri."""
    ogeler = [
        {
            "kind": "marker",
            "variant": "highlight",
            "lat": 40.6971,
            "lon": 30.3564,
            "title": "TMMT — Arifiye, Sakarya",
            "text": "Corolla Sedan ve C-HR (HEV / PHEV) üretim tesisi",
            "settings": {"open": True},
        }
    ]
    ogeler += [
        {
            "kind": "marker",
            "variant": "plant",
            "lat": lat,
            "lon": lon,
            "title": ulke,
            "subtitle": bolge,
            "text": kisa_not,
        }
        for lat, lon, ulke, bolge, kisa_not in IHRACAT_PAZARLARI
    ]
    ogeler.append({"kind": "legend", "variant": "gold",
                   "title": "Üretim tesisi (Sakarya)"})
    ogeler.append({"kind": "legend", "variant": "red",
                   "title": "Başlıca ihracat pazarı"})
    return ogeler


BOLUM_IHRACAT = {
    "type": "map",
    "heading": "İhracat pazarları",
    "intro":
        "Arifiye'deki fabrikada üretilen araçların büyük bölümü yurt dışına "
        "gönderiliyor; başlıca pazarlar Avrupa ülkeleri ile Orta Doğu ve Kuzey "
        "Afrika. Haritada üretim tesisi ve başlıca ihracat pazarları işaretli — "
        "bir noktaya tıklayarak ülke adını ve kısa notu görebilirsin.",
    "settings": {
        "map_id": "tmmt-ihracat-haritasi",
        "center": [34, 18],
        "zoom": 3,
        "min_zoom": 2,
        "max_zoom": 8,
        "world_copy_jump": True,
        "tile": {
            "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "max_zoom": 18,
            "attribution": "&copy; OpenStreetMap katkıda bulunanlar",
        },
    },
    "items": ihracat_ogeleri(),
}

# --- 7) Toplumla birlikte (sosyal sorumluluk) ---
BOLUM_TOPLUM = {
    "type": "card_grid",
    "heading": "Toplumla birlikte",
    "intro": "TMMT'nin Sakarya ve çevresinde yıllardır sürdürdüğü sosyal "
             "sorumluluk çalışmalarından dördü.",
    "settings": {"variant": "plain", "columns": "4"},
    "items": [
        {"kind": "card", "title": "Trafik Güvenliği Resim Yarışması",
         "children": [{"kind": "paragraph", "text":
                       "Genç yeteneklerin trafik güvenliği bilincini görsel "
                       "sanatlarla ifade ettiği yarışma."}]},
        {"kind": "card", "title": "Teknik Proje Yarışması",
         "children": [{"kind": "paragraph", "text":
                       "Sakarya İl Millî Eğitim Müdürlüğü iş birliğiyle "
                       "ilköğretim ve lise öğrencileri arasında düzenlenen "
                       "proje yarışması."}]},
        {"kind": "card", "title": "“Önce Bağış Sonra Fabrika Turu”",
         "children": [{"kind": "paragraph", "text":
                       "Bağış yapan ziyaretçilere fabrika turu imkânı sunan "
                       "sosyal sorumluluk projesi."}]},
        {"kind": "card", "title": "Kan Bağışı Kampanyası",
         "children": [{"kind": "paragraph", "text":
                       "Kızılay'ın Güvenli Kan Temini Projesi kapsamında her "
                       "yıl tekrarlanan çalışan kan bağışı kampanyası."}]},
    ],
}

# --- 8) Kariyer ---
#     DOGRULANACAK: uc kartin hedef adresi BOS birakildi. Adres bos
#     oldugu surece kart baglantisiz basilir; panelden doldurulunca
#     kartin altinda baglanti belirir.
BOLUM_KARIYER = {
    "type": "card_grid",
    "heading": "Kariyer",
    "intro": "TMMT, üretimden mühendisliğe, kalite kontrolden lojistiğe kadar "
             "çok farklı alanda binlerce kişiye istihdam sağlıyor. Gerçek "
             "anlamda küresel bir şirkette çalışma ve gelişme imkânı sunuyor.",
    "settings": {"variant": "plain", "columns": "auto"},
    "items": [
        {"kind": "card", "title": "Toyota Türkiye'de Çalışmak",
         "url": None, "link_label": "Daha fazlası →",
         "children": [{"kind": "paragraph", "text":
                       "Üretim, mühendislik, kalite ve lojistik alanlarındaki "
                       "kariyer imkânları ve çalışan deneyimi."}]},
        {"kind": "card", "title": "Staj Programı",
         "url": None, "link_label": "Daha fazlası →",
         "children": [{"kind": "paragraph", "text":
                       "Üniversite öğrencilerine yönelik staj başvuruları ve "
                       "program takvimi."}]},
        {"kind": "card", "title": "Açık Pozisyonlar",
         "url": None, "link_label": "Daha fazlası →",
         "children": [{"kind": "paragraph", "text":
                       "Güncel iş ilanları ve başvuru adımları."}]},
    ],
}

# --- 9) Sertifikalar ve oduller (rozet seridi) ---
BOLUM_SERTIFIKA = {
    "type": "badge_strip",
    "heading": "Sertifikalar ve ödüller",
    "items": [
        {"kind": "badge", "slug": "iso-14001",
         "title": "ISO 14001 Çevre Yönetim Sistemi",
         "text": "1999'dan bu yana"},
        {"kind": "badge", "slug": "tim-ihracat",
         "title": "TİM İhracat Ödülü"},
        {"kind": "badge", "slug": "avrupa-hacim",
         "title": "Toyota Avrupa'nın en yüksek hacimli fabrikası"},
        {"kind": "badge", "slug": "lider-fabrika",
         "title": "Toyota iç değerlendirmesinde en üst “lider fabrika” seviyesi"},
        # DOGRULANACAK: rozet var ama BASLIGI BOS -- bu yuzden sitede
        # gorunmuyor. `slug` panelde ne oldugunu soyluyor; editor
        # dogrulayip basligi yazinca serit uzerinde belirir.
        {"kind": "badge", "slug": "iso-9001-iatf-16949", "title": None},
    ],
}

# --- 10) Haberler ve basin bultenleri ---
#     Bilerek BOS: bu bolum tamamen panelden yonetiliyor ve hic bulten
#     yokken sayfada HIC gorunmuyor. Alttaki "Tum bultenler" baglantisi
#     hazir duruyor, ilk bulten eklendiginde birlikte gorunur.
BOLUM_HABERLER = {
    "type": "news_list",
    "heading": "Haberler ve basın bültenleri",
    "settings": {"limit": 5},
    "items": [
        {"kind": "link", "title": "Tüm bültenler →",
         "url": "https://global.toyota/en/"},
    ],
}


# ------------------------------------------------------------
#  1) TMMT   (templates/tmmt.html)
# ------------------------------------------------------------
SAYFA_TMMT = {
    "slug": "tmmt",
    "url": "/tmmt",
    "is_home": True,
    "nav_order": 1,
    "theme": "tmmt",
    "reveal_default": False,
    "title": "TMMT — Toyota Motor Manufacturing Türkiye",
    "nav_label": "TMMT",
    "background": "img/tmmt-bg.jpg",
    "blocks": [
        {
            "type": "rich_text",
            "heading": "TMMT — Toyota Motor Manufacturing Türkiye",
            "heading_level": 1,
            "items": [
                {"kind": "paragraph", "text":
                 "TMMT (Toyota Motor Manufacturing Türkiye), 1990 yılında \"Toyotasa\" adıyla "
                 "kuruldu ve üretime 1994'te Corolla Sedan ile başladı. Fabrika, Sakarya'nın "
                 "Arifiye ilçesinde yer alıyor ve bugün Toyota'nın Avrupa'daki en önemli "
                 "üretim üslerinden biri konumunda."},
                {"kind": "paragraph", "text":
                 "Şirketin bugünkü ortaklık yapısı <strong>Toyota Motor Europe NV/SA (%90)</strong> "
                 "ve <strong>Mitsui &amp; Co. (%10)</strong> şeklinde."},
            ],
        },
        BOLUM_VIZYON,
        BOLUM_KUNYE,
        {
            "type": "stat_grid",
            "settings": {"variant": "card", "columns": "auto"},
            "items": [
                {"kind": "stat", "value": "280.000",
                 "title": "Yıllık üretim kapasitesi",
                 "text": "Bu kapasiteyle TMMT, Avrupa'daki en yüksek hacimli Toyota fabrikası."},
                {"kind": "stat", "value": "~5.000–5.400",
                 "title": "Çalışan",
                 "text": "Üretimden mühendisliğe pek çok farklı alanda istihdam."},
                {"kind": "stat", "value": "215.645",
                 "title": "2024 üretim adedi",
                 "text": "Fabrikanın 2024 yılında ürettiği toplam araç sayısı."},
            ],
        },
        {
            "type": "rich_text",
            "heading": "Üretilen modeller",
            "items": [
                {"kind": "paragraph", "text":
                 "TMMT bugün başlıca iki model ailesi üretiyor: <strong>Toyota Corolla Sedan</strong> "
                 "ve <strong>Toyota C-HR</strong> (klasik hibrit ve şarj edilebilir hibrit / PHEV "
                 "versiyonlarıyla). Kasım 2023'ten bu yana fabrika, C-HR PHEV'in bataryasını da "
                 "üretiyor; bu, Toyota'nın Avrupa'da PHEV bataryası üreten ilk fabrikası olması "
                 "anlamına geliyor."},
            ],
        },
        BOLUM_YOLCULUK,
        BOLUM_KILOMETRE,
        BOLUM_IHRACAT,
        BOLUM_PHEV,
        {
            "type": "rich_text",
            "heading": "Üretim yaklaşımı ve çevre",
            "items": [
                {"kind": "paragraph", "text":
                 "TMMT, kuruluşundan bu yana <strong>Toyota Production System (TPS)</strong> "
                 "ilkeleriyle çalışıyor. Fabrika 1999'dan beri ISO 14001 çevre yönetim sistemi "
                 "sertifikasına sahip ve enerji/su verimliliği ile atık azaltımına yönelik "
                 "sürekli iyileştirme (kaizen) projeleri yürütüyor."},
            ],
        },
        BOLUM_TOPLUM,
        BOLUM_KARIYER,
        BOLUM_SERTIFIKA,
        BOLUM_HABERLER,
        {
            "type": "source_list",
            "heading": "Kaynaklar",
            "items": [
                {"kind": "link", "variant": "external",
                 "title": "Wikipedia – Toyota Motor Manufacturing Türkiye",
                 "url": "https://en.wikipedia.org/wiki/Toyota_Motor_Manufacturing_T%C3%BCrkiye"},
                {"kind": "link", "variant": "external",
                 "title": "Grokipedia – Toyota Motor Manufacturing Turkey",
                 "url": "https://grokipedia.com/page/Toyota_Motor_Manufacturing_Turkey"},
                # Sablonda bu satir "global.toyota – {{ _('resmi haber duyuruları') }}"
                # seklindeydi: sabit on ek + cevrilen kisim. Tek alana birlestirildi;
                # Ingilizce karsiligi asagida elle olusturuluyor (bkz. EL_ILE_EN).
                {"kind": "link", "variant": "external",
                 "title": "global.toyota – resmi haber duyuruları",
                 "url": "https://global.toyota/en/"},
            ],
        },
    ],
}


# ============================================================
#  GLOBAL TOYOTA -- sonradan eklenen bolumler
#
#  TMMT'deki BOLUM_* sabitleriyle ayni mantik: icerigin tek
#  dogruluk kaynagi burasi, tools/global_bolumleri.py bunlari
#  MEVCUT veritabanina da ekleyebiliyor.
# ============================================================

# --- 1) Mobility for All (misyon bandi) ---
BOLUM_MOBILITY = {
    "type": "mission",
    "items": [
        {"kind": "statement", "text":
         "“Mobility for All” arayışıyla “Happiness for All” üretmek."},
        {"kind": "paragraph", "text":
         "Toyota'nın misyonu, herkes için erişilebilir hareketlilik sağlayarak "
         "herkes için mutluluk üretmek. Bu, yalnızca otomobil üretmek değil; "
         "insanların özgürce hareket edebildiği bir toplum kurmak anlamına "
         "geliyor."},
        {"kind": "paragraph", "text":
         "Şirket bugün kendini bir otomobil üreticisinden bir hareketlilik "
         "(mobility) şirketine dönüştürüyor. Bağlantılı, otonom, paylaşımlı ve "
         "elektrikli (CASE) teknolojiler bu dönüşümün merkezinde yer alıyor; "
         "hedefler Environmental Challenge 2050 ve Birleşmiş Milletler "
         "Sürdürülebilir Kalkınma Amaçları ile hizalı."},
    ],
}

# --- 2) Toyota'nin hikayesi (zaman tuneli) ---
#     Cevre ve TMMT sayfalarindaki `timeline` blogunun AYNISI; yeni bir
#     bilesen yazilmadi.
#
#     DOGRULANACAK: 1929 ve 1957 duraklarinin tarih ve ayrintilari
#     yayina almadan once dogrulanmali. Bu yuzden ikisinde de KESIN
#     RAKAM YOK (satis adedi, patent bedeli vb.); metinler panelden
#     duzenlenebilir.
#
#     2021 ve 2025 duraklari, sayfadaki "Toyota'nin Sosyal Yuzu"
#     bolumundeki Woven City kartiyla ayni bilgiyi tekrar ediyor
#     (acilis: 25 Eylul 2025, ilk "Weaver" sakinler). Celiski olmasin
#     diye referans o karttir.
BOLUM_HIKAYE = {
    "type": "timeline",
    "anchor": "hikaye",
    "heading": "Toyota'nın hikâyesi",
    "intro": "Bir dokuma tezgâhından küresel bir hareketlilik şirketine: "
             "Toyota'nın dönüm noktaları. Bir yıla dokunarak o adımın "
             "ayrıntısını görebilirsiniz.",
    "items": [
        {"kind": "stop", "slug": "1924", "eyebrow": "1924",
         "title": "Otomatik dokuma tezgâhı",
         "text": "Sakichi Toyoda'nın geliştirdiği tezgâh, iplik koptuğunda "
                 "kendi kendini durduruyordu. Bugünkü jidoka ilkesinin "
                 "kökeni bu makinedir."},
        {"kind": "stop", "slug": "1929", "eyebrow": "1929",
         "title": "Patentin Platt Brothers'a satılması",
         "text": "Dokuma tezgâhının patenti İngiliz Platt Brothers'a satıldı; "
                 "elde edilen gelir otomobil çalışmalarının sermayesi oldu."},
        {"kind": "stop", "slug": "1937", "eyebrow": "1937",
         "title": "Toyota Motor Co. Ltd.'in kuruluşu",
         "text": "Kiichiro Toyoda liderliğinde, dokuma tezgâhı işinden ayrılan "
                 "otomobil bölümü bağımsız bir şirkete dönüştü."},
        {"kind": "stop", "slug": "1957", "eyebrow": "1957",
         "title": "İlk denizaşırı adımlar",
         "text": "Toyota'nın ilk denizaşırı ihracat adımları atıldı ve ABD "
                 "pazarına giriş yapıldı."},
        {"kind": "stop", "slug": "1966", "eyebrow": "1966",
         "title": "Corolla'nın tanıtımı",
         "text": "Dünyanın en çok satan otomobil ailesinin başlangıcı."},
        {"kind": "stop", "slug": "1997", "eyebrow": "1997",
         "title": "Prius",
         "text": "Dünyanın ilk seri üretim hibrit otomobili."},
        {"kind": "stop", "slug": "2014", "eyebrow": "2014",
         "title": "Mirai",
         "text": "Hidrojen yakıt hücreli seri üretim otomobil."},
        {"kind": "stop", "slug": "2021", "eyebrow": "2021",
         "title": "Woven City'nin temelinin atılması",
         "text": "Fuji Dağı eteğinde inşa edilen deneysel “yaşayan "
                 "laboratuvar” şehrin temeli atıldı."},
        {"kind": "stop", "slug": "2025", "eyebrow": "2025",
         "title": "Woven City'nin açılışı",
         "text": "25 Eylül 2025'te resmen açıldı; ilk “Weaver” sakinler "
                 "taşınmaya başladı."},
    ],
}

# --- 3) Toyota Way: iki sutun, bes deger ---
#     Sutun ve deger basliklarinin Ingilizce/Japonca terimleri
#     cevrilmemeli; KILITLI_CEVIRI listesinde duruyorlar. Sablon,
#     alt basligi baslikla ayni cikarsa basmiyor -- Ingilizce sayfada
#     "Challenge / Challenge" gibi tekrarlar boyle onleniyor.
BOLUM_TOYOTA_WAY = {
    "type": "value_columns",
    "anchor": "toyota-way",
    "heading": "Toyota Way: iki sütun, beş değer",
    "intro": "Toyota'nın çalışma kültürü iki sütun üzerine kurulu; bu "
             "sütunların altında şirketin her kademesinde tekrarlanan beş "
             "temel değer var.",
    "items": [
        {"kind": "column", "title": "Sürekli İyileştirme",
         "subtitle": "Continuous Improvement", "children": [
             {"kind": "value", "title": "Challenge", "subtitle": "Meydan okuma",
              "text": "Uzun vadeli bir vizyon kurmak ve hedeflere cesaret ve "
                      "yaratıcılıkla ilerlemek."},
             {"kind": "value", "title": "Kaizen",
              "subtitle": "Sürekli iyileştirme",
              "text": "Hiçbir sürecin mükemmel olmadığını kabul edip her gün "
                      "küçük adımlarla ilerlemek."},
             {"kind": "value", "title": "Genchi Genbutsu",
              "subtitle": "Yerinde gör",
              "text": "Karar vermeden önce sorunun yaşandığı yere gidip "
                      "gerçeği kendi gözünle görmek."},
         ]},
        {"kind": "column", "title": "İnsana Saygı",
         "subtitle": "Respect for People", "children": [
             {"kind": "value", "title": "Respect", "subtitle": "Saygı",
              "text": "Paydaşlara saygı duymak, sorumluluk almak, karşılıklı "
                      "güven inşa etmek."},
             {"kind": "value", "title": "Teamwork",
              "subtitle": "Takım çalışması",
              "text": "Bireysel gelişimi teşvik ederek ekip performansını en "
                      "üst düzeye çıkarmak."},
         ]},
        {"kind": "link",
         "title": "Bu ilkelerin üretim hattındaki karşılığı: "
                  "Toyota Production System",
         "url": "/uretim-sistemi"},
    ],
}


# --- 4) Bolum menusu (sayfa ici hizli gecis) ---
#     Icerigi yok: sayfadaki `anchor` alani dolu bloklardan uretiliyor.
BOLUM_MENU = {
    "type": "section_nav",
    "heading": "Bu sayfada",
    "items": [],
}

# --- 5) Platform ve teknoloji (iki buyuk kart) ---
BOLUM_PLATFORM = {
    "type": "card_grid",
    "anchor": "platform",
    "heading": "Platform ve teknoloji",
    "settings": {"variant": "plain", "columns": "2"},
    "items": [
        {"kind": "card", "title": "TNGA",
         "subtitle": "Toyota New Global Architecture",
         "url": "/tmmt", "link_label": "TMMT'de TNGA-2 üretimi →",
         "children": [
             {"kind": "paragraph", "text":
              "Toyota'nın küresel araç platformu. Ortak bir mimari üzerinden "
              "farklı segmentlerde araç geliştirmeyi mümkün kılıyor; daha "
              "düşük ağırlık merkezi, daha iyi sürüş dinamiği ve daha verimli "
              "üretim sağlıyor. TMMT'de üretilen yeni nesil C-HR de bu "
              "platformun TNGA-2 versiyonu üzerinde üretiliyor."},
         ]},
        {"kind": "card", "title": "Toyota Safety Sense",
         "children": [
             {"kind": "paragraph", "text":
              "Toyota'nın standart olarak sunduğu sürücü destek ve aktif "
              "güvenlik teknolojileri paketi. Şirketin uzun vadeli hedefi "
              "trafikte sıfır kaza; teknolojiler bu hedefe yönelik olarak "
              "sürekli geliştiriliyor."},
         ]},
    ],
}

# --- 6) Ar-Ge ve tasarim (giris + 5 kart, masaustunde 3'lu) ---
#
#     DOGRULANACAK: merkezlerin GUNCEL adi ve konumu yayina almadan once
#     dogrulanmali -- bazilari son yillarda yeniden adlandirildi. Kart
#     icerigi kodda sabit degil: her alan panelden duzenlenebiliyor,
#     bu sozluk yalnizca ilk doldurma icin.
#
#     `columns: auto` masaustunde 3 kolon veriyor (sayfa kabi 980px,
#     kart alt siniri 240px), dar ekranda tek kolona duyuyor. Yeni bir
#     izgara kurali gerekmedi.
BOLUM_ARGE = {
    "type": "card_grid",
    "anchor": "ar-ge",
    "heading": "Ar-Ge ve tasarım",
    "intro": "Toyota'nın araştırma ve tasarım faaliyetleri Japonya ile sınırlı "
             "değil; Avrupa, Kuzey Amerika ve Asya'ya yayılmış merkezlerde "
             "yürütülüyor.",
    "settings": {"variant": "plain", "columns": "auto"},
    "items": [
        {"kind": "card", "title": "Toyota Motor Europe Ar-Ge Merkezi",
         "subtitle": "Zaventem, Belçika", "children": [
             {"kind": "paragraph", "text":
              "Avrupa pazarına yönelik araç geliştirme ve mühendislik."}]},
        {"kind": "card", "title": "ED² (Toyota Europe Design Development)",
         "subtitle": "Nice, Fransa", "children": [
             {"kind": "paragraph", "text":
              "Avrupa'ya yönelik ileri tasarım stüdyosu."}]},
        {"kind": "card", "title": "Toyota Gazoo Racing Europe",
         "subtitle": "Köln, Almanya", "children": [
             {"kind": "paragraph", "text":
              "Motorsporları geliştirme ve yüksek performans mühendisliği."}]},
        {"kind": "card", "title": "Toyota Research Institute",
         "subtitle": "Kaliforniya, ABD", "children": [
             {"kind": "paragraph", "text":
              "Yapay zekâ, otonom sürüş ve robotik araştırmaları."}]},
        {"kind": "card", "title": "Woven by Toyota",
         "subtitle": "Tokyo, Japonya", "children": [
             {"kind": "paragraph", "text":
              "Yazılım tanımlı araç ve Woven City projesi."}]},
    ],
}

# --- 7) Avrupa'da Toyota (metin + 3 rakam kutusu + TMMT baglantisi) ---
#
#     DOGRULANACAK: UC RAKAMIN DA DEGERI BILEREK BOS. Rakami bos olan
#     kutu sitede basilmiyor (bkz. blocks/stat_grid.html), yani bolum
#     dogrulanana kadar metin + baglanti olarak gorunuyor. Etiketler
#     panelde duruyor; editor rakami girince kutu kendiliginden cikiyor.
BOLUM_AVRUPA = {
    "type": "stat_grid",
    "anchor": "avrupa",
    "heading": "Avrupa'da Toyota",
    "intro": "Toyota'nın Avrupa operasyonları, merkezi Brüksel'de bulunan "
             "Toyota Motor Europe tarafından yürütülüyor. Şirketin Avrupa "
             "genelinde birden fazla üretim tesisi, Ar-Ge ve tasarım merkezi "
             "bulunuyor. Sakarya'daki TMMT, bu yapının en yüksek hacimli "
             "üretim tesislerinden biri ve Toyota'nın Avrupa'daki "
             "elektrifikasyon dönüşümünde merkezi bir rol üstleniyor.",
    "settings": {
        "variant": "card",
        "columns": "auto",
        "panel_note": "Üç rakam da DOĞRULANMADI, bu yüzden boş bırakıldı ve "
                      "kutular sitede görünmüyor. Yayından önce "
                      "global.toyota / Toyota Motor Europe basın "
                      "sayfalarından doğrulayıp gir.",
    },
    "items": [
        {"kind": "stat", "value": None,
         "title": "Avrupa'daki üretim tesisi sayısı"},
        {"kind": "stat", "value": None,
         "title": "Toyota Motor Europe'un faaliyet gösterdiği ülke sayısı"},
        {"kind": "stat", "value": None,
         "title": "Avrupa'daki çalışan sayısı"},
        {"kind": "link", "title": "Türkiye'deki fabrikamız: TMMT →",
         "url": "/tmmt"},
    ],
}

# --- 8) Yonetim (iki bos profil karti) ---
#
#     DOGRULANACAK: YONETICI ISIMLERI BILEREK KODA YAZILMADI -- unvanlar
#     ve kisiler sik degisiyor. Iki kart basligi bos olarak olusturuluyor;
#     basligi bos kart basilmadigi ve hicbir kart kalmayinca blok
#     tamamen gizlendigi icin bolum, editor doldurana kadar sitede HIC
#     GORUNMUYOR. Panel notu ne yapilmasi gerektigini soyluyor.
BOLUM_YONETIM = {
    "type": "card_grid",
    "anchor": "yonetim",
    "heading": "Yönetim",
    "settings": {
        "variant": "plain",
        "columns": "2",
        "panel_note": "Yönetici adları bilerek boş bırakıldı; unvanlar ve "
                      "kişiler sık değişiyor. Yayından önce global.toyota "
                      "üzerinden doğrulayıp doldurun. Kart başlığı boş "
                      "kaldığı sürece bu bölüm sitede hiç görünmez.",
    },
    "items": [
        {"kind": "card", "title": None, "subtitle": "Yönetim Kurulu Başkanı"},
        {"kind": "card", "title": None, "subtitle": "Başkan ve CEO"},
    ],
}


# ------------------------------------------------------------
#  2) GLOBAL TOYOTA   (templates/global_toyota.html)
# ------------------------------------------------------------
SAYFA_GLOBAL = {
    "slug": "global-toyota",
    "url": "/global-toyota",
    "is_home": False,
    "nav_order": 2,
    "theme": "global",
    "reveal_default": True,
    "title": "Global Toyota",
    "nav_label": "Global Toyota",
    "background": "img/global-bg.jpg",
    "blocks": [
        {
            "type": "hero",
            "heading": "Global Toyota",
            "heading_level": 1,
            "intro":
                "1937'de Japonya'da, Sakichi Toyoda'nın otomatik dokuma tezgahı patentinden "
                "elde ettiği gelirle Kiichiro Toyoda tarafından kurulan Toyota, bugün "
                "dünyanın en büyük otomotiv üreticilerinden biri. Merkezi hâlâ Japonya'daki "
                "Toyota City'de bulunuyor, ama üretim ve satış ağı altı kıtaya yayılmış "
                "durumda.",
            "items": [],
        },
        BOLUM_MENU,
        BOLUM_MOBILITY,
        {
            "type": "stat_badge",
            "items": [
                {"kind": "stat", "value": "300.000.000+",
                 "count_to": 300000000, "count_suffix": "+", "count_group": True,
                 "title": "1935'ten bu yana üretilen toplam araç",
                 "text": "Bu kilometre taşına Kasım 2023'te ulaşıldı."},
            ],
        },
        {
            "type": "stat_grid",
            "settings": {"variant": "card", "columns": "auto"},
            "items": [
                {"kind": "stat", "value": "~390.000",
                 "count_to": 390000, "count_prefix": "~", "count_group": True,
                 "title": "Çalışan",
                 "text": "Dünya genelinde, üretimden mühendisliğe pek çok farklı alanda."},
                {"kind": "stat", "value": "170+",
                 "count_to": 170, "count_suffix": "+",
                 "title": "Ülke ve bölge",
                 "text": "Toyota araçlarının satıldığı pazar sayısı."},
                {"kind": "stat", "value": "70+",
                 "count_to": 70, "count_suffix": "+",
                 "title": "Üretim şirketi",
                 "text": "Japonya dışında da onlarca ülkede kurulu fabrika ve iştirak."},
            ],
        },
        BOLUM_HIKAYE,
        BOLUM_TOYOTA_WAY,
        {
            "type": "rich_text",
            "anchor": "elektrikli",
            "heading": "Elektrikli Araç ve Rekabet Ortamı",
            "items": [
                {"kind": "paragraph", "text":
                 "2025'te Toyota'nın sattığı araçların yaklaşık 200 bini tam elektrikliydi — "
                 "bir önceki yıla göre yüzde 42'lik bir artış. Yine de şirket, elektrikli "
                 "araçlara topyekûn geçmek yerine hibrit, şarj edilebilir hibrit, tam "
                 "elektrikli ve hidrojen yakıt hücreli araçları bir arada geliştiren \"çoklu "
                 "yol\" stratejisine bağlı kalıyor. Bu arada BYD, SAIC ve Geely gibi Çinli "
                 "üreticilerin özellikle elektrikli araç segmentinde hızla büyümesi, "
                 "Toyota'nın önümüzdeki yıllarda karşılaşacağı en büyük rekabet "
                 "baskılarından biri olarak görülüyor."},
            ],
        },
        {
            "type": "map",
            "anchor": "harita",
            "heading": "Üretim Tesisleri Haritası",
            "intro":
                "Toyota'nın araçlarını sattığı 170'ten fazla ülke ile araçlarını "
                "<strong>ürettiği</strong> yerler aynı şey değil. Aşağıdaki harita, altı "
                "kıtaya yayılmış başlıca üretim ve montaj tesislerini gösteriyor — "
                "fareyle sürükleyerek gezebilir, tekerlekle yakınlaştırabilir, bir "
                "noktaya tıklayarak o tesis hakkında bilgi görebilirsin.",
            "settings": {
                "map_id": "toyota-map",
                "center": [20, 20],
                "zoom": 2,
                "min_zoom": 2,
                "max_zoom": 8,
                "world_copy_jump": True,
                "tile": {
                    "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    "max_zoom": 18,
                    # Leaflet bunu HTML olarak basar; &copy; bilerek boyle.
                    "attribution": "&copy; OpenStreetMap katkıda bulunanlar",
                },
            },
            "items": harita_ogeleri(),
        },
        BOLUM_AVRUPA,
        {
            "type": "card_grid",
            "anchor": "oduller",
            "heading": "Ödüller, Marka Değeri ve Kalite Sıralamaları",
            "intro":
                "Bağımsız kuruluşların 2025-2026 değerlendirmelerinde Toyota, hem marka "
                "değeri hem de güvenilirlik tarafında otomotiv sektörünün önünde yer aldı.",
            "note": "Kaynak: Interbrand, Brand Finance, J.D. Power, motor1.com, carexpert.com.au",
            "settings": {"variant": "award", "columns": "auto"},
            "items": [
                {"kind": "card", "eyebrow": "2025", "title": "Interbrand",
                 "children": [{"kind": "paragraph", "text":
                               "Otomotivde kesintisiz 1. sıra; marka değeri 74,2 milyar dolar."}]},
                {"kind": "card", "eyebrow": "2025–2026", "title": "Brand Finance",
                 "children": [{"kind": "paragraph", "text":
                               "Üst üste 2 yıl dünyanın en değerli ve en güçlü otomobil markası (AAA+)."}]},
                {"kind": "card", "eyebrow": "2023–2026", "title": "J.D. Power — Lexus",
                 "children": [{"kind": "paragraph", "text":
                               "Lexus, 4 yıl üst üste en güvenilir marka seçildi."}]},
                {"kind": "card", "eyebrow": "2023–2026", "title": "J.D. Power — Toyota",
                 "children": [{"kind": "paragraph", "text":
                               "En çok segment ödülünü alan üretici (6–9 model)."}]},
                {"kind": "card", "eyebrow": "2025", "title": "En Çok Satan Grup",
                 "children": [{"kind": "paragraph", "text":
                               "11,3 milyon araçla üst üste 6. kez dünyanın 1.'si."}]},
            ],
        },
        {
            "type": "chip_groups",
            "anchor": "marka-ailesi",
            "heading": "Toyota Grubu Marka Ailesi",
            "intro":
                "Toyota yalnızca kendi markasından ibaret değil; tamamına sahip olduğu "
                "markaların yanında birkaç rakibinde de stratejik hisseler tutuyor.",
            "note": "Kaynaklar: toyotaautodealer.com, slashgear.com",
            "items": [
                {"kind": "chip_group", "title": "Tamamı Toyota'ya ait", "children": [
                    {"kind": "chip", "title": "Lexus"},
                    {"kind": "chip", "title": "Daihatsu"},
                    {"kind": "chip", "title": "Hino Motors"},
                ]},
                {"kind": "chip_group", "title": "Stratejik hisseler", "children": [
                    {"kind": "chip", "title": "Subaru", "note": "yüzde 20 · oy hakkıyla"},
                    {"kind": "chip", "title": "Suzuki", "note": "~%4,9"},
                    {"kind": "chip", "title": "Mazda", "note": "~%5,1"},
                ]},
                # Ucuncu kutu: gorunumu ilk ikisiyle birebir ayni (ayni
                # cip stili). `note` alani markanin kisa aciklamasini
                # tasiyor -- mevcut kutulardaki kirmizi yazinin ta kendisi.
                {"kind": "chip_group", "title": "Markalar ve hizmetler", "children": [
                    {"kind": "chip", "title": "Toyota",
                     "note": "Ana marka; binek ve ticari araç ailesi"},
                    {"kind": "chip", "title": "Toyota Professional",
                     "note": "Avrupa'da ticari araç ve filo müşterilerine yönelik marka"},
                    {"kind": "chip", "title": "Toyota Gazoo Racing",
                     "note": "Motorsporları ve performans araçları markası"},
                    {"kind": "chip", "title": "KINTO",
                     "note": "Abonelik, kiralama ve paylaşımlı mobilite hizmetleri markası"},
                    {"kind": "chip", "title": "Woven by Toyota",
                     "note": "Yazılım, otonom sürüş ve Woven City projesini yürüten iştirak"},
                ]},
                {"kind": "outro", "text":
                 "Mazda ortaklığı, ABD Alabama'daki Mazda Toyota Manufacturing tesisinin "
                 "temelini oluşturuyor."},
                {"kind": "outro", "variant": "muted", "text":
                 "Hino Motors'un önümüzdeki dönemde Mitsubishi Fuso ile yeni bir ittifaka "
                 "dahil olacağı duyuruldu — grubun yapısının hâlâ hareketli olduğunu "
                 "gösteren güncel bir detay."},
            ],
        },
        BOLUM_PLATFORM,
        BOLUM_ARGE,
        {
            "type": "stat_grid",
            "anchor": "hidrojen",
            "heading": "Hidrojen ve Katı Hal Batarya Teknolojisi",
            "intro":
                "Toyota'nın \"çoklu yol\" stratejisi bataryalı elektrikle sınırlı değil; "
                "hidrojen ve yeni nesil batarya kimyaları da paralel olarak geliştiriliyor.",
            "settings": {"variant": "card", "columns": "2"},
            "items": [
                {"kind": "stat", "value": "~647 km",
                 "count_to": 647, "count_prefix": "~", "count_suffix": " km",
                 "title": "Mirai — Hidrojen yakıt hücresi",
                 "text": "182 beygir güç ve ABD EPA testine göre yaklaşık 647 km (402 mil) "
                         "menzil. Egzozdan çıkan tek atık su.",
                 "note": "Kaynak: pressroom.toyota.com"},
                {"kind": "stat", "value": "~1.200 km",
                 "count_to": 1200, "count_prefix": "~", "count_suffix": " km",
                 "count_group": True,
                 "title": "Katı hal bataryalar",
                 "text": "Sumitomo Metal Mining ve Idemitsu ortaklığıyla geliştiriliyor; "
                         "2027-2028'de araçlara girmesi hedefleniyor. Prototip paket yaklaşık "
                         "1.200 km menzil ve 10 dakikanın altında hızlı şarj vadediyor.",
                 "note": "Kaynak: electrek.co"},
            ],
        },
        {
            "type": "card_grid",
            "anchor": "sosyal",
            "heading": "Toyota'nın Sosyal Yüzü",
            "settings": {"variant": "plain", "columns": "2"},
            "items": [
                {"kind": "card", "title": "Woven City",
                 "note": "Kaynaklar: global.toyota, pressroom.toyota.com",
                 "children": [
                     {"kind": "bullet", "text":
                      "Fuji Dağı eteğinde inşa edilen deneysel \"yaşayan laboratuvar\" şehir."},
                     {"kind": "bullet", "text":
                      "25 Eylül 2025'te resmen açıldı; ilk \"Weaver\" sakinler taşınmaya başladı."},
                     {"kind": "bullet", "text":
                      "Faz 1'de yaklaşık 300 kişilik bir nüfus hedefleniyor."},
                     {"kind": "bullet", "text":
                      "Japonya'nın ilk LEED for Communities Platin sertifikasını aldı."},
                 ]},
                {"kind": "card", "title": "Motorsporları — Toyota Gazoo Racing",
                 "note": "Kaynak: media.toyota.ca",
                 "children": [
                     {"kind": "bullet", "text":
                      "Haziran 2026: 94. Le Mans 24 Saat'te 6. kez zafer; 3 yıllık kazanamama "
                      "serisi sona erdi (350.105 seyirci)."},
                     {"kind": "bullet", "text":
                      "Dünya Rallye Şampiyonası'nda üst üste 4. üretici şampiyonluğu."},
                 ]},
            ],
        },
        BOLUM_YONETIM,
    ],
}


# ============================================================
#  TPS SAYFASI -- sonradan eklenen bolumler
#
#  JAPONCA TERIM KURALI: bir terim SAYFADA ILK GECTIGI yerde
#  Turkce karsiligiyla verilir ("Jidoka (otonomasyon)"), sonraki
#  kullanimlarda sade birakilir. Sayfa sirasi:
#    giris (muda) -> TPS Evi (jidoka, just-in-time, kanban, andon,
#    poka-yoke, heijunka, kaizen) -> dogus -> iki sutun -> yedi israf
#  Bu yuzden ilk tanimlar TPS Evi'nin icinde.
# ============================================================

# --- 1) TPS Evi (SVG diyagram) ---
#     Semanin yapisi sablonda sabit; buradaki metinler kutularin
#     icini ve tiklaninca acilan aciklamalari besliyor.
#     `slug` hangi kutuya oturacagini belirler.
BOLUM_TPS_EVI = {
    "type": "tps_house",
    "anchor": "tps-evi",
    "heading": "TPS Evi",
    "intro": "TPS'i anlatmanın en bilinen yolu bir eve benzetmektir: çatı "
             "hedefleri, iki sütun sistemi taşıyan ilkeleri, temel ise "
             "hepsini mümkün kılan istikrarı gösterir. Bir parçaya "
             "dokunarak ayrıntısını görebilirsiniz.",
    "items": [
        # Diyagramin YAZILI KARSILIGI: ekranda gorunmez, ekran okuyucu
        # okur. `settings` yerine oge olarak duruyor cunku cevrilmesi
        # gerekiyor (bkz. block_types.py'deki not).
        {"kind": "paragraph", "text":
         "Ev şeklinde bir şema. En üstteki çatıda hedefler yer alır. Çatıyı "
         "iki sütun taşır: solda Just-in-Time, sağda Jidoka. İki sütunun "
         "arasında, evin merkezinde insan ve takım çalışması bulunur. "
         "Hepsinin altında, evi ayakta tutan temel vardır. Aşağıdaki "
         "listeden her parçanın açıklamasını açabilirsiniz."},
        {"kind": "part", "slug": "roof", "title": "Hedefler",
         "subtitle": "En yüksek kalite · en düşük maliyet · en kısa teslim "
                     "süresi · en yüksek güvenlik · en yüksek çalışan morali",
         "text": "Evin çatısı, tüm sistemin neye hizmet ettiğini söyler. "
                 "Bu beş hedef birbirinden bağımsız değildir: kaliteyi "
                 "yükselten bir iyileştirme genellikle maliyeti de düşürür, "
                 "güvenli ve düzenli bir hat ise çalışan moralini yükseltir."},
        {"kind": "part", "slug": "pillar_left",
         "title": "Just-in-Time (tam zamanında üretim)",
         "subtitle": "Sürekli akış · çekme sistemi · takt zamanı · kanban",
         "text": "Doğru parçanın, doğru anda, doğru miktarda hatta ulaşması. "
                 "Üretimi başlatan şey tahmin değil, bir sonraki sürecin "
                 "gerçek talebidir — buna çekme sistemi denir. Takt zamanı "
                 "müşteri talebinin belirlediği üretim temposudur; kanban "
                 "(çekme kartı) ise hangi parçadan ne zaman ne kadar "
                 "gerektiğini hat üzerinde görünür kılar."},
        {"kind": "part", "slug": "center",
         "title": "İnsan ve takım çalışması",
         "subtitle": "Sürekli iyileştirme · israfın ortadan kaldırılması",
         "text": "İki sütunun arasındaki boşluk boş değildir: sistemi "
                 "çalıştıran insandır. Sorunu gören, durduran ve çözen "
                 "kişi hattın başındaki çalışandır. Sürekli iyileştirme "
                 "ve israfın ortadan kaldırılması bir departmanın işi "
                 "değil, her kademedeki takımın ortak sorumluluğudur."},
        {"kind": "part", "slug": "pillar_right",
         "title": "Jidoka (otonomasyon)",
         "subtitle": "Otomatik durdurma · andon · poka-yoke · yerinde kalite",
         "text": "\"İnsan dokunuşlu otomasyon\": makine bir sorun sezdiğinde "
                 "kendi kendine durur, böylece hatalı ürün bir sonraki "
                 "sürece geçmez. Andon (uyarı panosu) sorunu anında görünür "
                 "kılar; poka-yoke (hata önleme) yanlış işlemi baştan "
                 "imkânsız hale getiren basit düzeneklerdir. Kalite en "
                 "sonda denetlenmez, oluştuğu yerde sağlanır."},
        {"kind": "part", "slug": "foundation", "title": "Temel",
         "subtitle": "Heijunka · standart iş · kaizen · görsel yönetim · "
                     "istikrarlı süreçler",
         "text": "Sütunlar ancak sağlam bir zemin üzerinde durur. Heijunka "
                 "(üretim dengeleme) iş yükünü zamana ve ürün çeşidine "
                 "yayar; standart iş her işin bilinen en iyi yolunu "
                 "tanımlar; kaizen (sürekli iyileştirme) o standardı her "
                 "gün biraz daha ileri taşır; görsel yönetim ise hattın "
                 "durumunu bakışta anlaşılır kılar."},
    ],
}

# --- 2) TPS nasil dogdu (uc adimli anlati) ---
#     TMMT'deki "Fabrikada bir aracin yolculugu" ile AYNI bilesen
#     (process_steps): genis ekranda tek sira, dar ekranda akordeon.
BOLUM_TPS_DOGUS = {
    "type": "process_steps",
    "anchor": "dogus",
    "heading": "TPS nasıl doğdu",
    "intro": "Sistem bir günde tasarlanmadı; üç kuşağın birbirini "
             "tamamlayan fikirlerinden oluştu. Bir adıma dokunarak "
             "ayrıntısını görebilirsiniz.",
    "items": [
        {"kind": "step", "eyebrow": "1", "slug": "sakichi",
         "title": "Sakichi Toyoda ve dokuma tezgâhı",
         "subtitle": "1920'ler",
         "text": "Sakichi Toyoda, ipliği koptuğunda kendi kendini durduran "
                 "bir otomatik dokuma tezgâhı geliştirdi. Böylece bir "
                 "işçinin tek bir tezgâhın başında beklemesi gerekmiyor, "
                 "hatalı kumaş üretilmiyordu. Bu fikir, bugün jidoka olarak "
                 "bilinen \"insan dokunuşlu otomasyon\" ilkesinin kökeni "
                 "oldu."},
        {"kind": "step", "eyebrow": "2", "slug": "kiichiro",
         "title": "Kiichiro Toyoda ve tam zamanında üretim",
         "subtitle": "1930'lar",
         "text": "Sakichi'nin oğlu Kiichiro Toyoda, otomobil üretimine "
                 "geçerken her parçanın tam gerektiği anda ve tam gerektiği "
                 "miktarda hatta ulaşması gerektiğini savundu. "
                 "\"Just-in-Time\" kavramı bu yaklaşımdan doğdu."},
        {"kind": "step", "eyebrow": "3", "slug": "ohno",
         "title": "Taiichi Ohno ve sistemin kurulması",
         "subtitle": "1945 sonrası",
         "text": "İkinci Dünya Savaşı sonrasında Taiichi Ohno, bu iki fikri "
                 "tutarlı bir üretim sistemine dönüştürdü. Amerikan "
                 "süpermarketlerinde rafın yalnızca satılan kadar "
                 "doldurulmasından esinlenerek çekme sistemini ve kanban'ı "
                 "geliştirdi. Kaynakların kıt olduğu bir dönemde israfı "
                 "ortadan kaldırmak zorunluluktu; bu zorunluluk bir yönetim "
                 "felsefesine dönüştü."},
    ],
}

# --- 3) Yedi israf (muda) ---
#     Mevcut JIT/Jidoka kartlariyla AYNI stil: `station` varyanti,
#     numarali kirmizi rozet. `columns: 4` masaustunde 4, tablette 2,
#     telefonda 1 kolon veriyor (bkz. card.css -> .tk-grid--4).
BOLUM_MUDA = {
    "type": "card_grid",
    "anchor": "muda",
    "heading": "Yedi israf (muda)",
    "intro": "TPS, değer katmayan her şeyi israf sayar ve yedi başlıkta "
             "toplar. Hattı iyileştirmenin ilk adımı bunları görebilmektir.",
    "settings": {"variant": "station", "columns": "4"},
    "items": [
        {"kind": "card", "eyebrow": "1", "title": "Fazla üretim",
         "children": [{"kind": "paragraph", "text":
                       "İhtiyaçtan fazla veya erken üretmek. Diğer tüm "
                       "israfları besleyen temel israf."}]},
        {"kind": "card", "eyebrow": "2", "title": "Bekleme",
         "children": [{"kind": "paragraph", "text":
                       "Parça, bilgi, onay veya makine beklerken geçen "
                       "zaman."}]},
        {"kind": "card", "eyebrow": "3", "title": "Taşıma",
         "children": [{"kind": "paragraph", "text":
                       "Ürünün süreçler arasında gereksiz yere hareket "
                       "ettirilmesi."}]},
        {"kind": "card", "eyebrow": "4", "title": "Gereksiz işlem",
         "children": [{"kind": "paragraph", "text":
                       "Müşteriye değer katmayan fazladan işlem "
                       "adımları."}]},
        {"kind": "card", "eyebrow": "5", "title": "Stok",
         "children": [{"kind": "paragraph", "text":
                       "Hatta veya depoda bekleyen, sermayeyi bağlayan ve "
                       "sorunları gizleyen fazla malzeme."}]},
        {"kind": "card", "eyebrow": "6", "title": "Gereksiz hareket",
         "children": [{"kind": "paragraph", "text":
                       "Çalışanın uzanma, eğilme, yürüme gibi değer "
                       "katmayan hareketleri."}]},
        {"kind": "card", "eyebrow": "7", "title": "Hatalı ürün",
         "children": [{"kind": "paragraph", "text":
                       "Yeniden işleme, hurda ve müşteriye ulaşan "
                       "hatalar."}]},
        {"kind": "outro", "title": "Muda, Mura, Muri",
         "text": "TPS yalnızca israfı (muda) değil, dengesizliği (mura) ve "
                 "aşırı yüklenmeyi (muri) de hedef alır. Üçü birbirini "
                 "besler: dengesiz bir üretim planı aşırı yüklenmeye, aşırı "
                 "yüklenme hataya yol açar."},
    ],
}

# Mevcut "Hattin iki sutunu" bolumunun basligi USTUNE eklenen gecis
# cumlesi (`lead` turunde oge). Blogun `intro` alani zaten dolu ve o
# basligin ALTINDA duruyor; bu ise TPS Evi'nden koprudur.
GECIS_IKI_SUTUN = {
    "kind": "lead",
    "text": "Evi ayakta tutan iki sütuna yakından bakalım.",
}


# --- 4) Bolum menusu (Global sayfasindaki bilesenin aynisi) ---
BOLUM_TPS_MENU = {
    "type": "section_nav",
    "heading": "Bu sayfada",
    "items": [],
}

# --- 5) Yerinde kalite ve andon ---
BOLUM_ANDON = {
    "type": "andon",
    "anchor": "andon",
    "heading": "Yerinde kalite ve andon",
    "items": [
        {"kind": "paragraph", "text":
         "TPS'te mükemmel kaliteye ulaşmanın temel prensibi \"yerinde "
         "kalite\"dir: hata, tespit edildiği yerde ve o anda çözülür, bir "
         "sonraki sürece asla aktarılmaz."},
        {"kind": "paragraph", "text":
         "Bunu mümkün kılan en çarpıcı uygulama andon'dur. Hattaki her "
         "çalışan, bir sorun fark ettiğinde andon ipini çekerek üretim "
         "hattını durdurma yetkisine sahiptir. Hattı durdurmak bir "
         "başarısızlık değil, sorumluluğun gereğidir. Sorun anında ekipçe "
         "incelenir, kök nedeni bulunur ve tekrar etmemesi için önlem "
         "alınır."},
        {"kind": "light", "variant": "green", "title": "Yeşil ışık",
         "text": "Süreç normal akışında."},
        {"kind": "light", "variant": "amber", "title": "Sarı ışık",
         "text": "Çalışan yardım çağırdı, hat henüz duruyor değil."},
        {"kind": "light", "variant": "red", "title": "Kırmızı ışık",
         "text": "Sorun çözülemedi, hat durdu."},
    ],
}

# --- 6) Kaizen dongusu (PDCA) ---
BOLUM_KAIZEN = {
    "type": "cycle_steps",
    "anchor": "kaizen",
    "heading": "Kaizen döngüsü",
    "intro": "İyileştirme tek seferlik bir proje değil, kapanmayan bir "
             "döngüdür. Her tur, bir sonrakinin başlangıç noktasını "
             "yükseltir.",
    "items": [
        {"kind": "step", "eyebrow": "1", "title": "Planla",
         "text": "Sorunu yerinde gör (genchi genbutsu), kök nedeni "
                 "\"5 Neden\" ile araştır, bir iyileştirme önerisi "
                 "geliştir."},
        {"kind": "step", "eyebrow": "2", "title": "Uygula",
         "text": "Öneriyi küçük ölçekte, hızlıca dene."},
        {"kind": "step", "eyebrow": "3", "title": "Kontrol Et",
         "text": "Sonucu ölç. Beklenen iyileşme gerçekleşti mi?"},
        {"kind": "step", "eyebrow": "4", "title": "Önlem Al",
         "text": "İşe yarıyorsa standart iş haline getir ve yokoten ile "
                 "diğer hatlara yay. Yaramıyorsa döngüye geri dön."},
        {"kind": "outro", "text":
         "Kaizen büyük atılımlarla değil, her gün yapılan küçük "
         "iyileştirmelerle ilerler. TPS'te iyileştirme fikrinin kaynağı "
         "çoğunlukla yönetim değil, işi bizzat yapan çalışandır."},
    ],
}

# --- 7) TPS kavram sozlugu ---
#     Terimler `slug` tasiyor: dogrudan link verilebilsin ve panelde
#     satirlar birbirine karismasin diye.
BOLUM_SOZLUK = {
    "type": "glossary",
    "anchor": "sozluk",
    "heading": "TPS kavram sözlüğü",
    "intro": "Sayfada geçen terimlerin kısa karşılıkları. Aramak için "
             "kutuya yazmaya başlayın.",
    "items": [
        {"kind": "term", "slug": "kanban", "title": "Kanban",
         "text": "Bir sonraki sürecin ihtiyacını önceki sürece bildiren "
                 "üretim kartı. Çekme sisteminin işleyiş aracı."},
        {"kind": "term", "slug": "heijunka", "title": "Heijunka",
         "text": "Üretimin tür ve miktar olarak dengelenmesi; dalgalanmayı "
                 "azaltarak hattı ve tedarikçileri istikrarlı çalıştırır."},
        {"kind": "term", "slug": "takt", "title": "Takt zamanı",
         "text": "Müşteri talebini karşılamak için bir aracın hattan "
                 "çıkması gereken süre. Üretimin ritmini belirler."},
        {"kind": "term", "slug": "poka-yoke", "title": "Poka-yoke",
         "text": "Hatayı en baştan imkânsız kılan basit tasarım önlemleri; "
                 "yanlış parçanın takılamayacağı bir aparat gibi."},
        {"kind": "term", "slug": "genchi-genbutsu", "title": "Genchi Genbutsu",
         "text": "Karar vermeden önce sahaya gidip gerçeği kendi gözünle "
                 "görmek."},
        {"kind": "term", "slug": "standart-is", "title": "Standart iş",
         "text": "Bir işin bilinen en iyi, en güvenli ve en tutarlı yapılış "
                 "biçimi. Kaizen'in başlangıç noktasıdır; standart yoksa "
                 "iyileştirme ölçülemez."},
        {"kind": "term", "slug": "5s", "title": "5S",
         "text": "Ayıkla, düzenle, temizle, standartlaştır, disiplini "
                 "sürdür. Görsel ve düzenli bir çalışma alanı."},
        {"kind": "term", "slug": "5-neden", "title": "5 Neden",
         "text": "Bir sorunun kök nedenine ulaşana kadar arka arkaya "
                 "\"neden?\" diye sormak."},
        {"kind": "term", "slug": "yokoten", "title": "Yokoten",
         "text": "Bir yerde işe yarayan iyileştirmenin diğer hatlara ve "
                 "fabrikalara yatay olarak yayılması."},
        {"kind": "term", "slug": "andon", "title": "Andon",
         "text": "Hattaki sorunu görünür kılan ve gerektiğinde hattı "
                 "durduran uyarı sistemi."},
        {"kind": "term", "slug": "muda-mura-muri", "title": "Muda / Mura / Muri",
         "text": "İsraf, dengesizlik ve aşırı yüklenme."},
    ],
}

# --- 8) TPS bugun nerede ---
BOLUM_TPS_BUGUN = {
    "type": "card_grid",
    "anchor": "bugun",
    "heading": "TPS bugün nerede",
    "intro": "TPS, önce otomotiv sektöründe, ardından üretimin çok ötesinde "
             "yayıldı. Bugün \"yalın (lean)\" adıyla bilinen yaklaşımın "
             "temelini oluşturuyor ve üretimle hiç ilgisi olmayan alanlarda "
             "uygulanıyor.",
    "settings": {"variant": "plain", "columns": "auto"},
    "items": [
        {"kind": "card", "title": "Sağlık", "children": [
            {"kind": "paragraph", "text":
             "Hastanelerde hasta akışının düzenlenmesi, bekleme sürelerinin "
             "kısaltılması ve ilaç hatalarının önlenmesinde yalın yöntemler "
             "kullanılıyor."}]},
        {"kind": "card", "title": "Yazılım", "children": [
            {"kind": "paragraph", "text":
             "Kanban panoları, sürekli teslimat ve küçük artımlı "
             "iyileştirme, çevik yazılım geliştirmenin temel araçları "
             "arasında."}]},
        {"kind": "card", "title": "Hizmet ve lojistik", "children": [
            {"kind": "paragraph", "text":
             "Depo yönetiminden bankacılık süreçlerine kadar, değer "
             "katmayan adımların ayıklanmasında aynı mantık işliyor."}]},
    ],
}

# --- 9) TPS'i TMMT'de gormek (yonlendirme bandi) ---
#     `mission` bloku = genis vurgu bandi; `link` ogesi butonu basiyor.
#     Hedef TMMT sayfasindaki "Fabrikada bir aracin yolculugu" bolumu:
#     o bloga `anchor: yolculuk` verildi (bkz. SAYFA_TMMT).
BOLUM_TMMT_KOPRU = {
    "type": "mission",
    "anchor": "tmmt",
    "items": [
        {"kind": "statement", "text":
         "TPS'i Sakarya'daki hatta çalışırken görün."},
        {"kind": "paragraph", "text":
         "TMMT, kurulduğu ilk günden bu yana TPS ilkeleriyle çalışıyor. "
         "Sakarya'daki fabrikada bir aracın presten montaja uzanan "
         "yolculuğunu inceleyin."},
        {"kind": "link", "title": "TMMT üretim sürecine göz atın",
         "url": "/tmmt#yolculuk"},
    ],
}


# ------------------------------------------------------------
#  3) URETIM SISTEMI (TPS)   (templates/uretim_sistemi.html)
# ------------------------------------------------------------
SAYFA_URETIM = {
    "slug": "uretim-sistemi",
    "url": "/uretim-sistemi",
    "is_home": False,
    "nav_order": 3,
    "theme": "uretim",
    "reveal_default": True,
    "title": "Toyota Production System",
    "nav_label": "Toyota Production System",
    "background": "img/tps-bg.jpg",
    "blocks": [
        {
            "type": "rich_text",
            "heading": "Toyota Production System",
            "heading_level": 1,
            "items": [
                {"kind": "paragraph", "text":
                 "Toyota Production System (TPS), İkinci Dünya Savaşı sonrasında Taiichi Ohno "
                 "öncülüğünde geliştirilen ve Toyota'nın üretim felsefesinin temelini oluşturan "
                 "yönetim sistemidir. Amacı, israfı (muda) ortadan kaldırarak müşteriye "
                 "en yüksek kaliteyi, en düşük maliyetle ve en kısa sürede sunmaktır. Bugün "
                 "dünya genelinde birçok sektörde \"yalın üretim\" (lean manufacturing) "
                 "adıyla uygulanan yaklaşımın da temelini oluşturur."},
            ],
        },
        BOLUM_TPS_MENU,
        BOLUM_TPS_EVI,
        BOLUM_TPS_DOGUS,
        # Serit dekoratif; sablonda .reveal SINIFI YOK. Sayfa geneli reveal
        # acik oldugu icin burada acikca kapatiliyor.
        {"type": "divider", "reveal": False, "settings": {"variant": "conveyor"}},
        {
            "type": "card_grid",
            "anchor": "iki-sutun",
            "heading": "Hattın iki sütunu",
            "intro": "Parça hattan akarken her istasyon kendi işini yapar; bu iki sütun "
                     "tüm hattın üzerine kurulduğu temeldir.",
            "settings": {"variant": "station", "columns": "2"},
            "items": [
                GECIS_IKI_SUTUN,
                {"kind": "card", "eyebrow": "1", "title": "Just-in-Time (JIT)",
                 "children": [{"kind": "paragraph", "text":
                               "Bir sonraki sürecin ihtiyaç duyduğu parçayı, ihtiyaç duyduğu anda ve "
                               "ihtiyaç duyduğu miktarda üretmek. Bu sayede fazla stok, fazla üretim ve "
                               "bekleme gibi israflar ortadan kalkar."}]},
                {"kind": "card", "eyebrow": "2", "title": "Jidoka",
                 "children": [{"kind": "paragraph", "text":
                               "\"İnsan dokunuşlu otomasyon.\" Bir sorun ya da hata tespit edildiğinde "
                               "makine ya da hat otomatik olarak durur; böylece hatalı ürün bir sonraki "
                               "aşamaya asla geçmez."}]},
            ],
        },
        {"type": "divider", "reveal": False, "settings": {"variant": "conveyor"}},
        {
            "type": "rich_text",
            "anchor": "iki-ilke",
            "heading": "Temeldeki iki ilke",
            "items": [
                {"kind": "paragraph", "text":
                 "Bu iki sütunun altında, sistemi ayakta tutan iki temel ilke yer alır: "
                 "<strong>Kaizen</strong> — küçük ama sürekli iyileştirme kültürü — ve "
                 "<strong>insana saygı</strong> — çalışanların fikirlerine değer verilmesi ve "
                 "sorun çözme sürecine dahil edilmesi. TPS, sadece bir üretim tekniği değil, "
                 "bu iki ilke üzerine kurulmuş bir çalışma kültürüdür."},
            ],
        },
        BOLUM_MUDA,
        BOLUM_ANDON,
        BOLUM_KAIZEN,
        BOLUM_SOZLUK,
        BOLUM_TPS_BUGUN,
        BOLUM_TMMT_KOPRU,
    ],
}


# ============================================================
#  CEVRE SAYFASI -- sonradan eklenenler
# ============================================================

# --- Altı hedef izgarasinin ALTINA: kalan uc hedef ---
#     Environmental Challenge 2050 alti hedeften olusuyor; izgarada
#     yalnizca ucunun sayisal karsiligi var. Kalan ucu rakamsiz,
#     kompakt bir liste olarak veriliyor (stat_grid'in `fact` ogeleri).
#
#     DOGRULANACAK: hedeflerin resmi TURKCE adlandirmalari yayina
#     almadan once Toyota Sustainability Data Book uzerinden
#     dogrulanmali. Adlar kodda sabit degil -- hepsi panelden
#     duzenlenebiliyor.
KALAN_HEDEFLER = [
    {"kind": "fact", "title": "Hedef 4: Su Kullanımını En Aza İndirme",
     "text": "Üretimde su tüketimini azaltmak ve kullanılan suyu doğaya "
             "güvenli biçimde geri kazandırmak."},
    {"kind": "fact", "title": "Hedef 5: Geri Dönüşüm Temelli Toplum ve Sistemler",
     "text": "Kaynakları döngüsel biçimde kullanmak; araçların ve "
             "bataryaların yeniden değerlendirilmesini sağlamak."},
    {"kind": "fact", "title": "Hedef 6: Doğayla Uyum İçinde Bir Gelecek",
     "text": "Biyoçeşitliliği korumak ve doğal yaşam alanlarını "
             "iyileştirmek."},
]

# --- 1) Hangi teknoloji size uygun? (karsilastirma tablosu) ---
#     Hucreler SUTUNUN altinda, satirlarla ayni sirada duruyor:
#     yeni bir sutun eklemek mevcut tabloyu bozmuyor.
BOLUM_TEKNOLOJI = {
    "type": "compare_table",
    "anchor": "teknoloji",
    "heading": "Hangi teknoloji size uygun?",
    "intro": "Aynı yolu dört farklı şekilde gidebilirsiniz. Aşağıdaki tablo, "
             "her teknolojinin nasıl çalıştığını ve kime uygun olduğunu yan "
             "yana koyuyor.",
    "settings": {"corner_label": "Özellik", "note_label": "Not"},
    "items": [
        {"kind": "row", "title": "Nasıl çalışır"},
        {"kind": "row", "title": "Şarj gereksinimi"},
        {"kind": "row", "title": "Kime uygun"},
        {"kind": "row", "title": "Toyota'daki örnek"},
        {"kind": "column", "title": "Hibrit (HEV)",
         "note": "Bu araçlar Sakarya'da üretiliyor",
         "url": "/tmmt", "link_label": "TMMT üretimi →",
         "children": [
             {"kind": "cell", "text":
              "İçten yanmalı motor ve elektrik motoru birlikte çalışır; "
              "batarya frenleme ve motor tarafından şarj edilir, prize "
              "takmak gerekmez."},
             {"kind": "cell", "text": "Yok."},
             {"kind": "cell", "text":
              "Şehir içi ve karma kullanım; şarj altyapısı olmayan "
              "bölgeler."},
             {"kind": "cell", "text": "Corolla, C-HR (hibrit)."},
         ]},
        {"kind": "column", "title": "Şarj Edilebilir Hibrit (PHEV)",
         "note": "Bu araçlar Sakarya'da üretiliyor",
         "url": "/tmmt", "link_label": "TMMT üretimi →",
         "children": [
             {"kind": "cell", "text":
              "Daha büyük bir bataryayla kısa mesafeleri tamamen "
              "elektrikle gider; batarya bitince hibrit olarak çalışmaya "
              "devam eder."},
             {"kind": "cell", "text": "Evde veya şarj noktasında."},
             {"kind": "cell", "text":
              "Günlük kısa mesafe + ara sıra uzun yol yapanlar."},
             {"kind": "cell", "text": "C-HR (şarj edilebilir hibrit)."},
         ]},
        {"kind": "column", "title": "Tam Elektrikli (BEV)", "children": [
            {"kind": "cell", "text":
             "Yalnızca elektrik motoruyla çalışır, egzoz emisyonu yoktur."},
            {"kind": "cell", "text": "Düzenli şarj gerekir."},
            {"kind": "cell", "text":
             "Şarj imkânı olan, ağırlıklı şehir içi kullanım."},
            {"kind": "cell", "text": "bZ ailesi."},
        ]},
        {"kind": "column", "title": "Hidrojen Yakıt Hücreli (FCEV)", "children": [
            {"kind": "cell", "text":
             "Hidrojen ve havadaki oksijen yakıt hücresinde birleşerek "
             "elektrik üretir; egzozdan yalnızca su çıkar."},
            {"kind": "cell", "text":
             "Hidrojen istasyonunda dakikalar içinde dolum."},
            {"kind": "cell", "text":
             "Uzun mesafe, ağır taşımacılık ve yüksek kullanım süresi "
             "gerektiren araçlar."},
            {"kind": "cell", "text": "Mirai."},
        ]},
        {"kind": "outro", "text":
         "Toyota'nın çoklu yol yaklaşımı, bölgenin enerji altyapısına ve "
         "kullanıcının ihtiyacına göre doğru teknolojiyi sunmayı hedefler. "
         "Tek bir çözüm her yerde en iyisi değildir."},
    ],
}

# --- 2) Hibrit nasil calisir? (asamali diyagram) ---
#     Asamanin `slug`u semada hangi bilesenin yanacagini belirliyor
#     (sablondaki AKTIF_BILESEN sozlugu). Metinler panelden.
BOLUM_HIBRIT = {
    "type": "hybrid_flow",
    "anchor": "hibrit",
    "heading": "Hibrit nasıl çalışır?",
    "intro": "Hibrit sistem, sürüşün her anında motor ile elektrik motoru "
             "arasındaki iş bölümünü kendisi ayarlar. Bir aşamaya dokunarak "
             "o anda hangi parçanın çalıştığını görebilirsiniz.",
    "items": [
        {"kind": "paragraph", "text":
         "Üstten görünen bir araç şeması. Önde içten yanmalı motor, ortada "
         "elektrik motoru, arkada batarya yer alır. Seçilen aşamada o anda "
         "çalışan parçalar vurgulanır."},
        {"kind": "step", "slug": "kalkis", "eyebrow": "1",
         "title": "Kalkış ve düşük hız",
         "text": "Araç yalnızca elektrik motoruyla hareket eder. Yakıt "
                 "tüketimi ve emisyon sıfırdır, çalışma sessizdir."},
        {"kind": "step", "slug": "normal", "eyebrow": "2",
         "title": "Normal sürüş",
         "text": "İçten yanmalı motor devreye girer. Gücün bir kısmı "
                 "tekerleklere, bir kısmı bataryayı şarj etmeye ayrılır."},
        {"kind": "step", "slug": "hizlanma", "eyebrow": "3",
         "title": "Hızlanma",
         "text": "Motor ve elektrik motoru birlikte çalışarak ek güç "
                 "sağlar."},
        {"kind": "step", "slug": "fren", "eyebrow": "4",
         "title": "Yavaşlama ve fren",
         "text": "Rejeneratif frenleme devreye girer; normalde ısı olarak "
                 "kaybolacak enerji elektriğe çevrilerek bataryaya geri "
                 "kazandırılır."},
        {"kind": "outro", "text":
         "Toyota hibrit sistemi prize takmayı gerektirmez; batarya sürüş "
         "sırasında kendi kendine şarj olur."},
    ],
}


# --- 3) Bolum menusu (diger sayfalardaki bilesenin aynisi) ---
BOLUM_CEVRE_MENU = {
    "type": "section_nav",
    "heading": "Bu sayfada",
    "items": [],
}

# --- 4) Dongusel ekonomi: 4R ---
BOLUM_4R = {
    "type": "card_grid",
    "anchor": "dongusel",
    "heading": "Döngüsel ekonomi: 4R",
    "intro": "Bir aracın çevresel etkisi yalnızca yolda geçirdiği sürede "
             "değil, üretiminden ömrünün sonuna kadar tüm yaşam döngüsünde "
             "ortaya çıkar. Toyota'nın döngüsel ekonomi yaklaşımı bu "
             "döngünün her aşamasını hedef alır.",
    "settings": {"variant": "plain", "columns": "4"},
    "items": [
        {"kind": "card", "title": "Redesign", "subtitle": "Yeniden tasarla",
         "children": [{"kind": "paragraph", "text":
                       "Araçlar, ömrünün sonunda kolay ayrıştırılabilecek ve "
                       "geri kazanılabilecek şekilde tasarlanır; geri "
                       "dönüştürülmüş malzeme kullanımı artırılır."}]},
        {"kind": "card", "title": "Reduce", "subtitle": "Azalt",
         "children": [{"kind": "paragraph", "text":
                       "Üretimde kullanılan malzeme, enerji ve su miktarı "
                       "sürekli azaltılır."}]},
        {"kind": "card", "title": "Reuse / Remanufacture",
         "subtitle": "Yeniden kullan",
         "children": [{"kind": "paragraph", "text":
                       "Kullanılabilir parçalar toplanır, yenilenir ve "
                       "yeniden dolaşıma sokulur."}]},
        {"kind": "card", "title": "Recycle", "subtitle": "Geri dönüştür",
         "children": [{"kind": "paragraph", "text":
                       "Ömrünü tamamlayan araç ve bileşenler ayrıştırılarak "
                       "malzemeler yeni üretim süreçlerine kazandırılır."}]},
    ],
}

# --- 5) Bataryanin ikinci hayati ---
#     DUZ akis (variant: linear): dongusel degil, o yuzden sonda
#     "basa doner" seridi cikmiyor.
BOLUM_BATARYA = {
    "type": "cycle_steps",
    "anchor": "batarya",
    "heading": "Bataryanın ikinci hayatı",
    "intro": "Bir batarya, araçtaki görevi bittiğinde kullanım ömrünü "
             "tamamlamış olmuyor. Toyota bataryaları dört aşamalı bir yolda "
             "izliyor.",
    "settings": {"variant": "linear"},
    "items": [
        {"kind": "step", "eyebrow": "1", "title": "Araçta kullanım",
         "text": "Batarya, aracın kullanım ömrü boyunca hizmet verir."},
        {"kind": "step", "eyebrow": "2", "title": "Toplama",
         "text": "Ömrünü tamamlayan bataryalar yetkili ağ üzerinden "
                 "toplanır ve durumu değerlendirilir."},
        {"kind": "step", "eyebrow": "3", "title": "İkinci hayat",
         "text": "Araçta kullanım için yeterli kapasitesi kalmayan "
                 "bataryalar, yenilenebilir enerji depolama gibi sabit "
                 "uygulamalarda kullanılmaya devam eder."},
        {"kind": "step", "eyebrow": "4", "title": "Geri dönüşüm",
         "text": "Kullanım ömrü tamamen dolduğunda değerli metaller geri "
                 "kazanılarak yeni batarya üretimine kazandırılır."},
        # Hedef: TMMT sayfasindaki "PHEV Batarya Hatti" bolumu.
        # O bloga `anchor: phev` veriliyor (bkz. SAYFA_TMMT).
        {"kind": "link",
         "title": "Sakarya'daki fabrika, Toyota'nın Avrupa'daki ilk PHEV "
                  "batarya üretim hattına ev sahipliği yapıyor →",
         "url": "/tmmt#phev"},
    ],
}

# --- 6) TMMT'de cevre ---
#
#     DOGRULANACAK: son dort kartin DEGERI BILEREK BOS. Rakami ve
#     aciklamasi olmayan kart sitede basilmiyor (bkz.
#     blocks/stat_grid.html), yani bolum dogrulanana kadar ilk uc
#     kartla gorunuyor. Etiketler panelde duruyor; fabrika verisi
#     girilince kartlar kendiliginden cikiyor.
BOLUM_TMMT_CEVRE = {
    "type": "stat_grid",
    "anchor": "tmmt",
    "heading": "TMMT'de çevre",
    "intro": "Global hedefler, Sakarya'daki fabrikada somut uygulamalara "
             "dönüşüyor. TMMT, 1999'dan bu yana ISO 14001 çevre yönetim "
             "sistemi sertifikasına sahip ve enerji, su ve atık azaltımına "
             "yönelik sürekli iyileştirme (kaizen) projeleri yürütüyor.",
    "settings": {
        "variant": "card",
        "columns": "auto",
        "panel_note": "Değeri boş bırakılan dört kart FABRİKA VERİSİYLE "
                      "DOĞRULANMALI. Rakamı ve açıklaması olmayan kart "
                      "sitede görünmez; doğrulayıp girdiğinde kendiliğinden "
                      "çıkar.",
    },
    "items": [
        {"kind": "stat", "value": "1999", "title": "ISO 14001 sertifikası",
         "text": "Sertifikasyonun başlangıç yılı. Fabrika, çevre yönetim "
                 "sistemini bu tarihten bu yana uyguluyor."},
        {"kind": "stat", "value": None, "title": "Enerji ve su verimliliği",
         "text": "Üretim süreçlerinde tüketimin azaltılmasına yönelik "
                 "kaizen projeleri."},
        {"kind": "stat", "value": None, "title": "Atık azaltımı",
         "text": "Üretim atıklarının kaynağında azaltılması ve geri kazanım "
                 "oranının artırılması."},
        # --- dogrulanacak: deger de aciklama da bos ---
        {"kind": "stat", "value": None, "text": None,
         "title": "Yıllık su tüketimi azaltım oranı"},
        {"kind": "stat", "value": None, "text": None,
         "title": "Düzenli depolamaya giden atık oranı"},
        {"kind": "stat", "value": None, "text": None,
         "title": "Fabrikada kullanılan yenilenebilir elektrik oranı"},
        {"kind": "stat", "value": None, "text": None,
         "title": "Ağaçlandırma / biyoçeşitlilik projeleri"},
    ],
}

# --- 7) Karbon notr fabrikaya giden yol ---
#     Cevre yolculugu ile AYNI bilesen (timeline).
#     2035 rakami sayfadaki "Karbon notr fabrikalar" kartiyla ayni;
#     2030 icin RAKAM VERILMIYOR, yalnizca niteliksel birakiliyor.
BOLUM_KARBON_YOL = {
    "type": "timeline",
    "anchor": "karbon",
    "heading": "Karbon nötr fabrikaya giden yol",
    "intro": "Fabrikalarda net sıfır karbon tek adımda değil, birbirini "
             "izleyen üç durakta hedefleniyor.",
    "items": [
        {"kind": "stop", "slug": "bugun", "eyebrow": "Bugün",
         "title": "Enerji verimliliği ve yenilenebilir elektrik",
         "text": "Üretimde enerji verimliliği ve yenilenebilir elektrik "
                 "kullanımının artırılması."},
        {"kind": "stop", "slug": "2030", "eyebrow": "2030",
         "title": "Kademeli azaltım",
         "text": "Ara hedefler doğrultusunda fabrika CO2 emisyonlarının "
                 "kademeli azaltımı."},
        {"kind": "stop", "slug": "2035", "eyebrow": "2035",
         "title": "Net sıfır karbon",
         "text": "Toyota'nın küresel üretim tesislerinde net sıfır karbon "
                 "hedef yılı."},
    ],
}

# --- 8) Surdurulebilirlik Raporu (yonlendirme bandi) ---
#     `mission` bloku, split varyanti: solda metin, sagda buton.
#     URL kodda sabit DEGIL -- rapor her yil degistigi icin panelden
#     guncellenebilir bir `link` ogesi.
BOLUM_RAPOR = {
    "type": "mission",
    "anchor": "rapor",
    "settings": {"variant": "split"},
    "items": [
        {"kind": "statement", "text": "Toyota Sustainability Data Book"},
        {"kind": "paragraph", "text":
         "Bu sayfadaki rakamların kaynağı olan yıllık sürdürülebilirlik "
         "raporunun tamamına ulaşın."},
        {"kind": "link", "title": "Raporu görüntüle",
         "url": "https://global.toyota/en/sustainability/report/"},
    ],
}


# ------------------------------------------------------------
#  4) TOYOTA VE CEVRE   (templates/cevre.html)
# ------------------------------------------------------------
SAYFA_CEVRE = {
    "slug": "cevre",
    "url": "/cevre",
    "is_home": False,
    "nav_order": 4,
    "theme": "cevre",
    "reveal_default": False,
    "title": "Toyota ve Çevre",
    "nav_label": "Toyota ve Çevre",
    "background": "img/cevre-bg.jpg",
    "blocks": [
        {
            "type": "rich_text",
            "heading": "Toyota ve Çevre",
            "heading_level": 1,
            "items": [
                {"kind": "paragraph", "text":
                 "Toyota'nın çevreye verdiği önem, 1997'de piyasaya sürdüğü ilk hibrit "
                 "modeli Prius'a kadar uzanır. Bugün bu yaklaşım, şirketin \"Gezegene Saygı\" "
                 "vizyonu doğrultusunda 2015 yılında ilan edilen "
                 "<strong>Toyota Environmental Challenge 2050</strong> stratejisiyle "
                 "devam ediyor. Bu strateji, 2050 yılına kadar karbon nötr olmayı "
                 "hedefleyen altı uzun vadeli hedeften oluşuyor."},
            ],
        },
        BOLUM_CEVRE_MENU,
        {
            "type": "stat_grid",
            "anchor": "hedefler",
            "heading": "Altı hedef, güncel ilerleme",
            "intro": "Toyota Environmental Challenge 2050 altı uzun vadeli hedeften oluşuyor. "
                     "Aşağıdaki rakamlar, Sustainability Data Book 2025'e göre ara "
                     "hedeflerdeki güncel durumu gösteriyor.",
            "note": "Kaynak: Toyota Sustainability Data Book 2025",
            "settings": {"variant": "progress", "columns": "auto"},
            "items": [
                {"kind": "stat", "value": "32", "count_to": 32, "subtitle": "Hedef 1: Yeni Araç Sıfır CO2", "count_suffix": "%",
                 "title": "Yeni araç CO2 emisyonu",
                 "text": "2010'a kıyasla azalma. Hedef yüzde 30'du, planlanandan önce aşıldı."},
                {"kind": "stat", "value": "34", "count_to": 34, "subtitle": "Hedef 3: Fabrika Sıfır CO2", "count_suffix": "%",
                 "title": "Fabrika CO2 emisyonu",
                 "text": "2013'e kıyasla azalma. Hedef yüzde 30'du."},
                {"kind": "stat", "value": "19", "count_to": 19, "subtitle": "Hedef 2: Yaşam Döngüsü Sıfır CO2", "count_suffix": "%",
                 "title": "Yaşam döngüsü CO2 emisyonu",
                 "text": "2013'e kıyasla azalma. Hedef yüzde 18'di."},
                {"kind": "stat", "value": "36", "count_to": 36, "subtitle": "Karbon nötrlüğe giden yol", "count_suffix": "%",
                 "title": "Yenilenebilir elektrik (küresel)",
                 "text": "Toplam elektrik kullanımında. Hedef yüzde 25'ti."},
                {"kind": "stat", "value": "100", "count_to": 100, "subtitle": "Karbon nötrlüğe giden yol", "count_suffix": "%",
                 "title": "Avrupa & Güney Amerika",
                 "text": "Bölgedeki tüm fabrikalar yenilenebilir elektrikle çalışıyor."},
                {"kind": "stat", "value": "2035", "count_to": 2035, "subtitle": "Karbon nötrlüğe giden yol", "count_from": 2013,
                 "count_format": "plain",
                 "title": "Karbon nötr fabrikalar",
                 "text": "Üretimde net sıfır karbon için hedeflenen yıl."},
                *KALAN_HEDEFLER,
            ],
        },
        {
            "type": "timeline",
            "anchor": "yolculuk",
            "heading": "Çevre yolculuğu",
            "intro": "Bir durağa dokunarak o yılın kısa özetini görebilirsiniz.",
            "note": "Kaynak: global.toyota sürdürülebilirlik sayfaları; "
                    "thesustainableinnovation.com özeti",
            "items": [
                {"kind": "stop", "slug": "1992", "eyebrow": "1992",
                 "title": "Earth Charter",
                 "text": "Toyota Earth Charter yayımlandı: şirketin çevre politikasının "
                         "temelini oluşturan ilke metni (2000'de güncellendi)."},
                {"kind": "stop", "slug": "1997", "eyebrow": "1997",
                 "title": "İlk hibrit: Prius",
                 "text": "Dünyanın ilk seri üretim hibrit otomobili Prius piyasaya sürüldü ve "
                         "Toyota'nın elektrikli aktarma organı deneyiminin başlangıcı oldu."},
                {"kind": "stop", "slug": "2015", "eyebrow": "2015",
                 "title": "Challenge 2050",
                 "text": "Paris İklim Anlaşması ile aynı yıl açıklanan Toyota Environmental "
                         "Challenge 2050, 2050'ye kadar ulaşılacak altı uzun vadeli hedefi "
                         "içeriyor."},
                {"kind": "stop", "slug": "2022", "eyebrow": "2022",
                 "title": "SBTi doğrulaması",
                 "text": "Toyota'nın sera gazı azaltım hedefleri, Science Based Targets "
                         "initiative (SBTi) tarafından bilimsel temelli olarak onaylandı."},
                {"kind": "stop", "slug": "2025", "eyebrow": "2025",
                 "title": "Güncel Data Book",
                 "text": "Yayımlanan güncel Sustainability Data Book'a göre birçok ara hedefe "
                         "planlanandan önce ulaşıldı."},
            ],
        },
        {
            "type": "media_split",
            "anchor": "hidrojen",
            "heading": "Hidrojenle Geleceğe",
            "note": "Kaynak: pressroom.toyota.com — \"2025 Toyota Year in Review\"",
            "settings": {"media_position": "end"},
            "items": [
                {"kind": "paragraph", "text":
                 "Toyota Mirai, elektriğini bir bataryadan değil, hidrojen ile havadaki "
                 "oksijeni birleştiren yakıt hücresinden üretir; egzozundan yalnızca su "
                 "çıkar. Şirket bu teknolojiyi otomobilin ötesinde kamyon, otobüs ve sabit "
                 "jeneratörlere de taşıyor."},
                {"kind": "bullet", "text":
                 "Toyota Hydrogen Solutions (2025): hidrojen çözümleriyle ilgilenen "
                 "işletmelere yönelik kurulan kurumsal hub."},
                {"kind": "bullet", "text":
                 "Hydrogen Headquarters (H2HQ), Gardena, Kaliforniya: hidrojen Ar-Ge ve "
                 "demo faaliyetlerinin merkezi."},
                # Gorselin alt metni ve altyazisi cevrilebilir oldugu icin
                # settings'te degil, oge olarak saklaniyor.
                {"kind": "media", "slug": "h2-car",
                 "title": "Yakıt hücreli araç görseli",
                 "text": "Görsel alanı — buraya yakıt hücreli araç fotoğrafı veya kısa video "
                         "eklenebilir.",
                 "settings": {"kind": "svg", "key": "h2-car", "image_id": None}},
            ],
        },
        {
            "type": "co2_calculator",
            "anchor": "hesaplayici",
            "heading": "Kişisel CO2 ve Yakıt Tasarrufu Hesaplayıcısı",
            "intro": "Mevcut aracınızı bir Toyota elektrikli teknolojisiyle değiştirseydiniz "
                     "yıllık olarak kabaca ne kadar tasarruf edeceğinizi görün.",
            "note": "Değerler tahminidir. Toyota resmi WLTP yakıt tüketimi verileri ile "
                    "güncel ortalama Türkiye yakıt ve elektrik fiyatları esas alınmıştır; "
                    "gerçek tasarruf sürüş koşullarına göre değişir.",
            # static/js/cevre.js icindeki sabitler buraya tasindi.
            "settings": {
                "rates": {
                    "fuel_per_100km": {"benzin": 7.4, "dizel": 6.0, "hev": 4.3,
                                       "phev": 1.6, "bev": 0},
                    "kwh_per_100km": {"benzin": 0, "dizel": 0, "hev": 0,
                                      "phev": 8.5, "bev": 14.5},
                    "co2_per_unit": {"benzin": 2.31, "dizel": 2.65, "elektrik": 0.42},
                    "price_per_unit": {"benzin": 44.0, "dizel": 45.0, "elektrik": 2.6},
                },
                "number_locale": "tr-TR",
                # Panelde gorunen hatirlatma (sitede basilmaz).
                "panel_note": "Yakıt ve elektrik fiyatları sık değişiyor. "
                              "Zam geldikçe aşağıdaki “Fiyatlar” kutusunu "
                              "güncelle; tüketim ve CO2 katsayıları da "
                              "buradan düzenlenir. Hesaplayıcının altındaki "
                              "açıklama metni ise “Kaynak dipnotu” alanıdır.",
            },
            "items": [
                {"kind": "field", "slug": "distance",
                 "title": "Yıllık ortalama kilometre",
                 "settings": {"default": 15000, "min": 0, "step": 500}},
                {"kind": "field", "slug": "vehicle", "title": "Mevcut araç tipi",
                 "children": [
                     {"kind": "option", "value": "benzin", "title": "Benzinli"},
                     {"kind": "option", "value": "dizel", "title": "Dizel"},
                 ]},
                {"kind": "field", "slug": "technology",
                 "title": "Karşılaştırılacak Toyota teknolojisi",
                 "children": [
                     {"kind": "option", "value": "hev", "title": "Hibrit (HEV)"},
                     {"kind": "option", "value": "phev",
                      "title": "Şarj Edilebilir Hibrit (PHEV)"},
                     {"kind": "option", "value": "bev", "title": "Tam Elektrikli (BEV)"},
                 ]},
                {"kind": "label", "slug": "co2", "title": "Yıllık CO2 tasarrufu",
                 "subtitle": "kg"},
                # "₺" sablonda cevrilmiyor -> cevrilmeyen `value` sutununda.
                {"kind": "label", "slug": "money",
                 "title": "Yıllık yakıt/enerji tasarrufu", "value": "₺"},
                {"kind": "label", "slug": "chart", "title": "Yıllık CO2 emisyonu (kg)"},
                {"kind": "label", "slug": "current", "title": "Mevcut araç"},
                {"kind": "label", "slug": "toyota", "title": "Toyota"},
            ],
        },
        {
            "type": "rich_text",
            "anchor": "coklu-yol",
            "heading": "Çoklu yol yaklaşımı",
            "items": [
                {"kind": "paragraph", "text":
                 "Toyota, karbon nötrlüğe tek bir teknolojiyle değil, bölgeye ve müşteri "
                 "ihtiyacına göre değişen birden fazla yolla ulaşmayı hedefliyor: hibrit "
                 "(HEV), şarj edilebilir hibrit (PHEV), tam elektrikli (BEV) ve hidrojen "
                 "yakıt hücreli (FCEV) araçlar bir arada geliştiriliyor. Bu yaklaşımın "
                 "arkasındaki fikir, şarj altyapısının zayıf olduğu bir bölgede hibritin, "
                 "altyapının güçlü olduğu bir bölgede ise elektrikli araçların daha "
                 "gerçekçi bir çözüm olabileceği."},
            ],
        },
        BOLUM_TEKNOLOJI,
        BOLUM_HIBRIT,
        BOLUM_4R,
        BOLUM_BATARYA,
        BOLUM_TMMT_CEVRE,
        BOLUM_KARBON_YOL,
        BOLUM_RAPOR,
        {
            "type": "source_list",
            "heading": "Kaynaklar",
            "items": [
                {"kind": "link", "variant": "external",
                 "title": "Toyota Global – Environmental Initiatives",
                 "url": "https://global.toyota/en/sustainability/esg/environmental/"},
                {"kind": "link", "variant": "external",
                 "title": "Toyota – 2050 Environmental Challenge",
                 "url": "https://www.toyota.com/2050challenge/"},
            ],
        },
    ],
}

SAYFALAR = [SAYFA_TMMT, SAYFA_GLOBAL, SAYFA_URETIM, SAYFA_CEVRE]


# ============================================================
#  Elle olusturulan Ingilizce karsiliklar
#
#  Sablonda sabit on ek + cevrilen kisim seklinde olan, dolayisiyla
#  onbellekte tek parca halinde bulunmayan metinler. Ingilizcesi
#  bugunku ciktiyla ayni olsun diye burada birlestiriliyor.
# ============================================================
KILITLI_EN = set(KILITLI_CEVIRI)


def el_ile_en(onbellek: dict) -> dict[str, str]:
    parca = onbellek.get("resmi haber duyuruları", "resmi haber duyuruları")
    karsiliklar = {
        "global.toyota – resmi haber duyuruları": f"global.toyota – {parca}",
    }
    karsiliklar.update(KILITLI_CEVIRI)
    return karsiliklar


# ============================================================
#  YAZMA
# ============================================================
def onbellegi_oku() -> dict:
    try:
        veri = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}
    return veri.get("en", {}) if isinstance(veri, dict) else {}


class Yazici:
    def __init__(self, onbellek: dict):
        self.onbellek = onbellek
        self.elle = el_ile_en(onbellek)
        self.ceviri_sayisi = 0
        self.onbellekten = 0
        self.aynen = 0

    # --- ceviri satirlari ---
    def cevirileri_yaz(self, nesne, entity_type: str) -> None:
        """Nesnenin cevrilebilir alanlari icin EN satiri olustur.

        AG KULLANILMAZ. Onbellekte varsa oradaki karsilik, yoksa Turkce
        metnin kendisi yazilir -- ikisi de bugunku ciktinin aynisidir.
        """
        # BlockItem'da cevrilecek alanlar ogenin turune gore degisir
        # (bkz. BlockItem.translatable_fields): "stat" ogesinin `value`
        # alani ekranda gorunur ve cevrilir, "option" ogesininki koddur.
        alanlar = getattr(nesne, "translatable_fields", None) or getattr(
            nesne, "TRANSLATABLE", ()
        )
        for alan in alanlar:
            kaynak = getattr(nesne, alan, None)
            if not kaynak or not str(kaynak).strip():
                continue
            kaynak = str(kaynak)
            if kaynak in self.elle:
                deger = self.elle[kaynak]
                self.onbellekten += 1
            elif kaynak in self.onbellek:
                deger = self.onbellek[kaynak]
                self.onbellekten += 1
            else:
                deger = kaynak
                self.aynen += 1
            for dil in HEDEF_DILLER:
                db.session.add(
                    Translation(
                        entity_type=entity_type,
                        entity_id=nesne.id,
                        field=alan,
                        locale=dil,
                        value=deger,
                        is_manual=kaynak in KILITLI_EN,
                        source_hash=text_hash(kaynak),
                    )
                )
                self.ceviri_sayisi += 1

    # --- ogeler ---
    def oge_yaz(self, block: Block, veri: dict, sira: int,
                parent: BlockItem | None = None) -> BlockItem:
        oge = BlockItem(
            block=block,
            parent=parent,
            position=sira,
            kind=veri.get("kind", "item"),
            variant=veri.get("variant"),
            slug=veri.get("slug"),
            eyebrow=veri.get("eyebrow"),
            title=veri.get("title"),
            subtitle=veri.get("subtitle"),
            value=veri.get("value"),
            text=veri.get("text"),
            note=veri.get("note"),
            url=veri.get("url"),
            link_label=veri.get("link_label"),
            lat=veri.get("lat"),
            lon=veri.get("lon"),
            count_to=veri.get("count_to"),
            count_from=veri.get("count_from", 0),
            count_prefix=veri.get("count_prefix"),
            count_suffix=veri.get("count_suffix"),
            count_group=veri.get("count_group", False),
            count_format=veri.get("count_format", "group"),
            settings=veri.get("settings", {}) or {},
        )
        db.session.add(oge)
        db.session.flush()          # id gerekiyor (ceviri satirlari icin)
        self.cevirileri_yaz(oge, "block_item")

        for alt_sira, alt in enumerate(veri.get("children", [])):
            self.oge_yaz(block, alt, alt_sira, parent=oge)
        return oge

    # --- bloklar ---
    def blok_yaz(self, page: Page, veri: dict, sira: int) -> Block:
        tip = veri["type"]
        if tip not in BLOCK_TYPES:
            raise ValueError(f"Bilinmeyen blok tipi: {tip}")

        blok = Block(
            page=page,
            position=sira,
            type=tip,
            is_visible=veri.get("is_visible", True),
            # PANEL KILIDI -- sifirdan kurulan veritabani da dogru
            # durumda gelsin diye. Yalnizca haber bloklari panelden
            # duzenlenebilir; digerleri salt okunur.
            # (Mevcut veritabanina uygulamak icin: tools/kilit_ekle.py)
            is_locked=(tip not in ACIK_BLOK_TIPLERI),
            anchor=veri.get("anchor"),
            heading=veri.get("heading"),
            heading_level=veri.get("heading_level", 2),
            intro=veri.get("intro"),
            note=veri.get("note"),
            reveal=veri.get("reveal"),
            settings=veri.get("settings", {}) or {},
        )
        db.session.add(blok)
        db.session.flush()
        self.cevirileri_yaz(blok, "block")

        for oge_sira, oge in enumerate(veri.get("items", [])):
            self.oge_yaz(blok, oge, oge_sira)
        return blok

    # --- sayfalar ---
    def sayfa_yaz(self, veri: dict, gorseller: dict[str, MediaAsset]) -> Page:
        arka = gorseller.get(veri.get("background") or "")
        sayfa = Page(
            slug=veri["slug"],
            url=veri["url"],
            is_home=veri.get("is_home", False),
            nav_order=veri["nav_order"],
            theme=veri["theme"],
            reveal_default=veri.get("reveal_default", False),
            is_published=True,
            title=veri["title"],
            nav_label=veri["nav_label"],
            background_image=arka,
        )
        db.session.add(sayfa)
        db.session.flush()
        self.cevirileri_yaz(sayfa, "page")

        for sira, blok in enumerate(veri["blocks"]):
            self.blok_yaz(sayfa, blok, sira)
        return sayfa


def doldur(yazici: Yazici) -> None:
    # --- gorseller ---
    gorseller: dict[str, MediaAsset] = {}
    for g in GORSELLER:
        varlik = MediaAsset(
            path=g["path"],
            original_name=Path(g["path"]).name,
            mime="image/jpeg",
            alt=g["alt"],
            is_builtin=True,
            size_bytes=_dosya_boyutu(g["path"]),
        )
        db.session.add(varlik)
        db.session.flush()
        yazici.cevirileri_yaz(varlik, "media")
        gorseller[g["path"]] = varlik

    # --- site ayarlari ---
    cevrilebilir_ayarlar = {
        f["key"] for f in SETTING_FIELDS if f.get("translatable")
    }
    for anahtar, deger in SITE_AYARLARI.items():
        ayar = SiteSetting(key=anahtar, value=deger)
        db.session.add(ayar)
        db.session.flush()
        if anahtar in cevrilebilir_ayarlar:
            # SiteSetting'in TRANSLATABLE listesi yok; alan adi sabit: "value"
            kaynak = deger
            if kaynak in yazici.onbellek:
                en = yazici.onbellek[kaynak]
                yazici.onbellekten += 1
            else:
                en = kaynak
                yazici.aynen += 1
            db.session.add(
                Translation(
                    entity_type="setting",
                    entity_id=ayar.id,
                    field="value",
                    locale="en",
                    value=en,
                    is_manual=False,
                    source_hash=text_hash(kaynak),
                )
            )
            yazici.ceviri_sayisi += 1

    # --- sayfalar ---
    for sayfa in SAYFALAR:
        yazici.sayfa_yaz(sayfa, gorseller)


def _dosya_boyutu(goreli: str) -> int:
    yol = ROOT / "static" / goreli
    try:
        return yol.stat().st_size
    except OSError:
        return 0


# ============================================================
#  RAPOR
# ============================================================
def rapor() -> None:
    print("VERITABANI DURUMU")
    print("-" * 52)
    print(f"  sayfa           : {db.session.query(Page).count()}")
    print(f"  blok            : {db.session.query(Block).count()}")
    print(f"  blok ogesi      : {db.session.query(BlockItem).count()}")
    print(f"  ceviri satiri   : {db.session.query(Translation).count()}")
    print(f"  gorsel          : {db.session.query(MediaAsset).count()}")
    print(f"  site ayari      : {db.session.query(SiteSetting).count()}")
    print()
    print("SAYFA BAZINDA")
    print("-" * 52)
    for sayfa in db.session.query(Page).order_by(Page.nav_order).all():
        ogeler = sum(len(b.all_items) for b in sayfa.blocks)
        ev = " (ana sayfa)" if sayfa.is_home else ""
        print(f"  {sayfa.url:20s} {len(sayfa.blocks)} blok, {ogeler:3d} oge{ev}")
        for blok in sayfa.blocks:
            ad = BLOCK_TYPES[blok.type]["label"]
            baslik = blok.heading or "-"
            print(f"      {blok.position}. {blok.type:16s} {len(blok.all_items):3d} oge  {baslik[:38]}")
    print()


# ============================================================
#  ANA
# ============================================================
def main() -> int:
    p = argparse.ArgumentParser(description="Icerigi veritabanina aktar")
    p.add_argument("--reset", action="store_true",
                   help="mevcut tablolari SIL ve yeniden olustur")
    p.add_argument("--rapor", action="store_true",
                   help="yazma, sadece mevcut durumu goster")
    a = p.parse_args()

    uygulama = create_app()
    with uygulama.app_context():
        if a.rapor:
            db.create_all()
            rapor()
            return 0

        if a.reset:
            print("mevcut tablolar siliniyor...")
            db.drop_all()

        db.create_all()

        mevcut = db.session.query(Page).count()
        if mevcut and not a.reset:
            print(f"Veritabaninda zaten {mevcut} sayfa var. Uzerine yazmamak icin")
            print("durduruldu. Yeniden olusturmak icin:  python tools/seed.py --reset")
            return 1

        onbellek = onbellegi_oku()
        print(f"ceviri onbellegi: {len(onbellek)} EN kaydi okundu")

        yazici = Yazici(onbellek)
        doldur(yazici)
        db.session.commit()

        print()
        print("CEVIRI OZETI (ag kullanilmadi)")
        print("-" * 52)
        print(f"  onbellekten gelen : {yazici.onbellekten}")
        print(f"  Turkce birakilan  : {yazici.aynen}")
        print(f"  toplam EN satiri  : {yazici.ceviri_sayisi}")
        print()
        rapor()
        print(f"veritabani: {uygulama.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"dosya     : {Path(uygulama.instance_path) / 'toyota.db'}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
