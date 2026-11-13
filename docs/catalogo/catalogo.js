// Linux para todos os rolês: animações e alternâncias das páginas do catálogo.
// Tudo funciona sem isto: sem JavaScript, as ilustrações aparecem paradas e completas.
(function () {
  // Quem pediu menos movimento no sistema vê tudo pronto, sem animação.
  var parado = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Terminal que se escreve sozinho, linha por linha.
  function tocar(janela) {
    var linhas = janela.querySelectorAll("pre .l");
    var timers = janela._timers || [];
    timers.forEach(clearTimeout);
    janela._timers = [];
    linhas.forEach(function (l) { l.classList.remove("ok"); });
    if (parado) { linhas.forEach(function (l) { l.classList.add("ok"); }); return; }
    var t = 250;
    linhas.forEach(function (l) {
      t += Number(l.getAttribute("data-pausa") || (l.classList.contains("cmd") ? 700 : 110));
      janela._timers.push(setTimeout(function () { l.classList.add("ok"); }, t));
    });
  }

  // O botão "rever" ao lado de cada terminal toca a animação de novo.
  document.querySelectorAll(".janela.replay").forEach(function (janela) {
    var botao = janela.parentNode.querySelector("[data-rever]");
    if (botao) botao.addEventListener("click", function () { tocar(janela); });
  });

  // Mostra e anima o que entra na tela.
  function ver(el) {
    if (el.classList.contains("revelar")) el.classList.add("visivel");
    if (el.hasAttribute("data-anima")) el.classList.add("anima");
    if (el.classList.contains("replay") && !el._tocou) { el._tocou = true; tocar(el); }
  }
  // Anima cada elemento quando um quarto dele aparece na tela, uma vez só.
  // Navegador sem IntersectionObserver (ou com movimento reduzido) mostra tudo de cara.
  var alvos = document.querySelectorAll(".revelar, [data-anima], .janela.replay");
  if (!("IntersectionObserver" in window) || parado) {
    alvos.forEach(ver);
  } else {
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting) { ver(e.target); obs.unobserve(e.target); }
      });
    }, { threshold: 0.25 });
    alvos.forEach(function (el) { obs.observe(el); });
  }

  // Alternância de perfis e cenários: botões com data-mostrar e elementos com data-quando.
  document.querySelectorAll("[data-alternar]").forEach(function (grupo) {
    var alvo = document.getElementById(grupo.getAttribute("data-alternar"));
    if (!alvo) return;
    var botoes = grupo.querySelectorAll("button[data-mostrar]");
    // Marca o botão escolhido e esconde o que não vale para esse valor.
    // data-quando pode ter vários valores, separados por espaço.
    function escolher(valor) {
      botoes.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-mostrar") === valor)); });
      alvo.querySelectorAll("[data-quando]").forEach(function (el) {
        var lista = el.getAttribute("data-quando").split(" ");
        el.classList.toggle("perfil-oculto", lista.indexOf(valor) < 0);
      });
    }
    botoes.forEach(function (b) {
      b.addEventListener("click", function () { escolher(b.getAttribute("data-mostrar")); });
    });
    escolher(botoes[0].getAttribute("data-mostrar"));
  });
})();
