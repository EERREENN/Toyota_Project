/* Panel etkilesimleri: tekrarlayan satirlar ve suruk-birak siralama.
   Klasik script (modul degil): panelin baska bagimliligi yok. */
(function () {
  "use strict";

  var sayac = 0;

  /* ---------------------------------------------------------
     Ortak: bir grubun gizli "sira" alanini DOM'a gore tazele.
     Bu alan HEM SIRAYI HEM VARLIGI belirler; listede olmayan
     oge sunucuda silinir.
     --------------------------------------------------------- */
  function siralamayiYaz(grup) {
    var alan = grup.querySelector(':scope > input[type="hidden"]');
    var liste = grup.querySelector(":scope > .yn-tekrar__liste");
    if (!alan || !liste) return;
    var anahtarlar = [];
    liste.querySelectorAll(":scope > .yn-satir").forEach(function (satir) {
      anahtarlar.push(satir.getAttribute("data-anahtar"));
    });
    alan.value = anahtarlar.join(",");
  }

  function tumSiralamalariYaz() {
    document.querySelectorAll(".yn-tekrar").forEach(siralamayiYaz);
  }

  /* ---------------------------------------------------------
     Satir ekleme: <template> kalibini kopyala, %K% yerine
     benzersiz bir anahtar yaz.
     --------------------------------------------------------- */
  function satirEkle(grup) {
    var kalip = grup.querySelector(":scope > .yn-tekrar__sablon");
    if (!kalip) return;
    sayac += 1;
    var anahtar = "yeni-" + sayac + "-" + Date.now().toString(36).slice(-4);

    var html = kalip.innerHTML.split("%K%").join(anahtar);
    var kap = document.createElement("div");
    kap.innerHTML = html;

    var liste = grup.querySelector(":scope > .yn-tekrar__liste");
    var yeni = kap.querySelector(".yn-satir");
    if (!yeni || !liste) return;
    liste.appendChild(yeni);
    siralamayiYaz(grup);

    var ilkAlan = yeni.querySelector("input, textarea, select");
    if (ilkAlan) ilkAlan.focus();
  }

  document.addEventListener("click", function (olay) {
    /* --- ekle --- */
    var ekle = olay.target.closest(".yn-tekrar__ekle");
    if (ekle) {
      olay.preventDefault();
      satirEkle(ekle.closest(".yn-tekrar"));
      return;
    }

    /* --- sil --- */
    var sil = olay.target.closest(".yn-satir__sil");
    if (sil) {
      olay.preventDefault();
      var satir = sil.closest(".yn-satir");
      var grup = satir.closest(".yn-tekrar");
      if (!confirm("Bu satır silinecek. Emin misin?")) return;
      satir.remove();
      /* Ic ice gruplarda silinen satirin ICINDEKI gruplar da gitti;
         hepsini yeniden yaz. */
      tumSiralamalariYaz();
      if (grup) siralamayiYaz(grup);
    }
  });

  /* ---------------------------------------------------------
     Suruk-birak siralama.
     Tekrarlayan satirlar icin ve sayfa blok listesi icin ayni kod.
     --------------------------------------------------------- */
  var suruklenen = null;

  function surukleKur(kap, satirSecici, bitince) {
    kap.addEventListener("dragstart", function (olay) {
      var tut = olay.target.closest("[draggable='true']");
      if (!tut) return;
      suruklenen = tut.closest(satirSecici);
      if (!suruklenen) return;
      suruklenen.classList.add("suruklenirken");
      olay.dataTransfer.effectAllowed = "move";
      /* Firefox surukleme baslamasi icin veri ister */
      olay.dataTransfer.setData("text/plain", "");
    });

    kap.addEventListener("dragover", function (olay) {
      if (!suruklenen) return;
      olay.preventDefault();
      var uzerinde = olay.target.closest(satirSecici);
      if (!uzerinde || uzerinde === suruklenen) return;
      if (uzerinde.parentNode !== suruklenen.parentNode) return;

      var kutu = uzerinde.getBoundingClientRect();
      var ustYari = olay.clientY < kutu.top + kutu.height / 2;
      uzerinde.parentNode.insertBefore(
        suruklenen,
        ustYari ? uzerinde : uzerinde.nextSibling
      );
    });

    kap.addEventListener("drop", function (olay) { olay.preventDefault(); });

    kap.addEventListener("dragend", function () {
      if (!suruklenen) return;
      suruklenen.classList.remove("suruklenirken");
      suruklenen = null;
      bitince();
    });
  }

  /* tekrarlayan satirlar */
  var form = document.getElementById("blok-form");
  if (form) {
    surukleKur(form, ".yn-satir", tumSiralamalariYaz);
    tumSiralamalariYaz();
  }

  /* sayfadaki blok listesi */
  var blokListe = document.getElementById("blok-liste");
  if (blokListe) {
    var siraAlani = document.getElementById("blok-sira");
    function bloklariYaz() {
      var idler = [];
      blokListe.querySelectorAll(".yn-blok").forEach(function (b, i) {
        idler.push(b.getAttribute("data-id"));
        var no = b.querySelector(".yn-blok__no");
        if (no) no.textContent = i + 1;
      });
      if (siraAlani) siraAlani.value = idler.join(",");
    }
    surukleKur(blokListe, ".yn-blok", bloklariYaz);
  }
})();
