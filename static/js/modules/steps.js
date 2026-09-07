/* "Fabrikada bir aracin yolculugu" -- adim adim (stepper) bloku.

   Masaustunde adimlar tek sirada; birine tiklayinca aciklamasi sirenin
   ALTINDA tam genislikte acilir. Dar ekranda dikey akordeona doner.
   Ikisi de ayni DOM'la, yalnizca CSS ile.

   Davranis zaman tuneliyle ayni oldugu icin paylasilan `akordeon`
   yardimcisi kullaniliyor. */

import { akordeon } from "./utils.js";

export function init() {
  akordeon({
    buton: ".tk-steps .tk-steps__button",
    oge: ".tk-steps__item",
  });
}
