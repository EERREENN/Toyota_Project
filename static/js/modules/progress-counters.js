/* Cevre sayfasindaki ilerleme kartlari -- ekrana girince sayar.
   Kaynak: static/js/cevre.js, 1. bolum. */

import { azHareket, bicimlendirici, say } from "./utils.js";

const trFmt = bicimlendirici("tr-TR");

function bicim(n, duz) {
  return duz || !trFmt ? String(n) : trFmt.format(n);
}

function sayacBaslat(kart) {
  const el = kart.querySelector(".tk-stat-grid__count");
  if (!el) return;

  const hedef = parseFloat(kart.getAttribute("data-hedef"));
  const baslangic = parseFloat(kart.getAttribute("data-baslangic") || "0");
  const duz = kart.getAttribute("data-format") === "plain";

  function yaz(v) {
    el.textContent = bicim(Math.round(v), duz);
  }

  if (azHareket() || !window.requestAnimationFrame) {
    yaz(hedef);
    return;
  }

  say(1100, function (e) { yaz(baslangic + (hedef - baslangic) * e); });
}

export function init() {
  const kartlar = document.querySelectorAll(".tk-stat-grid__progress-card[data-sayac]");
  if (!kartlar.length) return;

  if (!("IntersectionObserver" in window)) {
    kartlar.forEach(sayacBaslat);
    return;
  }

  const gozlemci = new IntersectionObserver(function (girisler) {
    girisler.forEach(function (giris) {
      if (giris.isIntersecting) {
        sayacBaslat(giris.target);
        gozlemci.unobserve(giris.target);
      }
    });
  }, { threshold: 0.35 });

  kartlar.forEach(function (k) {
    const el = k.querySelector(".tk-stat-grid__count");
    if (el) {
      const duz = k.getAttribute("data-format") === "plain";
      el.textContent = bicim(parseFloat(k.getAttribute("data-baslangic") || "0"), duz);
    }
    gozlemci.observe(k);
  });
}
