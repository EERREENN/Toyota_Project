/* Mobil menu ac/kapa.
   Kaynak: templates/base.html icindeki satir ici <script>. */

export function init() {
  const btn = document.querySelector(".nav-toggle");
  const menu = document.getElementById("nav-menu");
  if (!btn || !menu) return;

  function setOpen(open) {
    menu.classList.toggle("is-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("nav-open", open);
    if (open) {
      // dil secici pill'i acilinca yeniden olcsun
      window.dispatchEvent(new Event("resize"));
    }
  }

  btn.addEventListener("click", function () {
    setOpen(!menu.classList.contains("is-open"));
  });

  // link'e tiklayinca menuyu kapat
  menu.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", function () { setOpen(false); });
  });

  // genis ekrana gecince acik kalmasin
  const mq = window.matchMedia("(min-width: 861px)");
  const dinle = mq.addEventListener
    ? mq.addEventListener.bind(mq, "change")
    : mq.addListener.bind(mq);
  dinle(function () { if (mq.matches) setOpen(false); });
}
