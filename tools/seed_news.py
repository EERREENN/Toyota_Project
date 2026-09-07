# -*- coding: utf-8 -*-
"""Haber veritabanina ORNEK icerik yazar.

    python tools/seed_news.py            # eksik haberleri ekler
    python tools/seed_news.py --liste    # veritabanindakileri gosterir
    python tools/seed_news.py --sifirla  # ONCE hepsini siler, sonra ekler

TEKRAR CALISTIRILABILIR: eslesme `slug` uzerinden yapilir, ayni haber
ikinci kez eklenmez. Var olan kayitlarin uzerine de YAZMAZ -- elle
duzeltilmis bir metni ezmesin diye.

DIKKAT: buradaki haberler GERCEK DEGIL. Haber sayfasinin akisini
(liste -> kart -> detay, sayfalama, taslak filtresi) calisir halde
gostermek icin duruyorlar. Gercek haberler girildiginde bu dosya
silinebilir.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app                     # noqa: E402
from app.extensions import db                  # noqa: E402
from app.metin import benzersiz_slug           # noqa: E402
from app.models import News                    # noqa: E402

# Sayfalamayi gorebilmek icin sayfa boyutundan (6) fazla yayin var.
# Sonuncusu TASLAK: sitede gorunmemeli.
ORNEKLER = [
    {
        "date": date(2026, 2, 18),
        "image": "img/tmmt_img/corolla.jpg",
        "is_published": True,
        "category_tr": "Üretim", "category_en": "Production",
        "title_tr": "Örnek haber başlığı — üretim",
        "title_en": "Sample news headline — production",
        "summary_tr": "Bu bir örnek haber özetidir. Gerçek haber metni "
                      "eklendiğinde bu alan değiştirilecek.",
        "summary_en": "This is a sample news summary. It will be replaced "
                      "when the real article is added.",
        "content_tr": "Bu paragraf, haber detay sayfasının düzenini göstermek "
                      "için konulmuş örnek bir metindir.\n\n"
                      "Gerçek haberler eklendiğinde başlık, tarih, kategori, "
                      "görsel ve metin bu yapıyı aynen kullanacak.",
        "content_en": "This paragraph is sample text placed here to show the "
                      "layout of the news detail page.\n\n"
                      "When real articles are added, the headline, date, "
                      "category, image and body will use this same structure.",
    },
    {
        "date": date(2026, 2, 4),
        "image": "img/tmmt_img/kalite.webp",
        "is_published": True,
        "category_tr": "Kalite", "category_en": "Quality",
        "title_tr": "Örnek haber başlığı — kalite",
        "title_en": "Sample news headline — quality",
        "summary_tr": "İkinci örnek haber. Kart ızgarasının iki sütunlu "
                      "yerleşimini göstermek için duruyor.",
        "summary_en": "Second sample article. It is here to show the "
                      "two-column layout of the card grid.",
        "content_tr": "Örnek metin. Haber içeriği düz metin olarak saklanır; "
                      "boş satır yeni paragraf başlatır.\n\n"
                      "Paragraf içindeki tek satır sonları\nolduğu gibi "
                      "korunur.",
        "content_en": "Sample text. Article content is stored as plain text; "
                      "a blank line starts a new paragraph.\n\n"
                      "Single line breaks inside a paragraph\nare preserved "
                      "as they are.",
    },
    {
        "date": date(2026, 1, 22),
        "image": "img/tmmt_img/montaj.jpg",
        "is_published": True,
        "category_tr": "Çevre", "category_en": "Environment",
        "title_tr": "Örnek haber başlığı — çevre",
        "title_en": "Sample news headline — environment",
        "summary_tr": "Üçüncü örnek haber. Listede tarihe göre sıralama "
                      "yapıldığını göstermek için farklı bir tarih taşıyor.",
        "summary_en": "Third sample article. It carries a different date to "
                      "show that the list is sorted by date.",
        "content_tr": "Örnek metin. Haberler listede en yeniden en eskiye "
                      "doğru sıralanır.",
        "content_en": "Sample text. Articles are listed from newest to "
                      "oldest.",
    },
    {
        # Gorseli BILEREK bos: gorseli olmayan haberde kartin yer tutucu
        # gostermesi gerekiyor (bkz. templates/components/news_card.html).
        "date": date(2026, 1, 9),
        "image": "",
        "is_published": True,
        "category_tr": "Kurumsal", "category_en": "Corporate",
        "title_tr": "Örnek haber başlığı — görselsiz",
        "title_en": "Sample news headline — without image",
        "summary_tr": "Dördüncü örnek haber. Görseli olmayan bir haberin "
                      "kartta nasıl göründüğünü gösterir.",
        "summary_en": "Fourth sample article. It shows how a card looks when "
                      "the article has no image.",
        "content_tr": "Örnek metin. Görsel girilmemişse detay sayfasında da "
                      "görsel alanı hiç basılmaz.",
        "content_en": "Sample text. When no image is given, the detail page "
                      "does not print an image area at all.",
    },
    {
        "date": date(2025, 12, 15),
        "image": "img/tmmt_img/pres.jpg",
        "is_published": True,
        "category_tr": "Üretim", "category_en": "Production",
        "title_tr": "Örnek haber başlığı — pres hattı",
        "title_en": "Sample news headline — press line",
        "summary_tr": "Beşinci örnek haber.",
        "summary_en": "Fifth sample article.",
        "content_tr": "Örnek metin.",
        "content_en": "Sample text.",
    },
    {
        "date": date(2025, 11, 28),
        "image": "img/tmmt_img/kaynak.jpg",
        "is_published": True,
        "category_tr": "Üretim", "category_en": "Production",
        "title_tr": "Örnek haber başlığı — kaynak hattı",
        "title_en": "Sample news headline — welding line",
        "summary_tr": "Altıncı örnek haber. Bu haberle birlikte ilk sayfa dolar.",
        "summary_en": "Sixth sample article. With this one the first page is full.",
        "content_tr": "Örnek metin.",
        "content_en": "Sample text.",
    },
    {
        "date": date(2025, 11, 6),
        "image": "img/tmmt_img/boya.jpg",
        "is_published": True,
        "category_tr": "Kalite", "category_en": "Quality",
        "title_tr": "Örnek haber başlığı — boya hattı",
        "title_en": "Sample news headline — paint shop",
        "summary_tr": "Yedinci örnek haber. Sayfa boyutu 6 olduğu için bu "
                      "haber ikinci sayfaya düşer.",
        "summary_en": "Seventh sample article. Since the page size is 6, this "
                      "one falls onto the second page.",
        "content_tr": "Örnek metin.",
        "content_en": "Sample text.",
    },
    {
        # TASLAK -- sitede gorunmemeli, adresi yazan 404 almali.
        "date": date(2026, 3, 1),
        "image": "img/tmmt_img/2023.webp",
        "is_published": False,
        "category_tr": "Kurumsal", "category_en": "Corporate",
        "title_tr": "Örnek taslak haber — yayında değil",
        "title_en": "Sample draft article — not published",
        "summary_tr": "Bu haber TASLAK. Tarihi en yeni olmasına rağmen "
                      "listede görünmemeli.",
        "summary_en": "This article is a DRAFT. Even though its date is the "
                      "newest, it must not appear in the list.",
        "content_tr": "Örnek metin. Taslak haberin adresi doğrudan yazılırsa "
                      "404 dönmeli.",
        "content_en": "Sample text. Typing a draft article's address directly "
                      "must return 404.",
    },
]


def _slug_var_mi(slug: str) -> bool:
    return db.session.query(News.id).filter_by(slug=slug).first() is not None


def ekle() -> tuple[int, int]:
    """Eksik ornekleri ekler. -> (eklenen, atlanan)"""
    eklenen = atlanan = 0
    for veri in ORNEKLER:
        # Ayni haber ikinci kez eklenmesin: basliktan uretilen temel
        # slug zaten varsa bu ornek islenmis demektir.
        from app.metin import slugify
        temel = slugify(veri["title_tr"])
        if _slug_var_mi(temel):
            atlanan += 1
            continue
        haber = News(slug=benzersiz_slug(veri["title_tr"], _slug_var_mi), **veri)
        db.session.add(haber)
        eklenen += 1
    db.session.commit()
    return eklenen, atlanan


def listele() -> None:
    kayitlar = db.session.query(News).order_by(News.date.desc()).all()
    if not kayitlar:
        print("veritabani bos")
        return
    print(f"{'tarih':12} {'durum':8} {'slug':46} baslik")
    print("-" * 100)
    for h in kayitlar:
        durum = "yayinda" if h.is_published else "TASLAK"
        print(f"{h.date.isoformat():12} {durum:8} {h.slug:46} {h.title_tr}")
    print(f"\ntoplam {len(kayitlar)} "
          f"({sum(1 for h in kayitlar if h.is_published)} yayinda)")


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

        if secenek.sifirla:
            silinen = db.session.query(News).delete()
            db.session.commit()
            print(f"{silinen} haber silindi")

        eklenen, atlanan = ekle()
        print(f"eklenen: {eklenen}   zaten vardi: {atlanan}")
        print()
        listele()
    return 0


if __name__ == "__main__":
    sys.exit(main())
