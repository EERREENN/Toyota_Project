/* CO2 / yakit tasarrufu hesaplayicisi.
   Kaynak: static/js/cevre.js, 3. bolum.

   FARK: katsayilar (tuketim, emisyon, fiyat) artik bu dosyada SABIT
   DEGIL; sunucu <script type="application/json" id="hesap-veri">
   icine basiyor, buradan okunuyor. Formul birebir ayni. */

import { veriOku, bicimlendirici } from "./utils.js";

export function init() {
  const form = document.getElementById("hesap-form");
  if (!form) return;

  const veri = veriOku("hesap-veri");
  if (!veri) return;

  const TUKETIM = veri.fuelPer100km || {};   // L/100 km
  const ELEKTRIK = veri.kwhPer100km || {};   // kWh/100 km
  const CO2 = veri.co2PerUnit || {};         // benzin/dizel kg/L, elektrik kg/kWh
  const FIYAT = veri.pricePerUnit || {};     // TL/L ve TL/kWh
  const fmt = bicimlendirici(veri.numberLocale);

  const elKm = document.getElementById("h-km");
  const elArac = document.getElementById("h-arac");
  const elToyota = document.getElementById("h-toyota");

  const sCo2 = document.getElementById("s-co2");
  const sPara = document.getElementById("s-para");
  const bMevcut = document.getElementById("b-mevcut");
  const bToyota = document.getElementById("b-toyota");
  const barMevcut = document.getElementById("bar-mevcut");
  const barToyota = document.getElementById("bar-toyota");

  if (!elKm || !elArac || !elToyota) return;

  function yaz(n) {
    const t = Math.round(n);
    return fmt ? fmt.format(t) : String(t);
  }

  function hesapla() {
    const km = Math.max(0, parseFloat(elKm.value) || 0);
    const arac = elArac.value;      // benzin | dizel
    const tek = elToyota.value;     // hev | phev | bev
    const yuzKm = km / 100;

    const mevcutCo2 = yuzKm * (TUKETIM[arac] || 0) * (CO2[arac] || 0);
    const mevcutTl = yuzKm * (TUKETIM[arac] || 0) * (FIYAT[arac] || 0);

    // Hibritler benzin yakar: Toyota tarafinda benzin katsayisi kullanilir.
    const toyotaCo2 = yuzKm * (TUKETIM[tek] || 0) * (CO2.benzin || 0) +
                      yuzKm * (ELEKTRIK[tek] || 0) * (CO2.elektrik || 0);
    const toyotaTl = yuzKm * (TUKETIM[tek] || 0) * (FIYAT.benzin || 0) +
                     yuzKm * (ELEKTRIK[tek] || 0) * (FIYAT.elektrik || 0);

    sCo2.textContent = yaz(Math.max(0, mevcutCo2 - toyotaCo2));
    sPara.textContent = yaz(Math.max(0, mevcutTl - toyotaTl));
    bMevcut.textContent = yaz(mevcutCo2);
    bToyota.textContent = yaz(toyotaCo2);

    const enBuyuk = Math.max(mevcutCo2, toyotaCo2, 1);
    barMevcut.style.width = (mevcutCo2 / enBuyuk * 100) + "%";
    barToyota.style.width = (toyotaCo2 / enBuyuk * 100) + "%";
  }

  form.addEventListener("input", hesapla);
  form.addEventListener("change", hesapla);
  hesapla();
}
