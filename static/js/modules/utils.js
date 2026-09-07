/* Modullerin paylastigi kucuk yardimcilar. */

/** Kullanici "hareketi azalt" dediyse animasyonlari atla. */
export function azHareket() {
  return !!(window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches);
}

/** Sayfadaki <script type="application/json"> blogunu oku. */
export function veriOku(kimlik) {
  const el = document.getElementById(kimlik);
  if (!el) return null;
  try {
    return JSON.parse(el.textContent);
  } catch (e) {
    console.error("veri okunamadi:", kimlik, e);
    return null;
  }
}

/** Intl.NumberFormat, desteklenmezse ham sayi. */
export function bicimlendirici(dil) {
  try {
    return new Intl.NumberFormat(dil || "tr-TR");
  } catch (e) {
    return null;
  }
}

/** easeOutCubic ile 0'dan hedefe sayan animasyon. */
export function say(sure, hedefeUlas) {
  let t0 = null;
  function adim(t) {
    if (t0 === null) t0 = t;
    const p = Math.min((t - t0) / sure, 1);
    hedefeUlas(1 - Math.pow(1 - p, 3));
    if (p < 1) requestAnimationFrame(adim);
  }
  requestAnimationFrame(adim);
}

/**
 * Akordeon: bir gruptaki butonlardan birine tiklayinca kendi detayini
 * acar, digerlerini kapatir.
 *
 * Zaman tuneli ve adim adim (stepper) bloklarinin ortak davranisi.
 * Buton `aria-controls` ile detayina baglidir; acik oge `is-open`
 * sinifini alir.
 *
 *   akordeon({ buton: ".tk-timeline__button", oge: ".tk-timeline__stop" })
 */
export function akordeon(ayar) {
  const butonlar = document.querySelectorAll(ayar.buton);
  if (!butonlar.length) return;

  function kapat(btn) {
    btn.setAttribute("aria-expanded", "false");
    const detay = document.getElementById(btn.getAttribute("aria-controls"));
    if (detay) detay.hidden = true;
    const oge = btn.closest(ayar.oge);
    if (oge) oge.classList.remove("is-open");
  }

  butonlar.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const detay = document.getElementById(btn.getAttribute("aria-controls"));
      const acik = btn.getAttribute("aria-expanded") === "true";

      butonlar.forEach(function (b) {
        if (b !== btn) kapat(b);
      });

      btn.setAttribute("aria-expanded", acik ? "false" : "true");
      if (detay) detay.hidden = acik;
      const oge = btn.closest(ayar.oge);
      if (oge) oge.classList.toggle("is-open", !acik);
    });
  });
}
