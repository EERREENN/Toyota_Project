# -*- coding: utf-8 -*-
"""CSS bolunmesinin dogrulanmasi.

Iki bagimsiz kontrol yapar:

  1) DENKLIK  (--denklik)
     Eski tek dosya (tools/_retired/style.css) uzerindeki her kural,
     sinif adlari yeniden adlandirildiktan sonra yeni dosyalarda
     BIREBIR var mi? Bir bildirim (declaration) bile kaybolduysa
     ya da degistiyse burada gorunur.

  2) KAPSAM  (--kapsam)
     Uretilen HTML'de kullanilan her sinif CSS'te tanimli mi?
     (tanimsizsa o eleman stilsiz kalir -- gorunum bozulur)
     Ve tersi: CSS'te tanimli olup HTML'de hic kullanilmayan sinif
     var mi? (yeniden adlandirmada atlanmis bir yer olabilir)

    python tools/css_check.py            # ikisini de calistir
    python tools/css_check.py --denklik
    python tools/css_check.py --kapsam
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.css_rename_map import (          # noqa: E402
    ATILAN,
    DEGISTIRILEN,
    EDITORE_BAGLI,
    STILSIZ_KABUL,
    ID_TO_CLASS,
    KEYFRAME_RENAME,
    KORUNAN,
    RENAME,
)

ESKI_CSS = ROOT / "tools" / "_retired" / "style.css"
YENI_KOK = ROOT / "static" / "css"

# Sablonlarda uretilen HTML'i okumak icin
ANLIK = ROOT / "tools" / "_snapshots" / "after"


# ============================================================
#  Basit CSS ayristirici
#
#  Elle yazilmis, duzenli bir CSS icin yeterli: yorumlari atar,
#  @media / @keyframes bloklarina iner ve her kurali
#  (baglam, secici, bildirimler) uclusu olarak dondurur.
# ============================================================
_YORUM = re.compile(r"/\*.*?\*/", re.S)


def ayristir(css: str, baglam: str = "") -> list[tuple[str, str, str]]:
    css = _YORUM.sub("", css)
    kurallar: list[tuple[str, str, str]] = []
    i = 0
    n = len(css)
    while i < n:
        acilis = css.find("{", i)
        if acilis == -1:
            break
        baslik = css[i:acilis].strip()

        # eslesen kapanis parantezini bul
        derinlik = 1
        j = acilis + 1
        while j < n and derinlik:
            if css[j] == "{":
                derinlik += 1
            elif css[j] == "}":
                derinlik -= 1
            j += 1
        govde = css[acilis + 1:j - 1]

        if baslik.startswith("@media") or baslik.startswith("@supports"):
            ic_baglam = (baglam + " " + _sadelestir(baslik)).strip()
            kurallar.extend(ayristir(govde, ic_baglam))
        elif baslik.startswith("@keyframes"):
            ad = baslik.split(None, 1)[1].strip()
            ad = KEYFRAME_RENAME.get(ad, ad)
            kurallar.append((baglam, f"@keyframes {ad}", _sadelestir(govde)))
        elif baslik.startswith("@"):
            kurallar.append((baglam, _sadelestir(baslik), _sadelestir(govde)))
        else:
            for secici in baslik.split(","):
                secici = _sadelestir(secici)
                if secici:
                    kurallar.append((baglam, secici, _bildirimler(govde)))
        i = j
    return kurallar


def _sadelestir(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _bildirimler(govde: str) -> str:
    """Bildirimleri sadelestirip sirala.

    Siralama, bolerken kurallarin sirasinin degismesini onemsiz kilar;
    ayni kural icindeki kisayol cakismalari zaten tek bildirimde durur.
    """
    parcalar = [
        _sadelestir(p) for p in govde.split(";")
        if _sadelestir(p)
    ]
    # url(...) yollari klasor degisikligi yuzunden farkli; dosya adina indir
    parcalar = [re.sub(r'url\(["\']?[^)"\']*/([^)"\'/]+)["\']?\)',
                       r'url(\1)', p) for p in parcalar]
    return "; ".join(sorted(parcalar))


# ============================================================
#  Secici yeniden adlandirma
# ============================================================
_SINIF = re.compile(r"\.([A-Za-z_][\w-]*)")
_ID = re.compile(r"#([A-Za-z_][\w-]*)")


def secici_donustur(secici: str) -> str:
    def sinif_degistir(m):
        return "." + RENAME.get(m.group(1), m.group(1))

    def id_degistir(m):
        ad = m.group(1)
        if ad in ID_TO_CLASS:
            return "." + ID_TO_CLASS[ad]
        return "#" + ad

    return _ID.sub(id_degistir, _SINIF.sub(sinif_degistir, secici))


def bildirim_donustur(bildirim: str) -> str:
    """Eski bildirimlerdeki @keyframes adlarini yeni adlarina cevirir.

    `animation: hat-kay 0.9s linear infinite` gibi kisayollarda animasyon
    adi bildirimin ICINDE gecer; secici donusumu buraya ulasmaz.
    """
    for eski, yeni in KEYFRAME_RENAME.items():
        bildirim = re.sub(rf"(?<![\w-]){re.escape(eski)}(?![\w-])", yeni, bildirim)
    return bildirim


# ============================================================
#  1) DENKLIK
# ============================================================
# Panelin CSS'i sitenin degil: anlik goruntulerde panel HTML'i yok,
# o yuzden kapsam kontrolunde disarida tutulur (yoksa butun yn-*
# siniflari "kullanilmiyor" gorunur).
PANEL_CSS = {"admin.css", "admin-news.css"}


def yeni_dosyalar(panel_dahil: bool = True) -> list[Path]:
    dosyalar = sorted(YENI_KOK.rglob("*.css"))
    if not panel_dahil:
        dosyalar = [d for d in dosyalar if d.name not in PANEL_CSS]
    return dosyalar


def denklik() -> int:
    if not ESKI_CSS.exists():
        print(f"  ! {ESKI_CSS} yok -- denklik kontrolu atlandi")
        return 0

    eski = ayristir(ESKI_CSS.read_text(encoding="utf-8"))
    yeni: list[tuple[str, str, str]] = []
    for yol in yeni_dosyalar():
        yeni.extend(ayristir(yol.read_text(encoding="utf-8")))

    # eski kurallari yeni adlara cevir
    eski_donuk = []
    atlanan = 0
    for baglam, secici, bildirim in eski:
        if any(f".{ad}" in secici for ad in ATILAN):
            atlanan += 1
            continue
        eski_donuk.append(
            (baglam, secici_donustur(secici), bildirim_donustur(bildirim))
        )

    yeni_kume = {}
    for k in yeni:
        yeni_kume.setdefault((k[0], k[1]), []).append(k[2])

    eksik = []
    farkli = []
    bilerek = []
    for baglam, secici, bildirim in eski_donuk:
        adaylar = yeni_kume.get((baglam, secici))
        if adaylar is None:
            eksik.append((baglam, secici, bildirim))
        elif bildirim not in adaylar:
            # Kasitli tasarim degisiklikleri hata degil (bkz.
            # css_rename_map.DEGISTIRILEN). Kural HALA VAR, yalnizca
            # bildirimleri farkli -- kaybolan bir sey yok.
            if secici in DEGISTIRILEN:
                bilerek.append((secici, DEGISTIRILEN[secici]))
            else:
                farkli.append((baglam, secici, bildirim, adaylar))

    print("1) DENKLIK  (eski kural -> yeni dosyalarda var mi)")
    print("-" * 62)
    print(f"  eski kural sayisi     : {len(eski)}")
    print(f"  bilerek atilan        : {atlanan}")
    print(f"  yeni kural sayisi     : {len(yeni)}")
    print(f"  EKSIK (bulunamadi)    : {len(eksik)}")
    print(f"  bilerek degistirilen  : {len(bilerek)}")
    print(f"  FARKLI (bildirim)     : {len(farkli)}")
    print()

    for baglam, secici, _b in eksik:
        yer = f"@{baglam} " if baglam else ""
        print(f"  ! EKSIK  {yer}{secici}")
    for baglam, secici, bildirim, adaylar in farkli:
        yer = f"@{baglam} " if baglam else ""
        print(f"  ! FARKLI {yer}{secici}")
        print(f"      eski: {bildirim[:110]}")
        for a in adaylar:
            print(f"      yeni: {a[:110]}")

    if bilerek:
        print()
        for secici, sebep in bilerek:
            print(f"  [bilerek] {secici} -- {sebep}")
    if atlanan:
        print()
        for ad, sebep in ATILAN.items():
            print(f"  [atildi] .{ad} -- {sebep}")
    print()
    return len(eksik) + len(farkli)


# ============================================================
#  2) KAPSAM
# ============================================================
def html_siniflari() -> set[str]:
    siniflar: set[str] = set()
    if not ANLIK.exists():
        return siniflar
    for yol in ANLIK.glob("*.html"):
        metin = yol.read_text(encoding="utf-8")
        for m in re.finditer(r'class="([^"]*)"', metin):
            for ad in m.group(1).split():
                siniflar.add(ad)
    return siniflar


def css_siniflari() -> set[str]:
    siniflar: set[str] = set()
    for yol in yeni_dosyalar(panel_dahil=False):
        for _baglam, secici, _b in ayristir(yol.read_text(encoding="utf-8")):
            for m in _SINIF.finditer(secici):
                siniflar.add(m.group(1))
    return siniflar


def kapsam() -> int:
    html = html_siniflari()
    css = css_siniflari()

    if not html:
        print("2) KAPSAM")
        print("-" * 62)
        print("  ! tools/_snapshots/after bos -- once: python tools/snapshot.py after")
        print()
        return 1

    # Bilerek stilsiz olanlar: JS tutamaklari ve calisma aninda
    # eklenen durum siniflari (bkz. css_rename_map.STILSIZ_KABUL)
    js_ekli = set(STILSIZ_KABUL)

    tanimsiz = sorted(html - css - js_ekli)
    kullanilmayan = sorted(css - html - js_ekli - KORUNAN - set(EDITORE_BAGLI))

    print("2) KAPSAM  (HTML sinifi <-> CSS tanimi)")
    print("-" * 62)
    print(f"  HTML'de kullanilan sinif : {len(html)}")
    print(f"  CSS'te tanimli sinif     : {len(css)}")
    print(f"  TANIMSIZ (stilsiz kalir) : {len(tanimsiz)}")
    print(f"  CSS'te var, HTML'de yok  : {len(kullanilmayan)}")
    print()

    for ad in tanimsiz:
        print(f"  ! TANIMSIZ  .{ad}")
    if not tanimsiz:
        print("  Bilerek stilsiz birakilanlar:")
        for ad, sebep in sorted(STILSIZ_KABUL.items()):
            print(f"    .{ad:32s} {sebep}")
    for ad in kullanilmayan:
        print(f"  - kullanilmayan  .{ad}")
    if EDITORE_BAGLI:
        print("  Editor gorsel secince devreye girenler:")
        for ad, sebep in sorted(EDITORE_BAGLI.items()):
            print(f"    .{ad:28s} {sebep}")
    print()
    return len(tanimsiz)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--denklik", action="store_true")
    p.add_argument("--kapsam", action="store_true")
    a = p.parse_args()

    hepsi = not (a.denklik or a.kapsam)
    hata = 0
    if hepsi or a.denklik:
        hata += denklik()
    if hepsi or a.kapsam:
        hata += kapsam()

    print("=" * 62)
    print("SONUC:", "BASARISIZ" if hata else "CSS BOLUNMESI KAYIPSIZ")
    print("=" * 62)
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
