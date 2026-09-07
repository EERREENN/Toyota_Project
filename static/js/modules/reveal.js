/* Kaydirdikca yumusakca belirme.
   Kaynak: static/js/global.js ve static/js/uretim.js (ikisi de aynıydı). */

import { azHareket } from "./utils.js";

export function init() {
  const parcalar = document.querySelectorAll(".reveal");
  if (!parcalar.length) return;

  if (azHareket() || !("IntersectionObserver" in window)) {
    parcalar.forEach(function (el) { el.classList.add("reveal-in"); });
    return;
  }

  const gozlemci = new IntersectionObserver(
    function (girisler) {
      girisler.forEach(function (g) {
        if (g.isIntersecting) {
          g.target.classList.add("reveal-in");
          gozlemci.unobserve(g.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  parcalar.forEach(function (el) { gozlemci.observe(el); });
}
