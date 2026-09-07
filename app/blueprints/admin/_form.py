# -*- coding: utf-8 -*-
"""Panel formlarindan gelen POST verisini modellere yazan yardimcilar.

ONEMLI AYRIM
------------
Formlarin KENDISI her blok tipi icin elle yaziliyor
(templates/admin/fields/<tip>.html) -- alan adlari Turkce, sirasi ve
gruplandirmasi o tipe ozel. Buradaki kod yalnizca gelen POST'u okuyup
veritabanina yaziyor; "her tabloya otomatik form ureten" bir yapi degil.

ALAN ADI DUZENI
---------------
    f__<anahtar>__<alan>      bir ogenin alani
    sira__<grup>              o gruptaki ogelerin sirasi (virgullu)

`<anahtar>` mevcut oge icin veritabani id'si, yeni eklenen icin
"yeni-1" gibi bir sey. `sira__<grup>` HEM SIRAYI HEM VARLIGI belirler:
listede olmayan oge silinir. Boylece "sil" dugmesi satiri DOM'dan
kaldirmakla yetinir, ayrica bir silme alani gerekmez.

`<grup>` ust seviye ogeler icin oge turudur ("stat", "card"), alt
ogeler icin "<ustanahtar>-<tur>" ("12-bullet").
"""

from __future__ import annotations

import bleach

from ...extensions import db
from ...models import BlockItem

# ============================================================
#  Zengin metin suzgeci
#
#  Editorler kod bilmiyor ama paragraflara kalin/link koyabilmeleri
#  gerekiyor. Bu alanlar sitede |safe ile basildigi icin gelen HTML
#  BEYAZ LISTEDEN geciriliyor: asagidakiler disinda ne varsa etiket
#  olarak silinir (icindeki yazi kalir).
#
#  Sadece kotu niyete karsi degil: yanlislikla yapistirilan Word/
#  tarayici HTML'i sayfayi bozmasin diye de gerekli.
# ============================================================
IZINLI_ETIKETLER = {"strong", "b", "em", "i", "u", "br", "a", "span", "sup", "sub"}
IZINLI_OZNITELIKLER = {"a": ["href", "title", "target", "rel"]}
IZINLI_PROTOKOLLER = ["http", "https", "mailto", "tel"]


def temizle_html(metin: str) -> str:
    """Beyaz liste disindaki etiketleri soker, yaziyi birakir."""
    if not metin:
        return metin
    return bleach.clean(
        metin,
        tags=IZINLI_ETIKETLER,
        attributes=IZINLI_OZNITELIKLER,
        protocols=IZINLI_PROTOKOLLER,
        strip=True,          # etiketi sil, icerigi koru
        strip_comments=True,
    )

# Alan turleri
METIN = "metin"
UZUN = "uzun"
# Bastaki/sondaki boslugu KORUYAN metin. Sayac on/son ekleri icin:
# " km" ile "km" farkli seydir (647 km / 647km). Kirpmak sessizce
# gorunumu bozar -- gidis-donus testi tam bunu yakaladi.
METIN_BOSLUKLU = "metin_bosluklu"
SAYI = "sayi"
TAMSAYI = "tamsayi"
EVET_HAYIR = "evet_hayir"
# Gorsel secici: bos = gorsel yok (0 DEGIL, None)
GORSEL = "gorsel"


# ============================================================
#  Tekil deger okuma
# ============================================================
def _oku(form, ad: str, tur: str):
    ham = form.get(ad)
    if tur == EVET_HAYIR:
        return ham is not None            # isaretli kutu gonderilir
    if ham is None:
        return None
    if tur == METIN_BOSLUKLU:
        return ham if ham != "" else None
    ham = ham.strip()
    if ham == "":
        return None
    if tur == GORSEL:
        try:
            return int(ham)
        except ValueError:
            return None
    if tur == UZUN:
        return temizle_html(ham)
    if tur == SAYI:
        try:
            return float(ham.replace(",", "."))
        except ValueError:
            return None
    if tur == TAMSAYI:
        try:
            return int(float(ham.replace(",", ".")))
        except ValueError:
            return None
    return ham


def _ata(nesne, alan: str, deger, tur: str) -> None:
    """Bos sayilar 0 degil None olmali; bos metin de None."""
    if tur == EVET_HAYIR:
        setattr(nesne, alan, bool(deger))
        return
    setattr(nesne, alan, deger)


# ============================================================
#  Blogun ortak alanlari
# ============================================================
def ortak_alanlari_kaydet(blok, form) -> None:
    blok.heading = _oku(form, "heading", METIN)
    seviye = _oku(form, "heading_level", TAMSAYI)
    blok.heading_level = seviye if seviye in (1, 2, 3) else 2
    blok.intro = _oku(form, "intro", UZUN)
    blok.note = _oku(form, "note", METIN)
    blok.anchor = _oku(form, "anchor", METIN)
    blok.is_visible = _oku(form, "is_visible", EVET_HAYIR)

    # reveal: "sayfadan" (bos) / "evet" / "hayir"
    ham = (form.get("reveal") or "").strip()
    blok.reveal = True if ham == "evet" else (False if ham == "hayir" else None)

    # Panel notu: YALNIZCA panelde gorunen, editore birakilan hatirlatma
    # ("yayindan once dogrulayin" gibi). Sitede hicbir yerde basilmaz ve
    # cevrilmez, o yuzden `settings` icinde -- bir sutun hak etmiyor.
    # Buradan yazilmasi onemli: `ayarlari_kaydet` sonra calisip
    # settings'i kopyaladigi icin deger korunuyor.
    ayarlar = dict(blok.settings or {})
    not_metni = _oku(form, "panel_note", METIN)
    if not_metni:
        ayarlar["panel_note"] = not_metni
    else:
        ayarlar.pop("panel_note", None)
    blok.settings = ayarlar


# ============================================================
#  settings JSON'una yazma
# ============================================================
def ayarlari_kaydet(blok, form, alanlar) -> None:
    """alanlar: [("variant", METIN), ("rates.co2_per_unit.benzin", SAYI), ...]

    Noktali yol ic ice sozluk olusturur. `settings` icinde YALNIZCA
    sayi ve yapisal ayar bulunur -- cevrilebilir metin buraya girmez
    (bkz. app/block_types.py notu).
    """
    ayarlar = dict(blok.settings or {})
    for yol, tur in alanlar:
        deger = _oku(form, "ayar__" + yol.replace(".", "__"), tur)
        parcalar = yol.split(".")
        hedef = ayarlar
        for p in parcalar[:-1]:
            if not isinstance(hedef.get(p), dict):
                hedef[p] = {}
            hedef = hedef[p]
        # GORSEL bos birakilabilir; sayilar 0 olur
        if deger is None and tur in (SAYI, TAMSAYI):
            deger = 0
        hedef[parcalar[-1]] = deger
    blok.settings = ayarlar


# ============================================================
#  Tekrarlayan ogeler
# ============================================================
class OgeYazici:
    """Bir blogun ogelerini yazar ve listede olmayanlari siler.

    Kullanim:
        yazici = OgeYazici(blok, form)
        yazici.grup("stat", [("title", METIN), ("value", METIN)])
        yazici.temizle()
    """

    def __init__(self, blok, form):
        self.blok = blok
        self.form = form
        self.tutulan: list[BlockItem] = []
        self._mevcut = {str(o.id): o for o in blok.all_items if o.id is not None}

    def grup(self, kind: str, alanlar, ust: BlockItem | None = None,
             ust_anahtar: str | None = None, varsayilan=None) -> list[BlockItem]:
        grup_adi = kind if ust is None else f"{ust_anahtar}-{kind}"
        ham = self.form.get("sira__" + grup_adi) or ""
        anahtarlar = [a.strip() for a in ham.split(",") if a.strip()]

        sonuc: list[BlockItem] = []
        for sira_no, anahtar in enumerate(anahtarlar):
            oge = self._mevcut.get(anahtar)
            if oge is None:
                oge = BlockItem(block=self.blok, kind=kind)
                db.session.add(oge)
            oge.kind = kind
            oge.parent = ust
            oge.position = sira_no
            if varsayilan:
                for alan, deger in varsayilan.items():
                    if getattr(oge, alan, None) in (None, ""):
                        setattr(oge, alan, deger)

            for tanim in alanlar:
                # (alan, tur) ya da (alan, tur, varsayilan)
                alan, tur = tanim[0], tanim[1]
                deger = _oku(self.form, f"f__{anahtar}__{alan}", tur)
                if deger is None and len(tanim) > 2:
                    # NOT NULL sutunlar icin (count_from, count_format...)
                    deger = tanim[2]
                _ata(oge, alan, deger, tur)

            oge._form_anahtari = anahtar   # alt ogeler icin gerekiyor
            self.tutulan.append(oge)
            sonuc.append(oge)
        return sonuc

    def temizle(self) -> None:
        """Formda yer almayan ogeleri sil (once alt ogeler)."""
        kalan = {id(o) for o in self.tutulan}
        silinecek = [o for o in self.blok.all_items if id(o) not in kalan]
        # once cocuklar, sonra ebeveynler
        silinecek.sort(key=lambda o: 0 if o.parent_id is None else -1)
        for oge in silinecek:
            db.session.delete(oge)


def yeni_anahtar_uret(onek: str = "yeni") -> str:
    """Sablonun bos satir sablonunda kullandigi yer tutucu."""
    return f"{onek}-__N__"
