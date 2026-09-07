/* Zaman tuneli akordeonu.
   Kaynak: static/js/cevre.js, 2. bolum.

   Davranisin kendisi utils.js icindeki paylasilan `akordeon`
   yardimcisinda; adim adim (steps) bloku da ayni yardimciyi kullaniyor. */

import { akordeon } from "./utils.js";

export function init() {
  akordeon({
    buton: ".tk-timeline .tk-timeline__button",
    oge: ".tk-timeline__stop",
  });
}
