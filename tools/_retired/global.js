/* Global Toyota sayfasi: akis efektleri
   1) Sayilar sayfa acilinca sayarak dolar
   2) Bolumler asagi kaydirdikca yumusakca belirir
*/
(function () {
  "use strict";

  var azHareket =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------
     1) Sayac animasyonu
     --------------------------------------------------------- */
  var nf;
  try { nf = new Intl.NumberFormat("tr-TR"); } catch (e) { nf = null; }

  function yaz(el, deger) {
    var n = Math.round(deger);
    var govde = (nf && el.hasAttribute("data-count-group"))
      ? nf.format(n)
      : String(n);
    el.textContent =
      (el.getAttribute("data-count-prefix") || "") +
      govde +
      (el.getAttribute("data-count-suffix") || "");
  }

  function say(el) {
    var hedef = parseFloat(el.getAttribute("data-count-to"));
    if (isNaN(hedef)) return;

    if (azHareket || !window.requestAnimationFrame) {
      yaz(el, hedef);
      return;
    }

    var sure = 1500;
    var t0 = null;
    yaz(el, 0);

    function adim(t) {
      if (t0 === null) t0 = t;
      var p = Math.min((t - t0) / sure, 1);
      var e = 1 - Math.pow(1 - p, 3); // easeOutCubic
      yaz(el, hedef * e);
      if (p < 1) requestAnimationFrame(adim);
    }
    requestAnimationFrame(adim);
  }

  var sayaclar = document.querySelectorAll("[data-count-to]");
  // istek: sayilar SAYFA ACILINCA saymaya baslasin
  sayaclar.forEach(say);

  /* ---------------------------------------------------------
     2) Kaydirdikca belirme
     --------------------------------------------------------- */
  var parcalar = document.querySelectorAll(".reveal");
  if (azHareket || !("IntersectionObserver" in window)) {
    parcalar.forEach(function (el) { el.classList.add("reveal-in"); });
  } else {
    var gozlemci = new IntersectionObserver(
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
})();
