/* [data-count-to] sayaclari -- sayfa acilir acilmaz saymaya baslar.
   Kaynak: static/js/global.js, 1. bolum. */

import { azHareket, bicimlendirici, say } from "./utils.js";

const nf = bicimlendirici("tr-TR");

function yaz(el, deger) {
  const n = Math.round(deger);
  const govde = (nf && el.hasAttribute("data-count-group"))
    ? nf.format(n)
    : String(n);
  el.textContent =
    (el.getAttribute("data-count-prefix") || "") +
    govde +
    (el.getAttribute("data-count-suffix") || "");
}

function sayacBaslat(el) {
  const hedef = parseFloat(el.getAttribute("data-count-to"));
  if (isNaN(hedef)) return;

  if (azHareket() || !window.requestAnimationFrame) {
    yaz(el, hedef);
    return;
  }

  yaz(el, 0);
  say(1500, function (e) { yaz(el, hedef * e); });
}

export function init() {
  const sayaclar = document.querySelectorAll("[data-count-to]");
  if (!sayaclar.length) return;
  // istek: sayilar SAYFA ACILINCA saymaya baslasin
  sayaclar.forEach(sayacBaslat);
}
