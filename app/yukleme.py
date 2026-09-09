# -*- coding: utf-8 -*-
"""Haber gorseli yukleme.

CMS gorsel kutuphanesi bu asamada yok; haber formunun kendi
dosya alani static/uploads/news/ altina yazar. Kayit, static/
klasorune gore yol olarak durur (ornek:
"uploads/news/toyota-corolla-2026-1.jpg") -- kapak icin
News.image sutununda, galeri icin NewsImage.path sutununda.

SAYI SINIRI
-----------
Bir haberde en fazla `Config.MAX_NEWS_IMAGES` gorsel olabilir.
Deger burada TEKRAR YAZILMAZ, azami_gorsel() ile okunur; panelin
sayaci ve tarayici tarafi da ayni degeri sablona basilan bir
data- ozniteliginden alir. Tek yerde durmasinin sebebi acik:
uc katmandan biri digerinden farkli bir sayi bilirse ya kullanici
kabul edilecek bir dosyada reddedilir ya da sunucu limitin
ustunu kabul eder.

Sinir SUNUCUDA da zorlanir: tarayici kontrolu atlanabilir
(curl, devtools, eski tarayici), o yuzden dogrula() son sozu
soyler ve DISKE YAZMADAN once soyler -- reddedilen bir gonderim
uploads/ klasorunde artik dosya birakmaz.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .metin import slugify

IZINLI_UZANTILAR = {".jpg", ".jpeg", ".png", ".webp"}
HABER_KLASORU = Path("uploads") / "news"


class YuklemeHatasi(Exception):
    """Kullaniciya gosterilecek, beklenen bir yukleme hatasi."""


def azami_gorsel() -> int:
    """Haber basina azami gorsel sayisi (Config.MAX_NEWS_IMAGES).

    Limitin okundugu TEK yer. Uygulama baglami disinda cagrilirsa
    (ornek: betikler) 5'e duser.
    """
    try:
        return int(current_app.config.get("MAX_NEWS_IMAGES", 5))
    except RuntimeError:          # uygulama baglami yok
        return 5


def _kok() -> Path:
    return Path(current_app.config["STATIC_DIR"])


def haber_klasoru() -> Path:
    yol = _kok() / HABER_KLASORU
    yol.mkdir(parents=True, exist_ok=True)
    return yol


def uzanti_uygun_mu(ad: str) -> bool:
    return Path(ad).suffix.lower() in IZINLI_UZANTILAR


def panel_yuklenen_mi(gorsel_yolu: str) -> bool:
    """Bu dosya panelden mi geldi? (ornek gorselleri silme)"""
    if not gorsel_yolu:
        return False
    parca = Path(gorsel_yolu.replace("\\", "/"))
    try:
        return parca.parts[:2] == ("uploads", "news")
    except Exception:  # noqa: BLE001
        return False


def _bos_ad(kok: str, uzanti: str) -> str:
    """Cakismayan dosya adi uretir: "kok-1.jpg", "kok-2.jpg", ...

    Ayni kokun BASKA uzantilisi da varsa o numara atlanir; boylece
    klasorde "haber-1.jpg" ve "haber-1.png" yan yana durup hangisinin
    hangi haberin ilk gorseli oldugu belirsizlesmez.
    """
    klasor = haber_klasoru()
    sayac = 1
    while any((klasor / f"{kok}-{sayac}{u}").exists() for u in IZINLI_UZANTILAR):
        sayac += 1
    return f"{kok}-{sayac}{uzanti}"


def _dosya_dogrula(dosya: FileStorage) -> None:
    """Tek dosyanin uzantisi ve boyutu. Uygunsuzsa YuklemeHatasi.

    Diske hicbir sey yazmaz -- cagiran taraf butun dosyalari once
    dogrular, sonra yazar.
    """
    ham_ad = secure_filename(dosya.filename or "")
    if not ham_ad or not uzanti_uygun_mu(ham_ad):
        raise YuklemeHatasi("Görsel jpg, jpeg, png veya webp olmalı.")

    mb = current_app.config.get("UPLOAD_MAX_MB", 4)
    dosya.stream.seek(0, 2)
    boyut = dosya.stream.tell()
    dosya.stream.seek(0)
    if boyut > mb * 1024 * 1024:
        raise YuklemeHatasi(f"Görsel en fazla {mb} MB olabilir.")
    if boyut == 0:
        raise YuklemeHatasi("Yüklenen görsel boş.")


def secilenler(dosyalar) -> list[FileStorage]:
    """Form alanindaki GERCEKTEN secilmis dosyalar.

    Bos bir <input type="file"> de istekte adsiz bir parca birakir;
    onlar sayilirsa "0 dosya sectim ama limit doldu" gibi anlamsiz
    hatalar cikar.
    """
    return [d for d in (dosyalar or []) if d is not None and d.filename]


def dogrula(dosyalar, mevcut_sayi: int = 0) -> list[FileStorage]:
    """SUNUCU TARAFI SON SOZ: sayi + uzanti + boyut.

    `mevcut_sayi` habere KAYITLI ve silinmeyecek gorsel sayisidir.
    Kontrol yeni yuklenenlerin sayisi uzerinden DEGIL, MEVCUT + YENI
    TOPLAMI uzerinden yapilir: 4 gorselli bir habere 2 gorsel daha
    eklenmek istendiginde ikisi de tek basina limitin altinda kalir,
    toplam ise 6'dir ve reddedilmelidir.

    Diske yazmadan once cagrilir; hata durumunda uploads/ klasorune
    tek bir artik dosya bile dusmez.
    """
    gecerli = secilenler(dosyalar)
    azami = azami_gorsel()
    toplam = max(0, mevcut_sayi) + len(gecerli)
    if toplam > azami:
        raise YuklemeHatasi(
            f"En fazla {azami} fotoğraf yükleyebilirsiniz. "
            f"Bu haberde {mevcut_sayi} fotoğraf var, {len(gecerli)} tane daha "
            f"eklenmek isteniyor (toplam {toplam})."
        )
    for dosya in gecerli:
        _dosya_dogrula(dosya)
    return gecerli


def kaydet_coklu(dosyalar, ad_kok: str, mevcut_sayi: int = 0) -> list[str]:
    """Secilen gorselleri yazar, static'e gore yollarini dondurur.

    `ad_kok` haberin slug'idir; dosyalar "<slug>-1.jpg", "<slug>-2.jpg"
    diye adlandirilir -- klasore bakan biri hangi dosyanin hangi habere
    ait oldugunu gorebilsin diye (eskiden uuid idi, okunmuyordu).

    Once TAMAMI dogrulanir, sonra TAMAMI yazilir: ucuncu dosya
    reddedilecekse ilk ikisi de diske dusmemis olur.
    """
    gecerli = dogrula(dosyalar, mevcut_sayi)
    kok = slugify(ad_kok) if ad_kok else uuid4().hex

    yollar: list[str] = []
    for dosya in gecerli:
        uzanti = Path(secure_filename(dosya.filename or "")).suffix.lower()
        ad = _bos_ad(kok, uzanti)
        dosya.save(haber_klasoru() / ad)
        yollar.append(str(HABER_KLASORU / ad).replace("\\", "/"))
    return yollar


def kaydet(dosya: FileStorage | None, ad_kok: str = "") -> str:
    """Tek dosya yukler; yoksa bos metin doner.

    kaydet_coklu()'nun tek dosyalik kisayolu -- dogrulama ve
    adlandirma ayni yerden gecsin diye ayri bir govdesi yok.
    """
    if dosya is None or not dosya.filename:
        return ""
    yollar = kaydet_coklu([dosya], ad_kok)
    return yollar[0] if yollar else ""


def sahipsiz_dosyalar(kullanilan: set[str]) -> list[Path]:
    """uploads/news/ altinda olup veritabaninda GECMEYEN dosyalar.

    `kullanilan` static'e gore yollardan olusur ("uploads/news/x.jpg").
    .gitkeep gibi nokta ile baslayan dosyalar sayilmaz.
    """
    klasor = haber_klasoru()
    sahipsiz = []
    for yol in sorted(klasor.iterdir()):
        if not yol.is_file() or yol.name.startswith("."):
            continue
        goreli = str(HABER_KLASORU / yol.name).replace("\\", "/")
        if goreli not in kullanilan:
            sahipsiz.append(yol)
    return sahipsiz


def sil_dosya(gorsel_yolu: str) -> None:
    """Yalnizca panelin yukledigi haber gorselini siler."""
    if not panel_yuklenen_mi(gorsel_yolu):
        return
    yol = (_kok() / gorsel_yolu).resolve()
    kok = haber_klasoru().resolve()
    if kok not in yol.parents and yol != kok:
        return
    if yol.is_file():
        yol.unlink()
