/* Ceviri yardimcisi + dil secici pill animasyonu */
(function () {
  var I18N = { lang: "tr", t: {} };
  var dataEl = document.getElementById("app-i18n");
  if (dataEl) {
    try { I18N = JSON.parse(dataEl.textContent); } catch (e) { /* yoksay */ }
  }
  window.APP_I18N = I18N;

  /* JS icinden cevrilebilir metin almak icin:  i18n("map.factory")  */
  window.i18n = function (key, fallback) {
    return (I18N.t && I18N.t[key]) || fallback || key;
  };

  document.addEventListener("DOMContentLoaded", function () {
    /* 1) data-i18n="anahtar" olan tum elemanlarin metnini doldur
          (JS ile dinamik basilan/statik fark etmez) */
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = window.i18n(key, null);
      if (val) el.textContent = val;
    });

    /* 2) Dil secici: aktif secenegin altina pill'i kaydir */
    var box = document.querySelector(".lang-switch");
    if (!box) return;
    var pill = box.querySelector(".lang-pill");
    var opts = box.querySelectorAll(".lang-opt");

    function pillKaydir(el) {
      if (!pill || !el) return;
      pill.style.width = el.offsetWidth + "px";
      pill.style.transform = "translateX(" + el.offsetLeft + "px)";
    }

    var aktif = box.querySelector(".lang-opt.active") || opts[0];
    pillKaydir(aktif);

    opts.forEach(function (el) {
      /* tiklaninca once pill akici sekilde kaysin, sonra sayfa gecsin */
      el.addEventListener("click", function (e) {
        if (el.classList.contains("active")) return;
        e.preventDefault();
        opts.forEach(function (o) { o.classList.remove("active"); });
        el.classList.add("active");
        pillKaydir(el);
        setTimeout(function () { window.location.href = el.href; }, 240);
      });
    });

    window.addEventListener("resize", function () {
      pillKaydir(box.querySelector(".lang-opt.active") || opts[0]);
    });
  });
})();
