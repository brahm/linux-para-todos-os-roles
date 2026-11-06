// Linux para todos os rolês: o questionário de "Escolher e instalar a distro".
// Roda só no navegador; nada é enviado. Sem JavaScript, a tabela de resumo dá as mesmas respostas.
(function () {
  var form = document.getElementById("questionario");
  var saida = document.getElementById("resultado");
  var bruto = document.getElementById("distros-dados");
  if (!form || !saida || !bruto) return;
  var D = JSON.parse(bruto.textContent);

  // Cada regra devolve [principal, alternativa, por que a principal, por que a alternativa].
  function sugerir(maq, uso, exp) {
    var novato = exp === "nunca";
    if (maq === "antiga") {
      if (uso === "servidor") return ["debian", "mint-xfce", "Numa máquina antiga que vai ficar ligada servindo a casa, o Debian gasta pouco, muda pouco e é uma das bases testadas pelo bora. Sem ambiente gráfico, roda até com 1 GB de memória.", "Se você quer também usar a máquina como computador, com tela e mouse."];
      if (uso === "jogar") return ["mint-xfce", "debian", "Jogo novo não vai rodar numa máquina antiga, mas o Mint com Xfce sobra memória para jogos leves, emuladores e o navegador.", "Ainda mais leve com LXQt, para quem já se vira um pouco."];
      if (novato) return ["mint-xfce", "debian", "Leve, com tudo no lugar de sempre, e com a base do Ubuntu, que tem resposta para quase toda dúvida na internet.", "Ainda mais leve com Xfce ou LXQt, se o Mint engasgar."];
      return ["debian", "mint-xfce", "Com Xfce ou LXQt, é a melhor base para máquinas antigas: leve, estável e testada pelo bora.", "Se quiser algo que já vem mais pronto, com a cara do Windows."];
    }
    if (uso === "jogar") {
      if (exp === "bastante") return ["cachyos", "bazzite", "Arch por baixo, kernel e pacotes otimizados para desempenho e tudo dos jogos à mão. Para quem não se assusta com uma distro rolante.", "Se preferir um sistema que não se mexe e volta atrás sozinho quando uma atualização dá errado."];
      return ["bazzite", "pop", "Steam, drivers e ajustes de jogo já vêm prontos, e o sistema base não se mexe: uma atualização ruim se desfaz escolhendo a anterior no boot.", "Se quiser usar o bora já: é da família Ubuntu e tem uma imagem com o driver da NVIDIA."];
    }
    if (uso === "servidor") return ["debian", "ubuntu", "Para ficar ligado anos sem surpresa: muda pouco, gasta pouco e é uma das bases testadas pelo bora. Instale só com o servidor SSH, sem ambiente gráfico, ou com Xfce se quiser uma tela.", "Também testado pelo bora, com mais tutoriais na internet."];
    if (uso === "programar") {
      if (exp === "bastante") return ["fedora", "ubuntu", "Ferramentas novas a cada seis meses, sem perder a estabilidade, e o caminho mais curto para contêineres com Podman.", "Se quiser os rolês de programação do bora desde já."];
      return ["ubuntu", novato ? "mint" : "fedora", "Quase todo tutorial, curso e ferramenta de programação pensa no Ubuntu primeiro, e o bora tem as receitas testadas nele.", novato ? "Mesma base, com a cara do Windows." : "Programas mais novos, a cada seis meses. O bora chega nele na onda 2."];
    }
    if (exp === "bastante") return ["fedora", "debian", "Programas novos, um GNOME redondo e SELinux por padrão. Uma versão nova a cada seis meses.", "Se preferir algo que muda pouco e já é testado pelo bora."];
    if (novato) return ["mint", "zorin", "É a mais fácil para quem vem do Windows: menu no canto, barra embaixo, programas fáceis de achar. Usa a base do Ubuntu, então o bora já roda nela.", "Se quiser escolher entre a cara do Windows e a do macOS, com um visual caprichado."];
    return ["mint", "ubuntu", "Tudo no lugar, sem Snap e com a base do Ubuntu LTS, onde o bora já roda.", "A mais documentada de todas, testada pelo bora."];
  }

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  function suporte(d) {
    if (d.suporte === "testada") return "Testada com o bora.";
    if (d.suporte === "herdada") return "Usa as receitas do bora para o Ubuntu, que ainda não foram testadas nela.";
    return "O bora chega na família dela na " + d.suporte + ".";
  }

  function bloco(id, rotulo, porque, cls) {
    var d = D[id];
    var b = el("div", cls);
    b.appendChild(el("p", "rotulo-s", rotulo));
    b.appendChild(el("h3", null, d.nome));
    b.appendChild(el("p", null, porque + " <strong>" + suporte(d) + "</strong>"));
    var acoes = el("div", "acoes-s");
    var ver = el("a", "botao-mini", "Ver detalhes");
    ver.href = "#d-" + id;
    var baixar = el("a", "botao-mini", "Baixar");
    baixar.href = d.baixar;
    acoes.appendChild(ver);
    acoes.appendChild(baixar);
    b.appendChild(acoes);
    return b;
  }

  function valor(nome) {
    var m = form.querySelector('input[name="' + nome + '"]:checked');
    return m ? m.value : null;
  }

  function atualizar() {
    var maq = valor("maquina"), uso = valor("uso"), exp = valor("experiencia");
    if (!maq || !uso || !exp) return;
    var r = sugerir(maq, uso, exp);
    var s = el("div", "sugestao");
    s.appendChild(bloco(r[0], "Comece por", r[2], "principal-s"));
    s.appendChild(bloco(r[1], "Ou então", r[3], "alternativa-s"));
    if (maq === "potente" && r[0] !== "pop" && r[1] !== "pop" && uso !== "jogar")
      s.appendChild(el("p", "nota-s", "Placa NVIDIA? Instale primeiro e depois ative o driver pelo gerenciador de drivers. Se a tela ficar preta no boot do pendrive, veja as <a href=\"#armadilhas\">armadilhas comuns</a>."));
    if (D[r[0]].suporte.indexOf("onda") === 0)
      s.appendChild(el("p", "nota-s alerta", "O bora ainda não tem receitas para a família de " + D[r[0]].nome + ". Dá para instalar e usar normalmente, e o bora diag já reconhece a distro; os rolês chegam na " + D[r[0]].suporte + "."));
    saida.textContent = "";
    saida.appendChild(s);
    document.querySelectorAll(".distro.destaque").forEach(function (c) { c.classList.remove("destaque"); });
    var cartao = document.getElementById("d-" + r[0]);
    if (cartao) cartao.classList.add("destaque");
  }

  form.addEventListener("change", atualizar);
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  atualizar();
})();
