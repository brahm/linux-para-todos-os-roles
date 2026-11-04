// Linux para todos os rolês: "Últimas mudanças" lidas da API pública do GitHub.
// A página funciona sem isto; se a API falhar, fica o link para o histórico.
(function () {
  var lista = document.getElementById("commits");
  var vazio = document.getElementById("commits-vazio");
  if (!lista || !window.fetch) return;
  var URL = "https://api.github.com/repos/brahm/linux-para-todos-os-roles/commits?sha=main&per_page=5";
  var CHAVE = "lptr-commits";

  function quando(iso) {
    var seg = (new Date(iso).getTime() - Date.now()) / 1000;
    var rtf = new Intl.RelativeTimeFormat("pt-BR", { numeric: "auto" });
    var passos = [["year", 31536000], ["month", 2592000], ["week", 604800], ["day", 86400], ["hour", 3600], ["minute", 60]];
    for (var i = 0; i < passos.length; i++) {
      if (Math.abs(seg) >= passos[i][1]) return rtf.format(Math.round(seg / passos[i][1]), passos[i][0]);
    }
    return "agora há pouco";
  }

  function mostrar(itens) {
    lista.textContent = "";
    itens.forEach(function (c) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = c.url;
      a.textContent = c.msg;
      var t = document.createElement("time");
      t.dateTime = c.data;
      t.textContent = quando(c.data);
      t.title = new Date(c.data).toLocaleString("pt-BR");
      li.appendChild(a);
      li.appendChild(t);
      lista.appendChild(li);
    });
    lista.hidden = false;
    vazio.hidden = true;
  }

  try {
    var salvo = JSON.parse(sessionStorage.getItem(CHAVE) || "null");
    if (salvo && Date.now() - salvo.em < 10 * 60 * 1000) { mostrar(salvo.itens); return; }
  } catch (e) {}

  fetch(URL, { headers: { Accept: "application/vnd.github+json" } })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (dados) {
      var itens = dados
        .filter(function (c) { return !/^Merge /.test(c.commit.message); })
        .slice(0, 5)
        .map(function (c) {
          return { msg: c.commit.message.split("\n")[0], data: c.commit.author.date, url: c.html_url };
        });
      if (!itens.length) return;
      mostrar(itens);
      try { sessionStorage.setItem(CHAVE, JSON.stringify({ em: Date.now(), itens: itens })); } catch (e) {}
    })
    .catch(function () {});
})();
