# Toyota Bilgi Sitesi — İçerik Yönetim Sistemi

Flask ile hazırlanmış, 4 sayfalı ve sabit üst menülü Toyota temalı bir web sitesi.
İçerik veritabanında tutuluyor; kod bilmeyen editörler tarayıcıdan düzenleyebilecek.

> **Taşıma tamamlandı.** Site veritabanından okuyor, panel çalışıyor,
> görsel yükleme ve çeviri akışı bağlı. Yayına alma adımları için
> [DEPLOY.md](DEPLOY.md).

## Kurulum ve çalıştırma

```bash
pip install -r requirements.txt

cp .env.example .env
python tools/hash_password.py --anahtar   # FLASK_SECRET_KEY
python tools/hash_password.py --yol       # ADMIN_PATH
python tools/hash_password.py             # ADMIN_PASSWORD_HASH
# üç çıktıyı .env içine yapıştır

python tools/seed.py      # içeriği veritabanına aktar (bir kez)
python run.py
```

Sonra tarayıcıda **http://127.0.0.1:5000** adresini aç.

## Yapı

```
toyota_project/
├── run.py                      # geliştirme sunucusu
├── .env                        # gizli ayarlar (git'e girmez)
├── instance/toyota.db          # SQLite veritabanı (git'e girmez)
├── app/
│   ├── factory.py              # create_app() — app factory
│   ├── config.py               # tüm ayarlar, .env'den okunur
│   ├── models.py               # 7 tablo
│   ├── content.py              # ★ içeriği okuyan TEK modül
│   ├── block_types.py          # 25 blok tipinin kataloğu
│   ├── i18n.py                 # dil seçimi
│   ├── security.py             # şifre, oturum, IP kilidi, CSRF
│   └── blueprints/
│       ├── public.py           # site rotaları
│       └── admin/              # panel: auth, pages, blocks
├── templates/
│   ├── base.html               # kabuk: üst bar, dil seçici
│   ├── page.html               # ★ TEK sayfa şablonu, blok döngüsü
│   └── blocks/                 # her blok tipi için ayrı parça
├── static/
│   ├── css/
│   │   ├── tokens.css          # renk / font / boşluk değişkenleri
│   │   ├── base.css            # sıfırlama, tipografi, .tk-block, .tk-note
│   │   ├── layout.css          # üst bar, hamburger, dil seçici
│   │   ├── blocks/             # her blok tipi için ayrı dosya
│   │   └── themes/             # sayfa başına renk/arkaplan override
│   ├── js/main.js              # ES module giriş noktası
│   └── js/modules/             # nav, dil, harita, hesaplayıcı...
└── tools/                      # seed, doğrulama, regresyon araçları
```

## Nasıl çalışıyor

- **Sayfalar veritabanından geliyor.** `page` tablosundaki her satır bir sayfa;
  adresi `url` sütununda. Ana sayfa (`is_home`) hem `/` hem kendi adresinden
  servis ediliyor.
- **Her sayfa sıralı bir blok listesi.** `page.html` blokları dolaşıp her birini
  `templates/blocks/<tip>.html` ile basıyor. 25 blok tipi var: `hero`,
  `rich_text`, `stat_grid`, `stat_badge`, `card_grid`, `chip_groups`,
  `process_steps`, `cycle_steps`, `timeline`, `map`, `co2_calculator`,
  `source_list`, `media_split`, `compare_table`, `section_nav`, `mission`,
  `value_columns`, `tps_house`, `hybrid_flow`, `andon`, `glossary`,
  `fact_table`, `badge_strip`, `news_list`, `divider`.
- **Alt başlık kendini tekrar etmez.** Bir öğenin `subtitle` alanı, başlığın
  zaten söylediği bir şeye dönüşürse basılmaz — "Redesign / Yeniden tasarla"
  çifti İngilizce'de yalnızca "Redesign" olur. Kural tek yerde:
  `content.ItemView.alt_baslik_farkli`; `card_grid` ve `value_columns` aynı
  yerden okur.
- **Karşılaştırma tablosunda hücreler sütunun içinde durur.** `compare_table`
  bloğunda `row` öğeleri yalnızca satır etiketidir; hücreler (`cell`) ilgili
  `column` öğesinin altında, satırlarla aynı sırada saklanır. Böylece **yeni
  bir sütun eklemek mevcut sütunlara hiç dokunmaz** — tablo bozulmaz. Eksik
  hücre boş görünür, hata vermez.
- **Sözlük araması tarayıcıda.** `glossary` bloğunda aranacak metin sunucuda
  Türkçe karakterlerden arındırılıp (`content.sadelestir`) satırın
  `data-arama` özniteliğine yazılır; JS yalnızca sorguyu aynı şekilde
  sadeleştirip içinde arar. **İki tarafın harf tablosu aynı olmalı**
  (`app/content.py` ve `static/js/modules/glossary.js`) — ayrışırlarsa arama
  sessizce eksik sonuç döndürür. JS kapalıysa arama kutusu CSS ile gizlenir,
  liste yine tam çalışır.
- **TPS Evi diyagramı veri, çizim değil.** `tps_house` bloğunun SVG'si
  şablonda sabittir (kutuların koordinatları `YERLESIM` sözlüğünde); panelden
  yalnızca kutuların **içindeki metinler** düzenlenir. Hangi metnin hangi
  kutuya gideceğini öğenin `slug` alanı söyler. Diyagram `viewBox` ile
  ölçeklenir, sabit piksel genişliği yoktur; 720px altında yazı okunmaz hale
  geldiği için aynı hiyerarşiyi koruyan dikey akordeona döner. İki sunum da
  **aynı** açıklama panellerini açar (aynı `aria-controls`), görünmeyen sunum
  `display:none` ile erişilebilirlik ağacından da çıkar.
- **Boş alanlar kendini gizler.** Doğrulanmamış içerik panelde yer tutar ama
  sitede görünmez: değeri boş `fact_table` satırı, başlığı boş `badge_strip`
  rozeti, **rakamı boş `stat_grid` kutusu** ve **başlığı boş `card_grid`
  kartı** basılmaz. Hiç içerik kalmazsa `card_grid`, `mission` ve `news_list`
  **başlığıyla birlikte** tamamen gizlenir.
  Bu kural tek yerde duruyor: `content.BlockView.renders`. Hem bloğun kendi
  şablonu hem de bölüm menüsü oradan okuyor — yoksa menüde hiçbir yere
  gitmeyen bir bağlantı kalırdı.
- **Bölüm menüsü kendini üretir.** `section_nav` bloğunun içeriği yok:
  sayfadaki blokları tarayıp “Bağlantı adresi (#)” alanı dolu, başlığı olan ve
  gerçekten basılan bölümleri listeler. Menü metni ile bölüm başlığı asla
  ayrışamaz.
- **Panel notu.** Her bloğa, yalnızca yönetim panelinde görünen bir hatırlatma
  yazılabilir (`settings.panel_note`) — “yayından önce şurayı doğrula” gibi.
  Sitede hiçbir yerde basılmaz, çevrilmez.
- **`value_columns` alt başlığı kendini tekrar etmez.** Bir değerin Türkçe
  karşılığı (`subtitle`), İngilizce sayfada başlığın aynısına dönüşürse
  basılmaz — "Challenge / Challenge" yerine sadece "Challenge" görünür.
- **Harita ve hesaplayıcı HTML olarak değil veri olarak saklanıyor.** Koordinatlar
  `block_item` satırlarında, emisyon katsayıları `block.settings` içinde. Sunucu
  bunları `<script type="application/json">` olarak basıyor, ilgili JS modülü
  okuyor. Harita modülü sayfadaki **her** `.tk-map__canvas` için ayrı bir
  Leaflet haritası kuruyor: global sayfasındaki üretim tesisleri haritası ile
  TMMT sayfasındaki ihracat pazarları haritası aynı koddan, farklı veri
  kümesiyle çiziliyor.
- **İçeriği okuyan tek yer `app/content.py`.** Şablonlar veritabanını doğrudan
  görmüyor. Depolama değişirse değişecek tek dosya budur.
- Üst menü `base.html` içinde, sayfa kayıtlarından üretiliyor (sabit/sticky).
- **CSS bloklara bölünmüş.** Her sayfa yalnızca kullandığı blok tiplerinin
  dosyasını yükler; tema dosyası en sonda gelir ki blok kurallarını ezebilsin.
  Sınıf adları `tk-<blok>__<parça>` düzenindedir; eşleme tablosu
  `tools/css_rename_map.py` içinde.

## Yönetim paneli

- Adres `.env` içindeki `ADMIN_PATH` — sitede hiçbir link yok.
- Kullanıcı adı yok, tek ortak şifre. Yanlış şifre **404** döner; aynı IP'den
  5 hatalı denemeden sonra 15 dakika kilit.
- Oturum 60 dakika sonra düşer. Şifre panelden değiştirilebilir.
- Editör sayfa **açamaz/silemez**; blok ekleyebilir, silebilir, sürükleyerek
  sıralayabilir.
- **Görseller** ekranından resim yüklenir; kapak, kartlar, metin+görsel bloğu
  ve sayfa arka planında kullanılabilir. Dosya Pillow ile gerçekten resim mi
  diye açılıp doğrulanır, rastgele bir adla kaydedilir.
- Her bloğun **İngilizce çeviriler** ekranı var (bkz. aşağısı).

## Dil / çeviri (TR → EN)

- Türkçe metin varlığın kendi sütununda (kaynak doğru), İngilizcesi ayrı
  `translation` tablosunda durur.
- Türkçeyi kaydettiğinde İngilizcesi **otomatik üretilir**.
- İngilizceyi panelden elle düzeltirsen o alan **kilitlenir** (`is_manual`) ve
  otomatik çeviri bir daha üzerine yazmaz. Kutuyu boşaltmak otomatiğe döndürür.
- Türkçe sonradan değişirse alan **"kaynak değişti"** olarak işaretlenir;
  elle yazdığın çeviri korunur, kararı sen verirsin.
- Çeviri satırı yoksa `auto_translate.py` çalışma zamanında çevirir ve
  `translations/auto_cache.json` dosyasına yazar. Ağ yoksa metin Türkçe
  gösterilir; uygulama asla hata vermez.

## Doğrulama araçları

```bash
python tools/seed.py --rapor      # veritabanı içeriğinin dökümü
python tools/verify_seed.py       # taşıma öncesi metinlerin hepsi DB'de mi
python tools/snapshot.py after    # 4 sayfa × 2 dil HTML fotoğrafı
python tools/snapshot.py diff --dom   # etiket/öznitelik farkı
python tools/snapshot.py diff --text  # görünen metin farkı
python tools/css_check.py         # CSS bölünmesi kayıpsız mı
python tools/panel_roundtrip.py   # panelden kaydetmek veri bozuyor mu

python tools/kontrol.py           # ★ hepsini sırayla çalıştır

python tools/ceviri_yenile.py --rapor   # çeviri durumu özeti
python tools/ceviri_yenile.py           # eksik/bayat çevirileri tamamla
```

## Sayfaya sonradan bölüm ekleyen betikler

Bunlar veritabanını **sıfırlamaz**; yalnızca eksik bölümü ekler ve iki kez
çalıştırılırsa ikinci seferde bir şey yapmaz. İçerik `tools/seed.py` içindeki
`BOLUM_*` sabitlerinden okunur — aynı metnin iki kopyası olmasın diye.
Ortak yazma/sıralama/çeviri yardımcıları `tools/_bolum_yazici.py` içinde.

```bash
python tools/tmmt_bolumleri.py    # TMMT — 1. grup (süreç, zaman tüneli, PHEV)
python tools/tmmt_bolumleri2.py   # TMMT — 2. grup (künye, harita, kariyer...)
python tools/global_bolumleri.py  # Global — misyon bandı, hikâye, Toyota Way
python tools/global_bolumleri2.py # Global — bölüm menüsü, Avrupa, platform,
                                  #          Ar-Ge, yönetim + marka ailesi 3. kutu
python tools/tps_bolumleri.py     # TPS — TPS Evi, sistemin doğuşu, yedi israf
python tools/tps_bolumleri2.py    # TPS — bölüm menüsü, andon, kaizen döngüsü,
                                  #       sözlük, TPS bugün, TMMT köprüsü
python tools/cevre_bolumleri.py   # Çevre — hedef adları, teknoloji tablosu,
                                  #         hibrit diyagramı
python tools/cevre_bolumleri2.py  # Çevre — bölüm menüsü, 4R, batarya akışı,
                                  #         TMMT'de çevre, karbon yolu, rapor

python tools/global_bolumleri.py --rapor   # yazmadan ne yapacağını göster
python tools/global_bolumleri.py --geri    # eklediklerini geri al
```

**Çeviri notu:** Google'ın ücretsiz ucu peş peşe çok istek gelince arada bir
"çeviri bulunamadı" döndürüyor; `deep-translator` bunu "çevrilemez" sayıp
**kaynak metni** veriyor ve önbelleğe öyle yazılıyor — yani İngilizce sayfada
Türkçe metin kalıyor ve bir daha denenmiyor. Betikler bunu her çalıştırmada
tespit edip yeniden deniyor. Bir kez çalıştırmak yetmezse **çıktı 0 düzelme
diyene kadar tekrar çalıştır**; kalanlar için `python warm_cache.py --refresh`.

## Erişilebilirlik kuralları

- **Açılır kapanır her şey gerçek `<button>`.** Zaman tüneli, adım adım, TPS Evi
  ve sözlük aynı `akordeon()` yardımcısını kullanır; `<div onclick>` yoktur, bu
  yüzden tab ile odaklanma ve enter/space ile açma tarayıcıdan bedava gelir.
  Her kontrolde `aria-expanded` + `aria-controls` bulunur.
- **TPS Evi'nin tıklanabilir parçaları** SVG içinde `<foreignObject>` içine
  konmuş gerçek butonlardır — SVG şekline `tabindex` eklemek yerine. Şemanın
  görünmez bir yazılı karşılığı vardır (`.tk-gizli-metin`, `aria-describedby`);
  metin CMS'ten gelir ve çevrilir.
- **Animasyonlar `prefers-reduced-motion` ile durur.** Andon ışıkları bu
  durumda sönmez, her biri kendi renginde sabit yanar — bilgi kaybolmasın diye.
- Bölüm menüsü bağlantıları sabit üst barın altında kalmasın diye
  `.page > [id] { scroll-margin-top: ... }` kuralı vardır.
- **Karşılaştırma tablosu gerçek bir `<table>`**: satır başlıkları
  `<th scope="row">`, sütun başlıkları `<th scope="col">`. Dar ekranda yatay
  kayar (`.table-wrap`), satır etiketleri `position: sticky` ile solda kalır.
- **Hesaplayıcının sabitleri koda gömülü değil.** Yakıt/elektrik fiyatları,
  tüketim ve CO2 katsayıları `co2_calculator` bloğunun `settings.rates.*`
  alanlarında; panelde "Fiyatlar", "Yakıt tüketimi", "CO2 katsayıları"
  kutularından düzenlenir. JS bunları `<script type="application/json">`
  bloğundan okur, kendi içinde hiçbir sayı tutmaz. Hesaplayıcının altındaki
  açıklama metni bloğun "Kaynak dipnotu" alanıdır.
- **Şablondaki sabit metinler** (`Motor`, `Batarya`, `Özellik`, `döngü baştan
  başlar`) içerik değil arayüzdür; `settings`'e değil `{{ _() }}` ile çeviriye
  bağlanır — `settings` çevrilmez (bkz. `app/block_types.py` notu).

Editörlerin paragraflara yazdığı HTML `bleach` ile beyaz listeden geçer
(`<strong> <em> <a> <br>` vb.); `<script>`, `onerror`, `javascript:` gibi
şeyler kaydederken temizlenir.

`tools/_retired/` ve `tools/baseline_strings.json` taşıma öncesi halin kalıcı
kaydıdır; doğrulama bunlara dayanır, silme.

## İçerik hakkında

Sayfalardaki metinler güncel kaynaklardan derlenmiş genel bilgilerdir; kaynak
linkleri ilgili sayfaların altında yer alıyor.
