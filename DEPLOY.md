# Yayına alma kontrol listesi

Siteyi kendi bilgisayarından çıkarıp internete koyarken sırayla bunları yap.
Atlanması en tehlikeli olanlar **kalın** yazıldı.

---

## 1. Sunucuda kurulum

```bash
git clone <depo>            # ya da klasörü kopyala
cd toyota_project
python -m venv venv
venv/bin/pip install -r requirements.txt
```

`instance/toyota.db` ve `static/uploads/` **git'e girmez**. Sunucuda ilk kez
kuruyorsan içeriği oluştur:

```bash
venv/bin/python tools/seed.py
```

Zaten çalışan bir siten varsa bunun yerine kendi bilgisayarındaki
`instance/toyota.db` ve `static/uploads/` klasörünü sunucuya kopyala —
seed script'i **mevcut veritabanının üstüne yazmaz**, uyarıp durur.

---

## 2. `.env` dosyası

```bash
cp .env.example .env
venv/bin/python tools/hash_password.py --anahtar   # FLASK_SECRET_KEY
venv/bin/python tools/hash_password.py --yol       # ADMIN_PATH
venv/bin/python tools/hash_password.py             # ADMIN_PASSWORD_HASH
```

Üç çıktıyı `.env`'ye yapıştır, sonra **yayına özel** üç ayarı değiştir:

```bash
SESSION_COOKIE_SECURE=true     # HTTPS kurulduktan SONRA
TRUST_PROXY=true               # nginx / Caddy arkasındaysan
SQLITE_WAL=true                # senkronize edilen klasörde DEĞİLSE
```

> ⚠️ **`SESSION_COOKIE_SECURE=true`'yu HTTPS çalışmadan açma.** Güvenli çerez
> HTTP üzerinden gönderilmez; panele giremezsin.

Dosya izinleri:
```bash
chmod 600 .env
chmod 600 instance/toyota.db
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

**`TRUST_PROXY=true` yapmayı unutma.** Bu olmadan:
- IP kilidi tüm ziyaretçileri tek IP sanar → bir kişi yanlış şifre girince
  herkes kilitlenir
- Flask kendini HTTP zanneder, güvenli çerez çalışmaz

HTTPS sorunsuz çalıştığını gördükten **sonra** HSTS ekle (geri dönüşü zor):
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## 4. Uygulamayı çalıştırma

`run.py` **sadece geliştirme içindir** (debug açık). Yayında:

```bash
# Linux
venv/bin/gunicorn -w 1 -b 127.0.0.1:8000 "app:create_app()"

# Windows
venv\Scripts\waitress-serve --port=8000 "app:create_app()"
```

**`-w 1` (tek işçi)** — SQLite yazma kilidi yüzünden. Trafiğin artarsa
`SQLITE_WAL=true` çoklu okuyucuyu kaldırır; yine de tek yazıcı kalmalı.

Sistem servisi olarak kur (systemd örneği):

```ini
[Unit]
Description=Toyota sitesi
After=network.target

[Service]
WorkingDirectory=/srv/toyota_project
ExecStart=/srv/toyota_project/venv/bin/gunicorn -w 1 -b 127.0.0.1:8000 "app:create_app()"
Restart=always
User=toyota

[Install]
WantedBy=multi-user.target
```

---

## 5. Yükleme klasörü güvenliği

`static/uploads/` içindeki dosyalar ziyaretçiye sunulur. Proxy'nin bu
klasörde **hiçbir şey çalıştırmadığından** emin ol:

```nginx
location /static/uploads/ {
    add_header X-Content-Type-Options nosniff;
    location ~ \.(php|py|cgi|pl|sh)$ { deny all; }
}
```

Uygulama zaten dosyayı Pillow ile açıp gerçekten resim olduğunu doğruluyor ve
rastgele bir adla kaydediyor; bu ikinci savunma hattı.

---

## 6. Yedekleme

Üç şey yedeklenirse site tamamen geri gelir:

```
instance/toyota.db              ← tüm içerik ve çeviriler
static/uploads/                 ← yüklenen görseller
translations/auto_cache.json    ← çeviri önbelleği
```

Günlük yedek için basit bir cron:

```bash
0 3 * * * cd /srv/toyota_project && tar czf /yedek/toyota-$(date +\%F).tar.gz \
          instance/toyota.db static/uploads translations/auto_cache.json
```

`FLASK_SECRET_KEY`'i de bir yere not et — değişirse tüm oturumlar düşer.

---

## 7. Yayına aldıktan sonra kontrol et

```bash
curl -I https://toyota.example.com/                    # 200, HTTPS
curl     https://toyota.example.com/robots.txt         # gizli adres GEÇMEMELİ
curl -I  https://toyota.example.com/<ADMIN_PATH>/      # X-Robots-Tag: noindex
```

- Panele gir, bir blok kaydet, sitede göründüğünü doğrula
- Yanlış şifreyle gir → **404** almalısın
- Görsel yükle, sayfada göründüğünü doğrula

---

## 8. Bakım

| Ne zaman | Ne yap |
|---|---|
| Çeviriler bozulursa | Panelde blok → **İngilizce çeviriler** → elle düzelt |
| Toplu çeviri tazeleme | `venv/bin/python tools/ceviri_yenile.py` (elle düzeltilenlere dokunmaz) |
| Şifre değişimi | Panelden **Şifre** ekranı (`.env`'ye dokunma) |
| İçerik bozulursa | Yedekten `instance/toyota.db` geri koy |
| Kod güncellemesi sonrası | `venv/bin/python tools/kontrol.py` |
