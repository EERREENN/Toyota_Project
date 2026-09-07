# Yayına alma kontrol listesi

Siteyi kendi bilgisayarından çıkarıp internete koyarken sırayla bunları yap.
Atlanması en tehlikeli olanlar **kalın** yazıldı.

Site statik içerikle çalışır: **veritabanı yok, yönetim paneli yok, kurulum
adımı yok.** Kod neyse yayındaki site odur.

---

## 1. Sunucuda kurulum

```bash
git clone <depo>            # ya da klasörü kopyala
cd toyota_project
python -m venv venv
venv/bin/pip install -r requirements.txt
```

Bu kadar. Ayrıca içerik oluşturmak, veritabanı taşımak ya da bir betik
çalıştırmak gerekmez — sayfaların tamamı `templates/pages/` altındaki
Jinja şablonlarında.

---

## 2. `.env` dosyası

Zorunlu değil; yalnızca dil çerezini imzalayan anahtar için.

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # FLASK_SECRET_KEY
```

Çıktıyı `.env`'ye yapıştır, sonra **yayına özel** iki ayarı değiştir:

```bash
SESSION_COOKIE_SECURE=true     # HTTPS kurulduktan SONRA
TRUST_PROXY=true               # nginx / Caddy arkasındaysan
```

```bash
chmod 600 .env
```

---

## 3. HTTPS

**En kolayı Caddy** — sertifikayı kendi alır ve yeniler:

```
toyota.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

nginx kullanacaksan `certbot --nginx` ile sertifika al ve HTTP → HTTPS
yönlendirmesini ekle.

**`TRUST_PROXY=true` yapmayı unutma.** Bu olmadan Flask kendini HTTP zanneder
ve güvenli çerez çalışmaz.

HTTPS sorunsuz çalıştığını gördükten **sonra** HSTS ekle (geri dönüşü zor):
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## 4. Uygulamayı çalıştırma

`run.py` **sadece geliştirme içindir** (debug açık). Yayında:

```bash
# Linux
venv/bin/gunicorn -b 127.0.0.1:8000 "app:create_app()"

# Windows
venv\Scripts\waitress-serve --port=8000 "app:create_app()"
```

Yazılacak bir durum olmadığı için işçi sayısı serbesttir; birden fazla işçi
çalıştırabilirsin.

Sistem servisi olarak kur (systemd örneği):

```ini
[Unit]
Description=Toyota sitesi
After=network.target

[Service]
WorkingDirectory=/srv/toyota_project
ExecStart=/srv/toyota_project/venv/bin/gunicorn -b 127.0.0.1:8000 "app:create_app()"
Restart=always
User=toyota

[Install]
WantedBy=multi-user.target
```

---

## 5. Yedekleme

Yedeklenecek ayrı bir veri yok: içerik ve görseller depoda duruyor, dolayısıyla
**git deposunun kendisi yedektir.**

`FLASK_SECRET_KEY`'i bir yere not et — değişirse ziyaretçilerin seçtiği dil
sıfırlanır (kalıcı `lang` çerezi yine de tutar).

---

## 6. Yayına aldıktan sonra kontrol et

```bash
curl -I https://toyota.example.com/                    # 200, HTTPS
curl     https://toyota.example.com/robots.txt
```

- Dört sayfa da açılıyor: `/tmmt`, `/global-toyota`, `/uretim-sistemi`, `/cevre`
- TR/EN geçişi çalışıyor, sayfayı yenileyince seçim korunuyor
- Harita, CO2 hesaplayıcı ve sözlük araması çalışıyor
- Dar pencerede hamburger menü açılıyor

---

## 7. İçerik güncelleme

Her sayfa kendi şablonudur: `templates/pages/tmmt.html`, `global.html`,
`tps.html`, `cevre.html`. Bölümler düz HTML olarak duruyor — düzenle,
sunucuyu yeniden başlat.

Çevrilebilir metinler `{{ _('Türkçe metin') }}` içinde; İngilizce
karşılıkları `app/ceviri.py` dosyasında. Yeni bir metin eklerken
karşılığını oraya da yaz, yoksa İngilizce sayfada Türkçe görünür.

| Ne zaman | Ne yap |
|---|---|
| Metin/rakam güncellemesi | İlgili `templates/pages/*.html` dosyasını düzenle |
| Yeni İngilizce karşılık | `app/ceviri.py` içine ekle |
| Değişiklik sonrası kontrol | `python tools/kontrol.py` |
| Sayfa çıktısı karşılaştırma | `python tools/snapshot.py before` → değiştir → `... diff` |
