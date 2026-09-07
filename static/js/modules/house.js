/* TPS Evi diyagrami.

   Semanin bes parcasi (cati, iki sutun, merkez, temel) tiklanabilir;
   tiklanan parcanin aciklamasi diyagramin ALTINDA acilir.

   Iki buton kumesi var -- SVG icindekiler (genis ekran) ve akordeon
   satirlari (dar ekran) -- ama IKISI DE AYNI paneli aciyor
   (aria-controls ayni). Ayni anda yalnizca biri gorunur oldugu icin
   (CSS display:none) cakisma olmaz.

   Davranis zaman tuneli / adim adim ile ayni oldugu icin paylasilan
   `akordeon` yardimcisi kullaniliyor. */

import { akordeon } from "./utils.js";

export function init() {
  akordeon({
    buton: ".tk-house .tk-house__hit, .tk-house .tk-house__row",
    oge: ".tk-house__part",
  });
}
