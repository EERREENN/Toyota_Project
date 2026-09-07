/* Sitenin tek JS giris noktasi.

   Her modul kendi DOM'unu bulamazsa sessizce cekilir; bu yuzden butun
   sayfalarda ayni dosya yuklenebiliyor. Bir modulun hatasi digerlerini
   durdurmasin diye her biri ayri try/catch icinde.

   <script type="module"> ertelenir: DOM hazir oldugunda calisir,
   ayrica Leaflet gibi klasik script'ler bundan once yuklenmis olur. */

import { init as nav } from "./modules/nav.js";
import { init as langSwitch } from "./modules/lang-switch.js";
import { init as reveal } from "./modules/reveal.js";
import { init as counters } from "./modules/counters.js";
import { init as progressCounters } from "./modules/progress-counters.js";
import { init as timeline } from "./modules/timeline.js";
import { init as steps } from "./modules/steps.js";
import { init as ev } from "./modules/house.js";
import { init as hibrit } from "./modules/hybrid.js";
import { init as sozluk } from "./modules/glossary.js";
import { init as harita } from "./modules/map.js";
import { init as hesaplayici } from "./modules/co2-calculator.js";

const MODULLER = [
  ["nav", nav],
  ["lang-switch", langSwitch],
  ["reveal", reveal],
  ["counters", counters],
  ["progress-counters", progressCounters],
  ["timeline", timeline],
  ["steps", steps],
  ["house", ev],
  ["hybrid", hibrit],
  ["glossary", sozluk],
  ["map", harita],
  ["co2-calculator", hesaplayici],
];

for (const [ad, baslat] of MODULLER) {
  try {
    baslat();
  } catch (hata) {
    console.error("[" + ad + "] modulu baslatilamadi:", hata);
  }
}
