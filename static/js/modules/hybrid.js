/* Hibrit akis diyagrami.

   Iki is yapiyor:
     1. Asama dugmeleri akordeon gibi calisir (paylasilan yardimci).
     2. Acik asamanin `data-aktif` listesi semanin kabina tasinir;
        vurgulamayi CSS yapiyor ([data-aktif~="motor"] gibi).

   Dinleyici `akordeon`dan SONRA eklendigi icin tiklama sirasinda
   aria-expanded zaten guncellenmis oluyor -- durumu oradan okuyoruz,
   ayrica bir yerde tutmuyoruz. */

import { akordeon } from "./utils.js";

function semayi_kur(bolum) {
  const sema = bolum.querySelector("[data-hibrit-sema]");
  const butonlar = bolum.querySelectorAll(".tk-hybrid__button");
  if (!sema || !butonlar.length) return;

  butonlar.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const acik = btn.getAttribute("aria-expanded") === "true";
      // Kapatilinca sema notr hale doner.
      sema.setAttribute("data-aktif", acik ? (btn.dataset.aktif || "") : "");
    });
  });
}

export function init() {
  const bolumler = document.querySelectorAll(".tk-hybrid");
  if (!bolumler.length) return;

  akordeon({
    buton: ".tk-hybrid .tk-hybrid__button",
    oge: ".tk-hybrid__step",
  });

  bolumler.forEach(semayi_kur);
}
