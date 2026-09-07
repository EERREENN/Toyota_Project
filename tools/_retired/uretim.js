/* TPS sayfasi: bolumler kaydirdikca hattan akiyormus gibi yandan girer */
(function () {
  "use strict";

  var azHareket =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var parcalar = document.querySelectorAll(".reveal");

  if (azHareket || !("IntersectionObserver" in window)) {
    parcalar.forEach(function (el) { el.classList.add("reveal-in"); });
    return;
  }

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
})();
