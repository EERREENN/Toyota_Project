# -*- coding: utf-8 -*-
"""Haber veritabanina GERCEK Toyota haberlerini yazar.

    python tools/seed_news.py            # eksik haberleri ekler
    python tools/seed_news.py --liste    # veritabanindakileri gosterir
    python tools/seed_news.py --sifirla  # ONCE hepsini siler, sonra ekler

TEKRAR CALISTIRILABILIR: eslesme `slug` uzerinden yapilir, ayni haber
ikinci kez eklenmez. Var olan kayitlarin uzerine de YAZMAZ -- elle
duzeltilmis bir metni ezmesin diye.

ICERIK GERCEK
-------------
Asagidaki sekiz haber Toyota'nin kendi basin kanallarindan alindi
(her kaydin `kaynak` alaninda adres var). Metinler BIREBIR KOPYA
DEGIL: her biri Turkce olarak yeniden yazilmis ozetlerdir ve
govdenin sonunda kaynak baglantisi durur.

Yayin durumu bilerek karisik: yedi haber yayinda, biri TASLAK.
Taslak olan sitede hicbir yerde gorunmez -- ne listede ne de kendi
adresinde (bkz. app/haberler.py). Panelde ise gorunur.

GORSELLER
---------
Her haberin `gorseller` listesi iki tur kaynak kabul eder:

    "https://..."          indirilir
    "img/tmmt_img/x.jpg"   depodan kopyalanir (static/ koklu yol)

Ikisi de static/uploads/news/ altina SLUG adiyla yazilir
("<slug>-1.jpg"), yani sitede hicbir dis adrese baglanti verilmez.
Gorseller web icin AZAMI_GENISLIK'e indirilir.

Depodan kopyalananlar bilerek var: Toyota'nin Turkce basin
bultenleri (toyotatr.com) metin yayinliyor, gorsel yayinlamiyor.
O haberlerde depodaki Toyota gorselleri kullanildi; hangisinin
hangi kaynaktan geldigi asagida her kayitta yaziyor.

Haber basina gorsel sayisi app/yukleme.py -> azami_gorsel()
sinirini asamaz; betik fazlasini keser ve uyarir.

BAGIMLILIK
----------
Yeniden boyutlandirma icin Pillow gerekir. Kurulu degilse betik
durmaz: gorselleri oldugu boyutta kopyalar ve uyarir.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app                     # noqa: E402
from app import yukleme                        # noqa: E402
from app.extensions import db                  # noqa: E402
from app.metin import benzersiz_slug, slugify  # noqa: E402
from app.models import News, NewsImage         # noqa: E402

# Web icin yeterli. Toyota basin gorselleri 4000 pikseli asabiliyor;
# oylece konulsa hem sayfa agirlasir hem de panelin 4 MB yukleme
# siniri asilirdi.
AZAMI_GENISLIK = 1600

# Bazi CDN'ler ajanini soylemeyen istegi reddediyor.
TARAYICI = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0 Safari/537.36")

PP = "https://content.presspage.com/uploads/1523"


# ============================================================
#  HABERLER
# ============================================================
HABERLER = [
    # --------------------------------------------------------
    {
        "date": date(2026, 9, 7),
        "is_published": True,
        "kategori": "cevre",
        "kaynak": ("https://newsroom.toyota.eu/toyota-and-scania-collaborate-"
                   "to-test-hydrogen-fuel-cell-technology-in-heavy-duty-transport/"),
        "title_tr": "Toyota ile Scania ağır vasıtada hidrojeni sahada sınıyor",
        "title_en": "Toyota and Scania put hydrogen to the test in heavy transport",
        "summary_tr":
            "Toyota'nın üçüncü nesil yakıt hücresi sistemi, Scania'nın 40 ağır "
            "vasıtasına takılacak. Amaç hidrojenin uzun menzil ve yüksek "
            "kullanım oranı isteyen taşımacılıkta gerçek koşullarda ne "
            "yaptığını ölçmek.",
        "summary_en":
            "Toyota's third-generation fuel cell system will be fitted to 40 "
            "Scania heavy-duty vehicles, to measure what hydrogen actually "
            "does in transport that demands long range and high utilisation.",
        "content_tr":
            "Toyota ve Scania, ağır vasıta taşımacılığında hidrojen yakıt "
            "hücresi çözümlerini birlikte denemek üzere anlaştı. Anlaşma "
            "kapsamında Toyota, Scania'nın Pilot Partner programında yer alan "
            "40 ağır vasıta için yakıt hücresi sistemi sağlayacak.\n\n"
            "Araçlarda Toyota'nın en yeni, üçüncü nesil yakıt hücresi sistemi "
            "kullanılacak. Sistem, ağır vasıta uygulamaları için oldukça "
            "kompakt bir gövdede 300 kW güç veriyor. İlk hidrojenli Scania "
            "çekicilerinin 2027'nin ilk çeyreğinde sahaya çıkması bekleniyor.\n\n"
            "Scania'nın Pilot Partner programı, seçilmiş müşterilerle birlikte "
            "sürdürülebilir taşımacılık teknolojilerini gerçek çalışma "
            "koşullarında değerlendirmeyi amaçlıyor. Bu iş birliğiyle teknik "
            "performans, işletme verimliliği ve toplam sahip olma maliyeti "
            "laboratuvarda değil sahadan gelen veriyle ölçülecek.\n\n"
            "Toyota Motor Corporation İcra Kurulu Başkan Yardımcısı Hiroki "
            "Nakajima, hidrojen talebinin ve altyapısının büyümesinde ağır "
            "vasıta taşımacılığının belirleyici olduğunu; uzun menzilin, "
            "yüksek kullanım oranının ve işletme verimliliğinin şart olduğu bu "
            "alanda hidrojenin doğru çözüm olduğunu söyledi. Scania "
            "Teknolojiden Sorumlu Genel Müdürü Sara Forsberg ise programın, "
            "teknolojinin zorlu gerçek koşullardaki fırsatlarını ve "
            "zorluklarını görmelerini sağlayacağını belirtti.",
        "content_en":
            "Toyota and Scania have agreed to test hydrogen fuel cell "
            "solutions for heavy-duty transport together. Toyota will supply "
            "fuel cell systems for 40 heavy-duty vehicles in Scania's Pilot "
            "Partner programme.\n\n"
            "The vehicles use Toyota's latest, third-generation fuel cell "
            "system, which delivers 300 kW in a compact package built for "
            "heavy-duty use. The first hydrogen Scania trucks are expected to "
            "start operating in the first quarter of 2027.\n\n"
            "Scania's Pilot Partner programme evaluates sustainable transport "
            "technologies with selected customers under real operating "
            "conditions. Technical performance, operational efficiency and "
            "total cost of ownership will be measured from field data rather "
            "than in a laboratory.\n\n"
            "Hiroki Nakajima, Executive Vice President of Toyota Motor "
            "Corporation, said heavy-duty transport is key to building "
            "hydrogen demand and infrastructure, and that hydrogen is the "
            "right solution where long range, high utilisation and "
            "operational efficiency are essential. Sara Forsberg, Chief "
            "Technology Officer at Scania, said the programme will show the "
            "opportunities and challenges of the technology in demanding "
            "real-world operations.",
        # 1. gorsel Toyota Avrupa basin odasindan; 2. gorsel depodaki
        # hidrojen fotografi (basin bulteninde tek gorsel vardi).
        "gorseller": [
            PP + "/49181a11-bcb6-40c5-b44a-31abe2286e0c/26103-003.jpg",
            "img/toyota_cevre_img/hidrojen.jpg",
        ],
    },
    # --------------------------------------------------------
    {
        "date": date(2026, 9, 3),
        "is_published": True,
        "kategori": "uretim",
        "kaynak": ("https://newsroom.toyota.eu/toyota-c-hr-gr-sport-marks-"
                   "10-year-milestone-with-stylish-updates/"),
        "title_tr": "Sakarya'da üretilen C-HR 10 yaşında: GR SPORT'a mat Onyx Grey",
        "title_en": "Sakarya-built C-HR turns 10: GR SPORT gains matte Onyx Grey",
        "summary_tr":
            "Toyota C-HR, tanıtımından bu yana 2,1 milyon satışla 10. yılını "
            "dolduruyor. GR SPORT donanımı yeni mat Onyx Grey rengi ve 20 inç "
            "mat gri jantlarla tazeleniyor.",
        "summary_en":
            "The Toyota C-HR marks 10 years and 2.1 million global sales. The "
            "GR SPORT grade is refreshed with a new matte Onyx Grey colour and "
            "20-inch matte grey wheels.",
        "content_tr":
            "Toyota C-HR, C-SUV segmentinde tasarım ve yenilik tarafındaki 10. "
            "yılını GR SPORT donanımına gelen güncellemeyle karşılıyor. "
            "Tanıtımından bu yana dünya genelinde 2,1 milyon adet satan "
            "modelin 1,2 milyondan fazlası Avrupa'da alıcı buldu.\n\n"
            "Motorsporlarından esinlenen GR SPORT donanımı, yeni mat Onyx Grey "
            "rengine kavuşuyor. Renk yalnızca GR SPORT'a özel bi-tone+ "
            "uygulamasıyla sunuluyor; tavan ve arka panellerdeki kontrast "
            "siyah, modelin keskin hatlarını öne çıkarıyor. Görünümü, yine bu "
            "donanıma özel geliştirilen 20 inç mat gri jantlar tamamlıyor.\n\n"
            "GR SPORT'ta sürüş tarafında Frequency Selective Control (FSC) "
            "amortisörler bulunuyor; sönümleme yol koşuluna göre kendini "
            "ayarlayarak yol tutuşu ile konfor arasındaki dengeyi koruyor. Ön "
            "süspansiyon kulesindeki dinamik damper ise yol gürültüsünü ve "
            "titreşimi azaltıyor.\n\n"
            "Modelde üç güç ünitesi seçeneği var: 140 DIN hp veren 1,8 litre "
            "hibrit, 180 DIN hp veren 2,0 litre hibrit ve 223 DIN hp veren 2,0 "
            "litre şarj edilebilir hibrit. 2023'te tanıtılan ikinci nesil "
            "C-HR, Toyota Otomotiv Sanayi Türkiye'nin Sakarya'daki fabrikasında "
            "üretiliyor; şarj edilebilir hibrit versiyonun bataryaları da aynı "
            "tesiste hattan iniyor.",
        "content_en":
            "The Toyota C-HR marks 10 years at the front of C-SUV design with "
            "an update to the GR SPORT grade. Since launch the model has sold "
            "2.1 million units worldwide, more than 1.2 million of them in "
            "Europe.\n\n"
            "The motorsport-inspired GR SPORT gains a new matte Onyx Grey "
            "colour, offered exclusively in a bi-tone+ execution where "
            "contrasting black across the roof and rear panels emphasises the "
            "car's sharp lines. New 20-inch matte grey wheels, developed for "
            "this grade only, complete the look.\n\n"
            "The GR SPORT uses Frequency Selective Control (FSC) shock "
            "absorbers that adapt damping to road conditions, balancing "
            "handling against ride comfort. A dynamic damper on the front "
            "strut reduces road noise and vibration.\n\n"
            "Three powertrains are offered: a 1.8-litre hybrid with 140 DIN "
            "hp, a 2.0-litre hybrid with 180 DIN hp and a 2.0-litre plug-in "
            "hybrid with 223 DIN hp. The second-generation C-HR, launched in "
            "2023, is built at Toyota Motor Manufacturing Turkey in Sakarya, "
            "where the plug-in hybrid's batteries are also produced.",
        "gorseller": [
            PP + "/86fbe1c6-f7ec-4a8f-b41a-6a528d258913/toyotac-hronyx20271.png",
            PP + "/541f44dd-528e-4e02-bdf8-0057a64d1299/toyotac-hronyx20272.png",
            PP + "/a1ba0a96-a57e-4b05-a937-f266e4030b8e/toyotac-hronyx20273.png",
            PP + "/f50150cc-767b-4ebe-a8c6-11107577a191/toyotac-hronyx20274.png",
        ],
    },
    # --------------------------------------------------------
    {
        "date": date(2026, 8, 25),
        "is_published": True,
        "kategori": "kalite",
        "kaynak": ("https://newsroom.toyota.eu/toyota-marks-60-years-of-"
                   "corolla-with-exclusive-special-editions/"),
        "title_tr": "Corolla 60 yaşında: Toyota özel seri modellerle kutluyor",
        "title_en": "Corolla at 60: Toyota marks the anniversary with special editions",
        "summary_tr":
            "Dünyanın en çok satan otomobili Corolla 60. yılını dolduruyor. "
            "Toyota, Avrupa'da üretilen Hatchback, Touring Sports ve Sedan "
            "gövdeler için özel seri sürümler çıkarıyor.",
        "summary_en":
            "Corolla, the world's best-selling car, turns 60. Toyota is "
            "launching special editions of the European-built Hatchback, "
            "Touring Sports and Sedan.",
        "content_tr":
            "Toyota Corolla bu yıl 60. yaşını kutluyor. Adını taşıyan "
            "araçlardan bugüne kadar dünya genelinde 57 milyondan fazlası "
            "satıldı ve model, dünyanın en çok satan otomobili unvanını "
            "koruyor.\n\n"
            "Corolla'nın sürekliliği, 1966'daki ilk modelde benimsenen ilkeye "
            "dayanıyor: erişilebilir fiyata, yüksek kaliteli ve çok yönlü bir "
            "otomobil. On iki nesil sonra da model aynı çizgide duruyor. Bugün "
            "dünya genelinde 12 noktada üretiliyor ve 150 ülke ile bölgede "
            "satılıyor. Avrupa'da kalite, dayanıklılık ve güvenilirlik "
            "denince ilk anılan modellerden biri.\n\n"
            "Model, Toyota'nın Avrupa üretim programının da merkezinde yer "
            "aldı. Üretim 1994'te yedinci nesille Toyota Otomotiv Sanayi "
            "Türkiye'de (TMMT) başladı, 1998'de İngiltere'deki TMUK "
            "fabrikasına genişledi. Sakarya, Corolla'yı Avrupa'da üreten ilk "
            "Toyota fabrikası olma özelliğini taşıyor.\n\n"
            "60. Yıl özel serileri Hatchback, Touring Sports ve Sedan "
            "gövdeler için hazırlandı. Hatchback ve Touring Sports "
            "versiyonları, kontrast Night Sky Black tavanla ikili renk "
            "uygulamasında sunulan özel New Boreal Blue metalik rengiyle "
            "ayrışıyor. Yeni 10 kollu 17 inç alaşım jantlar, ön tamponun alt "
            "kısmındaki ve marşpiyellerdeki mat gümüş süslemeler ile "
            "koyu kaplamalı sis farı çerçeveleri donanımı tamamlıyor.",
        "content_en":
            "The Toyota Corolla celebrates its 60th anniversary this year. "
            "More than 57 million cars bearing the name have been sold "
            "worldwide, and it remains the world's best-selling car.\n\n"
            "Corolla's staying power rests on the principle behind the 1966 "
            "original: a high-quality, versatile car at an affordable price. "
            "Twelve generations later it holds to that. It is built at 12 "
            "locations worldwide and sold in 150 countries and regions, and "
            "in Europe it is a byword for quality, durability and "
            "reliability.\n\n"
            "The model has been central to Toyota's European manufacturing "
            "programme. Production began with the seventh generation at "
            "Toyota Motor Manufacturing Turkey (TMMT) in 1994 and extended to "
            "TMUK in the United Kingdom in 1998 — Sakarya was the first Toyota "
            "plant in Europe to build a Corolla.\n\n"
            "The 60th Anniversary editions cover the Hatchback, Touring "
            "Sports and Sedan. The Hatchback and Touring Sports are set apart "
            "by an exclusive New Boreal Blue metallic paint in a bi-tone "
            "execution with a contrasting Night Sky Black roof, plus new "
            "10-spoke 17-inch alloy wheels, matt silver garnishes on the "
            "lower front bumper and side sills, and dark-plated fog light "
            "ornaments.",
        "gorseller": [
            PP + "/a45f7910-7a1b-4e58-81a3-32f87d08152d/toy_corolla_60th_2026_hub_dig_16x9_01.png",
            PP + "/5242694f-be09-483f-bbac-008f6aaef2d6/toy_corolla_60th_2026_hub_dig_16x9_02.png",
            PP + "/19343816-d025-4712-9d7b-c47744f13c92/toy_corolla_60th_2026_hub_dig_16x9_03.png",
            PP + "/00da59d5-a0cb-44e5-b73c-e0562a5252d7/toy_corolla_60th_2026_hub_dig_16x9_04.png",
        ],
    },
    # --------------------------------------------------------
    {
        "date": date(2026, 2, 19),
        "is_published": True,
        "kategori": "cevre",
        "kaynak": ("https://newsroom.toyota.eu/toyota-announces-a-new-"
                   "investment-in-a-circular-factory-in-poland/"),
        "title_tr": "Toyota, Polonya'da ikinci Döngüsel Fabrika yatırımını duyurdu",
        "title_en": "Toyota announces a second Circular Factory, in Poland",
        "summary_tr":
            "Toyota Motor Europe, Walbrzych'te 25 bin metrekarelik bir "
            "Döngüsel Fabrika kuruyor. Tesis yılda yaklaşık 20 bin ömrünü "
            "tamamlamış aracı işleyecek.",
        "summary_en":
            "Toyota Motor Europe is opening a 25,000 m² Circular Factory in "
            "Walbrzych that will process close to 20,000 end-of-life vehicles "
            "a year.",
        "content_tr":
            "Toyota Motor Europe (TME), Polonya'nın Walbrzych kentinde yeni "
            "bir Döngüsel Fabrika kuracağını açıkladı. 25 bin metrekarelik "
            "tesis, yılda yaklaşık 20 bin ömrünü tamamlamış aracı işleyecek.\n\n"
            "Yatırım, şirketin azalt–yeniden kullan–geri dönüştür ilkelerine "
            "dayanan döngüsel ekonomi stratejisinin bir parçası. Tesis, "
            "yeniden kullanılabilecek parçaları ve değerli ham maddeleri geri "
            "kazanacak. Batarya ve jant gibi bileşenler yeniden üretim, farklı "
            "amaçla kullanım ya da geri dönüşüm açısından değerlendirilecek; "
            "bakır, çelik, alüminyum ve plastik gibi malzemeler yeni araç "
            "üretiminde kullanılmak üzere toplanacak.\n\n"
            "Yeni fabrika, hâlihazırda Toyota'nın hibrit ve konvansiyonel güç "
            "aktarma organları için kritik parçalar üreten mevcut Walbrzych "
            "tesisinin faaliyetlerini genişletecek.\n\n"
            "TME Döngüsel Ekonomiden Sorumlu Başkan Yardımcısı Leon van der "
            "Merwe, bunun Avrupa'daki ikinci Döngüsel Fabrika olduğunu; "
            "ilkinin 2025'te İngiltere'nin Burnaston kentinde açıldığını ve "
            "referans noktası hâline geldiğini söyledi. Polonya'nın ömrünü "
            "tamamlamış araç kaynağı, geri dönüşüm ekosistemi ve mevcut üretim "
            "altyapısı nedeniyle seçildiğini, önümüzdeki yıllarda başka Avrupa "
            "pazarlarında da benzer yatırımların planlandığını belirtti.",
        "content_en":
            "Toyota Motor Europe (TME) has announced a new Circular Factory in "
            "Walbrzych, Poland. The 25,000 m² facility will process close to "
            "20,000 end-of-life vehicles every year.\n\n"
            "The investment is part of TME's circular economy strategy, built "
            "on reduce, reuse and recycle. The plant will recover components "
            "that can be used again as well as valuable raw materials. "
            "Batteries and wheels will be assessed for remanufacturing, "
            "repurposing or recycling, while copper, steel, aluminium and "
            "plastics will be recovered for use in new vehicles.\n\n"
            "The factory extends the activities of the existing Walbrzych "
            "plant, which already produces key components for Toyota's hybrid "
            "and conventional powertrains.\n\n"
            "Leon van der Merwe, Vice President of Circular Economy at TME, "
            "said this is the company's second Circular Factory in Europe "
            "after the first opened in Burnaston, United Kingdom in 2025 and "
            "became its benchmark. Poland was selected for its supply of "
            "end-of-life vehicles, its recycling ecosystem and Toyota's "
            "established manufacturing presence; similar investments are "
            "planned in other European markets.",
        "gorseller": [
            PP + "/3f5449c9-918f-4de6-8648-7f0c3dd10be8/dji_0468.jpg",
            PP + "/f09ed2bc-34cf-4476-a829-cb7265520e84/tmmp-w-plant.jpg",
            PP + "/63d29d6d-24be-48eb-aa33-80942f546837/toyota_circular_model_scheme.jpg",
        ],
    },
    # --------------------------------------------------------
    {
        "date": date(2026, 9, 7),
        "is_published": True,
        "kategori": "kurumsal",
        "kaynak": ("https://newsroom.toyota.eu/lone-star-le-mans-race---"
                   "heartbreak-for-toyota-racing-in-austin/"),
        "title_tr": "TOYOTA RACING Austin'de zaferi son 11 dakikada kaybetti",
        "title_en": "TOYOTA RACING loses Austin win in the final 11 minutes",
        "summary_tr":
            "FIA Dünya Dayanıklılık Şampiyonası'nın beşinci ayağında liderken "
            "hidrolik arıza yaşayan 7 numaralı TR010 HYBRID yarış dışı kaldı. "
            "Toyota yine de üretici klasmanındaki farkı dokuz puana çıkardı.",
        "summary_en":
            "Leading round five of the FIA World Endurance Championship, the "
            "#7 TR010 HYBRID retired with a hydraulic failure. Toyota still "
            "extended its manufacturers' championship lead to nine points.",
        "content_tr":
            "TOYOTA RACING, 2026 FIA Dünya Dayanıklılık Şampiyonası'nın "
            "(WEC) beşinci ayağı olan Austin'deki Lone Star Le Mans "
            "yarışında zafere son dakikalarda veda etti. Mike Conway, Kamui "
            "Kobayashi ve Nyck de Vries'in kullandığı 7 numaralı TR010 "
            "HYBRID rahat biçimde liderken, bitişe 11 dakika kala çıkan "
            "hidrolik arıza aracı yarış dışı bıraktı.\n\n"
            "Sébastien Buemi, Brendon Hartley ve Ryō Hirakawa'nın 8 numaralı "
            "aracı yarışın büyük bölümünde podyum mücadelesi verdi. Son 90 "
            "dakikaya üçüncü sırada giren ekip, pit yolunda hız limitini "
            "aşınca aldığı drive-through cezasıyla yedinci sıraya düştü. "
            "Hemen ardından gelen sanal güvenlik aracı dönemi de aleyhlerine "
            "işledi ve araç 14. sıraya kadar geriledi.\n\n"
            "Yarışın ortasındaki güvenlik aracı stratejileri sıfırlamıştı. "
            "Yeniden başlangıçta Nyck de Vries birinci virajda üç cesur "
            "geçişle liderliğe yükseldi, ardından direksiyonu devralan Kamui "
            "Kobayashi son saate girilirken iki Alpine'in baskısı altında "
            "önde kaldı. De Vries yarışın en hızlı turlarını atarak farkı "
            "açtığı sırada arıza geldi.\n\n"
            "Buemi son stintte etkileyici bir geri dönüşle birçok rakibini "
            "geçerek altıncılığı ve takıma bir miktar puanı getirdi. Sonuca "
            "rağmen Toyota, üretici klasmanındaki liderliğini dokuz puana "
            "çıkardı; 7 numaralı ekip sürücüler klasmanının zirvesinde puan "
            "eşitliğini korudu. Takım, üç hafta sonra 27 Eylül'de kendi "
            "evindeki Fuji 6 Saat yarışında toparlanmayı hedefliyor.",
        "content_en":
            "TOYOTA RACING was denied victory in the closing minutes of the "
            "Lone Star Le Mans in Austin, round five of the 2026 FIA World "
            "Endurance Championship. The #7 TR010 HYBRID of Mike Conway, "
            "Kamui Kobayashi and Nyck de Vries led comfortably until a "
            "hydraulic issue forced it into retirement with 11 minutes "
            "left.\n\n"
            "The #8 car of Sébastien Buemi, Brendon Hartley and Ryō Hirakawa "
            "fought for a podium for much of the race. Running third with 90 "
            "minutes to go, it dropped to seventh after a drive-through "
            "penalty for pit lane speeding, then fell to 14th when a virtual "
            "safety car let rivals gain time.\n\n"
            "A safety car at the midway point had reset the strategies. At "
            "the restart de Vries made three bold overtakes into turn one to "
            "take the lead, and Kobayashi held it under pressure from two "
            "Alpines. De Vries was setting fastest laps and pulling clear "
            "when the failure struck.\n\n"
            "Buemi recovered some points with a determined final stint, "
            "passing multiple rivals to finish sixth. Toyota nevertheless "
            "extended its manufacturers' championship lead to nine points, "
            "and the #7 crew remains tied at the top of the drivers' "
            "standings. The team's home race, the 6 Hours of Fuji, follows on "
            "27 September.",
        "gorseller": [
            PP + "/626ef6a9-ff30-4f39-9e80-ed1c96107eab/86250-tjm2603se481.jpg",
            PP + "/3dd9fe77-3a24-4abd-8b3e-48e833635d0e/86251-tjm2603se484.jpg",
            PP + "/ea974d57-0e08-4001-b4ea-b799e0fd7f5b/86253-tjm2603se444.jpg",
            PP + "/53da42ce-634d-4c1b-a43d-8daae962e27a/86255-tjm2603se491.jpg",
        ],
    },
    # --------------------------------------------------------
    {
        # Tarih bultenin KENDI metninde geciyor: toren 4 Kasim 2023'te
        # yapildi.
        "date": date(2023, 11, 4),
        "is_published": True,
        "kategori": "uretim",
        "kaynak": ("https://www.toyotatr.com/turkiyenin-otomotiv-gelecegi-"
                   "yeniden-sekilleniyor-yeni-toyota-c-hr-uretimi-basladi"),
        "title_tr": "Yeni nesil Toyota C-HR'ın üretimi Sakarya'da başladı",
        "title_en": "Production of the new Toyota C-HR has started in Sakarya",
        "summary_tr":
            "Toyota Otomotiv Sanayi Türkiye, Türkiye'de üretilen ilk şarj "
            "edilebilir hibrit otomobilin üretimine başladı. Sakarya, Toyota "
            "Avrupa'da şarj edilebilir otomobil ve batarya üreten ilk fabrika "
            "oldu.",
        "summary_en":
            "Toyota Motor Manufacturing Turkey has begun building the first "
            "plug-in hybrid car produced in Türkiye, making Sakarya the first "
            "Toyota plant in Europe to build plug-in cars and their batteries.",
        "content_tr":
            "Toyota Otomotiv Sanayi Türkiye (TMMT), Sakarya'daki fabrikasında "
            "yeni nesil Toyota C-HR'ın üretimine başladı. Model, Türkiye'de "
            "üretilen ilk şarj edilebilir hibrit (PHEV) otomobil olma "
            "özelliğini taşıyor. Hattan çıkış töreni 4 Kasım 2023'te, Sanayi "
            "ve Teknoloji Bakanı Mehmet Fatih Kacır'ın katılımıyla "
            "gerçekleşti.\n\n"
            "Yeni C-HR, Toyota Yeni Global Platformu (TNGA-2) üzerinde hibrit "
            "ve şarj edilebilir hibrit versiyonlarıyla üretiliyor. Proje için "
            "yapılan 308 milyon Euro'luk ilave yatırımla şirketin Türkiye'deki "
            "toplam yatırımı 2,5 milyar Euro'ya ulaştı. Model, ihracat "
            "pazarlarına Avustralya ve Yeni Zelanda'yı da ekleyerek Okyanusya "
            "bölgesine açıldı.\n\n"
            "Fabrikada kurulan yıllık 75 bin adet kapasiteli batarya üretim "
            "hattı, TMMT'yi Toyota'nın Avrupa operasyonlarında elektrifikasyon "
            "dönüşümünün merkezine taşıyor. Aynı dönemde devreye alınan yeni "
            "boya tesisi, Toyota'nın Avrupa tesislerindeki 2030 karbon nötr ve "
            "2040 karbon sıfır hedeflerine yönelik adımların parçası.\n\n"
            "TMMT Genel Müdürü ve CEO'su Erdoğan Şahin, Cumhuriyet'in 100. "
            "yılını yeni C-HR ile taçlandırmaktan gurur duyduklarını ve bunun "
            "Toyota'nın Avrupa operasyonlarında elektrifikasyon dönüşüm "
            "merkezi hâline gelmelerini sağladığını söyledi. Toyota Motor "
            "Avrupa Başkanı Yoshihiro Nakata ise TMMT'de üretilen bataryalarla "
            "birlikte yeni C-HR'ın, Toyota'nın 2035'te Avrupa'da sıfır "
            "karbondioksit hedefine katkı sağlayacağını belirtti.",
        "content_en":
            "Toyota Motor Manufacturing Turkey (TMMT) has started production "
            "of the new-generation Toyota C-HR at its Sakarya plant. It is the "
            "first plug-in hybrid car built in Türkiye. The line-off ceremony "
            "took place on 4 November 2023 with Minister of Industry and "
            "Technology Mehmet Fatih Kacır attending.\n\n"
            "The new C-HR is built on the Toyota New Global Architecture "
            "(TNGA-2) in hybrid and plug-in hybrid versions. An additional "
            "investment of EUR 308 million brought Toyota's total investment "
            "in Türkiye to EUR 2.5 billion. The model added Australia and New "
            "Zealand to its export markets, opening up Oceania.\n\n"
            "A battery production line with an annual capacity of 75,000 units "
            "makes TMMT a centre of Toyota's electrification shift in Europe. "
            "A new paint shop commissioned at the same time supports Toyota's "
            "2030 carbon neutral and 2040 zero carbon targets for its European "
            "plants.\n\n"
            "TMMT President and CEO Erdoğan Şahin said the company was proud "
            "to crown the Republic's centenary with the new C-HR. Toyota Motor "
            "Europe President Yoshihiro Nakata said the new C-HR, with "
            "batteries built at TMMT, will contribute to Toyota's target of "
            "zero carbon dioxide in Europe by 2035.",
        # toyotatr.com basin bultenleri gorsel yayinlamiyor; asagidakiler
        # depodaki Toyota Turkiye fotograflari.
        "gorseller": [
            "img/tmmt_img/CHR.jpg",
            "img/tmmt_img/PHEV.webp",
            "img/tmmt_img/2023.webp",
            "img/tmmt_img/montaj.jpg",
        ],
    },
    # --------------------------------------------------------
    {
        # toyotatr.com bu bultende tarih yayinlamiyor. Metin 2023
        # uretim ve ihracat rakamlarini GECMIS olarak aniyor, yani
        # 2024. Duraklamanin baslangic gunu tarih olarak kullanildi.
        "date": date(2024, 7, 29),
        "is_published": True,
        "kategori": "uretim",
        "kaynak": ("https://www.toyotatr.com/toyota-otomotiv-sanayi-turkiye-"
                   "gelecege-hazirlik-icin-uretime-kisa-bir-mola-veriyor"),
        "title_tr": "Sakarya fabrikası planlı bakım için üretime üç hafta ara veriyor",
        "title_en": "Sakarya plant pauses production for three weeks of planned maintenance",
        "summary_tr":
            "Toyota Otomotiv Sanayi Türkiye, 29 Temmuz – 17 Ağustos arasında "
            "planlı bakım ve revizyon çalışmaları için üretime ara veriyor.",
        "summary_en":
            "Toyota Motor Manufacturing Turkey is pausing production between "
            "29 July and 17 August for planned maintenance and overhaul work.",
        "content_tr":
            "Toyota Otomotiv Sanayi Türkiye, Sakarya'daki fabrikasında 29 "
            "Temmuz – 17 Ağustos tarihleri arasında üretime üç hafta ara "
            "veriyor. Duraklama, planlı bakım ve revizyon çalışmaları için "
            "yapılıyor.\n\n"
            "Şirket bu dönemde üretim hatlarında bakım, onarım ve revizyon "
            "işlerini yürütecek. Hedef, fabrikanın performansını ve "
            "verimliliğini en üst seviyeye çıkarmak. Planlı duruş, sürekli "
            "iyileştirme anlayışının bir parçası: hatlar üretim baskısı "
            "altındayken yapılamayacak işler bu pencereye alınıyor.\n\n"
            "Toyota Otomotiv Sanayi Türkiye, 2023 yılı boyunca Sakarya'da "
            "ürettiği 213 bin aracın 178 binini ihraç etti. Şirket, 4,1 milyar "
            "dolarlık ihracat geliriyle Türkiye İhracatçılar Meclisi (TİM) "
            "tarafından Türkiye'nin en büyük ikinci ihracatçısı olarak "
            "ödüllendirilmişti.\n\n"
            "İleri teknolojiyle donatılmış üretim hatları ve yüksek kalite "
            "standartları, fabrikanın Toyota'nın Avrupa organizasyonundaki "
            "konumunu belirleyen unsurlar arasında yer alıyor.",
        "content_en":
            "Toyota Motor Manufacturing Turkey is pausing production at its "
            "Sakarya plant for three weeks, between 29 July and 17 August, for "
            "planned maintenance and overhaul work.\n\n"
            "During this period the company will carry out maintenance, repair "
            "and revision work on the production lines, aiming to bring the "
            "plant's performance and efficiency to their highest level. The "
            "planned stoppage is part of a continuous improvement approach: "
            "work that cannot be done while the lines are running is moved "
            "into this window.\n\n"
            "In 2023 the company built 213,000 vehicles in Sakarya and "
            "exported 178,000 of them. With export revenue of USD 4.1 billion "
            "it was recognised by the Turkish Exporters Assembly (TİM) as "
            "Türkiye's second largest exporter.\n\n"
            "Advanced production lines and high quality standards remain among "
            "the factors that define the plant's position within Toyota's "
            "European organisation.",
        "gorseller": [
            "img/tmmt_img/pres.jpg",
            "img/tmmt_img/kaynak.jpg",
            "img/tmmt_img/boya.jpg",
            "img/tmmt_img/kalite.webp",
        ],
    },
    # --------------------------------------------------------
    {
        # TASLAK -- sitede gorunmemeli, adresi yazan 404 almali.
        #
        # toyotatr.com bu bultende de tarih yayinlamiyor. Metindeki
        # "Turkiye-Japonya iliskilerinin 100. yili" ve "Toyota'nin
        # Turkiye'de uretime baslamasinin 30. yili" ifadeleri 2024'u
        # gosteriyor; toren Trafik Haftasi kapsaminda yapiliyor
        # (1-7 Mayis).
        "date": date(2024, 5, 7),
        "is_published": False,
        "kategori": "kurumsal",
        "kaynak": ("https://www.toyotatr.com/toyota-otomotiv-sanayi-turkiye-"
                   "trafik-guvenligi-resim-yarismasiyla-genc-yetenekleri-"
                   "odullendirdi"),
        "title_tr": "Trafik Güvenliği Resim Yarışması'nda 20 öğrenci ödüllendirildi",
        "title_en": "Twenty students awarded in the Traffic Safety Painting Contest",
        "summary_tr":
            "Toyota Otomotiv Sanayi Türkiye'nin 2006'dan beri Sakarya'da "
            "düzenlediği resim yarışması tamamlandı. Dereceye giren 20 öğrenci "
            "Trafik Haftası töreninde ödüllerini aldı.",
        "summary_en":
            "The painting contest Toyota Motor Manufacturing Turkey has run in "
            "Sakarya since 2006 has concluded, with 20 students receiving "
            "awards during Traffic Week.",
        "content_tr":
            "Toyota Otomotiv Sanayi Türkiye'nin trafik güvenliği bilincini ve "
            "farkındalığı artırmak amacıyla düzenlediği resim yarışması bu yıl "
            "da tamamlandı. Dereceye giren 20 öğrenci düzenlenen törenle "
            "ödüllendirildi.\n\n"
            "Şirket, genç nesillerin trafik kurallarına uyumunu teşvik etmek "
            "ve trafik güvenliği bilincini erken yaşta kazandırmak amacıyla "
            "yarışmayı 2006'dan bu yana Sakarya'da düzenliyor. Sakarya İl "
            "Millî Eğitim Müdürlüğü ve Trafik İl Müdürlüğü iş birliğiyle "
            "Trafik Haftası kapsamında yapılan yarışmada bu yılın konusu "
            "\"Trafikte Araçlar ve Yayalar, Uyulması Gereken Kurallar\" oldu.\n\n"
            "Öğrenciler konuyu kendi gözlemleri ve hayal güçleriyle "
            "resimlerine taşıdı. Ödül töreni, Sakarya Valisi, Büyükşehir "
            "Belediye Başkanı, İl Emniyet Müdürü, İl Millî Eğitim Müdürü ve "
            "ilçe belediye başkanlarının yanı sıra Toyota Otomotiv Sanayi "
            "Türkiye Kıdemli Başkan Yardımcısı Kenji Tsuchiya'nın katılımıyla "
            "Demokrasi Meydanı'nda gerçekleşti.\n\n"
            "Tsuchiya, Türkiye ile Japonya arasındaki ilişkilerin 100. yılının "
            "ve Toyota'nın Türkiye'de üretime başlamasının 30. yılının aynı "
            "döneme denk geldiğini hatırlattı. Trafik güvenliği konusundaki "
            "yetersiz bilinçlenmenin kazaların önemli nedenlerinden biri "
            "olduğunu, bu yüzden eğitimin erken yaşta başlaması gerektiğini "
            "vurgulayarak şirketin bu tür etkinlikleri desteklemeye devam "
            "edeceğini söyledi.",
        "content_en":
            "The painting contest run by Toyota Motor Manufacturing Turkey to "
            "raise awareness of traffic safety has concluded again this year, "
            "with 20 students receiving awards at a ceremony.\n\n"
            "The company has held the contest in Sakarya since 2006 to "
            "encourage younger generations to follow traffic rules and to "
            "build road safety awareness early. Organised during Traffic Week "
            "with the Sakarya Provincial Directorate of National Education and "
            "the Provincial Traffic Directorate, this year's theme was "
            "\"Vehicles and Pedestrians in Traffic, and the Rules to "
            "Follow\".\n\n"
            "Students brought the theme into their paintings through their own "
            "observations and imagination. The award ceremony was held at "
            "Demokrasi Meydanı with the Governor of Sakarya, the Metropolitan "
            "Mayor, the Provincial Police Chief, the Provincial Director of "
            "National Education, district mayors and Kenji Tsuchiya, Senior "
            "Vice President of Toyota Motor Manufacturing Turkey.\n\n"
            "Tsuchiya noted that the centenary of relations between Türkiye "
            "and Japan coincided with the 30th year of Toyota's production in "
            "the country. He said insufficient awareness is one of the main "
            "causes of traffic accidents, that education should therefore "
            "begin at an early age, and that the company would continue to "
            "support such activities.",
        "gorseller": [
            "img/tmmt_img/trafik güvenliği resim yarismasi.jpg",
            "img/tmmt_img/trafik güvenliği.jpg",
        ],
    },
]


# ============================================================
#  Gorsel indirme / kopyalama
# ============================================================
def _indir(adres: str) -> bytes:
    istek = urllib.request.Request(adres, headers={"User-Agent": TARAYICI})
    with urllib.request.urlopen(istek, timeout=60) as yanit:
        return yanit.read()


def _boyutlandir(ham: bytes, hedef: Path) -> bool:
    """Gorseli AZAMI_GENISLIK'e indirip jpg olarak yazar.

    Pillow yoksa False doner; cagiran taraf ham baytlari oldugu gibi
    yazar. Betik bir bagimlilik yuzunden durmasin.
    """
    try:
        import io
        from PIL import Image
    except ImportError:
        return False

    with Image.open(io.BytesIO(ham)) as resim:
        # Saydam png/webp jpg'ye cevrilirken siyah zemin olusmasin.
        if resim.mode in ("RGBA", "LA", "P"):
            zemin = Image.new("RGB", resim.size, (255, 255, 255))
            donusen = resim.convert("RGBA")
            zemin.paste(donusen, mask=donusen.split()[-1])
            resim = zemin
        elif resim.mode != "RGB":
            resim = resim.convert("RGB")

        if resim.width > AZAMI_GENISLIK:
            yukseklik = round(resim.height * AZAMI_GENISLIK / resim.width)
            resim = resim.resize((AZAMI_GENISLIK, yukseklik),
                                 Image.LANCZOS)
        resim.save(hedef, "JPEG", quality=85, optimize=True)
    return True


def _gorsel_yaz(kaynak: str, slug: str, sira: int, statik: Path) -> str | None:
    """Tek gorseli uploads/news/ altina yazar, static'e gore yol doner.

    `kaynak` ya bir adres ("https://...") ya da depo icinde static'e
    gore bir yoldur ("img/tmmt_img/CHR.jpg").
    """
    hedef_ad = f"{slug}-{sira}.jpg"
    hedef = statik / "uploads" / "news" / hedef_ad
    hedef.parent.mkdir(parents=True, exist_ok=True)

    if kaynak.startswith("http"):
        try:
            ham = _indir(kaynak)
        except (urllib.error.URLError, OSError, TimeoutError) as hata:
            print(f"      ! indirilemedi ({hata}): {kaynak}")
            return None
    else:
        yerel = statik / kaynak
        if not yerel.is_file():
            print(f"      ! depoda yok: {kaynak}")
            return None
        ham = yerel.read_bytes()

    if not _boyutlandir(ham, hedef):
        # Pillow yok: ham baytlari uzantisiyla yaz.
        uzanti = Path(kaynak.split("?")[0]).suffix.lower() or ".jpg"
        if uzanti not in yukleme.IZINLI_UZANTILAR:
            uzanti = ".jpg"
        hedef = hedef.with_suffix(uzanti)
        hedef.write_bytes(ham)

    return f"uploads/news/{hedef.name}"


# ============================================================
#  Ekleme
# ============================================================
def _slug_var_mi(slug: str) -> bool:
    return db.session.query(News.id).filter_by(slug=slug).first() is not None


def ekle(statik: Path, azami: int) -> tuple[int, int]:
    """Eksik haberleri ekler. -> (eklenen, atlanan)"""
    from app import kategoriler

    eklenen = atlanan = 0
    for veri in HABERLER:
        temel = slugify(veri["title_tr"])
        if _slug_var_mi(temel):
            atlanan += 1
            continue

        slug = benzersiz_slug(veri["title_tr"], _slug_var_mi)
        kategori = kategoriler.bul(veri["kategori"])

        # Govdenin sonuna kaynak baglantisi. Icerik duz metin oldugu
        # icin baglanti tiklanabilir degil, adres olarak duruyor.
        govde_tr = veri["content_tr"] + "\n\nKaynak: " + veri["kaynak"]
        govde_en = veri["content_en"] + "\n\nSource: " + veri["kaynak"]

        haber = News(
            slug=slug,
            date=veri["date"],
            is_published=veri["is_published"],
            title_tr=veri["title_tr"],
            title_en=veri["title_en"],
            category_tr=kategori.tr if kategori else "",
            category_en=kategori.en if kategori else "",
            summary_tr=veri["summary_tr"],
            summary_en=veri["summary_en"],
            content_tr=govde_tr,
            content_en=govde_en,
            image="",
        )
        db.session.add(haber)

        durum = "yayinda" if veri["is_published"] else "TASLAK"
        print(f"  + {slug}  [{durum}]")

        kaynaklar = veri["gorseller"][:azami]
        if len(veri["gorseller"]) > azami:
            print(f"      ! {len(veri['gorseller'])} gorsel verilmis, "
                  f"limit {azami} -- fazlasi atlandi")

        for sira, kaynak in enumerate(kaynaklar, start=1):
            yol = _gorsel_yaz(kaynak, slug, sira, statik)
            if yol is None:
                continue
            haber.images.append(NewsImage(path=yol, position=sira - 1))
            nereden = "indirildi" if kaynak.startswith("http") else "depodan"
            print(f"      {sira}. {Path(yol).name}  ({nereden})")

        # Kapak = galerinin ilki. Panelde degistirilebilir
        # (bkz. app/blueprints/admin/news.py -> _kapak_yaz).
        if haber.images:
            haber.image = haber.images[0].path
        else:
            print("      ! hic gorsel eklenemedi")

        eklenen += 1

    db.session.commit()
    return eklenen, atlanan


def listele() -> None:
    kayitlar = db.session.query(News).order_by(News.date.desc()).all()
    if not kayitlar:
        print("veritabani bos")
        return
    print(f"{'tarih':12} {'durum':8} {'gorsel':7} {'slug':52} baslik")
    print("-" * 118)
    for h in kayitlar:
        durum = "yayinda" if h.is_published else "TASLAK"
        print(f"{h.date.isoformat():12} {durum:8} {len(h.images):<7} "
              f"{h.slug:52} {h.title_tr}")
    print(f"\ntoplam {len(kayitlar)} "
          f"({sum(1 for h in kayitlar if h.is_published)} yayinda, "
          f"{sum(1 for h in kayitlar if not h.is_published)} taslak)")


def main() -> int:
    ayrıştırıcı = argparse.ArgumentParser(description=__doc__)
    ayrıştırıcı.add_argument("--liste", action="store_true",
                             help="veritabanindaki haberleri goster")
    ayrıştırıcı.add_argument("--sifirla", action="store_true",
                             help="once butun haberleri sil")
    secenek = ayrıştırıcı.parse_args()

    app = create_app()
    with app.app_context():
        if secenek.liste:
            listele()
            return 0

        statik = Path(app.config["STATIC_DIR"])
        azami = app.config.get("MAX_NEWS_IMAGES", 5)

        if secenek.sifirla:
            for haber in db.session.query(News).all():
                for gorsel in list(haber.images):
                    yukleme.sil_dosya(gorsel.path)
            silinen = db.session.query(News).delete()
            db.session.commit()
            print(f"{silinen} haber silindi\n")

        eklenen, atlanan = ekle(statik, azami)
        print(f"\neklenen: {eklenen}   zaten vardi: {atlanan}")
        print()
        listele()
    return 0


if __name__ == "__main__":
    sys.exit(main())
