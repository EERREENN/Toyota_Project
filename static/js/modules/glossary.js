/* TPS kavram sozlugu -- arama kutusu + akordeon.

   Akordeon davranisi zaman tuneli / adim adim ile ayni oldugu icin
   paylasilan `akordeon` yardimcisi kullaniliyor.

   Arama TARAYICIDA: liste zaten sayfada, sunucuya gitmeye gerek yok.
   Her satirin aranacak metni sunucu tarafinda hazirlanip
   `data-arama` ozniteligine yazildi (app/content.py -> sadelestir),
   yani her tusta yeniden normalize etmiyoruz -- yalnizca SORGUYU
   sadelestirip icinde ariyoruz.

   DIKKAT: buradaki SADE_HARFLER tablosu app/content.py'deki
   `_SADE_HARFLER` ile ayni olmali. Ayrisirlarsa arama sessizce
   eksik sonuc dondurur. */

import { akordeon } from "./utils.js";

const SADE_HARFLER = {
  "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g",
  "ı": "i", "I": "i", "İ": "i",
  "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
  "â": "a", "Â": "a", "î": "i", "Î": "i", "û": "u", "Û": "u",
};

function sadelestir(metin) {
  let cikti = "";
  for (const harf of String(metin || "")) {
    cikti += SADE_HARFLER[harf] !== undefined ? SADE_HARFLER[harf] : harf;
  }
  return cikti.toLowerCase();
}

function sozlugu_kur(kap) {
  const kutu = kap.querySelector("[data-sozluk-arama]");
  const sayac = kap.querySelector("[data-sozluk-sayac]");
  const bos = kap.querySelector("[data-sozluk-bos]");
  const satirlar = Array.prototype.slice.call(
    kap.querySelectorAll(".tk-glossary__item")
  );
  if (!kutu || !satirlar.length) return;

  const toplam = satirlar.length;
  // Sayac birimi sablondan geliyor: JS app/ceviri.py sozlugunu
  // goremiyor, bu yuzden metin data-sozluk-birim ile aktariliyor.
  // Oznitelik yoksa Turkce varsayilana dusuyoruz ki bilesen baska
  // bir sayfada oznitelisiz kullanilirsa bozulmasin.
  const birim = kap.getAttribute("data-sozluk-birim") || "terim";

  function kapat(satir) {
    const btn = satir.querySelector(".tk-glossary__button");
    if (!btn || btn.getAttribute("aria-expanded") !== "true") return;
    btn.setAttribute("aria-expanded", "false");
    const detay = document.getElementById(btn.getAttribute("aria-controls"));
    if (detay) detay.hidden = true;
    satir.classList.remove("is-open");
  }

  function filtrele() {
    const sorgu = sadelestir(kutu.value).trim();
    let gorunen = 0;

    satirlar.forEach(function (satir) {
      const uygun = !sorgu ||
        (satir.getAttribute("data-arama") || "").indexOf(sorgu) !== -1;
      satir.hidden = !uygun;
      if (uygun) gorunen += 1;
      // Gizlenen satir acik kalmasin: arama temizlenince yarim
      // acilmis bir detay gorunmesin.
      else kapat(satir);
    });

    if (bos) bos.hidden = gorunen !== 0;
    if (sayac) {
      sayac.textContent = sorgu
        ? gorunen + " / " + toplam + " " + birim
        : "";
    }
  }

  kutu.addEventListener("input", filtrele);
  // Arama kutusundaki "temizle" (x) dugmesi de input uretir, ama
  // Escape uretmez -- klavyeyle temizleyebilmek icin:
  kutu.addEventListener("keydown", function (olay) {
    if (olay.key === "Escape" && kutu.value) {
      kutu.value = "";
      filtrele();
    }
  });
}

export function init() {
  const kaplar = document.querySelectorAll("[data-sozluk]");
  if (!kaplar.length) return;

  akordeon({
    buton: ".tk-glossary .tk-glossary__button",
    oge: ".tk-glossary__item",
  });

  kaplar.forEach(sozlugu_kur);
}
