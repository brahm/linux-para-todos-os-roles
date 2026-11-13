# Página "Escolher e instalar a distro" (docs/distro/index.html).
# As distros ficam numa lista só: dela saem os cartões, a tabela e os dados que o questionário usa.
import json
from comum import REPO, cabeca, janela, bloco_pedidos

# suporte: "testada" (o bora tem receitas testadas nela, em contêiner e em máquina virtual), "herdada" (usa as receitas da base)
# ou "onda N" (o bora ainda não chegou à família).
DISTROS = [
    {
        "id": "mint", "nome": "Linux Mint", "edicao": "edição Cinnamon", "familia": "ubuntu", "suporte": "herdada",
        "cor": ("#8ff0a4", "#26a269"), "letra": "M",
        "para": "Quem vem do Windows e quer tudo no lugar de sempre: menu no canto, barra embaixo, programas fáceis de achar.",
        "conforto": "4 GB de memória e 30 GB de disco",
        "saber": "Usa a base do Ubuntu LTS, mas sem Snap: os programas vêm do repositório e do Flatpak. No boot do pendrive há um “modo de compatibilidade” para placas de vídeo teimosas.",
        "baixar": "https://linuxmint.com/download.php",
        "guia": "https://linuxmint-installation-guide.readthedocs.io/",
    },
    {
        "id": "mint-xfce", "nome": "Linux Mint Xfce", "edicao": "edição Xfce", "familia": "ubuntu", "suporte": "herdada",
        "cor": ("#c0f5cf", "#2ec27e"), "letra": "M",
        "para": "Máquina antiga nas mãos de quem está começando. Os mesmos programas do Mint, com uma área de trabalho mais leve.",
        "conforto": "2 GB de memória e 20 GB de disco",
        "saber": "Na página de download, escolha a edição Xfce. Com 2 GB de memória, o navegador vai ser o que mais pesa, e o rolê “Dar vida nova a uma máquina antiga” cuida disso.",
        "baixar": "https://linuxmint.com/download.php",
        "guia": "https://linuxmint-installation-guide.readthedocs.io/",
    },
    {
        "id": "zorin", "nome": "Zorin OS", "edicao": "edição Core", "familia": "ubuntu", "suporte": "herdada",
        "cor": ("#99c1f1", "#1a5fb4"), "letra": "Z",
        "para": "Quem quer uma cara parecida com a do Windows ou a do macOS, trocada num clique, e um visual caprichado.",
        "conforto": "4 GB de memória e 30 GB de disco",
        "saber": "A edição Core é gratuita; a Pro é paga e só traz extras de visual e programas. A base é o Ubuntu LTS.",
        "baixar": "https://zorin.com/os/download/",
        "guia": "https://help.zorin.com/docs/getting-started/install-zorin-os/",
    },
    {
        "id": "ubuntu", "nome": "Ubuntu", "edicao": "LTS (24.04 ou 26.04)", "familia": "ubuntu", "suporte": "testada",
        "cor": ("#ffa348", "#e66100"), "letra": "U",
        "para": "Quem quer a distro mais documentada: quase todo tutorial e todo programa para Linux pensa no Ubuntu primeiro. Boa para estudar e programar.",
        "conforto": "4 GB de memória e 30 GB de disco",
        "saber": "Escolha sempre a versão LTS, que recebe atualizações por cinco anos. Alguns programas, como o Firefox, vêm como Snap.",
        "baixar": "https://ubuntu.com/download/desktop",
        "guia": "https://ubuntu.com/tutorials/install-ubuntu-desktop",
    },
    {
        "id": "pop", "nome": "Pop!_OS", "edicao": "24.04 LTS", "familia": "ubuntu", "suporte": "herdada",
        "cor": ("#93ddc2", "#2190a4"), "letra": "P",
        "para": "Quem tem placa NVIDIA e quer o driver já pronto no instalador, ou quer experimentar o COSMIC, a área de trabalho da System76.",
        "conforto": "4 GB de memória e 30 GB de disco",
        "saber": "Tem um download separado para quem tem NVIDIA. Usa um repositório próprio além do Ubuntu.",
        "baixar": "https://system76.com/pop/download/",
        "guia": "https://support.system76.com/articles/install-pop/",
    },
    {
        "id": "debian", "nome": "Debian", "edicao": "13, com Xfce ou LXQt", "familia": "debian", "suporte": "testada",
        "cor": ("#f66151", "#a51d2d"), "letra": "D",
        "para": "Máquina antiga, servidor da casa ou quem quer um sistema que muda pouco e dura anos sem surpresa.",
        "conforto": "2 GB de memória e 20 GB de disco com Xfce; 1 GB e 10 GB sem ambiente gráfico",
        "saber": "Não liga um firewall sozinho, e o bora resolve isso. No instalador, na tela “Seleção de software”, marque Xfce ou LXQt para máquina antiga, ou só “servidor SSH” para servidor.",
        "baixar": "https://www.debian.org/download",
        "guia": "https://www.debian.org/releases/stable/installmanual",
    },
    {
        "id": "fedora", "nome": "Fedora Workstation", "edicao": "versão atual", "familia": "fedora", "suporte": "onda 2",
        "cor": ("#99c1f1", "#1c71d8"), "letra": "F",
        "para": "Quem programa ou gosta de programas novos sem abrir mão da estabilidade. É a distro do dia a dia de quem mantém este projeto.",
        "conforto": "4 GB de memória e 30 GB de disco",
        "saber": "Sai uma versão nova a cada seis meses. Codecs e o driver da NVIDIA vêm do RPM Fusion, um repositório da comunidade. O pendrive se grava fácil com o Fedora Media Writer.",
        "baixar": "https://fedoraproject.org/workstation/download",
        "guia": "https://docs.fedoraproject.org/",
    },
    {
        "id": "bazzite", "nome": "Bazzite", "edicao": "imagem para a sua placa", "familia": "fedora-imutavel", "suporte": "onda 3",
        "cor": ("#dc8add", "#613583"), "letra": "B",
        "para": "Quem quer jogar: Steam, drivers e ajustes já vêm prontos, e há um modo que transforma o computador em videogame.",
        "conforto": "8 GB de memória e 64 GB de disco",
        "saber": "O sistema base não se mexe: os programas vêm por Flatpak, e uma atualização ruim se desfaz escolhendo a anterior no boot. Na página de download, escolha a placa de vídeo antes de baixar.",
        "baixar": "https://bazzite.gg/",
        "guia": "https://docs.bazzite.gg/",
    },
    {
        "id": "cachyos", "nome": "CachyOS", "edicao": "edição desktop", "familia": "arch", "suporte": "onda 3",
        "cor": ("#8ff0a4", "#1d6b4a"), "letra": "C",
        "para": "Quem já se vira no Linux e quer desempenho máximo nos jogos, com o Arch por baixo. É a primeira do ranking do DistroWatch em 2026.",
        "conforto": "8 GB de memória e 40 GB de disco",
        "saber": "É rolante: atualiza sempre, e às vezes pede atenção. Os pacotes do AUR ficam fora das receitas do bora.",
        "baixar": "https://cachyos.org/download/",
        "guia": "https://wiki.cachyos.org/",
    },
]
POR_ID = {d["id"]: d for d in DISTROS}

FAMILIA_NOME = {"ubuntu": "família Ubuntu", "debian": "família Debian", "fedora": "família Fedora",
                "fedora-imutavel": "Fedora imutável", "arch": "família Arch"}


# A etiqueta que diz o quanto o bora já foi testado nesta distro.
def ficha_suporte(d):
    s = d["suporte"]
    if s == "testada":
        return '<span class="ficha feito">✓ Testada com o <code>bora</code>, em máquina virtual</span>'
    if s == "herdada":
        return '<span class="ficha herdada">Usa as receitas do Ubuntu</span>'
    return f'<span class="ficha planejado"><code>bora</code> na {s}</span>'


# O selo redondo da distro, com a letra e as duas cores dela.
def selo(d, tamanho=""):
    c1, c2 = d["cor"]
    return (f'<span class="ladrilho selo-distro{tamanho}" style="--c1:{c1};--c2:{c2}" aria-hidden="true">'
            f'<b>{d["letra"]}</b></span>')


# O cartão de uma distro na lista do resultado.
def cartao(d):
    return f'''        <article class="cartao distro" id="d-{d["id"]}">
          <div class="distro-topo">
            {selo(d)}
            <div><h3>{d["nome"]}</h3><span class="edicao">{d["edicao"]} · {FAMILIA_NOME[d["familia"]]}</span></div>
          </div>
          {ficha_suporte(d)}
          <p>{d["para"]}</p>
          <dl>
            <dt>Confortável com</dt><dd>{d["conforto"]}</dd>
            <dt>Bom saber</dt><dd>{d["saber"]}</dd>
          </dl>
          <div class="distro-links">
            <a class="botao-mini" href="{d["baixar"]}">Baixar</a>
            <a class="botao-mini" href="{d["guia"]}">Guia oficial</a>
          </div>
        </article>'''


# Uma opção de resposta do questionário (um botão de rádio estilizado).
def opcao(nome, valor, titulo, texto, icone):
    return f'''            <label class="opcao">
              <input type="radio" name="{nome}" value="{valor}">
              <span class="opcao-caixa">
                <svg viewBox="0 0 24 24" aria-hidden="true">{icone}</svg>
                <strong>{titulo}</strong>
                <span>{texto}</span>
              </span>
            </label>'''


IC = {
    "notebook": '<rect x="4" y="5" width="16" height="10.5" rx="1.6"/><path d="M2.5 19h19"/>',
    "broto": '<rect x="3" y="4" width="18" height="12.5" rx="2"/><path d="M8.5 20.5h7M12 16.5v4"/><path d="M12 14v-3.2"/><path d="M12 10.8c0-2.2 1.4-3.4 3.6-3.4 0 2.2-1.4 3.4-3.6 3.4z"/><path d="M12 11.6c0-1.7-1.1-2.7-2.9-2.7 0 1.7 1.1 2.7 2.9 2.7z"/>',
    "controle": '<path d="M7 8h10a4 4 0 0 1 4 4.4l-.4 3.6a2.3 2.3 0 0 1-4 1.2L15 15.5H9l-1.6 1.7a2.3 2.3 0 0 1-4-1.2L3 12.4A4 4 0 0 1 7 8z"/><path d="M7.5 11v3M6 12.5h3M15.5 12h.01M17.5 13.5h.01"/>',
    "livro": '<path d="M3.5 5.5c2.6-.9 5.4-.6 8.5 1.2v12.6c-3.1-1.8-5.9-2.1-8.5-1.2z"/><path d="M20.5 5.5c-2.6-.9-5.4-.6-8.5 1.2v12.6c3.1-1.8 5.9-2.1 8.5-1.2z"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7.5 9.5l3 2.5-3 2.5M12.5 15h4"/>',
    "casa": '<path d="M3.5 11L12 4l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5h4v5"/>',
    "semente": '<path d="M12 20v-7"/><path d="M12 13c0-3.3 2.2-5 5.5-5 0 3.3-2.2 5-5.5 5z"/><path d="M12 14.5c0-2.6-1.7-4-4.3-4 0 2.6 1.7 4 4.3 4z"/>',
    "folhas": '<path d="M7 20c0-6 3-10 10-12-1 7-4 11-10 12z"/><path d="M7 20l6-7"/>',
    "arvore": '<path d="M12 21v-6"/><path d="M12 3l6 8h-3l4 5H5l4-5H6z"/>',
}


# A página inteira: questionário, resultado e o caminho até o primeiro boot.
# Os dados das distros vão também em JSON, para o distro.js montar o resultado.
def corpo():
    dados = json.dumps({d["id"]: {k: d[k] for k in ("nome", "edicao", "suporte", "baixar", "guia")} for d in DISTROS}, ensure_ascii=False)
    cartoes = "\n".join(cartao(d) for d in DISTROS)

    teclas = [
        ("Acer", "F12", "Às vezes é preciso ligar o “F12 Boot Menu” no setup, com F2"),
        ("Asus", "F8 ou Esc", "Setup com F2 ou Del"),
        ("Dell", "F12", "Setup com F2"),
        ("HP", "F9, ou Esc e depois F9", "Setup com F10"),
        ("Lenovo", "F12, ou Fn + F12", "Alguns têm um botãozinho “Novo” ao lado da tomada"),
        ("Samsung", "F10 ou Esc", "Setup com F2"),
        ("Placa-mãe de desktop", "F8, F11 ou F12", "A tecla aparece na tela por um instante ao ligar"),
    ]
    linhas_teclas = "\n".join(
        f"              <tr><td>{m}</td><td><kbd>{t}</kbd></td><td>{o}</td></tr>" for m, t, o in teclas)

    resumo = [
        ("Nunca usou Linux, computador comum", "mint", "zorin"),
        ("Máquina antiga, 4 GB de memória ou menos", "mint-xfce", "debian"),
        ("Estudante que vai programar", "ubuntu", "fedora"),
        ("Servidor da casa (pasta, filmes, acesso de fora)", "debian", "ubuntu"),
        ("Quer jogar e está começando", "bazzite", "pop"),
        ("Joga e já se vira no Linux", "cachyos", "bazzite"),
    ]
    # Link para o cartão da distro na mesma página.
    def link(i):
        return f'<a href="#d-{i}">{POR_ID[i]["nome"]}</a>'
    linhas_resumo = "\n".join(
        f"              <tr><td>{q}</td><td><strong>{link(a)}</strong></td><td>{link(b)}</td></tr>" for q, a, b in resumo)

    P = '<span class="p">você@computador:~$</span> '
    terminal = janela("Terminal", [
        ("cmd", P + '<span class="c">wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/bora-linux-x86_64</span>'),
        ("cmd", P + '<span class="c">wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/SHA256SUMS</span>'),
        ("cmd", P + '<span class="c">sha256sum --check --ignore-missing SHA256SUMS</span>'),
        ("", 'bora-linux-x86_64: <span class="v">OK</span>'),
        ("cmd", P + '<span class="c">sudo install -m 755 bora-linux-x86_64 /usr/local/bin/bora</span>'),
        ("cmd", P + '<span class="c">bora diag</span>'),
        ("", '<span class="o">Distro</span>'),
        ("", '  Ubuntu 26.04.1 LTS'),
        ("", '  família: ubuntu, base 26.04'),
        ("", ''),
        ("", '<span class="o">Sistema</span>'),
        ("", '  arquitetura: x86_64'),
        ("", '  systemd: sim, UEFI: sim'),
        ("", ''),
        ("", '<span class="o">Hardware</span>'),
        ("", '  memória: 7.6 GB'),
        ("", '  disco livre na raiz: 212.4 GB'),
        ("", '  disco do sistema: SSD'),
        ("", ''),
        ("", '<span class="o">Já tem</span>'),
        ("", '  snapshot do sistema: <span class="a">não configurado</span>'),
        ("", '  firewall: ufw'),
        ("", '  memória comprimida (zram): desligada'),
        ("", '  rede: <span class="v">conectada</span>'),
        ("cmd", P + '<span class="c">sudo bora</span>'),
    ], "Terminal: baixar o bora e o SHA256SUMS com wget, conferir com sha256sum, instalar em /usr/local/bin/bora, rodar bora diag, que mostra Ubuntu 26.04 LTS da família ubuntu, e abrir o menu com sudo bora.")

    return f'''    <div class="abertura interna">
      <div class="largura">
        <div>
          <ol class="migalhas" aria-label="Onde você está">
            <li><a href="../">Início</a></li>
            <li aria-current="page">Escolher e instalar a distro</li>
          </ol>
          <h1>Escolher e instalar a distro</h1>
          <p class="lema">Antes do <code>bora</code>, vem o Linux. <strong>Responda três perguntas</strong>, veja qual distro combina com você e siga do pendrive até o primeiro <code>bora diag</code>.</p>
          <div class="fichas">
            <span class="ficha">3 perguntas</span>
            <span class="ficha">{len(DISTROS)} distros comparadas</span>
            <span class="ficha agora">Só instalação limpa, por enquanto</span>
          </div>
          <div class="acoes">
            <a class="botao principal" href="#escolher">Fazer as perguntas</a>
            <a class="botao secundario" href="#instalar">Já escolhi, quero instalar</a>
          </div>
        </div>
        <figure class="palco" style="margin:0" data-anima>
          <svg class="ilustra trilha-role caminho-distro" viewBox="0 0 500 230" role="img" aria-labelledby="cd-t">
            <title id="cd-t">O caminho desta página: escolher a distro, gravar o pendrive, instalar e rodar o bora diag.</title>
            <path d="M60 95 C 120 30, 170 30, 190 95 S 290 160, 310 95 S 410 30, 440 95" class="traco tracejado"/>
            <g class="parada" style="--i:0"><circle cx="60" cy="95" r="34" class="caixa-svg"/><path transform="translate(42 77) scale(1.5)" class="traco" d="M11 3.5a7.5 7.5 0 1 0 0 15 7.5 7.5 0 0 0 0-15zM21 21l-4.6-4.6"/></g>
            <g class="parada" style="--i:3"><circle cx="190" cy="95" r="34" class="caixa-svg"/><path transform="translate(172 77) scale(1.5)" class="traco" d="M8 2.5h8v8H8zM6 10.5h12v9a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2zM10 5.5h.01M14 5.5h.01"/></g>
            <g class="parada" style="--i:6"><circle cx="310" cy="95" r="34" class="caixa-svg"/><path transform="translate(292 77) scale(1.5)" class="traco" d="M4 5h16v10.5H4zM2.5 19h19M12 7.5v5M9.5 10.5l2.5 2.5 2.5-2.5"/></g>
            <g class="parada" style="--i:9"><circle cx="440" cy="95" r="34" class="laranja"/><g transform="translate(418 73) scale(2.75)" style="color:#fff"><use href="#pegada" width="16" height="16"/></g></g>
            <g class="pe" style="--i:1"><use href="#pegada" x="112" y="40" width="18" height="18" transform="rotate(70 121 49)" class="laranja" style="color:var(--accent)"/></g>
            <g class="pe" style="--i:2"><use href="#pegada" x="148" y="34" width="18" height="18" transform="rotate(100 157 43)" style="color:var(--accent)"/></g>
            <g class="pe" style="--i:4"><use href="#pegada" x="232" y="140" width="18" height="18" transform="rotate(110 241 149)" style="color:var(--accent)"/></g>
            <g class="pe" style="--i:5"><use href="#pegada" x="268" y="140" width="18" height="18" transform="rotate(70 277 149)" style="color:var(--accent)"/></g>
            <g class="pe" style="--i:7"><use href="#pegada" x="352" y="34" width="18" height="18" transform="rotate(70 361 43)" style="color:var(--accent)"/></g>
            <g class="pe" style="--i:8"><use href="#pegada" x="390" y="40" width="18" height="18" transform="rotate(110 399 49)" style="color:var(--accent)"/></g>
            <text x="60" y="158" font-size="15" text-anchor="middle" font-weight="600">Escolher</text>
            <text x="190" y="158" font-size="15" text-anchor="middle" font-weight="600">Gravar</text>
            <text x="310" y="158" font-size="15" text-anchor="middle" font-weight="600">Instalar</text>
            <text x="440" y="158" font-size="15" text-anchor="middle" font-weight="600" class="mono">bora diag</text>
            <text x="60" y="178" font-size="12.5" text-anchor="middle" class="t2">3 perguntas</text>
            <text x="190" y="178" font-size="12.5" text-anchor="middle" class="t2">o pendrive</text>
            <text x="310" y="178" font-size="12.5" text-anchor="middle" class="t2">apagando o disco</text>
            <text x="440" y="178" font-size="12.5" text-anchor="middle" class="t2">e o primeiro rolê</text>
          </svg>
          <figcaption>Quatro passos. Os três primeiros não precisam do <code>bora</code>; o último é onde ele entra.</figcaption>
        </figure>
      </div>
    </div>

    <section id="escolher" class="largura">
{cabeca("Passo 1", "Qual distro combina com você?", "Distro é o jeito como o Linux chega pronto para usar: o visual, os programas e o ritmo das atualizações. Não existe a melhor, existe a que serve para você e para essa máquina.")}
      <form class="questionario cartao" id="questionario" aria-describedby="q-ajuda">
        <p id="q-ajuda" class="q-ajuda">Escolha uma resposta em cada pergunta. A sugestão aparece logo abaixo, e nada sai do seu navegador.</p>
        <fieldset>
          <legend><span class="n">1</span>Que computador é esse?</legend>
          <div class="opcoes">
{opcao("maquina", "comum", "Um computador comum", "Notebook ou desktop dos últimos dez anos, com mais de 4 GB de memória", IC["notebook"])}
{opcao("maquina", "antiga", "Uma máquina antiga", "4 GB de memória ou menos, ou que já anda engasgando", IC["broto"])}
{opcao("maquina", "potente", "Um computador para jogos", "Com placa de vídeo dedicada, NVIDIA ou AMD", IC["controle"])}
          </div>
        </fieldset>
        <fieldset>
          <legend><span class="n">2</span>O que você mais vai fazer nele?</legend>
          <div class="opcoes">
{opcao("uso", "estudar", "Estudar, trabalhar e navegar", "Navegador, documentos, vídeos, chamadas", IC["livro"])}
{opcao("uso", "programar", "Programar", "Ou aprender a programar, com ou sem IA", IC["terminal"])}
{opcao("uso", "jogar", "Jogar", "Steam, emuladores, jogos do Windows pelo Proton", IC["controle"])}
{opcao("uso", "servidor", "Servir a casa", "Ficar ligado com a pasta compartilhada, os filmes e as séries", IC["casa"])}
          </div>
        </fieldset>
        <fieldset>
          <legend><span class="n">3</span>Quanto você já mexeu com Linux?</legend>
          <div class="opcoes">
{opcao("experiencia", "nunca", "Nunca, ou quase nada", "É a primeira vez, e tudo bem", IC["semente"])}
{opcao("experiencia", "pouco", "Já usei um pouco", "Já instalei ou usei na escola, no trabalho", IC["folhas"])}
{opcao("experiencia", "bastante", "Bastante", "Me viro no terminal e não tenho medo de ler o erro", IC["arvore"])}
          </div>
        </fieldset>
        <div class="resultado" id="resultado" aria-live="polite">
          <p class="resultado-vazio" id="resultado-vazio">Responda as três perguntas para ver a sugestão. <span class="sem-js">Sem JavaScript? A tabela logo abaixo tem as mesmas respostas.</span></p>
        </div>
      </form>
      <script type="application/json" id="distros-dados">{dados}</script>

      <div class="bloco">
        <h3>O resumo em uma tabela</h3>
        <div class="tabela-envolta">
          <table class="tabela">
            <thead><tr><th>Se você é…</th><th>Comece por</th><th>Ou então</th></tr></thead>
            <tbody>
{linhas_resumo}
            </tbody>
          </table>
        </div>
        <p class="nota">Vai usar o <code>bora</code> agora? Fique com o Ubuntu, o Debian ou uma derivada do Ubuntu (Mint, Zorin, Pop!_OS): são as famílias da <a href="../#status">onda 1</a>. Fedora, Bazzite e CachyOS são ótimas escolhas, mas o <code>bora</code> só chega nelas nas próximas ondas. Máquinas de 32 bits ficam de fora: nenhuma destas distros instala nelas.</p>
      </div>
    </section>

    <section id="distros" class="largura">
{cabeca("As distros", "Uma a uma", "As que o projeto recomenda, com o que cada uma pede da máquina e a situação do <code>bora</code> em cada família. Baixe sempre do site oficial.")}
      <div class="grade-distros">
{cartoes}
      </div>
    </section>

    <section id="instalar" class="largura">
{cabeca("Passos 2 e 3", "Do pendrive ao primeiro boot", "O caminho é o mesmo em todas as distros da lista. Aqui fica o mapa e o que costuma dar errado; os detalhes de cada tela estão no guia oficial de cada uma.")}
      <ol class="etapas">
        <li class="etapa">
          <span class="marco" aria-hidden="true">1</span>
          <div class="corpo">
            <h3>Guarde o que importa <small>antes de tudo</small></h3>
            <p>A instalação limpa <strong>apaga o disco inteiro</strong>, com o Windows e os arquivos. Copie fotos, documentos e senhas salvas no navegador para um disco externo ou para a nuvem, e confira se a cópia abre.</p>
            <ul>
              <li>Instalar ao lado do Windows (dual boot) fica para depois: BitLocker, Secure Boot e partições variam demais de máquina para máquina, e o erro custa dados.</li>
              <li>Confira se o computador é de 64 bits. No Windows: Configurações › Sistema › Sobre, em “Tipo de sistema”.</li>
            </ul>
          </div>
        </li>
        <li class="etapa">
          <span class="marco" aria-hidden="true">2</span>
          <div class="corpo">
            <h3>Baixe a imagem e confira <small>uns 3 a 8 GB</small></h3>
            <p>A imagem é um arquivo <code>.iso</code>. Baixe só do site oficial (os links estão nos cartões acima) e compare o código de conferência, o SHA256, com o que o site mostra. Se for diferente, o download veio quebrado ou adulterado: baixe de novo.</p>
            <ul class="caixa comandos conferir-iso">
              <li class="linha"><code>Get-FileHash arquivo.iso</code><span>no PowerShell do Windows</span></li>
              <li class="linha"><code>shasum -a 256 arquivo.iso</code><span>no Terminal do macOS</span></li>
              <li class="linha"><code>sha256sum arquivo.iso</code><span>num Linux</span></li>
            </ul>
          </div>
        </li>
        <li class="etapa">
          <span class="marco" aria-hidden="true">3</span>
          <div class="corpo">
            <h3>Grave o pendrive <small>8 GB ou mais</small></h3>
            <p>Tudo o que estiver no pendrive será apagado. Copiar o <code>.iso</code> para dentro dele não funciona: é preciso um programa que grave a imagem.</p>
            <ul>
              <li><strong>No Windows:</strong> <a href="https://rufus.ie/pt_BR/">Rufus</a>, <a href="https://etcher.balena.io/">balenaEtcher</a> ou o <a href="https://fedoraproject.org/workstation/download">Fedora Media Writer</a>.</li>
              <li><strong>No macOS:</strong> balenaEtcher ou Fedora Media Writer.</li>
              <li><strong>Num Linux:</strong> o Fedora Media Writer, ou o app Discos (GNOME), em “Restaurar imagem de disco”.</li>
              <li><strong>Quer testar várias?</strong> O <a href="https://www.ventoy.net/">Ventoy</a> prepara o pendrive uma vez, e depois é só copiar quantas <code>.iso</code> couberem.</li>
              <li>O Bazzite tem uma imagem grande: use um pendrive de 16 GB.</li>
            </ul>
          </div>
        </li>
        <li class="etapa">
          <span class="marco" aria-hidden="true">4</span>
          <div class="corpo">
            <h3>Dê o boot pelo pendrive</h3>
            <p>Com o pendrive espetado, ligue o computador apertando várias vezes a tecla do menu de boot e escolha o pendrive (às vezes aparece como “UEFI: nome do pendrive”). Se o Windows estiver funcionando, há um atalho: segure <kbd>Shift</kbd>, clique em Reiniciar e escolha “Usar um dispositivo”.</p>
            <div class="tabela-envolta teclas">
              <table class="tabela">
                <thead><tr><th>Marca</th><th>Menu de boot</th><th>Observação</th></tr></thead>
                <tbody>
{linhas_teclas}
                </tbody>
              </table>
            </div>
          </div>
        </li>
        <li class="etapa azul">
          <span class="marco" aria-hidden="true">5</span>
          <div class="corpo">
            <h3>Experimente antes de instalar <small>nada é gravado no disco</small></h3>
            <p>Quase todas abrem um modo “ao vivo”, rodando do pendrive. Aproveite para conferir o que mais dá problema: Wi-Fi, som, brilho da tela, touchpad e webcam. Se algo não funcionar, veja as armadilhas logo abaixo antes de seguir.</p>
          </div>
        </li>
        <li class="etapa">
          <span class="marco" aria-hidden="true">6</span>
          <div class="corpo">
            <h3>Instale <small>uns 15 a 30 minutos</small></h3>
            <ul>
              <li><strong>Idioma:</strong> Português (Brasil). <strong>Teclado:</strong> “Português (Brasil)” se o teclado tem a tecla <kbd>Ç</kbd>; se não tem, “Inglês (EUA, internacional com teclas mortas)”.</li>
              <li><strong>Disco:</strong> “Apagar o disco e instalar”. Criptografar o disco protege seus dados se o notebook for roubado, mas sem a senha não há volta: anote.</li>
              <li><strong>Codecs e programas de terceiros:</strong> pode deixar desmarcado. O rolê <a href="../catalogo/roles/pronto-para-estudar.html">Pronto para estudar e trabalhar</a> instala os codecs depois, e sabe desfazer.</li>
              <li><strong>Usuário:</strong> um nome curto, sem acento nem espaço, e uma senha que você lembre. É ela que o <code>sudo</code> vai pedir.</li>
            </ul>
          </div>
        </li>
        <li class="etapa verde">
          <span class="marco" aria-hidden="true">7</span>
          <div class="corpo">
            <h3>Primeiro boot</h3>
            <p>Tire o pendrive quando o instalador pedir e reinicie. Não precisa sair instalando atualizações e programas: o próximo passo é conseguir internet e deixar o <code>bora</code> arrumar a casa. Pode pegar um café.</p>
          </div>
        </li>
      </ol>
    </section>

    <section id="armadilhas" class="largura">
{cabeca("Quando trava", "Armadilhas comuns", "O que mais dá errado na primeira instalação, e a saída para cada uma.")}
      <div class="porques">
        <article class="cartao porque"><h3>O computador ignora o pendrive</h3><p>Grave de novo com outro programa, tente outra porta USB (as de trás, no desktop) e desligue o “Fast Boot” no setup. Ubuntu, Mint, Debian e Fedora dão boot com o Secure Boot ligado; as outras podem pedir para desligá-lo, e o guia oficial diz se é o caso.</p></article>
        <article class="cartao porque"><h3>O instalador não acha o disco</h3><p>Muitos notebooks com Intel saem de fábrica com o disco em modo RST ou VMD. No setup, troque o modo do disco para AHCI, ou desligue o VMD. Numa instalação limpa isso não estraga nada.</p></article>
        <article class="cartao porque"><h3>Tela preta ou travada no boot</h3><p>É quase sempre a placa de vídeo, em geral NVIDIA, para surpresa de ninguém. No menu do pendrive, escolha “modo de compatibilidade” (Mint) ou “Safe graphics” (Ubuntu). Depois de instalar, o gerenciador de drivers resolve. O Pop!_OS tem uma imagem com o driver já dentro.</p></article>
        <article class="cartao porque"><h3>Sem Wi-Fi</h3><p>Algumas placas Broadcom e Realtek precisam de um driver que só vem pela internet. Ligue por cabo ou pelo celular (veja abaixo) e abra o “Gerenciador de drivers” no Mint ou “Drivers adicionais” no Ubuntu.</p></article>
        <article class="cartao porque"><h3>O teclado não faz ç nem acento</h3><p>O layout errado foi escolhido na instalação. Em Configurações › Teclado, troque para “Português (Brasil)” se houver a tecla <kbd>Ç</kbd>, ou “Inglês (EUA, internacional com teclas mortas)” se não houver.</p></article>
        <article class="cartao porque"><h3>Computador muito velho</h3><p>Se ele for de 32 bits, de antes de 2008 mais ou menos, nenhuma distro desta página instala nele, e o projeto deixou esse caso de fora. Com 64 bits e 2 GB de memória, o Mint Xfce e o Debian com LXQt ainda dão conta.</p></article>
      </div>
    </section>

    <section id="internet" class="largura">
{cabeca("Passo 4, primeiro pedaço", "Conseguir internet", "O <code>bora</code> baixa os programas da internet, então ela precisa estar funcionando.")}
      <div class="portas">
        <article class="cartao porta">
          <div class="rotulo"><span class="n">1</span><h3>Cabo</h3></div>
          <p>O caminho mais garantido: funciona sem driver e sem senha. Se o notebook não tem porta de rede, um adaptador USB para rede costuma funcionar direto.</p>
        </article>
        <article class="cartao porta">
          <div class="rotulo"><span class="n">2</span><h3>Wi-Fi</h3></div>
          <p>Clique no ícone de rede, no canto da tela, escolha a rede e digite a senha. Se a lista de redes não aparece, é caso de driver: use o cabo ou o celular uma vez para instalá-lo.</p>
        </article>
        <article class="cartao porta">
          <div class="rotulo"><span class="n">3</span><h3>Celular pelo USB</h3></div>
          <p>Ligue o Android no cabo USB e ative em Configurações › Rede e internet › Ponto de acesso › “Tethering USB” (o nome muda um pouco de marca para marca). Costuma funcionar sem instalar nada, mesmo quando o Wi-Fi do computador não funciona.</p>
        </article>
      </div>
    </section>

    <section id="bora" class="largura">
{cabeca("Passo 4", "Instalar o <code>bora</code> e rodar <code>bora diag</code>", "O <code>bora</code> é um arquivo só. Abra o Terminal (no Mint e no Ubuntu, <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd>), baixe, confira e instale em <code>/usr/local/bin</code>. O <code>bora diag</code> não muda nada: só mostra o que encontrou.")}
      <div class="bora-grade">
        <figure style="margin:0">
{terminal}
        </figure>
        <div class="bora-lado">
          <ul class="caixa">
            <li class="linha"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M8.5 12.3l2.4 2.4 4.6-4.9"/></svg><span class="txt"><strong>O <code>OK</code> do <code>sha256sum</code></strong><span>Garante que o arquivo é o mesmo que saiu do projeto. Se aparecer outra coisa, apague e baixe de novo.</span></span></li>
            <li class="linha"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="10.5" rx="1.6"/><path d="M2.5 19h19"/></svg><span class="txt"><strong>Processador ARM?</strong><span>O <code>bora</code> roda só em computadores de 64 bits com processador Intel ou AMD (x86_64).</span></span></li>
            <li class="linha"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10v4.5M12 17.3h.01"/></svg><span class="txt"><strong>Travou em algum ponto?</strong><span>Rode <code>bora ajuda</code>: ele monta uma pergunta pronta, sem dados sensíveis, para colar em qualquer chat de IA.</span></span></li>
            <li class="linha"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 5v6h-6"/></svg><span class="txt"><strong>Para atualizar</strong><span>Repita os mesmos comandos: o <code>install</code> troca o arquivo antigo pelo novo. O <code>bora versao</code> mostra qual você tem, e a <a href="{REPO}/releases">página de versões</a> conta o que mudou.</span></span></li>
          </ul>
          <a class="cartao proximo" href="../catalogo/roles/pronto-para-estudar.html">
            <span class="ladrilho l-azul" aria-hidden="true"><svg viewBox="0 0 24 24">{IC["livro"]}</svg></span>
            <span class="txt"><span class="sobretitulo">Próximo passo</span><strong>Pronto para estudar e trabalhar</strong><span>O primeiro rolê: atualização, firewall, codecs, Flatpak, snapshot e backup da pasta pessoal. Os outros três rolês prontos estão no <code>sudo bora</code> também.</span></span>
            <svg class="ir" aria-hidden="true"><use href="#seta"/></svg>
          </a>
        </div>
      </div>
    </section>

{bloco_pedidos("Escolher e instalar a distro", "esta página", "nesta página", outra_distro=True, editar=REPO + "/blob/main/ferramentas/catalogo/distro.py")}
'''
