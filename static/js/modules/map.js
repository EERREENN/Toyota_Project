/* Leaflet haritasi.
   Kaynak: static/js/toyota-map.js

   FARK: 37 tesis noktasi artik bu dosyada SABIT DEGIL. Sunucu, blogun
   verisini <script type="application/json" id="<mapId>-data"> icine
   basiyor; burasi onu okuyup ciziyor. Boylece editor panelden koordinat
   ekleyip silebiliyor.

   Modul sayfadaki HER .tk-map__canvas icin ayri bir harita kurar:
   global sayfasindaki uretim tesisleri haritasi ile TMMT sayfasindaki
   ihracat pazarlari haritasi ayni koddan, farkli veri kumesiyle
   ciziliyor. */

import { veriOku } from "./utils.js";

/* Nokta stilleri -- gorunum bilgisi oldugu icin veride degil burada. */
const STILLER = {
  plant: {
    radius: 6,
    color: "#ffffff",
    weight: 1.5,
    fillColor: "#c8102e",
    fillOpacity: 0.9,
  },
  highlight: {
    radius: 9,
    color: "#ffffff",
    weight: 2,
    fillColor: "#c9a227",
    fillOpacity: 1,
  },
};

function popupIcerigi(nokta) {
  let html = "<strong>" + nokta.title + "</strong>";
  if (nokta.kind === "highlight") {
    if (nokta.text) html += "<br>" + nokta.text;
    if (nokta.url) {
      html += "<br><a href='" + nokta.url + "'>" +
        (nokta.linkLabel || nokta.url) + "</a>";
    }
    return html;
  }
  if (nokta.subtitle) html += "<br>" + nokta.subtitle;
  if (nokta.text) html += "<br><span class='tk-map__product'>" + nokta.text + "</span>";
  return html;
}

/* Bir harita kabini kurar. Verisi kabin id'sine bagli JSON blogundan
   gelir; bu yuzden ayni sayfada birden fazla harita olabilir ve her
   biri kendi nokta kumesiyle calisir. */
function haritaKur(kap) {
  const veri = veriOku(kap.id + "-data");
  if (!veri) return;

  const harita = L.map(kap.id, {
    worldCopyJump: veri.worldCopyJump,
    minZoom: veri.minZoom,
    maxZoom: veri.maxZoom,
  }).setView(veri.center, veri.zoom);

  L.tileLayer(veri.tile.url, {
    attribution: veri.tile.attribution,
    maxZoom: veri.tile.maxZoom,
  }).addTo(harita);

  let acilacak = null;
  (veri.markers || []).forEach(function (nokta) {
    const stil = STILLER[nokta.kind] || STILLER.plant;
    const isaret = L.circleMarker([nokta.lat, nokta.lon], stil)
      .addTo(harita)
      .bindPopup(popupIcerigi(nokta));
    if (nokta.open) acilacak = isaret;
  });
  if (acilacak) acilacak.openPopup();

  // ekran / yon degisince harita yeniden olculsun
  let yenidenOlc;
  window.addEventListener("resize", function () {
    clearTimeout(yenidenOlc);
    yenidenOlc = setTimeout(function () { harita.invalidateSize(); }, 200);
  });
}

export function init() {
  if (typeof L === "undefined") return;
  document.querySelectorAll(".tk-map__canvas").forEach(haritaKur);
}
