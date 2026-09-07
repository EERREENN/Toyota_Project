# -*- coding: utf-8 -*-
"""Metin yardimcilari."""

from __future__ import annotations

import re
from typing import Any

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
    """'Genchi Genbutsu' / 'İsraf' -> aramada karsilastirilabilir hal.

    Sozluk sablonu bunu `data-arama` ozniteligine basar; tarayici
    tarafi her tusta yeniden normalize etmek zorunda kalmaz.
    """
    if not metin:
        return ""
    return str(metin).translate(_SADE_HARFLER).lower()


# Ay adlari: tarih ISO olarak saklaniyor ("2026-02-18"), ekranda dilin
# kendi yazimiyla gosteriliyor. Icerik degil arayuz oldugu icin
# app/ceviri.py sozlugune girmiyor.
_AYLAR = {
    "tr": ("Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
           "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"),
    "en": ("January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"),
}


def tarih_metni(iso: str | None, locale: str = "tr") -> str:
    """'2026-02-18' -> '18 Şubat 2026' / '18 February 2026'.

    Tanimadigi bicimi oldugu gibi dondurur: elle bir sey yazilmissa
    sayfa yine de bir sey gosterir.
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


# ============================================================
#  Adres parcasi (slug) uretimi
# ============================================================
# Turkce harf donusumu yukaridaki sadelestir() ile AYNI tablodan
# geliyor; ikisi ayrisirsa "Şubat" basligi ile sozluk aramasi farkli
# ASCII karsiliklar uretirdi.
_SLUG_TEMIZ = re.compile(r"[^a-z0-9]+")


def slugify(baslik: str) -> str:
    """'Toyota Türkiye İhracat Başarısını Sürdürüyor'
       -> 'toyota-turkiye-ihracat-basarisini-surduruyor'

    Turkce harfler ASCII karsiligina iner, kalan her sey tireye
    donusur, bastaki/sondaki tireler kirpilir. Sonuc bos cikarsa
    (ornek: yalnizca noktalama) "haber" dondurulur -- adres hicbir
    zaman bos kalmasin.
    """
    sade = sadelestir(baslik)
    slug = _SLUG_TEMIZ.sub("-", sade).strip("-")
    return slug or "haber"


def benzersiz_slug(baslik: str, var_mi) -> str:
    """Cakismayan bir slug uretir: 'ornek-haber', 'ornek-haber-2', ...

    `var_mi(slug)` -> bu slug kullanimda mi? True/False dondurmeli.
    Cagiran taraf boylece veritabanina nasil bakacagina kendi karar
    verir; bu fonksiyonun veritabanindan haberi olmaz.
    """
    temel = slugify(baslik)
    if not var_mi(temel):
        return temel
    sayac = 2
    while var_mi(f"{temel}-{sayac}"):
        sayac += 1
    return f"{temel}-{sayac}"
