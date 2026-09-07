/* Toyota ve Cevre sayfasi:
   1) Ilerleme kartlari - ekrana girince 0'dan hedefe sayan animasyon
   2) Zaman tuneli - duraga tiklayinca aciklama ac/kapa
   3) CO2 / yakit tasarrufu hesaplayicisi
*/
(function () {
  "use strict";

  var azHareket = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var trFmt = new Intl.NumberFormat("tr-TR");

  /* ---------------------------------------------------------
     1) Ilerleme kartlari
     --------------------------------------------------------- */
  function sayacBaslat(kart) {
    var el = kart.querySelector(".sayac");
    if (!el) return;

    var hedef = parseFloat(kart.getAttribute("data-hedef"));
    var baslangic = parseFloat(kart.getAttribute("data-baslangic") || "0");
    var duz = kart.getAttribute("data-format") === "plain";

    function yaz(v) {
      var n = Math.round(v);
      el.textContent = duz ? String(n) : trFmt.format(n);
    }

    if (azHareket || !window.requestAnimationFrame) {
      yaz(hedef);
      return;
    }

    var sure = 1100;
    var t0 = null;

    function adim(t) {
      if (t0 === null) t0 = t;
      var p = Math.min((t - t0) / sure, 1);
      // easeOutCubic
      var e = 1 - Math.pow(1 - p, 3);
      yaz(baslangic + (hedef - baslangic) * e);
      if (p < 1) requestAnimationFrame(adim);
    }
    requestAnimationFrame(adim);
  }

  var kartlar = document.querySelectorAll(".ilerleme-kart[data-sayac]");
  if (kartlar.length) {
    if (!("IntersectionObserver" in window)) {
      kartlar.forEach(sayacBaslat);
    } else {
      var gozlemci = new IntersectionObserver(function (girisler) {
        girisler.forEach(function (giris) {
          if (giris.isIntersecting) {
            sayacBaslat(giris.target);
            gozlemci.unobserve(giris.target);
          }
        });
      }, { threshold: 0.35 });
      kartlar.forEach(function (k) {
        var el = k.querySelector(".sayac");
        if (el) el.textContent = k.getAttribute("data-format") === "plain"
          ? (k.getAttribute("data-baslangic") || "0")
          : trFmt.format(parseFloat(k.getAttribute("data-baslangic") || "0"));
        gozlemci.observe(k);
      });
    }
  }

  /* ---------------------------------------------------------
     2) Zaman tuneli
     --------------------------------------------------------- */
  var duraklar = document.querySelectorAll(".zaman-tuneli .zt-nokta");
  duraklar.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var detay = document.getElementById(btn.getAttribute("aria-controls"));
      var acik = btn.getAttribute("aria-expanded") === "true";

      // digerlerini kapat (akordeon)
      duraklar.forEach(function (b) {
        if (b === btn) return;
        b.setAttribute("aria-expanded", "false");
        var d = document.getElementById(b.getAttribute("aria-controls"));
        if (d) d.hidden = true;
        b.closest(".zt-durak").classList.remove("acik");
      });

      btn.setAttribute("aria-expanded", acik ? "false" : "true");
      if (detay) detay.hidden = acik;
      btn.closest(".zt-durak").classList.toggle("acik", !acik);
    });
  });

  /* ---------------------------------------------------------
     3) Hesaplayici
     --------------------------------------------------------- */
  var form = document.getElementById("hesap-form");
  if (form) {
    // --- Sabitler (guncellenebilir) ---
    // Yakit tuketimi: L/100 km (benzin/dizel piyasa ortalamasi; Toyota WLTP yaklasik)
    var TUKETIM = { benzin: 7.4, dizel: 6.0, hev: 4.3, phev: 1.6, bev: 0 };
    // Elektrik tuketimi: kWh/100 km
    var ELEKTRIK = { benzin: 0, dizel: 0, hev: 0, phev: 8.5, bev: 14.5 };
    // CO2 katsayilari: benzin/dizel kg/L, elektrik kg/kWh (TR sebeke ort.)
    var CO2 = { benzin: 2.31, dizel: 2.65, elektrik: 0.42 };
    // Fiyatlar (yaklasik, Eylul 2026): benzin/dizel TL/L, elektrik TL/kWh
    var FIYAT = { benzin: 44.0, dizel: 45.0, elektrik: 2.6 };

    var elKm = document.getElementById("h-km");
    var elArac = document.getElementById("h-arac");
    var elToyota = document.getElementById("h-toyota");

    var sCo2 = document.getElementById("s-co2");
    var sPara = document.getElementById("s-para");
    var bMevcut = document.getElementById("b-mevcut");
    var bToyota = document.getElementById("b-toyota");
    var barMevcut = document.getElementById("bar-mevcut");
    var barToyota = document.getElementById("bar-toyota");

    function hesapla() {
      var km = Math.max(0, parseFloat(elKm.value) || 0);
      var arac = elArac.value;      // benzin | dizel
      var tek = elToyota.value;     // hev | phev | bev
      var yuzKm = km / 100;

      var mevcutCo2 = yuzKm * TUKETIM[arac] * CO2[arac];
      var mevcutTl = yuzKm * TUKETIM[arac] * FIYAT[arac];

      var toyotaCo2 = yuzKm * TUKETIM[tek] * CO2.benzin +
                      yuzKm * ELEKTRIK[tek] * CO2.elektrik;
      var toyotaTl = yuzKm * TUKETIM[tek] * FIYAT.benzin +
                     yuzKm * ELEKTRIK[tek] * FIYAT.elektrik;

      var co2Tasarruf = Math.max(0, mevcutCo2 - toyotaCo2);
      var tlTasarruf = Math.max(0, mevcutTl - toyotaTl);

      sCo2.textContent = trFmt.format(Math.round(co2Tasarruf));
      sPara.textContent = trFmt.format(Math.round(tlTasarruf));
      bMevcut.textContent = trFmt.format(Math.round(mevcutCo2));
      bToyota.textContent = trFmt.format(Math.round(toyotaCo2));

      var enBuyuk = Math.max(mevcutCo2, toyotaCo2, 1);
      barMevcut.style.width = (mevcutCo2 / enBuyuk * 100) + "%";
      barToyota.style.width = (toyotaCo2 / enBuyuk * 100) + "%";
    }

    form.addEventListener("input", hesapla);
    form.addEventListener("change", hesapla);
    hesapla();
  }
})();
