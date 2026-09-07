document.addEventListener("DOMContentLoaded", function () {
  var mapEl = document.getElementById("toyota-map");
  if (!mapEl || typeof L === "undefined") return;

  var map = L.map("toyota-map", {
    worldCopyJump: true,
    minZoom: 2,
    maxZoom: 8,
  }).setView([20, 20], 2);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap katkıda bulunanlar",
    maxZoom: 18,
  }).addTo(map);

  var fabrikalar = [
    { lat: 35.0833, lon: 137.1561, ulke: "Japonya", sehir: "Toyota City, Aichi", urun: "Ana üretim kümesi: Honsha, Motomachi, Tsutsumi, Tahara ve daha fazlası" },
    { lat: 33.7660, lon: 130.7690, ulke: "Japonya", sehir: "Miyawaka, Fukuoka", urun: "Lexus ES / RX / NX / UX, motor" },
    { lat: 42.6337, lon: 141.6044, ulke: "Japonya", sehir: "Tomakomai, Hokkaido", urun: "Şanzıman ve aktarma organları" },
    { lat: 39.2306, lon: 141.1464, ulke: "Japonya", sehir: "Kanegasaki, Iwate", urun: "Yaris, Yaris Cross, Aqua" },
    { lat: 38.2098, lon: -84.5588, ulke: "ABD", sehir: "Georgetown, Kentucky", urun: "Camry, RAV4, motor" },
    { lat: 38.3559, lon: -87.5661, ulke: "ABD", sehir: "Princeton, Indiana", urun: "Highlander, Grand Highlander, Sienna" },
    { lat: 34.7304, lon: -86.5861, ulke: "ABD", sehir: "Huntsville, Alabama", urun: "Motor, Corolla Cross (Mazda ortak girişimi)" },
    { lat: 34.4078, lon: -88.8945, ulke: "ABD", sehir: "Blue Springs, Mississippi", urun: "Corolla" },
    { lat: 29.4241, lon: -98.4936, ulke: "ABD", sehir: "San Antonio, Teksas", urun: "Tundra, Sequoia" },
    { lat: 38.6151, lon: -81.9887, ulke: "ABD", sehir: "Buffalo, Batı Virginia", urun: "Motor, şanzıman" },
    { lat: 38.9792, lon: -90.9807, ulke: "ABD", sehir: "Troy, Missouri", urun: "Alüminyum silindir kapağı" },
    { lat: 35.8493, lon: -79.5687, ulke: "ABD", sehir: "Liberty, Kuzey Karolina", urun: "Batarya paketleri (2025)" },
    { lat: 43.36, lon: -80.31, ulke: "Kanada", sehir: "Cambridge / Woodstock, Ontario", urun: "RAV4, Lexus RX / NX" },
    { lat: 32.5149, lon: -117.0382, ulke: "Meksika", sehir: "Tijuana, Baja California", urun: "Tacoma kasası" },
    { lat: 20.5667, lon: -100.6167, ulke: "Meksika", sehir: "Apaseo el Grande, Guanajuato", urun: "Tacoma" },
    { lat: -34.0967, lon: -59.0272, ulke: "Arjantin", sehir: "Zárate, Buenos Aires", urun: "Hilux, SW4 (Fortuner), HiAce" },
    { lat: -23.5015, lon: -47.4526, ulke: "Brezilya", sehir: "Sorocaba, São Paulo", urun: "Corolla Cross, Yaris" },
    { lat: -29.9633, lon: 30.9581, ulke: "Güney Afrika", sehir: "Prospecton, Durban", urun: "Corolla, Corolla Cross, Fortuner, Hilux" },
    { lat: 40.8613, lon: -8.6291, ulke: "Portekiz", sehir: "Ovar", urun: "Dyna, Land Cruiser, Toyota Sora otobüsü" },
    { lat: 52.8408, lon: -1.6683, ulke: "Birleşik Krallık", sehir: "Burnaston, Derbyshire", urun: "Corolla hatchback / estate" },
    { lat: 53.2205, lon: -3.0505, ulke: "Birleşik Krallık", sehir: "Deeside, Galler", urun: "Motor" },
    { lat: 50.3833, lon: 3.5333, ulke: "Fransa", sehir: "Onnaing", urun: "Yaris" },
    { lat: 50.0281, lon: 15.1998, ulke: "Çekya", sehir: "Kolín", urun: "Aygo X, Yaris" },
    { lat: 50.7716, lon: 16.2845, ulke: "Polonya", sehir: "Wałbrzych", urun: "Motor" },
    { lat: 39.3434, lon: 117.3616, ulke: "Çin", sehir: "Tianjin (FAW Toyota)", urun: "bZ3, Corolla, Crown Kluger" },
    { lat: 30.5728, lon: 104.0668, ulke: "Çin", sehir: "Chengdu (FAW Toyota)", urun: "Land Cruiser Prado, Coaster" },
    { lat: 43.8171, lon: 125.3235, ulke: "Çin", sehir: "Changchun (FAW Toyota)", urun: "RAV4" },
    { lat: 23.1291, lon: 113.2644, ulke: "Çin", sehir: "Guangzhou (GAC Toyota)", urun: "Camry, Highlander, bZ4X" },
    { lat: 12.7980, lon: 77.3903, ulke: "Hindistan", sehir: "Bidadi, Karnataka", urun: "Innova, Fortuner, Camry" },
    { lat: 24.8607, lon: 67.0011, ulke: "Pakistan", sehir: "Karaçi", urun: "Corolla Altis, Fortuner" },
    { lat: 24.9670, lon: 121.2360, ulke: "Tayvan", sehir: "Zhongli, Taoyuan", urun: "Corolla Altis, Yaris Cross" },
    { lat: -6.3227, lon: 107.3376, ulke: "Endonezya", sehir: "Karawang, Batı Java", urun: "Fortuner, Innova, bZ4X" },
    { lat: 13.6904, lon: 101.0770, ulke: "Tayland", sehir: "Chachoengsao", urun: "Camry, Corolla, Yaris" },
    { lat: 21.2333, lon: 105.7333, ulke: "Vietnam", sehir: "Phúc Yên", urun: "Fortuner, Innova, Veloz" },
    { lat: 3.0738, lon: 101.5183, ulke: "Malezya", sehir: "Shah Alam / Bukit Raja, Selangor", urun: "Corolla Cross, Vios" },
    { lat: 14.3122, lon: 121.0997, ulke: "Filipinler", sehir: "Santa Rosa, Laguna", urun: "Vios, Innova, Hilux" },
  ];

  fabrikalar.forEach(function (f) {
    L.circleMarker([f.lat, f.lon], {
      radius: 6,
      color: "#ffffff",
      weight: 1.5,
      fillColor: "#c8102e",
      fillOpacity: 0.9,
    })
      .addTo(map)
      .bindPopup(
        "<strong>" + f.sehir + "</strong><br>" +
        f.ulke + "<br><span class='map-urun'>" + f.urun + "</span>"
      );
  });

  // ekran / yon degisince harita yeniden olculsun
  var yenidenOlc;
  window.addEventListener("resize", function () {
    clearTimeout(yenidenOlc);
    yenidenOlc = setTimeout(function () { map.invalidateSize(); }, 200);
  });

  L.circleMarker([40.6971, 30.3564], {
    radius: 9,
    color: "#ffffff",
    weight: 2,
    fillColor: "#c9a227",
    fillOpacity: 1,
  })
    .addTo(map)
    .bindPopup(
      "<strong>TMMT — Sakarya, Türkiye</strong><br>C-HR, Corolla Sedan" +
      "<br><a href='/tmmt'>" +
      (window.i18n ? window.i18n("map.detail", "Detaylı bilgi için tıkla →") : "Detaylı bilgi için tıkla →") +
      "</a>"
    )
    .openPopup();
});
