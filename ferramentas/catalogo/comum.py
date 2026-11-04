# Peças comuns às páginas do catálogo: cabeçalho, rodapé, ícones e links de pedido.
from urllib.parse import quote

REPO = "https://github.com/brahm/linux-para-todos-os-roles"
SITE = "https://brahm.github.io/linux-para-todos-os-roles/"
import os as _os
RAIZ_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..")) + "/"
DOCS = RAIZ_REPO + "docs/"

# O ícone do GitHub e os símbolos vêm da página inicial, para não divergirem.
import re as _re
_inicio = open(DOCS + "index.html", encoding="utf-8").read()
GITHUB_SVG = _re.search(r'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 \.5C.*?</svg>', _inicio).group(0)
SIMBOLOS = _re.search(r'  <svg width="0" height="0".*?</svg>', _inicio, _re.S).group(0)



# Ícones de traço (viewBox 24), usados nos ladrilhos.
ICONES = {
    "atualizar": '<path d="M20 12a8 8 0 0 1-13.7 5.6"/><path d="M4 12a8 8 0 0 1 13.7-5.6"/><path d="M17.7 2.8v3.8h-3.8"/><path d="M6.3 21.2v-3.8h3.8"/>',
    "snapshot": '<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M8.5 7l1.5-3h4l1.5 3"/><circle cx="12" cy="13.5" r="3.6"/>',
    "firewall": '<path d="M12 3l7 3v5.2c0 4.4-2.9 7.9-7 9.8-4.1-1.9-7-5.4-7-9.8V6z"/><path d="M5.3 10.2h13.4M6.2 14.6h11.6M12 5.8v4.4M9 10.2v4.4M15 10.2v4.4M12 14.6v4.6"/>',
    "codecs": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M10 9.3v5.4l4.6-2.7z"/>',
    "flatpak": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
    "backup": '<path d="M3 7.5a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M12 16.5v-6M9.5 13l2.5-2.5 2.5 2.5"/>',
    "memoria": '<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 9h6v6H9zM9 2.5V5M15 2.5V5M9 19v2.5M15 19v2.5M2.5 9H5M2.5 15H5M19 9h2.5M19 15h2.5"/>',
    "janela": '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 8.5h18M6 6.3h.01M8.5 6.3h.01"/>',
    "navegador": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.6 3.6 5.4 3.6 8.5S14.5 17.9 12 20.5C9.5 17.9 8.4 15.1 8.4 12S9.5 6.1 12 3.5z"/>',
    "desligar": '<path d="M12 3.5v8"/><path d="M6.6 7a7.5 7.5 0 1 0 10.8 0"/>',
    "git": '<circle cx="6" cy="6" r="2.2"/><circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="12" r="2.2"/><path d="M6 8.2v7.6M8 7.2c4.5 1 7.6 2.2 8 3.2"/>',
    "ferramenta": '<path d="M14.5 6.5a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3z"/><path d="M14.5 6.5L17 4l3 3-2.5 2.5"/>',
    "python": '<path d="M12 3.5c-4 0-4 1.8-4 3V9h4.5v1H6.2C4.2 10 3 11.5 3 14s1.2 4 3.2 4H8v-2.5c0-1.5 1.2-2.5 2.6-2.5h3c1.4 0 2.4-1 2.4-2.4V6.5c0-1.7-1.5-3-4-3z"/><path d="M12 20.5c4 0 4-1.8 4-3V15h-4.5v-1h6.3c2 0 3.2-1.5 3.2-4s-1.2-4-3.2-4H16"/>',
    "node": '<path d="M12 3l7.8 4.5v9L12 21l-7.8-4.5v-9z"/><path d="M12 8v8M9 10.5l3-2.5 3 2.5"/>',
    "conteiner": '<rect x="3" y="8" width="18" height="11" rx="1.5"/><path d="M7 8v11M11 8v11M15 8v11M3 5h18"/>',
    "robo": '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 4v4M9.5 13h.01M14.5 13h.01M9.5 16.2h5"/><circle cx="12" cy="3.5" r="1"/>',
    "chave": '<circle cx="8" cy="15" r="4"/><path d="M11 12l8.5-8.5M16.5 6.5l2.5 2.5M14 9l2 2"/>',
    "lupa": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5M8 10.5l2 2 3.5-3.5"/>',
    "caixa": '<path d="M3.5 8.5L12 4l8.5 4.5v7L12 20l-8.5-4.5z"/><path d="M8 6.3l8.5 4.5"/>',
    "pasta": '<path d="M3 7.5a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 16.5v-3l3-2.5 3 2.5v3z"/>',
    "filme": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M10 9.3v5.4l4.6-2.7z"/><path d="M3 9h2M3 15h2M19 9h2M19 15h2"/>',
    "vpn": '<path d="M12 3l7 3v5.2c0 4.4-2.9 7.9-7 9.8-4.1-1.9-7-5.4-7-9.8V6z"/><circle cx="12" cy="10.5" r="1.8"/><path d="M12 12.3v3.2"/>',
    "rede": '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="M12 7v4M12 11l-6 5.3M12 11l6 5.3"/>',
    # Rolês, os mesmos da página inicial
    "livro": '<path d="M3.5 5.5c2.6-.9 5.4-.6 8.5 1.2v12.6c-3.1-1.8-5.9-2.1-8.5-1.2z"/><path d="M20.5 5.5c-2.6-.9-5.4-.6-8.5 1.2v12.6c3.1-1.8 5.9-2.1 8.5-1.2z"/>',
    "broto": '<rect x="3" y="4" width="18" height="12.5" rx="2"/><path d="M8.5 20.5h7M12 16.5v4"/><path d="M12 14v-3.2"/><path d="M12 10.8c0-2.2 1.4-3.4 3.6-3.4 0 2.2-1.4 3.4-3.6 3.4z"/><path d="M12 11.6c0-1.7-1.1-2.7-2.9-2.7 0 1.7 1.1 2.7 2.9 2.7z"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7.5 9.5l3 2.5-3 2.5M12.5 15h4"/>',
    "brilho": '<path d="M11 3.5l1.6 4.4 4.4 1.6-4.4 1.6L11 15.5l-1.6-4.4L5 9.5l4.4-1.6z"/><path d="M18 14.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/><path d="M6.5 16.5L4 19l2.5 2.5"/>',
    "escudo-chave": '<path d="M12 3l7 3v5.2c0 4.4-2.9 7.9-7 9.8-4.1-1.9-7-5.4-7-9.8V6z"/><circle cx="12" cy="10.5" r="1.8"/><path d="M12 12.3v3.2"/>',
}


def ladrilho(icone, cor, extra=""):
    return f'<span class="ladrilho {cor}"{extra} aria-hidden="true"><svg viewBox="0 0 24 24">{ICONES[icone]}</svg></span>'


def pedido(template, titulo, **campos):
    q = f"template={template}&title={quote(titulo)}"
    for k, v in campos.items():
        q += f"&{k}={quote(v)}"
    return f"{REPO}/issues/new?{q}".replace("&", "&amp;")


def bloco_pedidos(onde, nome, extra_titulo, outra_distro=True, editar=None):
    """Cartões no fim de cada página: pedir recurso, outra distro, receita nova, problema."""
    cartoes = [
        (pedido("1-pedido-de-recurso.yml", f"[{onde}] ", onde=onde),
         '<path d="M12 5v14M5 12h14"/>',
         f"Pedir um recurso {extra_titulo}",
         f"Uma opção nova, um comportamento diferente ou algo que {nome} ainda não faz.",
         "Fazer um pedido"),
    ]
    if outra_distro:
        cartoes.append((pedido("1-pedido-de-recurso.yml", f"[{onde}] Funcionar em ", onde=onde),
                        '<rect x="3" y="4" width="18" height="12.5" rx="2"/><path d="M8.5 20.5h7M12 16.5v4"/><path d="M9.5 10.3h5M12 7.8v5"/>',
                        "Pedir em outra distro",
                        "Usa Fedora, Arch ou outra família? Diga qual, e conte se puder testar.",
                        "Pedir outra distro"))
    cartoes.append((pedido("2-nova-receita.yml", "Receita: "),
                    '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13 7l4 4"/>',
                    "Pedir uma receita nova",
                    "Uma mudança que o bora ainda não sabe fazer, dentro deste rolê ou fora dele.",
                    "Pedir uma receita"))
    cartoes.append((pedido("4-problema.yml", f"Problema: {onde}", onde=onde),
                    '<path d="M12 4l9 16H3z"/><path d="M12 10v4.5M12 17.3h.01"/>',
                    "Relatar um problema",
                    "Algo não funcionou como esta página diz? O formulário já vem com o roteiro.",
                    "Relatar"))
    if editar:
        cartoes.append((editar,
                        '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/>',
                        "Melhorar esta explicação",
                        "Ficou confuso? Sugira um jeito melhor de dizer, direto no arquivo.",
                        "Ver no GitHub"))
    itens = "\n".join(
        f'''        <a class="cartao convite" href="{href}">
          <span class="bolha" aria-hidden="true"><svg viewBox="0 0 24 24">{ic}</svg></span>
          <h3>{t}</h3>
          <p>{d}</p>
          <span class="seta">{s}</span>
        </a>''' for href, ic, t, d, s in cartoes)
    return f'''    <section id="pedidos" class="largura pedidos">
      <div class="cabeca">
        <p class="sobretitulo"><svg aria-hidden="true"><use href="#pegada"/></svg>Bora melhorar</p>
        <h2>Falta alguma coisa?</h2>
        <p>Os pedidos viram issues no GitHub, onde qualquer pessoa pode comentar, votar com um 👍 ou se oferecer para fazer.</p>
      </div>
      <div class="convites">
{itens}
      </div>
    </section>'''


def pagina(*, raiz, caminho, titulo, descricao, corpo, ativo="catalogo"):
    """raiz: prefixo relativo até docs/ (por exemplo, "../../")."""
    url = SITE + caminho
    cat = f"{raiz}catalogo/"
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titulo} · Linux para todos os rolês</title>
  <meta name="description" content="{descricao}">
  <meta name="theme-color" content="#fff6ec" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#241f31" media="(prefers-color-scheme: dark)">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="{raiz}imagens/icone.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{raiz}imagens/icone-256.png">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="Linux para todos os rolês">
  <meta property="og:title" content="{titulo}">
  <meta property="og:description" content="{descricao}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}imagens/imagem-social.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preload" href="{raiz}fontes/InterDisplay-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{raiz}fontes/Inter-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{raiz}estilo.css">
  <link rel="stylesheet" href="{cat}catalogo.css">
  <script>document.documentElement.classList.add("js")</script>
  <script src="{cat}catalogo.js" defer></script>
</head>
<body>
{SIMBOLOS}

  <a class="pular" href="#conteudo">Pular para o conteúdo</a>

  <header class="topo">
    <div class="largura">
      <a class="marca-mini" href="{raiz}" aria-label="Linux para todos os rolês, início">
        <svg aria-hidden="true"><use href="#pegada"/></svg>
        <span>Linux para todos os <em>rolês</em></span>
      </a>
      <nav aria-label="Seções">
        <a href="{raiz}#o-que-e">O que é</a>
        <a href="{cat}"{' aria-current="page"' if ativo == "inicio" else ""}>Rolês e receitas</a>
        <a href="{raiz}#como-funciona">Como funciona</a>
        <a href="{raiz}#status">Status</a>
        <a href="{raiz}#bora-junto">Bora junto</a>
        <a class="github" href="{REPO}">
          {GITHUB_SVG}GitHub
        </a>
      </nav>
    </div>
  </header>

  <main id="conteudo">
{corpo}
  </main>

  <footer class="rodape-site">
    <div class="largura">
      <div>
        <a class="marca-mini" href="{raiz}"><svg aria-hidden="true"><use href="#pegada"/></svg><span>Linux para todos os <em>rolês</em></span></a>
        <p>Feito no Brasil, em português, sob a licença <a href="{REPO}/blob/main/LICENSE">0BSD</a>. A fonte é a Inter, sob a <a href="{raiz}fontes/OFL.txt">SIL Open Font License</a>.</p>
        <p class="grub">Nenhum demônio foi invocado no GRUB para fazer este site.</p>
      </div>
      <nav aria-label="Rodapé">
        <a href="{cat}">Rolês e receitas</a>
        <a href="{REPO}">Repositório</a>
        <a href="{REPO}/blob/main/CONTRIBUTING.md">Como contribuir</a>
        <a href="{REPO}/blob/main/docs/decisoes.md">Decisões</a>
      </nav>
    </div>
  </footer>
</body>
</html>
'''


def cabeca(sobre, titulo, texto=""):
    p = f"\n        <p>{texto}</p>" if texto else ""
    return f'''      <div class="cabeca">
        <p class="sobretitulo"><svg aria-hidden="true"><use href="#pegada"/></svg>{sobre}</p>
        <h2>{titulo}</h2>{p}
      </div>'''


def janela(titulo, linhas, rotulo, replay=True):
    """linhas: lista de (classe, html). A classe "cmd" marca um comando digitado."""
    corpo = "".join(f'<span class="l {c}">{h if h else "&nbsp;"}</span>' for c, h in linhas)
    cls = "janela replay" if replay else "janela"
    botao = ('\n        <div class="replay-controles"><button class="botao-mini" type="button" data-rever>'
             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 12a8 8 0 1 0 2.4-5.7"/><path d="M4 4v4h4"/></svg>Rever</button></div>') if replay else ""
    return f'''        <div class="{cls}" role="img" aria-label="{rotulo}">
          <div class="barra" aria-hidden="true">{titulo}<span class="fechar"><svg viewBox="0 0 10 10"><path d="M2 2l6 6M8 2L2 8" stroke="#deddda" stroke-width="1.6" stroke-linecap="round"/></svg></span></div>
<pre aria-hidden="true">{corpo}</pre>
        </div>{botao}'''


P = '<span class="p">você@computador:~$</span> '
