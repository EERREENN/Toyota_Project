# -*- coding: utf-8 -*-
"""Turkce -> Ingilizce metin sozlugu.

Sablonlardaki her {{ _('...') }} cagrisi buraya bakar: anahtar Turkce
metnin KENDISI, degeri Ingilizcesi. Karsiligi yazilmamis bir metin
Turkce haliyle gosterilir -- eksik ceviri sayfayi bozmaz.

Bu yuzden sablonlarda yalnizca INGILIZCESI FARKLI OLAN metinler _()
icine alinir. Ozel isimler, sayilar, yer adlari ("Prius", "1994",
"Arifiye / Sakarya") duz metin olarak durur.

Yeni metin eklerken: sablona {{ _('Turkce metin') }} yaz, karsiligini
asagiya ekle. Bittiginde  python tools/kontrol.py  ile dogrula.
"""

from __future__ import annotations

EN: dict[str, str] = {
    # ----------------------------------------------------------
    #  Kabuk (menu, dil secici)
    # ----------------------------------------------------------
    "Menü": "Menu",
    "Dil seçimi": "Language selection",

    # ----------------------------------------------------------
    #  TMMT sayfasi
    # ----------------------------------------------------------
    "TMMT (Toyota Motor Manufacturing Türkiye), 1990 yılında \"Toyotasa\" adıyla "
    "kuruldu ve üretime 1994'te Corolla Sedan ile başladı. Fabrika, Sakarya'nın "
    "Arifiye ilçesinde yer alıyor ve bugün Toyota'nın Avrupa'daki en önemli üretim "
    "üslerinden biri konumunda.":
        "TMMT (Toyota Motor Manufacturing Türkiye) was founded in 1990 under the name "
        "\"Toyotasa\" and started production with the Corolla Sedan in 1994. The factory "
        "is located in Arifiye district of Sakarya and is today one of Toyota's most "
        "important production bases in Europe.",
    "Şirketin bugünkü ortaklık yapısı <strong>Toyota Motor Europe NV/SA "
    "(%90)</strong> ve <strong>Mitsui &amp; Co. (%10)</strong> şeklinde.":
        "The current partnership structure of the company is between <strong>Toyota "
        "Motor Europe NV/SA (90%)</strong> and <strong>Mitsui &amp; Co. "
        "(10%)</strong>.",
    "Vizyon ve Misyon": "Vision and Mission",
    "Vizyon": "Vision",
    "Üretimde küresel mükemmellik.": "Global excellence in manufacturing.",
    "Misyon": "Mission",
    "Üstün kaliteyle beğeni toplayan ürünler üretmek.":
        "To produce acclaimed products with superior quality.",
    "Kurumsal bilgiler": "Corporate information",
    "Konum": "Location",
    "Kuruluş": "Establishment",
    "Üretimin başlangıcı": "Start of production",
    "Ortaklık yapısı": "Partnership structure",
    "Toyota Motor Europe NV/SA (%90), Mitsui &amp; Co. Ltd. (%10)":
        "Toyota Motor Europe NV/SA (90%), Mitsui &amp; Co. Ltd. (10%)",
    "Toplam yatırım": "Total investment",
    "yaklaşık 2,5 milyar €": "approximately €2.5 billion",
    "Yıllık üretim kapasitesi": "Annual production capacity",
    "280.000 araç": "280,000 vehicles",
    "Çalışan sayısı": "Number of employees",
    "yaklaşık 5.000–5.400": "about 5,000–5,400",
    "Üretilen modeller": "Models produced",
    "Arazi alanı / kapalı alan": "Land area/covered area",
    "Bu kapasiteyle TMMT, Avrupa'daki en yüksek hacimli Toyota fabrikası.":
        "With this capacity, TMMT is the highest volume Toyota plant in Europe.",
    "Çalışan": "Worker",
    "Üretimden mühendisliğe pek çok farklı alanda istihdam.":
        "Employment in many different fields from production to engineering.",
    "2024 üretim adedi": "2024 production quantity",
    "Fabrikanın 2024 yılında ürettiği toplam araç sayısı.":
        "The total number of vehicles produced by the factory in 2024.",
    "TMMT bugün başlıca iki model ailesi üretiyor: <strong>Toyota Corolla "
    "Sedan</strong> ve <strong>Toyota C-HR</strong> (klasik hibrit ve şarj "
    "edilebilir hibrit / PHEV versiyonlarıyla). Kasım 2023'ten bu yana fabrika, "
    "C-HR PHEV'in bataryasını da üretiyor; bu, Toyota'nın Avrupa'da PHEV bataryası "
    "üreten ilk fabrikası olması anlamına geliyor.":
        "TMMT today mainly produces two model families: <strong>Toyota Corolla "
        "Sedan</strong> and <strong>Toyota C-HR</strong> (with classic hybrid and "
        "plug-in hybrid / PHEV versions). Since November 2023, the factory has also "
        "been producing the battery for the C-HR PHEV; This means it will be Toyota's "
        "first factory in Europe to produce PHEV batteries.",
    "Fabrikada bir aracın yolculuğu": "The journey of a vehicle in the factory",
    "Bir aracın çelik rulodan yola çıkıp fabrikadan tamamlanmış olarak ayrılmasına "
    "kadar geçtiği altı durak. Bir adıma dokunarak o bölümde ne yapıldığını "
    "görebilirsiniz.":
        "The six stops a vehicle goes through before it leaves the steel coil and "
        "leaves the factory completed. By tapping a step you can see what's being done "
        "in that section.",
    "Pres Fabrikası": "Press Factory",
    "Çelik rulolar düz plakalara dönüştürülür ve pres hatlarında aracın kaput, "
    "kapı, tavan gibi gövde panellerine şekillendirilir.":
        "Steel rolls are converted into flat plates and shaped into body panels such "
        "as the hood, doors and ceiling of the vehicle on press lines.",
    "Kaynak Fabrikası": "Welding Factory",
    "Preste şekillenen paneller, yüksek hassasiyetli robotlar ve deneyimli "
    "ekiplerle birleştirilerek aracın gövdesi oluşturulur.":
        "The panels shaped by the press are combined with high-precision robots and "
        "experienced teams to form the body of the vehicle.",
    "Boya Fabrikası": "Paint Factory",
    "Gövde yalnızca renklendirilmez; korozyona karşı korunur ve ses yalıtımı "
    "sağlanır. Çok katmanlı bir süreçtir.":
        "The body is not only colored; It is protected against corrosion and sound "
        "insulation is provided. It is a multi-layered process.",
    "Montaj Fabrikası": "Assembly Factory",
    "Boyalı gövde hatta girer; motor, iç döşeme, cam ve elektronik parçalar \"tam "
    "zamanında\" prensibiyle istasyonlara ulaştırılarak monte edilir.":
        "The painted body enters the line; The engine, interior trim, glass and "
        "electronic parts are delivered to the stations and assembled on the \"just in "
        "time\" principle.",
    "Kalite": "Quality",
    "Temel prensip \"yerinde kalite\": hata tespit edildiği anda çözülür, bir "
    "sonraki sürece asla geçmez.":
        "The basic principle is \"quality in place\": the error is resolved as soon as "
        "it is detected, never passing on to the next process.",
    "Üretim Kontrol": "Production Control",
    "Günlük üretim planının takibi ve binlerce parçanın tedarikçilerden hatta "
    "kadar senkronizasyonu bu grup tarafından yürütülür.":
        "The monitoring of the daily production plan and the synchronization of "
        "thousands of parts from suppliers to the line are carried out by this group.",
    "İhracat ve kilometre taşları": "Exports and milestones",
    "Üretimin büyük bölümü, ağırlıklı olarak Avrupa'ya, ayrıca Orta Doğu ve "
    "Afrika'ya ihraç ediliyor. Fabrika, 2021 yılında 3 milyonuncu aracını üretti "
    "ve Türkiye'nin en büyük ihracatçı sanayi kuruluşlarından biri.":
        "The majority of production is exported, mainly to Europe, but also to the "
        "Middle East and Africa. The factory produced its 3 millionth vehicle in 2021 "
        "and is one of Türkiye's largest exporting industrial enterprises.",
    "Şirketin \"Toyotasa\" adıyla kuruluşu":
        "Establishment of the company under the name \"Toyotasa\"",
    "Corolla Sedan ile üretimin başlaması": "Start of production with Corolla Sedan",
    "Toyota C-HR üretiminin başlaması": "Start of Toyota C-HR production",
    "3 milyonuncu aracın üretimi": "Production of the 3 millionth vehicle",
    "Yeni nesil C-HR ve Avrupa'daki ilk PHEV batarya hattı":
        "New generation C-HR and the first PHEV battery line in Europe",
    "215.645 araç üretimi": "215,645 vehicles produced",
    "İhracat pazarları": "Export markets",
    "Arifiye'deki fabrikada üretilen araçların büyük bölümü yurt dışına "
    "gönderiliyor; başlıca pazarlar Avrupa ülkeleri ile Orta Doğu ve Kuzey Afrika. "
    "Haritada üretim tesisi ve başlıca ihracat pazarları işaretli — bir noktaya "
    "tıklayarak ülke adını ve kısa notu görebilirsin.":
        "Most of the vehicles produced in the factory in Arifiye are sent abroad; The "
        "main markets are European countries and the Middle East and North Africa. The "
        "production facility and major export markets are marked on the map — click on "
        "a dot to see the country name and brief note.",
    "Corolla Sedan ve C-HR (HEV / PHEV) üretim tesisi":
        "Corolla Sedan and C-HR (HEV/PHEV) production facility",
    "Üretim tesisi (Sakarya)": "Production facility (Sakarya)",
    "Almanya": "Germany",
    "Batı Avrupa": "Western Europe",
    "Avrupa'nın en büyük otomobil pazarı.": "Europe's largest automobile market.",
    "Başlıca ihracat pazarı": "Major export market",
    "Birleşik Krallık": "United Kingdom",
    "Başlıca ihracat pazarlarından biri.": "One of the main export markets.",
    "Fransa": "France",
    "Belçika": "Belgium",
    "Toyota Motor Europe'un merkezi Brüksel'de.":
        "Toyota Motor Europe is headquartered in Brussels.",
    "Hollanda": "Netherlands",
    "İtalya": "Italy",
    "Güney Avrupa": "Southern Europe",
    "İspanya": "Spain",
    "Polonya": "Poland",
    "Orta Avrupa": "Central Europe",
    "Çekya": "Czechia",
    "İsrail": "Israel",
    "Orta Doğu": "Middle East",
    "Birleşik Arap Emirlikleri": "United Arab Emirates",
    "Suudi Arabistan": "Saudi Arabia",
    "Mısır": "Egypt",
    "Kuzey Afrika": "North Africa",
    "Fas": "Morocco",
    "Güney Afrika": "South Africa",
    "PHEV Batarya Hattı": "PHEV Battery Line",
    "Kasım 2023'ten bu yana TMMT, C-HR'ın şarj edilebilir hibrit (PHEV) "
    "versiyonunun bataryasını da üretiyor. Bu, Toyota'nın Avrupa'daki tesisleri "
    "arasında bir ilk: Sakarya fabrikası hem şarj edilebilir otomobil hem de "
    "bataryasını üreten ilk Toyota Avrupa fabrikası. Üretim, Toyota'nın TNGA-2 "
    "platformu üzerinde yapılıyor ve fabrika, Toyota'nın Avrupa'daki "
    "elektrifikasyon dönüşümünde merkezi bir rol üstleniyor.":
        "Since November 2023, TMMT has also been producing the battery for the plug-in "
        "hybrid (PHEV) version of the C-HR. This is a first among Toyota's facilities "
        "in Europe: The Sakarya factory is the first Toyota European factory to "
        "produce both rechargeable cars and batteries. Production is on Toyota's "
        "TNGA-2 platform, and the factory plays a central role in Toyota's "
        "electrification transformation in Europe.",
    "Yeni nesil C-HR ve batarya hattı için yapılan ek yatırım":
        "Additional investment for the new generation C-HR and battery line",
    "308 milyon €": "€308 million",
    "Yıllık batarya üretim kapasitesi (adet)": "Annual battery production capacity (pieces)",
    "75.000": "75,000",
    "Hat için istihdam edilen ek uzman çalışan":
        "Additional expert employee employed for the line",
    "Üretim yaklaşımı ve çevre": "Production approach and environment",
    "TMMT, kuruluşundan bu yana <strong>Toyota Production System (TPS)</strong> "
    "ilkeleriyle çalışıyor. Fabrika 1999'dan beri ISO 14001 çevre yönetim sistemi "
    "sertifikasına sahip ve enerji/su verimliliği ile atık azaltımına yönelik "
    "sürekli iyileştirme (kaizen) projeleri yürütüyor.":
        "TMMT has been working with <strong>Toyota Production System (TPS)</strong> "
        "principles since its establishment. The factory has been certified with ISO "
        "14001 environmental management system since 1999 and carries out continuous "
        "improvement (kaizen) projects for energy/water efficiency and waste "
        "reduction.",
    "Toplumla birlikte": "Together with the community",
    "TMMT'nin Sakarya ve çevresinde yıllardır sürdürdüğü sosyal sorumluluk "
    "çalışmalarından dördü.":
        "Four of the social responsibility activities that TMMT has been carrying out "
        "in Sakarya and its surroundings for years.",
    "Trafik Güvenliği Resim Yarışması": "Traffic Safety Painting Competition",
    "Genç yeteneklerin trafik güvenliği bilincini görsel sanatlarla ifade ettiği yarışma.":
        "Competition where young talents express traffic safety awareness through "
        "visual arts.",
    "Teknik Proje Yarışması": "Technical Project Competition",
    "Sakarya İl Millî Eğitim Müdürlüğü iş birliğiyle ilköğretim ve lise "
    "öğrencileri arasında düzenlenen proje yarışması.":
        "Project competition organized among primary and high school students in "
        "cooperation with Sakarya Provincial Directorate of National Education.",
    "“Önce Bağış Sonra Fabrika Turu”": "“First Donation Then Factory Tour”",
    "Bağış yapan ziyaretçilere fabrika turu imkânı sunan sosyal sorumluluk projesi.":
        "A social responsibility project that offers factory tours to visitors who donate.",
    "Kan Bağışı Kampanyası": "Blood Donation Campaign",
    "Kızılay'ın Güvenli Kan Temini Projesi kapsamında her yıl tekrarlanan çalışan "
    "kan bağışı kampanyası.":
        "Employee blood donation campaign repeated every year within the scope of Red "
        "Crescent's Safe Blood Supply Project.",
    "Kariyer": "Career",
    "TMMT, üretimden mühendisliğe, kalite kontrolden lojistiğe kadar çok farklı "
    "alanda binlerce kişiye istihdam sağlıyor. Gerçek anlamda küresel bir şirkette "
    "çalışma ve gelişme imkânı sunuyor.":
        "TMMT employs thousands of people in many different fields, from production to "
        "engineering, from quality control to logistics. It offers the opportunity to "
        "work and develop in a truly global company.",
    "Toyota Türkiye'de Çalışmak": "Working at Toyota Türkiye",
    "Daha fazlası →": "More →",
    "Üretim, mühendislik, kalite ve lojistik alanlarındaki kariyer imkânları ve "
    "çalışan deneyimi.":
        "Career opportunities and employee experience in the fields of production, "
        "engineering, quality and logistics.",
    "Staj Programı": "Internship Program",
    "Üniversite öğrencilerine yönelik staj başvuruları ve program takvimi.":
        "Internship applications and program calendar for university students.",
    "Açık Pozisyonlar": "Open Positions",
    "Güncel iş ilanları ve başvuru adımları.": "Current job postings and application steps.",
    "Sertifikalar ve ödüller": "Certificates and awards",
    "ISO 14001 Çevre Yönetim Sistemi": "ISO 14001 Environmental Management System",
    "1999'dan bu yana": "since 1999",
    "TİM İhracat Ödülü": "TİM Export Award",
    "Toyota Avrupa'nın en yüksek hacimli fabrikası": "Toyota Europe's highest volume factory",
    "Toyota iç değerlendirmesinde en üst “lider fabrika” seviyesi":
        "The highest “leading factory” level in Toyota internal evaluation",
    "Kaynaklar": "Resources",
    "global.toyota – resmi haber duyuruları": "global.toyota – official news announcements",

    # ----------------------------------------------------------
    #  Global Toyota sayfasi
    # ----------------------------------------------------------
    "1937'de Japonya'da, Sakichi Toyoda'nın otomatik dokuma tezgahı patentinden "
    "elde ettiği gelirle Kiichiro Toyoda tarafından kurulan Toyota, bugün dünyanın "
    "en büyük otomotiv üreticilerinden biri. Merkezi hâlâ Japonya'daki Toyota "
    "City'de bulunuyor, ama üretim ve satış ağı altı kıtaya yayılmış durumda.":
        "Founded in Japan in 1937 by Kiichiro Toyoda with the income from Sakichi "
        "Toyoda's automatic loom patent, Toyota is today one of the largest automotive "
        "manufacturers in the world. Its headquarters are still located in Toyota City "
        "in Japan, but its production and sales network has spread across six "
        "continents.",
    "Bu sayfada": "On this page",
    "“Mobility for All” arayışıyla “Happiness for All” üretmek.":
        "Producing “Happiness for All” through the quest for “Mobility for All”.",
    "Toyota'nın misyonu, herkes için erişilebilir hareketlilik sağlayarak herkes "
    "için mutluluk üretmek. Bu, yalnızca otomobil üretmek değil; insanların "
    "özgürce hareket edebildiği bir toplum kurmak anlamına geliyor.":
        "Toyota's mission is to create happiness for all by providing accessible "
        "mobility for all. This is not just about producing cars; It means "
        "establishing a society where people can move freely.",
    "Şirket bugün kendini bir otomobil üreticisinden bir hareketlilik (mobility) "
    "şirketine dönüştürüyor. Bağlantılı, otonom, paylaşımlı ve elektrikli (CASE) "
    "teknolojiler bu dönüşümün merkezinde yer alıyor; hedefler Environmental "
    "Challenge 2050 ve Birleşmiş Milletler Sürdürülebilir Kalkınma Amaçları ile "
    "hizalı.":
        "Today, the company is transforming itself from an automobile manufacturer "
        "into a mobility company. Connected, autonomous, shared and electric (CASE) "
        "technologies are at the center of this transformation; The targets are "
        "aligned with the Environmental Challenge 2050 and the United Nations "
        "Sustainable Development Goals.",
    "1935'ten bu yana üretilen toplam araç": "Total vehicles produced since 1935",
    "300.000.000+": "300,000,000+",
    "Bu kilometre taşına Kasım 2023'te ulaşıldı.":
        "This milestone was reached in November 2023.",
    "Dünya genelinde, üretimden mühendisliğe pek çok farklı alanda.":
        "Around the world, in many different fields from production to engineering.",
    "Ülke ve bölge": "Country and region",
    "Toyota araçlarının satıldığı pazar sayısı.":
        "Number of markets where Toyota vehicles are sold.",
    "Üretim şirketi": "manufacturing company",
    "Japonya dışında da onlarca ülkede kurulu fabrika ve iştirak.":
        "Factories and subsidiaries established in dozens of countries outside Japan.",
    "Toyota'nın hikâyesi": "Toyota's story",
    "Bir dokuma tezgâhından küresel bir hareketlilik şirketine: Toyota'nın dönüm "
    "noktaları. Bir yıla dokunarak o adımın ayrıntısını görebilirsiniz.":
        "From a loom to a global mobility company: Toyota's milestones. By tapping on "
        "a year, you can see the detail of that step.",
    "Otomatik dokuma tezgâhı": "Automatic loom",
    "Sakichi Toyoda'nın geliştirdiği tezgâh, iplik koptuğunda kendi kendini "
    "durduruyordu. Bugünkü jidoka ilkesinin kökeni bu makinedir.":
        "The loom developed by Sakichi Toyoda stopped itself when the thread broke. "
        "This machine is the origin of today's jidoka principle.",
    "Patentin Platt Brothers'a satılması": "Sale of patent to Platt Brothers",
    "Dokuma tezgâhının patenti İngiliz Platt Brothers'a satıldı; elde edilen gelir "
    "otomobil çalışmalarının sermayesi oldu.":
        "The patent for the loom was sold to the British Platt Brothers; The income "
        "generated became the capital of the automobile works.",
    "Toyota Motor Co. Ltd.'in kuruluşu": "Founding of Toyota Motor Co., Ltd.",
    "Kiichiro Toyoda liderliğinde, dokuma tezgâhı işinden ayrılan otomobil bölümü "
    "bağımsız bir şirkete dönüştü.":
        "Under the leadership of Kiichiro Toyoda, the automobile division was "
        "separated from the loom business and became an independent company.",
    "İlk denizaşırı adımlar": "First overseas steps",
    "Toyota'nın ilk denizaşırı ihracat adımları atıldı ve ABD pazarına giriş yapıldı.":
        "Toyota's first overseas export steps were taken and the US market was entered.",
    "Corolla'nın tanıtımı": "Introduction of Corolla",
    "Dünyanın en çok satan otomobil ailesinin başlangıcı.":
        "The beginning of the world's best-selling car family.",
    "Dünyanın ilk seri üretim hibrit otomobili.":
        "The world's first mass-produced hybrid car.",
    "Hidrojen yakıt hücreli seri üretim otomobil.":
        "Mass production car with hydrogen fuel cells.",
    "Woven City'nin temelinin atılması": "Laying the foundation of Woven City",
    "Fuji Dağı eteğinde inşa edilen deneysel “yaşayan laboratuvar” şehrin temeli atıldı.":
        "The foundations of the experimental “living laboratory” city built at the "
        "foot of Mount Fuji were laid.",
    "Woven City'nin açılışı": "The opening of Woven City",
    "25 Eylül 2025'te resmen açıldı; ilk “Weaver” sakinler taşınmaya başladı.":
        "Officially opened on September 25, 2025; the first “Weaver” residents began "
        "moving in.",
    "Toyota Way: iki sütun, beş değer": "Toyota Way: two pillars, five values",
    "Toyota'nın çalışma kültürü iki sütun üzerine kurulu; bu sütunların altında "
    "şirketin her kademesinde tekrarlanan beş temel değer var.":
        "Toyota's work culture is based on two pillars; Underneath these pillars are "
        "five core values ​​that are repeated at every level of the company.",
    "Sürekli İyileştirme": "Continuous Improvement",
    "Meydan okuma": "Challenge",
    "Uzun vadeli bir vizyon kurmak ve hedeflere cesaret ve yaratıcılıkla ilerlemek.":
        "Establishing a long-term vision and pursuing goals with courage and creativity.",
    "Sürekli iyileştirme": "Continuous improvement",
    "Hiçbir sürecin mükemmel olmadığını kabul edip her gün küçük adımlarla ilerlemek.":
        "Accepting that no process is perfect and taking small steps every day.",
    "Yerinde gör": "See it on site",
    "Karar vermeden önce sorunun yaşandığı yere gidip gerçeği kendi gözünle görmek.":
        "Before making a decision, go to the place where the problem occurs and see "
        "the truth with your own eyes.",
    "Bu ilkelerin üretim hattındaki karşılığı: Toyota Production System":
        "The equivalent of these principles on the production line: Toyota Production "
        "System",
    "İnsana Saygı": "Respect for People",
    "Saygı": "Respect",
    "Paydaşlara saygı duymak, sorumluluk almak, karşılıklı güven inşa etmek.":
        "Respecting stakeholders, taking responsibility, building mutual trust.",
    "Takım çalışması": "teamwork",
    "Bireysel gelişimi teşvik ederek ekip performansını en üst düzeye çıkarmak.":
        "Maximizing team performance by encouraging individual development.",
    "Elektrikli Araç ve Rekabet Ortamı": "Electric Vehicle and Competitive Environment",
    "2025'te Toyota'nın sattığı araçların yaklaşık 200 bini tam elektrikliydi — "
    "bir önceki yıla göre yüzde 42'lik bir artış. Yine de şirket, elektrikli "
    "araçlara topyekûn geçmek yerine hibrit, şarj edilebilir hibrit, tam "
    "elektrikli ve hidrojen yakıt hücreli araçları bir arada geliştiren \"çoklu "
    "yol\" stratejisine bağlı kalıyor. Bu arada BYD, SAIC ve Geely gibi Çinli "
    "üreticilerin özellikle elektrikli araç segmentinde hızla büyümesi, Toyota'nın "
    "önümüzdeki yıllarda karşılaşacağı en büyük rekabet baskılarından biri olarak "
    "görülüyor.":
        "Nearly 200,000 of the vehicles Toyota sold in 2025 were fully electric — a 42 "
        "percent increase from the previous year. Still, the company is sticking to "
        "its \"multi-track\" strategy, developing a combination of hybrid, plug-in "
        "hybrid, fully electric and hydrogen fuel cell vehicles, rather than an "
        "all-out switch to electric vehicles. Meanwhile, the rapid growth of Chinese "
        "manufacturers such as BYD, SAIC and Geely, especially in the electric vehicle "
        "segment, is seen as one of the biggest competitive pressures that Toyota will "
        "face in the coming years.",
    "Üretim Tesisleri Haritası": "Production Facilities Map",
    "Toyota'nın araçlarını sattığı 170'ten fazla ülke ile araçlarını "
    "<strong>ürettiği</strong> yerler aynı şey değil. Aşağıdaki harita, altı "
    "kıtaya yayılmış başlıca üretim ve montaj tesislerini gösteriyor — fareyle "
    "sürükleyerek gezebilir, tekerlekle yakınlaştırabilir, bir noktaya tıklayarak "
    "o tesis hakkında bilgi görebilirsin.":
        "The more than 170 countries where Toyota sells its vehicles are not the same "
        "as the places where it produces its vehicles. The map below shows major "
        "manufacturing and assembly facilities spread across six continents — you can "
        "navigate by mouse-drag, wheel-to-zoom, or click on a point to see information "
        "about that facility.",
    "Ana üretim kümesi: Honsha, Motomachi, Tsutsumi, Tahara ve daha fazlası":
        "Main production cluster: Honsha, Motomachi, Tsutsumi, Tahara and more",
    "Üretim tesisi": "production facility",
    "Lexus ES / RX / NX / UX, motor": "Lexus ES/RX/NX/UX, engine",
    "Şanzıman ve aktarma organları": "Transmission and drivetrain",
    "Camry, RAV4, motor": "Camry, RAV4, engine",
    "Motor, Corolla Cross (Mazda ortak girişimi)":
        "Engine, Corolla Cross (Mazda joint venture)",
    "San Antonio, Teksas": "San Antonio, Texas",
    "Buffalo, Batı Virginia": "Buffalo, West Virginia",
    "Motor, şanzıman": "engine, transmission",
    "Alüminyum silindir kapağı": "aluminum cylinder head",
    "Liberty, Kuzey Karolina": "Liberty, North Carolina",
    "Batarya paketleri (2025)": "Battery packs (2025)",
    "Cambridge / Woodstock, Ontario": "Cambridge/Woodstock, Ontario",
    "RAV4, Lexus RX / NX": "RAV4, Lexus RX/NX",
    "Tacoma kasası": "Tacoma chassis",
    "Dyna, Land Cruiser, Toyota Sora otobüsü": "Dyna, Land Cruiser, Toyota Sora bus",
    "Corolla hatchback / estate": "Corolla hatchback/estate",
    "Deeside, Galler": "Deeside, Wales",
    "Bidadi, Karnataka": "Bidadi,Karnataka",
    "Karawang, Batı Java": "Karawang, West Java",
    "Detaylı bilgi için tıkla →": "Click for detailed information →",
    "Avrupa'da Toyota": "Toyota in Europe",
    "Toyota'nın Avrupa operasyonları, merkezi Brüksel'de bulunan Toyota Motor "
    "Europe tarafından yürütülüyor. Şirketin Avrupa genelinde birden fazla üretim "
    "tesisi, Ar-Ge ve tasarım merkezi bulunuyor. Sakarya'daki TMMT, bu yapının en "
    "yüksek hacimli üretim tesislerinden biri ve Toyota'nın Avrupa'daki "
    "elektrifikasyon dönüşümünde merkezi bir rol üstleniyor.":
        "Toyota's European operations are run by Toyota Motor Europe, headquartered in "
        "Brussels. The company has multiple production facilities, R&D and design "
        "centers across Europe. TMMT in Sakarya is one of this structure's highest "
        "volume production facilities and plays a central role in Toyota's "
        "electrification transformation in Europe.",
    "Avrupa'daki üretim tesisi sayısı": "Number of production facilities in Europe",
    "Türkiye'deki fabrikamız: TMMT →": "Our factory in Türkiye: TMMT →",
    "Toyota Motor Europe'un faaliyet gösterdiği ülke sayısı":
        "Number of countries where Toyota Motor Europe operates",
    "Avrupa'daki çalışan sayısı": "Number of employees in Europe",
    "Ödüller, Marka Değeri ve Kalite Sıralamaları": "Awards, Brand Value and Quality Rankings",
    "Bağımsız kuruluşların 2025-2026 değerlendirmelerinde Toyota, hem marka değeri "
    "hem de güvenilirlik tarafında otomotiv sektörünün önünde yer aldı.":
        "In the 2025-2026 evaluations of independent organizations, Toyota was ahead "
        "of the automotive industry in terms of both brand value and reliability.",
    "Kaynak: Interbrand, Brand Finance, J.D. Power, motor1.com, carexpert.com.au":
        "Source: Interbrand, Brand Finance, J.D. Power, motor1.com, carexpert.com.au",
    "Otomotivde kesintisiz 1. sıra; marka değeri 74,2 milyar dolar.":
        "Uninterrupted 1st place in automotive; brand value is 74.2 billion dollars.",
    "Üst üste 2 yıl dünyanın en değerli ve en güçlü otomobil markası (AAA+).":
        "The world's most valuable and most powerful automobile brand (AAA+) for 2 "
        "years in a row.",
    "J.D. Power — Lexus": "J.D. Power — Lexus",
    "Lexus, 4 yıl üst üste en güvenilir marka seçildi.":
        "Lexus was chosen as the most reliable brand for 4 consecutive years.",
    "J.D. Power — Toyota": "J.D. Power — Toyota",
    "En çok segment ödülünü alan üretici (6–9 model).":
        "Manufacturer with the most segment awards (6–9 models).",
    "En Çok Satan Grup": "Best Selling Group",
    "11,3 milyon araçla üst üste 6. kez dünyanın 1.'si.":
        "1st in the world for the 6th time in a row with 11.3 million vehicles.",
    "Toyota Grubu Marka Ailesi": "Toyota Group Brand Family",
    "Toyota yalnızca kendi markasından ibaret değil; tamamına sahip olduğu "
    "markaların yanında birkaç rakibinde de stratejik hisseler tutuyor.":
        "Toyota is not just about its own brand; In addition to its wholly owned "
        "brands, it also holds strategic stakes in several competitors.",
    "Kaynaklar: toyotaautodealer.com, slashgear.com":
        "Sources: toyotaautodealer.com, slashgear.com",
    "Tamamı Toyota'ya ait": "Wholly owned by Toyota",
    "Mazda ortaklığı, ABD Alabama'daki Mazda Toyota Manufacturing tesisinin "
    "temelini oluşturuyor.":
        "The Mazda partnership forms the basis of the Mazda Toyota Manufacturing "
        "facility in Alabama, USA.",
    "Stratejik hisseler": "Strategic shares",
    "yüzde 20 · oy hakkıyla": "with 20 percent voting rights",
    "Hino Motors'un önümüzdeki dönemde Mitsubishi Fuso ile yeni bir ittifaka dahil "
    "olacağı duyuruldu — grubun yapısının hâlâ hareketli olduğunu gösteren güncel "
    "bir detay.":
        "It has been announced that Hino Motors will enter into a new alliance with "
        "Mitsubishi Fuso in the coming period — an up-to-date detail that shows that "
        "the group's structure is still active.",
    "Markalar ve hizmetler": "Brands and services",
    "Ana marka; binek ve ticari araç ailesi":
        "Main brand; passenger and commercial vehicle family",
    "Avrupa'da ticari araç ve filo müşterilerine yönelik marka":
        "Brand for commercial vehicle and fleet customers in Europe",
    "Motorsporları ve performans araçları markası":
        "Motorsports and performance vehicles brand",
    "Abonelik, kiralama ve paylaşımlı mobilite hizmetleri markası":
        "Brand of subscription, rental and shared mobility services",
    "Yazılım, otonom sürüş ve Woven City projesini yürüten iştirak":
        "The subsidiary that carries out the software, autonomous driving and Woven "
        "City project",
    "Platform ve teknoloji": "Platform and technology",
    "TMMT'de TNGA-2 üretimi →": "TNGA-2 production at TMMT →",
    "Toyota'nın küresel araç platformu. Ortak bir mimari üzerinden farklı "
    "segmentlerde araç geliştirmeyi mümkün kılıyor; daha düşük ağırlık merkezi, "
    "daha iyi sürüş dinamiği ve daha verimli üretim sağlıyor. TMMT'de üretilen "
    "yeni nesil C-HR de bu platformun TNGA-2 versiyonu üzerinde üretiliyor.":
        "Toyota's global vehicle platform. It makes it possible to develop vehicles in "
        "different segments through a common architecture; lower center of gravity, "
        "better driving dynamics and more efficient production. The new generation "
        "C-HR produced at TMMT is also produced on the TNGA-2 version of this "
        "platform.",
    "Toyota'nın standart olarak sunduğu sürücü destek ve aktif güvenlik "
    "teknolojileri paketi. Şirketin uzun vadeli hedefi trafikte sıfır kaza; "
    "teknolojiler bu hedefe yönelik olarak sürekli geliştiriliyor.":
        "Toyota's standard suite of driver assistance and active safety technologies. "
        "The company's long-term goal is zero traffic accidents; Technologies are "
        "constantly being developed towards this goal.",
    "Ar-Ge ve tasarım": "R&D and design",
    "Toyota'nın araştırma ve tasarım faaliyetleri Japonya ile sınırlı değil; "
    "Avrupa, Kuzey Amerika ve Asya'ya yayılmış merkezlerde yürütülüyor.":
        "Toyota's research and design activities are not limited to Japan; It is "
        "carried out in centers spread across Europe, North America and Asia.",
    "Toyota Motor Europe Ar-Ge Merkezi": "Toyota Motor Europe R&D Center",
    "Zaventem, Belçika": "Zaventem, Belgium",
    "Avrupa pazarına yönelik araç geliştirme ve mühendislik.":
        "Vehicle development and engineering for the European market.",
    "Nice, Fransa": "Nice, France",
    "Avrupa'ya yönelik ileri tasarım stüdyosu.": "Advanced design studio for Europe.",
    "Köln, Almanya": "Cologne, Germany",
    "Motorsporları geliştirme ve yüksek performans mühendisliği.":
        "Motorsport development and high performance engineering.",
    "Kaliforniya, ABD": "California, USA",
    "Yapay zekâ, otonom sürüş ve robotik araştırmaları.":
        "Artificial intelligence, autonomous driving and robotics research.",
    "Tokyo, Japonya": "Tokyo, Japan",
    "Yazılım tanımlı araç ve Woven City projesi.":
        "Software-defined vehicle and the Woven City project.",
    "Hidrojen ve Katı Hal Batarya Teknolojisi": "Hydrogen and Solid State Battery Technology",
    "Toyota'nın \"çoklu yol\" stratejisi bataryalı elektrikle sınırlı değil; "
    "hidrojen ve yeni nesil batarya kimyaları da paralel olarak geliştiriliyor.":
        "Toyota's \"multi-track\" strategy isn't limited to battery electric; Hydrogen "
        "and next-generation battery chemistries are also being developed in parallel.",
    "Mirai — Hidrojen yakıt hücresi": "Mirai — Hydrogen fuel cell",
    "182 beygir güç ve ABD EPA testine göre yaklaşık 647 km (402 mil) menzil. "
    "Egzozdan çıkan tek atık su.":
        "182 horsepower and a range of approximately 647 km (402 miles) according to "
        "US EPA testing. The only waste water coming out of the exhaust.",
    "Kaynak: pressroom.toyota.com": "Source: pressroom.toyota.com",
    "Katı hal bataryalar": "solid state batteries",
    "~1.200 km": "~1,200 km",
    "Sumitomo Metal Mining ve Idemitsu ortaklığıyla geliştiriliyor; 2027-2028'de "
    "araçlara girmesi hedefleniyor. Prototip paket yaklaşık 1.200 km menzil ve 10 "
    "dakikanın altında hızlı şarj vadediyor.":
        "It is being developed in partnership with Sumitomo Metal Mining and Idemitsu; "
        "It is aimed to enter vehicles in 2027-2028. The prototype package promises a "
        "range of approximately 1,200 km and fast charging in under 10 minutes.",
    "Kaynak: electrek.co": "Source: electrek.co",
    "Toyota'nın Sosyal Yüzü": "Social Face of Toyota",
    "Woven City": "woven city",
    "Kaynaklar: global.toyota, pressroom.toyota.com":
        "Sources: global.toyota, pressroom.toyota.com",
    "Fuji Dağı eteğinde inşa edilen deneysel \"yaşayan laboratuvar\" şehir.":
        "Experimental \"living laboratory\" city built at the foot of Mount Fuji.",
    "25 Eylül 2025'te resmen açıldı; ilk \"Weaver\" sakinler taşınmaya başladı.":
        "Officially opened on September 25, 2025; the first \"Weaver\" residents began "
        "to move in.",
    "Faz 1'de yaklaşık 300 kişilik bir nüfus hedefleniyor.":
        "A population of approximately 300 people is targeted in Phase 1.",
    "Japonya'nın ilk LEED for Communities Platin sertifikasını aldı.":
        "Received Japan's first LEED for Communities Platinum certification.",
    "Motorsporları — Toyota Gazoo Racing": "Motorsports — Toyota Gazoo Racing",
    "Kaynak: media.toyota.ca": "Source: media.toyota.ca",
    "Haziran 2026: 94. Le Mans 24 Saat'te 6. kez zafer; 3 yıllık kazanamama serisi "
    "sona erdi (350.105 seyirci).":
        "June 2026: 6th victory at the 94th 24 Hours of Le Mans; 3-year winless streak "
        "ended (350,105 spectators).",
    "Dünya Rallye Şampiyonası'nda üst üste 4. üretici şampiyonluğu.":
        "4th consecutive manufacturer's championship in the World Rallye Championship.",
    "Yönetim": "Management",
    "Yönetim Kurulu Başkanı": "Chairman of the Board",
    "Başkan ve CEO": "President and CEO",

    # ----------------------------------------------------------
    #  Toyota Production System sayfasi
    # ----------------------------------------------------------
    "Toyota Production System (TPS), İkinci Dünya Savaşı sonrasında Taiichi Ohno "
    "öncülüğünde geliştirilen ve Toyota'nın üretim felsefesinin temelini oluşturan "
    "yönetim sistemidir. Amacı, israfı (muda) ortadan kaldırarak müşteriye en "
    "yüksek kaliteyi, en düşük maliyetle ve en kısa sürede sunmaktır. Bugün dünya "
    "genelinde birçok sektörde \"yalın üretim\" (lean manufacturing) adıyla "
    "uygulanan yaklaşımın da temelini oluşturur.":
        "Toyota Production System (TPS) is the management system developed under the "
        "leadership of Taiichi Ohno after World War II and forms the basis of Toyota's "
        "production philosophy. Its aim is to eliminate waste (muda) and provide the "
        "highest quality to the customer at the lowest cost and in the shortest time. "
        "It forms the basis of the approach applied today in many sectors around the "
        "world called \"lean manufacturing\".",
    "TPS Evi": "TPS House",
    "TPS'i anlatmanın en bilinen yolu bir eve benzetmektir: çatı hedefleri, iki "
    "sütun sistemi taşıyan ilkeleri, temel ise hepsini mümkün kılan istikrarı "
    "gösterir. Bir parçaya dokunarak ayrıntısını görebilirsiniz.":
        "The most common way to describe TPS is to compare it to a house: the roof "
        "represents the principles that support the two-column system, and the "
        "foundation represents the stability that makes it all possible. By touching a "
        "part you can see its detail.",
    "Hedefler": "Goals",
    "En yüksek kalite · en düşük maliyet · en kısa teslim süresi · en yüksek "
    "güvenlik · en yüksek çalışan morali":
        "Highest quality · lowest cost · shortest delivery time · highest safety · "
        "highest employee morale",
    "Evin çatısı, tüm sistemin neye hizmet ettiğini söyler. Bu beş hedef "
    "birbirinden bağımsız değildir: kaliteyi yükselten bir iyileştirme genellikle "
    "maliyeti de düşürür, güvenli ve düzenli bir hat ise çalışan moralini "
    "yükseltir.":
        "The roof of the house tells what the entire system serves. These five goals "
        "are not independent of each other: an improvement that increases quality "
        "often reduces cost, and a safe and orderly line increases employee morale.",
    "Ev şeklinde bir şema. En üstteki çatıda hedefler yer alır. Çatıyı iki sütun "
    "taşır: solda Just-in-Time, sağda Jidoka. İki sütunun arasında, evin "
    "merkezinde insan ve takım çalışması bulunur. Hepsinin altında, evi ayakta "
    "tutan temel vardır. Aşağıdaki listeden her parçanın açıklamasını "
    "açabilirsiniz.":
        "A house-shaped diagram. The targets are located on the top roof. Two columns "
        "support the roof: Just-in-Time on the left, Jidoka on the right. Between the "
        "two pillars, people and teamwork are at the center of the house. Beneath it "
        "all is the foundation that keeps the house standing. You can open the "
        "description of each track from the list below.",
    "Just-in-Time (tam zamanında üretim)": "Just-in-Time",
    "Sürekli akış · çekme sistemi · takt zamanı · kanban":
        "Continuous flow · pull system · takt time · kanban",
    "Doğru parçanın, doğru anda, doğru miktarda hatta ulaşması. Üretimi başlatan "
    "şey tahmin değil, bir sonraki sürecin gerçek talebidir — buna çekme sistemi "
    "denir. Takt zamanı müşteri talebinin belirlediği üretim temposudur; kanban "
    "(çekme kartı) ise hangi parçadan ne zaman ne kadar gerektiğini hat üzerinde "
    "görünür kılar.":
        "The right part reaches the line at the right time, in the right quantity. It "
        "is not the forecast that starts production, but the actual demand of the next "
        "process — this is called a pull system. Takt time is the production tempo "
        "determined by customer demand; Kanban (pull card) makes it visible on the "
        "line how much of which part is needed and when.",
    "İnsan ve takım çalışması": "People and teamwork",
    "Sürekli iyileştirme · israfın ortadan kaldırılması":
        "Continuous improvement · elimination of waste",
    "İki sütunun arasındaki boşluk boş değildir: sistemi çalıştıran insandır. "
    "Sorunu gören, durduran ve çözen kişi hattın başındaki çalışandır. Sürekli "
    "iyileştirme ve israfın ortadan kaldırılması bir departmanın işi değil, her "
    "kademedeki takımın ortak sorumluluğudur.":
        "The space between the two columns is not empty: it is the human who runs the "
        "system. The person at the head of the line is the person who sees the "
        "problem, stops it and solves it. Continuous improvement and elimination of "
        "waste is not the job of one department, but the collective responsibility of "
        "the team at all levels.",
    "Jidoka (otonomasyon)": "Jidoka (autonomation)",
    "Otomatik durdurma · andon · poka-yoke · yerinde kalite":
        "Automatic stop · andon · poka-yoke · quality at the source",
    "\"İnsan dokunuşlu otomasyon\": makine bir sorun sezdiğinde kendi kendine durur, "
    "böylece hatalı ürün bir sonraki sürece geçmez. Andon (uyarı panosu) sorunu "
    "anında görünür kılar; poka-yoke (hata önleme) yanlış işlemi baştan imkânsız "
    "hale getiren basit düzeneklerdir. Kalite en sonda denetlenmez, oluştuğu yerde "
    "sağlanır.":
        "“Human touch automation”: the machine stops itself when it senses a problem, "
        "so the faulty product does not pass on to the next process. Andon (alert "
        "board) makes the problem instantly visible; poka-yoke (error prevention) are "
        "simple mechanisms that make the wrong operation impossible in the first "
        "place. Quality is not controlled at the end, it is ensured where it occurs.",
    "Temel": "Foundation",
    "Heijunka · standart iş · kaizen · görsel yönetim · istikrarlı süreçler":
        "Heijunka · standard work · kaizen · visual management · stable processes",
    "Sütunlar ancak sağlam bir zemin üzerinde durur. Heijunka (üretim dengeleme) "
    "iş yükünü zamana ve ürün çeşidine yayar; standart iş her işin bilinen en iyi "
    "yolunu tanımlar; kaizen (sürekli iyileştirme) o standardı her gün biraz daha "
    "ileri taşır; görsel yönetim ise hattın durumunu bakışta anlaşılır kılar.":
        "Columns can only stand on solid ground. Heijunka (production balancing) "
        "spreads the workload over time and product type; standard work defines the "
        "best known way of doing every job; kaizen (continuous improvement) moves that "
        "standard a little further every day; Visual management makes the status of "
        "the line clear at a glance.",
    "TPS nasıl doğdu": "How was TPS born?",
    "Sistem bir günde tasarlanmadı; üç kuşağın birbirini tamamlayan fikirlerinden "
    "oluştu. Bir adıma dokunarak ayrıntısını görebilirsiniz.":
        "The system wasn't designed in a day; It consisted of the complementary ideas "
        "of three generations. By touching a step you can see its detail.",
    "Sakichi Toyoda ve dokuma tezgâhı": "Sakichi Toyoda and the loom",
    "1920'ler": "1920s",
    "Sakichi Toyoda, ipliği koptuğunda kendi kendini durduran bir otomatik dokuma "
    "tezgâhı geliştirdi. Böylece bir işçinin tek bir tezgâhın başında beklemesi "
    "gerekmiyor, hatalı kumaş üretilmiyordu. Bu fikir, bugün jidoka olarak bilinen "
    "\"insan dokunuşlu otomasyon\" ilkesinin kökeni oldu.":
        "Sakichi Toyoda developed an automatic loom that stopped itself when the "
        "thread broke. Thus, a worker did not have to wait at a single loom, and "
        "faulty fabric was not produced. This idea became the origin of the principle "
        "of \"automation with a human touch\" known today as jidoka.",
    "Kiichiro Toyoda ve tam zamanında üretim": "Kiichiro Toyoda and just-in-time production",
    "1930'lar": "1930s",
    "Sakichi'nin oğlu Kiichiro Toyoda, otomobil üretimine geçerken her parçanın "
    "tam gerektiği anda ve tam gerektiği miktarda hatta ulaşması gerektiğini "
    "savundu. \"Just-in-Time\" kavramı bu yaklaşımdan doğdu.":
        "Sakichi's son, Kiichiro Toyoda, argued that when moving into automobile "
        "production, every part should reach the line at the exact time and in the "
        "exact quantity. The concept of \"Just-in-Time\" was born from this approach.",
    "Taiichi Ohno ve sistemin kurulması": "Taiichi Ohno and the establishment of the system",
    "1945 sonrası": "after 1945",
    "İkinci Dünya Savaşı sonrasında Taiichi Ohno, bu iki fikri tutarlı bir üretim "
    "sistemine dönüştürdü. Amerikan süpermarketlerinde rafın yalnızca satılan "
    "kadar doldurulmasından esinlenerek çekme sistemini ve kanban'ı geliştirdi. "
    "Kaynakların kıt olduğu bir dönemde israfı ortadan kaldırmak zorunluluktu; bu "
    "zorunluluk bir yönetim felsefesine dönüştü.":
        "After World War II, Taiichi Ohno transformed these two ideas into a coherent "
        "production system. He developed the pull system and kanban, inspired by the "
        "fact that in American supermarkets the shelves are filled only with what is "
        "sold. In a time when resources were scarce, eliminating waste was imperative; "
        "This obligation turned into a management philosophy.",
    "Hattın iki sütunu": "The two pillars of the line",
    "Parça hattan akarken her istasyon kendi işini yapar; bu iki sütun tüm hattın "
    "üzerine kurulduğu temeldir.":
        "As a part flows down the line each station does its job; these two pillars "
        "are the foundation the whole line is built on.",
    "Bir sonraki sürecin ihtiyaç duyduğu parçayı, ihtiyaç duyduğu anda ve ihtiyaç "
    "duyduğu miktarda üretmek. Bu sayede fazla stok, fazla üretim ve bekleme gibi "
    "israflar ortadan kalkar.":
        "To produce the part needed by the next process, when it is needed and in the "
        "quantity it needs. In this way, wastes such as excess stock, overproduction "
        "and waiting are eliminated.",
    "Evi ayakta tutan iki sütuna yakından bakalım.":
        "Let's take a closer look at the two columns that hold the house up.",
    "\"İnsan dokunuşlu otomasyon.\" Bir sorun ya da hata tespit edildiğinde makine "
    "ya da hat otomatik olarak durur; böylece hatalı ürün bir sonraki aşamaya asla "
    "geçmez.":
        "\"Automation with a human touch.\" When a problem or error is detected, the "
        "machine or line stops automatically; so the faulty product never progresses "
        "to the next stage.",
    "Temeldeki iki ilke": "Two underlying principles",
    "Bu iki sütunun altında, sistemi ayakta tutan iki temel ilke yer alır: "
    "<strong>Kaizen</strong> — küçük ama sürekli iyileştirme kültürü — ve "
    "<strong>insana saygı</strong> — çalışanların fikirlerine değer verilmesi ve "
    "sorun çözme sürecine dahil edilmesi. TPS, sadece bir üretim tekniği değil, bu "
    "iki ilke üzerine kurulmuş bir çalışma kültürüdür.":
        "Under these two pillars, there are two basic principles that keep the system "
        "afloat: <strong>Kaizen</strong> — a culture of small but continuous "
        "improvement — and <strong>respect for people</strong> — valuing employees' "
        "ideas and involving them in the problem-solving process. TPS is not just a "
        "production technique, it is a working culture built on these two principles.",
    "Yedi israf (muda)": "Seven wastes (muda)",
    "TPS, değer katmayan her şeyi israf sayar ve yedi başlıkta toplar. Hattı "
    "iyileştirmenin ilk adımı bunları görebilmektir.":
        "TPS considers everything that does not add value as waste and collects it "
        "under seven headings. The first step to improving the pipeline is to be able "
        "to see them.",
    "Fazla üretim": "Overproduction",
    "İhtiyaçtan fazla veya erken üretmek. Diğer tüm israfları besleyen temel israf.":
        "Producing more than needed or too early. The basic waste that feeds all other "
        "waste.",
    "TPS yalnızca israfı (muda) değil, dengesizliği (mura) ve aşırı yüklenmeyi "
    "(muri) de hedef alır. Üçü birbirini besler: dengesiz bir üretim planı aşırı "
    "yüklenmeye, aşırı yüklenme hataya yol açar.":
        "TPS targets not only waste (muda) but also imbalance (mura) and overload "
        "(muri). The three feed into each other: an unbalanced production plan leads "
        "to overload, and overload leads to errors.",
    "Bekleme": "Waiting",
    "Parça, bilgi, onay veya makine beklerken geçen zaman.":
        "Time spent waiting for parts, information, approval or machinery.",
    "Taşıma": "Transport",
    "Ürünün süreçler arasında gereksiz yere hareket ettirilmesi.":
        "Unnecessary movement of product between processes.",
    "Gereksiz işlem": "unnecessary action",
    "Müşteriye değer katmayan fazladan işlem adımları.":
        "Extra processing steps that add no value to the customer.",
    "Stok": "Inventory",
    "Hatta veya depoda bekleyen, sermayeyi bağlayan ve sorunları gizleyen fazla malzeme.":
        "Excess material sitting on line or in the warehouse, tying up capital and "
        "hiding problems.",
    "Gereksiz hareket": "unnecessary movement",
    "Çalışanın uzanma, eğilme, yürüme gibi değer katmayan hareketleri.":
        "Movements of the employee that do not add value, such as reaching, bending, "
        "walking.",
    "Hatalı ürün": "Faulty product",
    "Yeniden işleme, hurda ve müşteriye ulaşan hatalar.":
        "Rework, scrap and errors reaching the customer.",
    "Yerinde kalite ve andon": "On-site quality and andon",
    "TPS'te mükemmel kaliteye ulaşmanın temel prensibi \"yerinde kalite\"dir: hata, "
    "tespit edildiği yerde ve o anda çözülür, bir sonraki sürece asla aktarılmaz.":
        "The fundamental principle of achieving excellent quality in TPS is \"quality "
        "in place\": the error is resolved where and when it is detected, never passed "
        "on to the next process.",
    "Yeşil ışık": "Green light",
    "Süreç normal akışında.": "The process is in its normal flow.",
    "Bunu mümkün kılan en çarpıcı uygulama andon'dur. Hattaki her çalışan, bir "
    "sorun fark ettiğinde andon ipini çekerek üretim hattını durdurma yetkisine "
    "sahiptir. Hattı durdurmak bir başarısızlık değil, sorumluluğun gereğidir. "
    "Sorun anında ekipçe incelenir, kök nedeni bulunur ve tekrar etmemesi için "
    "önlem alınır.":
        "The most striking application that makes this possible is andon. Every "
        "employee on the line has the authority to stop the production line by pulling "
        "the andon rope when he notices a problem. Stopping the line is not a failure, "
        "it is a requirement of responsibility. The problem is immediately "
        "investigated by the team, the root cause is found and precautions are taken "
        "to prevent it from recurring.",
    "Sarı ışık": "yellow light",
    "Çalışan yardım çağırdı, hat henüz duruyor değil.":
        "The employee called for help, the line is not stopped yet.",
    "Kırmızı ışık": "Red light",
    "Sorun çözülemedi, hat durdu.": "The problem could not be solved, the line stopped.",
    "Kaizen döngüsü": "Kaizen cycle",
    "İyileştirme tek seferlik bir proje değil, kapanmayan bir döngüdür. Her tur, "
    "bir sonrakinin başlangıç noktasını yükseltir.":
        "Improvement is not a one-time project, it is a never-ending cycle. Each round "
        "raises the starting point of the next.",
    "Planla": "Plan",
    "Sorunu yerinde gör (genchi genbutsu), kök nedeni \"5 Neden\" ile araştır, bir "
    "iyileştirme önerisi geliştir.":
        "See the problem on the spot (genchi genbutsu), investigate the root cause "
        "with \"5 Whys\", and develop an improvement suggestion.",
    "Kaizen büyük atılımlarla değil, her gün yapılan küçük iyileştirmelerle "
    "ilerler. TPS'te iyileştirme fikrinin kaynağı çoğunlukla yönetim değil, işi "
    "bizzat yapan çalışandır.":
        "Kaizen progresses not with big breakthroughs, but with small improvements "
        "made every day. In TPS, the source of the improvement idea is often not the "
        "management, but the employee who does the work himself.",
    "Uygula": "Do",
    "Öneriyi küçük ölçekte, hızlıca dene.": "Try the suggestion quickly, on a small scale.",
    "Kontrol Et": "Check",
    "Sonucu ölç. Beklenen iyileşme gerçekleşti mi?":
        "Measure the result. Has the expected recovery occurred?",
    "Önlem Al": "Act",
    "İşe yarıyorsa standart iş haline getir ve yokoten ile diğer hatlara yay. "
    "Yaramıyorsa döngüye geri dön.":
        "If it works, make it standard work and spread it to other lines with yokoten. "
        "If it doesn't work, go back to the loop.",
    "TPS kavram sözlüğü": "TPS concept glossary",
    "Sayfada geçen terimlerin kısa karşılıkları. Aramak için kutuya yazmaya başlayın.":
        "Short equivalents of the terms mentioned on the page. Start typing in the box "
        "to search.",
    "Terim ara": "Search terms",
    "Aramanla eşleşen terim yok.": "No terms match your search.",
    "terim": "terms",
    "Bir sonraki sürecin ihtiyacını önceki sürece bildiren üretim kartı. Çekme "
    "sisteminin işleyiş aracı.":
        "Production card that informs the previous process of the need of the next "
        "process. The means of operation of the traction system.",
    "Üretimin tür ve miktar olarak dengelenmesi; dalgalanmayı azaltarak hattı ve "
    "tedarikçileri istikrarlı çalıştırır.":
        "Balancing production in terms of type and quantity; It keeps the line and "
        "suppliers running stable by reducing fluctuation.",
    "Takt zamanı": "takt time",
    "Müşteri talebini karşılamak için bir aracın hattan çıkması gereken süre. "
    "Üretimin ritmini belirler.":
        "The amount of time a vehicle must be off the line to meet customer demand. It "
        "determines the rhythm of production.",
    "Hatayı en baştan imkânsız kılan basit tasarım önlemleri; yanlış parçanın "
    "takılamayacağı bir aparat gibi.":
        "Simple design measures that make error impossible in the first place; It's "
        "like an apparatus that cannot be fitted with the wrong part.",
    "Karar vermeden önce sahaya gidip gerçeği kendi gözünle görmek.":
        "Go to the field and see the truth with your own eyes before making a decision.",
    "Standart iş": "standard job",
    "Bir işin bilinen en iyi, en güvenli ve en tutarlı yapılış biçimi. Kaizen'in "
    "başlangıç noktasıdır; standart yoksa iyileştirme ölçülemez.":
        "The best, safest and most consistent way of doing a job. It is the starting "
        "point of Kaizen; If there are no standards, improvement cannot be measured.",
    "Ayıkla, düzenle, temizle, standartlaştır, disiplini sürdür. Görsel ve düzenli "
    "bir çalışma alanı.":
        "Sort, organize, clean, standardize, maintain discipline. A visual and "
        "organized workspace.",
    "5 Neden": "5 Whys",
    "Bir sorunun kök nedenine ulaşana kadar arka arkaya \"neden?\" diye sormak.":
        "Ask “why?” repeatedly until you reach the root cause of a problem.",
    "Bir yerde işe yarayan iyileştirmenin diğer hatlara ve fabrikalara yatay "
    "olarak yayılması.":
        "Horizontal spread of an improvement that works in one place to other lines "
        "and factories.",
    "Hattaki sorunu görünür kılan ve gerektiğinde hattı durduran uyarı sistemi.":
        "Warning system that makes the problem on the line visible and stops the line "
        "when necessary.",
    "İsraf, dengesizlik ve aşırı yüklenme.": "Waste, imbalance and overload.",
    "TPS bugün nerede": "Where is TPS today",
    "TPS, önce otomotiv sektöründe, ardından üretimin çok ötesinde yayıldı. Bugün "
    "\"yalın (lean)\" adıyla bilinen yaklaşımın temelini oluşturuyor ve üretimle hiç "
    "ilgisi olmayan alanlarda uygulanıyor.":
        "TPS spread first in the automotive industry and then well beyond "
        "manufacturing. It forms the basis of the approach known today as \"lean\" and "
        "is applied in areas that have nothing to do with production.",
    "Sağlık": "Healthcare",
    "Hastanelerde hasta akışının düzenlenmesi, bekleme sürelerinin kısaltılması ve "
    "ilaç hatalarının önlenmesinde yalın yöntemler kullanılıyor.":
        "Lean methods are used in hospitals to regulate patient flow, shorten waiting "
        "times and prevent medication errors.",
    "Yazılım": "Software",
    "Kanban panoları, sürekli teslimat ve küçük artımlı iyileştirme, çevik yazılım "
    "geliştirmenin temel araçları arasında.":
        "Kanban boards, continuous delivery, and small incremental improvement are "
        "among the key tools of agile software development.",
    "Hizmet ve lojistik": "Service and logistics",
    "Depo yönetiminden bankacılık süreçlerine kadar, değer katmayan adımların "
    "ayıklanmasında aynı mantık işliyor.":
        "From warehouse management to banking processes, the same logic applies in "
        "eliminating steps that do not add value.",
    "TPS'i Sakarya'daki hatta çalışırken görün.": "See TPS in action on the line in Sakarya.",
    "TMMT, kurulduğu ilk günden bu yana TPS ilkeleriyle çalışıyor. Sakarya'daki "
    "fabrikada bir aracın presten montaja uzanan yolculuğunu inceleyin.":
        "TMMT has been working with TPS principles since the first day it was founded. "
        "Examine the journey of a vehicle from press to assembly at the factory in "
        "Sakarya.",
    "TMMT üretim sürecine göz atın": "Check out the TMMT production process",

    # ----------------------------------------------------------
    #  Cevre sayfasi
    # ----------------------------------------------------------
    "Toyota ve Çevre": "Toyota and the Environment",
    "Toyota'nın çevreye verdiği önem, 1997'de piyasaya sürdüğü ilk hibrit modeli "
    "Prius'a kadar uzanır. Bugün bu yaklaşım, şirketin \"Gezegene Saygı\" vizyonu "
    "doğrultusunda 2015 yılında ilan edilen <strong>Toyota Environmental Challenge "
    "2050</strong> stratejisiyle devam ediyor. Bu strateji, 2050 yılına kadar "
    "karbon nötr olmayı hedefleyen altı uzun vadeli hedeften oluşuyor.":
        "Toyota's commitment to the environment dates back to its first hybrid model, "
        "the Prius, launched in 1997. Today, this approach continues with the "
        "<strong>Toyota Environmental Challenge 2050</strong> strategy announced in "
        "2015, in line with the company's \"Respect for the Planet\" vision. This "
        "strategy consists of six long-term goals aimed at achieving carbon neutrality "
        "by 2050.",
    "Altı hedef, güncel ilerleme": "Six goals, current progress",
    "Toyota Environmental Challenge 2050 altı uzun vadeli hedeften oluşuyor. "
    "Aşağıdaki rakamlar, Sustainability Data Book 2025'e göre ara hedeflerdeki "
    "güncel durumu gösteriyor.":
        "Toyota Environmental Challenge 2050 consists of six long-term goals. The "
        "figures below show the current status of the interim targets according to the "
        "Sustainability Data Book 2025.",
    "Kaynak: Toyota Sustainability Data Book 2025":
        "Source: Toyota Sustainability Data Book 2025",
    "Yeni araç CO2 emisyonu": "New vehicle CO2 emissions",
    "Hedef 1: Yeni Araç Sıfır CO2": "Goal 1: New Vehicle Zero CO2",
    "2010'a kıyasla azalma. Hedef yüzde 30'du, planlanandan önce aşıldı.":
        "Decrease compared to 2010. The target was 30 percent, it was exceeded ahead "
        "of schedule.",
    "Hedef 4: Su Kullanımını En Aza İndirme": "Goal 4: Minimize Water Use",
    "Üretimde su tüketimini azaltmak ve kullanılan suyu doğaya güvenli biçimde "
    "geri kazandırmak.":
        "To reduce water consumption in production and to safely return the used water "
        "to nature.",
    "Fabrika CO2 emisyonu": "Factory CO2 emissions",
    "Hedef 3: Fabrika Sıfır CO2": "Goal 3: Factory Zero CO2",
    "2013'e kıyasla azalma. Hedef yüzde 30'du.":
        "Decrease compared to 2013. The target was 30 percent.",
    "Hedef 5: Geri Dönüşüm Temelli Toplum ve Sistemler":
        "Goal 5: Recycling Based Society and Systems",
    "Kaynakları döngüsel biçimde kullanmak; araçların ve bataryaların yeniden "
    "değerlendirilmesini sağlamak.":
        "Using resources in a cyclical manner; To ensure the re-evaluation of vehicles "
        "and batteries.",
    "Yaşam döngüsü CO2 emisyonu": "Life cycle CO2 emissions",
    "Hedef 2: Yaşam Döngüsü Sıfır CO2": "Goal 2: Life Cycle Zero CO2",
    "2013'e kıyasla azalma. Hedef yüzde 18'di.":
        "Decrease compared to 2013. The target was 18 percent.",
    "Hedef 6: Doğayla Uyum İçinde Bir Gelecek": "Goal 6: A Future in Harmony with Nature",
    "Biyoçeşitliliği korumak ve doğal yaşam alanlarını iyileştirmek.":
        "Protecting biodiversity and improving natural habitats.",
    "Yenilenebilir elektrik (küresel)": "Renewable electricity (global)",
    "Karbon nötrlüğe giden yol": "The path to carbon neutrality",
    "Toplam elektrik kullanımında. Hedef yüzde 25'ti.":
        "In total electricity usage. The target was 25 percent.",
    "Avrupa & Güney Amerika": "Europe & South America",
    "Bölgedeki tüm fabrikalar yenilenebilir elektrikle çalışıyor.":
        "All factories in the region run on renewable electricity.",
    "Karbon nötr fabrikalar": "Carbon neutral factories",
    "Üretimde net sıfır karbon için hedeflenen yıl.":
        "Target year for net zero carbon in production.",
    "Çevre yolculuğu": "environmental journey",
    "Bir durağa dokunarak o yılın kısa özetini görebilirsiniz.":
        "By tapping on a stop, you can see a brief summary of that year.",
    "Kaynak: global.toyota sürdürülebilirlik sayfaları; thesustainableinnovation.com özeti":
        "Source: global.toyota sustainability pages; thesustainableinnovation.com summary",
    "Toyota Earth Charter yayımlandı: şirketin çevre politikasının temelini "
    "oluşturan ilke metni (2000'de güncellendi).":
        "Toyota Earth Charter published: the text of principles underlying the "
        "company's environmental policy (updated 2000).",
    "İlk hibrit: Prius": "First hybrid: Prius",
    "Dünyanın ilk seri üretim hibrit otomobili Prius piyasaya sürüldü ve "
    "Toyota'nın elektrikli aktarma organı deneyiminin başlangıcı oldu.":
        "Prius, the world's first mass-produced hybrid car, was launched and marked "
        "the beginning of Toyota's electric powertrain experience.",
    "Paris İklim Anlaşması ile aynı yıl açıklanan Toyota Environmental Challenge "
    "2050, 2050'ye kadar ulaşılacak altı uzun vadeli hedefi içeriyor.":
        "Announced the same year as the Paris Climate Agreement, Toyota Environmental "
        "Challenge 2050 includes six long-term goals to be achieved by 2050.",
    "SBTi doğrulaması": "SBTi verification",
    "Toyota'nın sera gazı azaltım hedefleri, Science Based Targets initiative "
    "(SBTi) tarafından bilimsel temelli olarak onaylandı.":
        "Toyota's greenhouse gas reduction targets have been approved as "
        "scientifically based by the Science Based Targets initiative (SBTi).",
    "Güncel Data Book": "Current Data Book",
    "Yayımlanan güncel Sustainability Data Book'a göre birçok ara hedefe "
    "planlanandan önce ulaşıldı.":
        "According to the updated Sustainability Data Book published, many "
        "intermediate targets were achieved ahead of schedule.",
    "Hidrojenle Geleceğe": "Towards the Future with Hydrogen",
    "Kaynak: pressroom.toyota.com — \"2025 Toyota Year in Review\"":
        "Source: pressroom.toyota.com — \"2025 Toyota Year in Review\"",
    "Toyota Mirai, elektriğini bir bataryadan değil, hidrojen ile havadaki "
    "oksijeni birleştiren yakıt hücresinden üretir; egzozundan yalnızca su çıkar. "
    "Şirket bu teknolojiyi otomobilin ötesinde kamyon, otobüs ve sabit "
    "jeneratörlere de taşıyor.":
        "Toyota Mirai produces its electricity not from a battery, but from a fuel "
        "cell that combines hydrogen and oxygen in the air; Only water comes out of "
        "the exhaust. The company carries this technology beyond automobiles to "
        "trucks, buses and stationary generators.",
    "Toyota Hydrogen Solutions (2025): hidrojen çözümleriyle ilgilenen işletmelere "
    "yönelik kurulan kurumsal hub.":
        "Toyota Hydrogen Solutions (2025): corporate hub for businesses interested in "
        "hydrogen solutions.",
    "Yakıt hücreli araç görseli": "Fuel cell vehicle image",
    "Görsel alanı — buraya yakıt hücreli araç fotoğrafı veya kısa video eklenebilir.":
        "Image area — a fuel cell vehicle photo or short video can be added here.",
    "Hydrogen Headquarters (H2HQ), Gardena, Kaliforniya: hidrojen Ar-Ge ve demo "
    "faaliyetlerinin merkezi.":
        "Hydrogen Headquarters (H2HQ), Gardena, California: headquarters of hydrogen "
        "R&D and demonstration activities.",
    "Kişisel CO2 ve Yakıt Tasarrufu Hesaplayıcısı": "Personal CO2 and Fuel Savings Calculator",
    "Mevcut aracınızı bir Toyota elektrikli teknolojisiyle değiştirseydiniz yıllık "
    "olarak kabaca ne kadar tasarruf edeceğinizi görün.":
        "See roughly how much you would save annually if you replaced your current "
        "vehicle with a Toyota electric technology.",
    "Değerler tahminidir. Toyota resmi WLTP yakıt tüketimi verileri ile güncel "
    "ortalama Türkiye yakıt ve elektrik fiyatları esas alınmıştır; gerçek tasarruf "
    "sürüş koşullarına göre değişir.":
        "Values ​​are estimates. Based on Toyota official WLTP fuel consumption data "
        "and current average Türkiye fuel and electricity prices; actual savings vary "
        "depending on driving conditions.",
    "Yıllık ortalama kilometre": "Average mileage per year",
    "Yıllık CO2 tasarrufu": "Annual CO2 savings",
    "Mevcut araç tipi": "Current vehicle type",
    "Benzinli": "gasoline",
    "Dizel": "Diesel",
    "Yıllık yakıt/enerji tasarrufu": "Annual fuel/energy savings",
    "Karşılaştırılacak Toyota teknolojisi": "Toyota technology to compare",
    "Hibrit (HEV)": "Hybrid (HEV)",
    "Şarj Edilebilir Hibrit (PHEV)": "Rechargeable Hybrid (PHEV)",
    "Tam Elektrikli (BEV)": "Full Electric (BEV)",
    "Yıllık CO2 emisyonu (kg)": "Annual CO2 emissions (kg)",
    "Mevcut araç": "current vehicle",
    "Çoklu yol yaklaşımı": "Multipath approach",
    "Toyota, karbon nötrlüğe tek bir teknolojiyle değil, bölgeye ve müşteri "
    "ihtiyacına göre değişen birden fazla yolla ulaşmayı hedefliyor: hibrit (HEV), "
    "şarj edilebilir hibrit (PHEV), tam elektrikli (BEV) ve hidrojen yakıt hücreli "
    "(FCEV) araçlar bir arada geliştiriliyor. Bu yaklaşımın arkasındaki fikir, "
    "şarj altyapısının zayıf olduğu bir bölgede hibritin, altyapının güçlü olduğu "
    "bir bölgede ise elektrikli araçların daha gerçekçi bir çözüm olabileceği.":
        "Toyota aims to achieve carbon neutrality not with a single technology, but in "
        "multiple ways that vary depending on region and customer need: hybrid (HEV), "
        "plug-in hybrid (PHEV), fully electric (BEV) and hydrogen fuel cell (FCEV) "
        "vehicles are being developed together. The idea behind this approach is that "
        "hybrid may be a more realistic solution in a region with weak charging "
        "infrastructure, and electric vehicles may be a more realistic solution in a "
        "region where the infrastructure is strong.",
    "Hangi teknoloji size uygun?": "Which technology is right for you?",
    "Aynı yolu dört farklı şekilde gidebilirsiniz. Aşağıdaki tablo, her "
    "teknolojinin nasıl çalıştığını ve kime uygun olduğunu yan yana koyuyor.":
        "You can follow the same path in four different ways. The table below "
        "juxtaposes how each technology works and who it's suitable for.",
    "Nasıl çalışır": "How does it work",
    "Bu araçlar Sakarya'da üretiliyor": "These vehicles are produced in Sakarya",
    "TMMT üretimi →": "TMMT production →",
    "İçten yanmalı motor ve elektrik motoru birlikte çalışır; batarya frenleme ve "
    "motor tarafından şarj edilir, prize takmak gerekmez.":
        "The internal combustion engine and electric motor work together; The battery "
        "is charged by braking and the engine, no need to plug it in.",
    "Yok.": "None.",
    "Şehir içi ve karma kullanım; şarj altyapısı olmayan bölgeler.":
        "Urban and mixed use; regions without charging infrastructure.",
    "Corolla, C-HR (hibrit).": "Corolla, C-HR (hybrid).",
    "Toyota'nın çoklu yol yaklaşımı, bölgenin enerji altyapısına ve kullanıcının "
    "ihtiyacına göre doğru teknolojiyi sunmayı hedefler. Tek bir çözüm her yerde "
    "en iyisi değildir.":
        "Toyota's multi-path approach aims to offer the right technology according to "
        "the region's energy infrastructure and the user's needs. No single solution "
        "is best everywhere.",
    "Şarj gereksinimi": "Charging requirement",
    "Daha büyük bir bataryayla kısa mesafeleri tamamen elektrikle gider; batarya "
    "bitince hibrit olarak çalışmaya devam eder.":
        "With a larger battery, it travels short distances entirely on electricity; It "
        "continues to work as a hybrid when the battery runs out.",
    "Evde veya şarj noktasında.": "At home or at the charging point.",
    "Günlük kısa mesafe + ara sıra uzun yol yapanlar.":
        "Daily short distance + occasional long distance travellers.",
    "C-HR (şarj edilebilir hibrit).": "C-HR (rechargeable hybrid).",
    "Kime uygun": "Who is it suitable for?",
    "Yalnızca elektrik motoruyla çalışır, egzoz emisyonu yoktur.":
        "It works only with an electric motor and has no exhaust emissions.",
    "Düzenli şarj gerekir.": "Regular charging required.",
    "Şarj imkânı olan, ağırlıklı şehir içi kullanım.":
        "Mainly urban use, with charging facility.",
    "bZ ailesi.": "bZ family.",
    "Toyota'daki örnek": "Example in Toyota",
    "Hidrojen Yakıt Hücreli (FCEV)": "Hydrogen Fuel Cell (FCEV)",
    "Hidrojen ve havadaki oksijen yakıt hücresinde birleşerek elektrik üretir; "
    "egzozdan yalnızca su çıkar.":
        "Hydrogen and oxygen in the air combine in the fuel cell to produce "
        "electricity; Only water comes out of the exhaust.",
    "Hidrojen istasyonunda dakikalar içinde dolum.":
        "Filling in minutes at the hydrogen station.",
    "Uzun mesafe, ağır taşımacılık ve yüksek kullanım süresi gerektiren araçlar.":
        "Vehicles that require long distance, heavy transportation and high usage time.",
    "Hibrit nasıl çalışır?": "How does hybrid work?",
    "Hibrit sistem, sürüşün her anında motor ile elektrik motoru arasındaki iş "
    "bölümünü kendisi ayarlar. Bir aşamaya dokunarak o anda hangi parçanın "
    "çalıştığını görebilirsiniz.":
        "The hybrid system itself adjusts the division of labor between the engine and "
        "the electric motor at every moment of driving. By tapping on a stage you can "
        "see which part is currently working.",
    "Üstten görünen bir araç şeması. Önde içten yanmalı motor, ortada elektrik "
    "motoru, arkada batarya yer alır. Seçilen aşamada o anda çalışan parçalar "
    "vurgulanır.":
        "A diagram of a vehicle viewed from above. There is an internal combustion "
        "engine at the front, an electric motor in the middle, and a battery at the "
        "back. The parts currently running in the selected phase are highlighted.",
    "Kalkış ve düşük hız": "Takeoff and low speed",
    "Araç yalnızca elektrik motoruyla hareket eder. Yakıt tüketimi ve emisyon "
    "sıfırdır, çalışma sessizdir.":
        "The vehicle moves only with the electric motor. Fuel consumption and "
        "emissions are zero, operation is quiet.",
    "Toyota hibrit sistemi prize takmayı gerektirmez; batarya sürüş sırasında "
    "kendi kendine şarj olur.":
        "The Toyota hybrid system does not require plugging in; The battery charges "
        "itself while driving.",
    "Normal sürüş": "normal driving",
    "İçten yanmalı motor devreye girer. Gücün bir kısmı tekerleklere, bir kısmı "
    "bataryayı şarj etmeye ayrılır.":
        "The internal combustion engine comes into play. Part of the power is "
        "allocated to the wheels and part to charging the battery.",
    "Hızlanma": "Acceleration",
    "Motor ve elektrik motoru birlikte çalışarak ek güç sağlar.":
        "The engine and electric motor work together to provide additional power.",
    "Yavaşlama ve fren": "Deceleration and braking",
    "Rejeneratif frenleme devreye girer; normalde ısı olarak kaybolacak enerji "
    "elektriğe çevrilerek bataryaya geri kazandırılır.":
        "Regenerative braking is activated; The energy that would normally be lost as "
        "heat is converted into electricity and returned to the battery.",
    "Döngüsel ekonomi: 4R": "Circular economy: 4Rs",
    "Bir aracın çevresel etkisi yalnızca yolda geçirdiği sürede değil, üretiminden "
    "ömrünün sonuna kadar tüm yaşam döngüsünde ortaya çıkar. Toyota'nın döngüsel "
    "ekonomi yaklaşımı bu döngünün her aşamasını hedef alır.":
        "The environmental impact of a vehicle occurs not only during the time it "
        "spends on the road, but throughout its entire life cycle, from production to "
        "the end of its life. Toyota's circular economy approach targets every stage "
        "of this cycle.",
    "Yeniden tasarla": "redesign",
    "Araçlar, ömrünün sonunda kolay ayrıştırılabilecek ve geri kazanılabilecek "
    "şekilde tasarlanır; geri dönüştürülmüş malzeme kullanımı artırılır.":
        "Vehicles are designed to be easily decomposed and recycled at the end of "
        "their life; The use of recycled materials is increased.",
    "Azalt": "reduce",
    "Üretimde kullanılan malzeme, enerji ve su miktarı sürekli azaltılır.":
        "The amount of materials, energy and water used in production is constantly "
        "reduced.",
    "Yeniden kullan": "reuse",
    "Kullanılabilir parçalar toplanır, yenilenir ve yeniden dolaşıma sokulur.":
        "Usable parts are collected, regenerated and put back into circulation.",
    "Geri dönüştür": "recycle",
    "Ömrünü tamamlayan araç ve bileşenler ayrıştırılarak malzemeler yeni üretim "
    "süreçlerine kazandırılır.":
        "Vehicles and components that have completed their service life are separated "
        "and the materials are used in new production processes.",
    "Bataryanın ikinci hayatı": "The second life of the battery",
    "Bir batarya, araçtaki görevi bittiğinde kullanım ömrünü tamamlamış olmuyor. "
    "Toyota bataryaları dört aşamalı bir yolda izliyor.":
        "A battery does not complete its useful life when its function in the vehicle "
        "is completed. Toyota tracks batteries on a four-step path.",
    "Araçta kullanım": "Use in vehicle",
    "Batarya, aracın kullanım ömrü boyunca hizmet verir.":
        "The battery lasts for the lifetime of the vehicle.",
    "Sakarya'daki fabrika, Toyota'nın Avrupa'daki ilk PHEV batarya üretim hattına "
    "ev sahipliği yapıyor →":
        "The factory in Sakarya hosts Toyota's first PHEV battery production line in "
        "Europe →",
    "Toplama": "Collection",
    "Ömrünü tamamlayan bataryalar yetkili ağ üzerinden toplanır ve durumu değerlendirilir.":
        "Batteries that have completed their life are collected through the authorized "
        "network and their condition is evaluated.",
    "İkinci hayat": "second life",
    "Araçta kullanım için yeterli kapasitesi kalmayan bataryalar, yenilenebilir "
    "enerji depolama gibi sabit uygulamalarda kullanılmaya devam eder.":
        "Batteries that do not have sufficient capacity for use in the vehicle "
        "continue to be used in stationary applications such as renewable energy "
        "storage.",
    "Geri dönüşüm": "Recycle",
    "Kullanım ömrü tamamen dolduğunda değerli metaller geri kazanılarak yeni "
    "batarya üretimine kazandırılır.":
        "When its useful life is completely completed, the precious metals are "
        "recovered and used for the production of new batteries.",
    "TMMT'de çevre": "Environment at TMMT",
    "Global hedefler, Sakarya'daki fabrikada somut uygulamalara dönüşüyor. TMMT, "
    "1999'dan bu yana ISO 14001 çevre yönetim sistemi sertifikasına sahip ve "
    "enerji, su ve atık azaltımına yönelik sürekli iyileştirme (kaizen) projeleri "
    "yürütüyor.":
        "Global targets turn into concrete practices at the factory in Sakarya. TMMT "
        "has been certified with ISO 14001 environmental management system since 1999 "
        "and carries out continuous improvement (kaizen) projects for energy, water "
        "and waste reduction.",
    "ISO 14001 sertifikası": "ISO 14001 certification",
    "Sertifikasyonun başlangıç yılı. Fabrika, çevre yönetim sistemini bu tarihten "
    "bu yana uyguluyor.":
        "Starting year of certification. The factory has been implementing the "
        "environmental management system since this date.",
    "Enerji ve su verimliliği": "Energy and water efficiency",
    "Üretim süreçlerinde tüketimin azaltılmasına yönelik kaizen projeleri.":
        "Kaizen projects aimed at reducing consumption in production processes.",
    "Atık azaltımı": "Waste reduction",
    "Üretim atıklarının kaynağında azaltılması ve geri kazanım oranının artırılması.":
        "Reducing production waste at the source and increasing the recovery rate.",
    "Yıllık su tüketimi azaltım oranı": "Annual water consumption reduction rate",
    "Düzenli depolamaya giden atık oranı": "Rate of waste going to landfill",
    "Fabrikada kullanılan yenilenebilir elektrik oranı":
        "Ratio of renewable electricity used in the factory",
    "Ağaçlandırma / biyoçeşitlilik projeleri": "Afforestation / biodiversity projects",
    "Karbon nötr fabrikaya giden yol": "The road to a carbon neutral factory",
    "Fabrikalarda net sıfır karbon tek adımda değil, birbirini izleyen üç durakta "
    "hedefleniyor.":
        "Net zero carbon in factories is targeted not in one step, but in three "
        "consecutive stops.",
    "Enerji verimliliği ve yenilenebilir elektrik":
        "Energy efficiency and renewable electricity",
    "Üretimde enerji verimliliği ve yenilenebilir elektrik kullanımının artırılması.":
        "Increasing energy efficiency and use of renewable electricity in production.",
    "Kademeli azaltım": "Gradual reduction",
    "Ara hedefler doğrultusunda fabrika CO2 emisyonlarının kademeli azaltımı.":
        "Gradual reduction of factory CO2 emissions in line with intermediate targets.",
    "Net sıfır karbon": "net zero carbon",
    "Toyota'nın küresel üretim tesislerinde net sıfır karbon hedef yılı.":
        "It's Toyota's net-zero carbon target year at its global manufacturing facilities.",
    "Bu sayfadaki rakamların kaynağı olan yıllık sürdürülebilirlik raporunun "
    "tamamına ulaşın.":
        "Access the full annual sustainability report from which the figures on this "
        "page come.",
    "Raporu görüntüle": "View report",

    # ----------------------------------------------------------
    #  Haberler sayfasi
    # ----------------------------------------------------------
    "Haberler": "News",
    "Toyota Otomotiv Sanayi Türkiye'den güncel haberler, gelişmeler ve duyurular.":
        "News, developments and announcements from Toyota Motor Manufacturing Türkiye.",
    "Haberi İncele": "Read the article",
    "Tüm Haberlere Dön": "Back to all news",
    "Henüz haber bulunmuyor.": "There are no news articles yet.",

    # Kategori filtresi. Kategori ADLARI burada YOK: onlar
    # app/kategoriler.py katalogundan geliyor -- ayni metin iki yerde
    # tutulursa er gec ayrisir.
    "Kategoriye göre filtrele": "Filter by category",
    "Tümü": "All",
    "Bu kategoride henüz haber yok.":
        "There are no news articles in this category yet.",
    "Kategori yok": "No category",

    "Sayfalar": "Pages",
    "Sayfa": "Page",
    "Önceki": "Previous",
    "Sonraki": "Next",

    # ----------------------------------------------------------
    #  Sablon arayuz metinleri
    # ----------------------------------------------------------
    "Aradığınız sayfa bulunamadı.":
        "The page you were looking for was not found.",
    "Ana sayfaya dön": "Return to home page",
    "döngü baştan başlar": "the cycle starts over",
    "Özellik": "Feature",
    "Not": "Notes",
    "Motor": "Engine",
    "Elektrik motoru": "electric motor",
    "Batarya": "Battery",
}
