/* Dil secici: aktif secenegin altindaki pill'i kaydirir.
   Kaynak: static/js/i18n.js.

   NOT: eski i18n.js ayrica data-i18n ozniteligi tasiyan elemanlarin
   metnini JS ile dolduruyordu. Artik gerek yok -- harita gostergesi
   dahil butun metinler sunucuda, app/icerik/ altindaki karsiliktan
   basiliyor. */

export function init() {
  const kutu = document.querySelector(".lang-switch");
  if (!kutu) return;

  const pill = kutu.querySelector(".lang-pill");
  const secenekler = kutu.querySelectorAll(".lang-opt");
  if (!secenekler.length) return;

  function pillKaydir(el) {
    if (!pill || !el) return;
    pill.style.width = el.offsetWidth + "px";
    pill.style.transform = "translateX(" + el.offsetLeft + "px)";
  }

  pillKaydir(kutu.querySelector(".lang-opt.active") || secenekler[0]);

  secenekler.forEach(function (el) {
    /* tiklaninca once pill akici sekilde kaysin, sonra sayfa gecsin */
    el.addEventListener("click", function (e) {
      if (el.classList.contains("active")) return;
      e.preventDefault();
      secenekler.forEach(function (o) { o.classList.remove("active"); });
      el.classList.add("active");
      pillKaydir(el);
      setTimeout(function () { window.location.href = el.href; }, 240);
    });
  });

  window.addEventListener("resize", function () {
    pillKaydir(kutu.querySelector(".lang-opt.active") || secenekler[0]);
  });
}
