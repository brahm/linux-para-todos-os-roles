# Páginas das receitas prontas.
from comum import REPO, RAIZ_REPO, ladrilho, cabeca, janela, bloco_pedidos, P
from dados import RECEITAS, FAMILIAS, NIVEL_TEXTO, ler_receita, ROLES, pagina_receita

ICONE_ETAPA = {
    "verificar": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
    "aplicar": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "testar": '<path d="M9 3.5h6M10 3.5v5.5L5 18.5A1.6 1.6 0 0 0 6.4 21h11.2a1.6 1.6 0 0 0 1.4-2.5L14 9V3.5"/><path d="M7.5 15h9"/>',
    "desfazer": '<path d="M9 14L4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
}


def etapas(lista):
    """lista: (chave, cor, título, subtítulo, html)"""
    itens = []
    for chave, cor, titulo, sub, html in lista:
        itens.append(f'''        <li class="etapa {cor} revelar">
          <span class="marco" aria-hidden="true"><svg viewBox="0 0 24 24">{ICONE_ETAPA[chave]}</svg></span>
          <div class="corpo">
            <h3>{titulo} <small>{sub}</small></h3>
            {html}
          </div>
        </li>''')
    return '      <ol class="etapas">\n' + "\n".join(itens) + "\n      </ol>"


def faz_nao(faz, nao, titulo_faz="O que faz", titulo_nao="O que não faz"):
    li = lambda xs: "\n".join(f"            <li>{x}</li>" for x in xs)
    return f'''      <div class="faz-nao">
        <div class="cartao faz revelar">
          <h3><span class="marca-icone" aria-hidden="true">✓</span>{titulo_faz}</h3>
          <ul>
{li(faz)}
          </ul>
        </div>
        <div class="cartao nao-faz revelar">
          <h3><span class="marca-icone" aria-hidden="true">✕</span>{titulo_nao}</h3>
          <ul>
{li(nao)}
          </ul>
        </div>
      </div>'''


def porques(lista):
    return '      <div class="porques">\n' + "\n".join(
        f'''        <article class="cartao porque revelar"><h3>{q}</h3><p>{r}</p></article>''' for q, r in lista) + "\n      </div>"


def mudancas(lista):
    """lista: (ícone, título, detalhe)"""
    ic = {
        "pacote": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
        "arquivo": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/>',
        "servico": '<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
        "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/>',
        "foto": '<rect x="3" y="7" width="18" height="13" rx="2.5"/><circle cx="12" cy="13.5" r="3.6"/>',
        "escudo": '<path d="M12 3l7 3v5.2c0 4.4-2.9 7.9-7 9.8-4.1-1.9-7-5.4-7-9.8V6z"/>',
        "copia": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8"/>',
    }
    itens = "\n".join(
        f'''        <li><div class="linha"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ic[i]}</svg><span class="txt"><strong>{t}</strong><span>{d}</span></span></div></li>'''
        for i, t, d in lista)
    return f'      <ul class="caixa revelar">\n{itens}\n      </ul>'


def parametros(rid, r):
    if not r.get("parametros"):
        return f'''      <p class="nota revelar">Esta receita não tem parâmetros: ela faz sempre a mesma coisa, em qualquer máquina. No menu, o <code>bora</code> não pergunta nada; num script ou num agente, basta <code>bora plano --receitas {rid}</code>.</p>'''
    linhas = []
    for nome, p in (r.get("parametros") or {}).items():
        padrao = p.get("padrao")
        if isinstance(padrao, bool):
            padrao = "sim" if padrao else "não"
        o_que = p.get("pergunta") or p.get("descricao") or ""
        if p.get("tipo") in ("escolha", "lista"):
            rot = p.get("rotulos") or {}
            ops = "".join(f"<li><code>{o}</code>{': ' + rot[o] if o in rot else ''}</li>" for o in p["opcoes"])
            o_que += f'<ul style="margin:8px 0 0;padding-left:18px">{ops}</ul>'
        linhas.append(f"<tr><td><code>{nome}</code></td><td><code>{padrao}</code></td><td>{o_que}</td></tr>")
    ps = list((r.get("parametros") or {}).items())
    ordem = {"escolha": 0, "lista": 0, "booleano": 1, "inteiro": 2}
    exemplo_nome, exemplo_valor = sorted(ps, key=lambda kv: ordem.get(kv[1].get("tipo"), 9))[0]
    tipo = exemplo_valor.get("tipo")
    ops = exemplo_valor.get("opcoes") or ["", ""]
    valor = {"escolha": ops[1], "lista": ",".join(ops[:2]), "booleano": "nao", "inteiro": "7"}.get(tipo, "auto")
    return f'''      <div class="tabela-envolta revelar">
        <table class="tabela">
          <thead><tr><th>Parâmetro</th><th>Padrão</th><th>O que é</th></tr></thead>
          <tbody>
            {"".join(linhas)}
          </tbody>
        </table>
      </div>
      <p class="nota">No menu, o <code>bora</code> pergunta o que precisa. Num script ou num agente, passe os parâmetros na linha de comando:<br><code>bora plano --receitas {rid} -p {rid}.{exemplo_nome}={valor}</code></p>'''


def comandos(lista):
    return '      <div class="comandos-conferir">\n' + "\n".join(
        f'        <div class="cartao comando revelar"><code>{c}</code><span>{d}</span></div>' for c, d in lista) + "\n      </div>"


# As capturas da máquina virtual com tela (testes/vm/telas/<distro>/, gravadas
# pelo workflow) que cada receita mostra: (arquivo, legenda).
CAPTURAS = {
    "desktop/ambiente-leve": [("1-tela-de-login", "A tela de login, antes da receita"),
                              ("2-ambiente-leve", "O ambiente leve, que abriu sozinho depois da receita")],
    "desktop/navegador-leve": [("3-firefox", "O Firefox com o uBlock Origin instalado pela política")],
    "desktop/sem-snap": [("3-firefox", "O Firefox depois da receita (no Ubuntu, o da Mozilla)"),
                         ("4-depois-de-desfazer", "A tela de login depois de desfazer tudo")],
}
DISTROS_TELAS = [("ubuntu-24.04", "Ubuntu 24.04"), ("ubuntu-26.04", "Ubuntu 26.04"), ("debian-13", "Debian 13"),
                 ("debian-13-lightdm", "Debian 13 com o LightDM")]
PASTA_TELAS = RAIZ_REPO + "testes/vm/telas/"


def capturas(rid):
    """As capturas da receita, por distro, ou nada se ainda não há nenhuma."""
    import os
    figuras = []
    for alvo, nome in DISTROS_TELAS:
        pasta = PASTA_TELAS + alvo + "/"
        if not os.path.isfile(pasta + "data.txt"):
            continue
        a, m, d = open(pasta + "data.txt").read().strip().split("-")
        for arq, legenda in CAPTURAS.get(rid, []):
            if os.path.isfile(pasta + arq + ".png"):
                figuras.append(f'''          <figure class="captura"><a href="../telas/{alvo}/{arq}.png"><img src="../telas/{alvo}/{arq}.png" alt="Captura da tela em {nome}: {legenda[0].lower() + legenda[1:]}" loading="lazy" width="640" height="400"></a><figcaption>{nome}, {d}/{m}/{a}. {legenda}.</figcaption></figure>''')
    if not figuras:
        return ""
    return f'''
      <div class="bloco">
        <h3>Na máquina virtual com tela</h3>
        <div class="capturas revelar">
{chr(10).join(figuras)}
        </div>
        <p class="nota">Capturas de verdade do <a href="{REPO}/blob/main/testes/vm/README.md#a-máquina-com-tela">teste automático com tela</a>, que roda toda semana. Elas são trocadas quando o registro de testes muda, no máximo uma vez por mês.</p>
      </div>'''


def onde_testada(r):
    fam = r.get("familias") or {}
    cartoes = "\n".join(
        f'''        <div class="cartao familia"><strong>{nome}</strong><span class="nivel {fam.get(f, 'planejada')}">{NIVEL_TEXTO.get(fam.get(f, 'planejada'))}</span><span style="color:var(--text-2);font-size:14px">{exemplos}</span></div>'''
        for f, nome, exemplos in FAMILIAS)
    onde = {"conteiner": "Contêiner (teste automático)", "vm": "Máquina virtual", "maquina": "Computador de verdade"}
    distros = {"ubuntu": "Ubuntu", "debian": "Debian"}
    testes = "".join(
        f"<tr><td>{distros.get(t['distro'], t['distro'])} {t['versao']}</td><td>{onde.get(t.get('onde'), t.get('onde', ''))}</td><td>{t['data']:%d/%m/%Y}</td><td>{'Passou' if t['resultado'] == 'ok' else t['resultado']}</td></tr>"
        for t in r.get("testes", []))
    return f'''      <div class="familias revelar">
{cartoes}
      </div>
      <div class="bloco">
        <h3>Registro de testes</h3>
        <div class="tabela-envolta revelar">
          <table class="tabela">
            <thead><tr><th>Distro</th><th>Onde</th><th>Data</th><th>Resultado</th></tr></thead>
            <tbody>{testes}</tbody>
          </table>
        </div>
        <p class="nota"><strong>Testada em contêiner</strong> quer dizer que a receita passou nos testes automáticos dessa família, que rodam num contêiner, sem kernel, disco nem tela de login de verdade. Quando ela passar numa máquina virtual ou num computador de verdade, o registro acima mostra; até lá, o <code>bora</code> avisa quando monta o plano. <a href="{REPO}/blob/main/CONTRIBUTING.md#antes-de-abrir-um-pull-request">Testar numa máquina sua</a> é uma das ajudas mais valiosas.</p>
      </div>{capturas(r.get('id', ''))}'''


def fontes(lista):
    return '      <ul class="caixa revelar">\n' + "\n".join(
        f'        <li><a class="linha" href="{u}"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/></svg><span class="txt"><strong>{t}</strong><span>{d}</span></span><svg class="ir" aria-hidden="true"><use href="#seta"/></svg></a></li>'
        for t, d, u in lista) + "\n      </ul>"


def roles_que_usam(rid):
    usos = [r for r in ROLES if any(x == rid for x, _ in r["receitas"])]
    itens = "\n".join(
        f'''        <a class="cartao role" href="../roles/{r['id']}.html">
          {ladrilho(r['icone'], r['cor'])}
          <h3>{r['nome']}</h3>
          <p>{next(n for x, n in r['receitas'] if x == rid) and 'Com ' + next(n for x, n in r['receitas'] if x == rid) + '. ' or ''}{r['resumo']}</p>
          <div class="rodape"><span class="num">{r['num']}</span><span class="vai">Ver o rolê</span></div>
        </a>''' for r in usos)
    return f'      <div class="grade">\n{itens}\n      </div>'


def abertura(rid, r, ilustracao, legenda):
    nome, icone, cor, _ = RECEITAS[rid]
    risco = r.get("risco", "baixo")
    risco_txt = {"baixo": "Risco baixo", "medio": "Risco médio", "alto": "Risco alto"}[risco]
    return f'''    <div class="abertura interna">
      <div class="largura">
        <div>
          <ol class="migalhas" aria-label="Onde você está">
            <li><a href="../">Rolês e receitas</a></li>
            <li><a href="../#receitas">Receitas</a></li>
            <li aria-current="page">{nome}</li>
          </ol>
          <h1>{ladrilho(icone, cor)}<span>{nome}</span></h1>
          <p class="lema">{r['descricao']}</p>
          <div class="fichas">
            <span class="ficha"><code>{rid}</code></span>
            <span class="ficha risco-{risco}">{risco_txt}</span>
            <span class="ficha">Pede a senha de administrador</span>
            <span class="ficha feito testada">Testada em contêiner no Ubuntu e no Debian</span>
          </div>
          <div class="acoes">
            <a class="botao principal" href="#passo-a-passo">Ver o passo a passo</a>
            <a class="botao secundario" href="{REPO}/tree/main/receitas/{rid}">Ver o código</a>
          </div>
        </div>
        <figure class="palco" style="margin:0" data-anima>
{ilustracao}
          <figcaption>{legenda}</figcaption>
        </figure>
      </div>
    </div>'''


def secao(id_, sobre, titulo, texto, conteudo):
    return f'''    <section id="{id_}" class="largura">
{cabeca(sobre, titulo, texto)}
{conteudo}
    </section>'''


# ---------------------------------------------------------------- base/atualizar

ILUSTRA_ATUALIZAR = '''          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ia-t">
            <title id="ia-t">Quatro pacotes ganham a versão nova, um depois do outro, e uma semana de atualizações automáticas vai sendo marcada dia a dia.</title>
            <text x="20" y="26" class="mono t2" font-size="13">sudo apt-get upgrade --with-new-pkgs</text>
            ''' + "".join(
    f'''<g class="pacote" style="--i:{i}">
              <rect x="20" y="{44 + i * 46}" width="440" height="38" rx="10" class="caixa-svg"/>
              <text x="36" y="{68 + i * 46}" font-size="14" font-weight="600" class="mono">{n}</text>
              <rect x="200" y="{59 + i * 46}" width="130" height="8" rx="4" class="caixa-svg"/>
              <rect class="barra-p laranja" x="200" y="{59 + i * 46}" width="130" height="8" rx="4"/>
              <text x="346" y="{68 + i * 46}" font-size="13" class="mono t2 velha">{v}</text>
              <text x="346" y="{68 + i * 46}" font-size="13" class="mono nova" fill="var(--ok)" style="fill:var(--ok)">{nv} ✓</text>
            </g>
            ''' for i, (n, v, nv) in enumerate([("firefox", "132.0", "133.0"), ("openssl", "3.0.13", "3.0.15"), ("linux-image", "6.8.0-45", "6.8.0-48"), ("libc6", "2.39-0.8", "2.39-0.8.3")])) + '''<text x="20" y="252" font-size="14" font-weight="600">Depois, as correções de segurança chegam sozinhas:</text>
            ''' + "".join(
    f'''<g class="dia" style="--i:{i}">
              <rect x="{20 + i * 63}" y="266" width="55" height="62" rx="10" class="caixa-svg"/>
              <text x="{47.5 + i * 63}" y="286" font-size="12.5" text-anchor="middle" class="t2">{d}</text>
              <path class="escudo verde" d="M{47.5 + i * 63} 294l10 4.2v6.6c0 5.7-4.1 10-10 12.7-5.9-2.7-10-7-10-12.7v-6.6z"/>
              <path class="escudo" d="M{42.5 + i * 63} 306l3.5 3.5 6.5-6.5" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            ''' for i, d in enumerate(["seg", "ter", "qua", "qui", "sex", "sáb", "dom"])) + '''
          </svg>'''


def pagina_atualizar():
    rid = "base/atualizar"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_ATUALIZAR, "Ilustração com versões de exemplo. No seu computador, a lista é a dos pacotes que estiverem atrasados.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Atualiza a lista de pacotes</strong> e todos os programas instalados pelo apt.",
         "<strong>Instala dependências novas</strong> que uma atualização pedir, como um kernel novo.",
         "<strong>Termina instalações que ficaram pela metade</strong>, com <code>dpkg --configure -a</code>.",
         "<strong>Liga as atualizações automáticas de segurança</strong>, que passam a ser instaladas sozinhas todo dia.",
         "<strong>Avisa quando é preciso reiniciar</strong> para usar o kernel novo."],
        ["Não remove nenhum pacote. Remoções ficam para você decidir.",
         "Não troca a versão da distro, por exemplo do Ubuntu 24.04 para o 26.04.",
         "Não atualiza aplicativos Flatpak ou Snap; só os pacotes do apt.",
         "Não reinicia o computador por você.",
         "Não volta versões ao desfazer: o apt não sabe fazer isso. Para isso existe o snapshot."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "Toda receita passa pelas mesmas quatro etapas. Esta é a sequência exata, com o que cada uma confere.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Antes de mudar qualquer coisa, o <code>bora</code> pergunta à receita se há algo a fazer. Ela responde que sim se:</p><ul><li>a lista de pacotes não foi atualizada nas últimas 6 horas;</li><li>há pacotes instalados pela metade;</li><li>a simulação <code>apt-get -s upgrade</code> mostra pacotes para atualizar;</li><li>as atualizações automáticas estão desligadas.</li></ul><p>Se nada disso acontece, o <code>bora</code> pula a receita e diz que ela já estava aplicada.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Roda <code>dpkg --configure -a</code> se algo ficou pela metade.</li><li>Roda <code>apt-get update</code> e <code>apt-get upgrade --with-new-pkgs</code>.</li><li>Instala o <code>unattended-upgrades</code>, se ainda não estiver instalado.</li><li>Liga as duas opções em <code>/etc/apt/apt.conf.d/20auto-upgrades</code>, só se elas ainda não estiverem ligadas.</li><li>Habilita os timers <code>apt-daily.timer</code> e <code>apt-daily-upgrade.timer</code>.</li></ul><p>No Ubuntu, quase tudo isso já vem ligado; aí a receita só atualiza os pacotes.</p>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>A receita confere quatro coisas e imprime cada uma: nenhum pacote pela metade, nenhum pacote para atualizar, o <code>unattended-upgrades</code> instalado e as duas opções valendo <code>1</code>. Pacotes retidos de propósito pela distro, como as atualizações em fases do Ubuntu, não contam.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Volta o <code>20auto-upgrades</code> ao que era, desabilita os timers que a receita habilitou e remove o <code>unattended-upgrades</code>, se foi ela que instalou. As versões novas dos pacotes ficam: para voltar a elas, use o snapshot criado antes do plano.</p>"),
    ])))
    corpo.append(f'''    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "Montada com as mensagens reais do bora e da receita, num Ubuntu 26.04. O número de pacotes muda de máquina para máquina.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("cmd", P + '<span class="c">sudo bora plano --receitas base/atualizar</span>'),
        ("", '<span class="v">✓</span> Plano salvo em plano.yaml. Para aplicar: sudo bora aplicar plano.yaml'),
        ("cmd", P + '<span class="c">sudo bora aplicar plano.yaml</span>'),
        ("", ""),
        ("", '<span class="c">Aplicando o plano (20261104-205625)</span>'),
        ("", 'Criando um snapshot do sistema antes de mudar qualquer coisa.'),
        ("", '<span class="v">✓</span> Snapshot criado: timeshift, 2026-11-04 20:56'),
        ("", ""),
        ("", '<span class="c">[1/1] Sistema atualizado</span>'),
        ("", '<span class="bar">  │</span> Atualizando a lista de pacotes.'),
        ("", '<span class="bar">  │</span> <span class="d">Hit:1 http://security.ubuntu.com/ubuntu resolute-security InRelease</span>'),
        ("", '<span class="bar">  │</span> Atualizando 23 pacote(s). Isso pode levar alguns minutos.'),
        ("", '<span class="bar">  │</span> Instalando: unattended-upgrades'),
        ("", '<span class="bar">  │</span> As atualizações automáticas de segurança já estavam ligadas.'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> nenhum pacote instalado pela metade (dpkg --audit)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> nenhum pacote para atualizar (apt-get -s upgrade)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> unattended-upgrades instalado'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> atualizações automáticas ligadas (apt-config dump)'),
        ("", '<span class="bar">  │</span> Tudo conferido.'),
        ("", '<span class="v">✓</span> Sistema atualizado: aplicada e testada'),
        ("", ""),
        ("", '<span class="v">✓</span> Pronto. O plano foi aplicado e cada receita passou no teste.'),
        ("", '  Para voltar atrás: sudo bora desfazer'),
    ], "Terminal mostrando o bora aplicar a receita Sistema atualizado: cria um snapshot, atualiza os pacotes, instala o unattended-upgrades e confere quatro testes, todos ok.")}
      </figure>
    </section>''')
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que atualizar antes de tudo?", "A maioria dos problemas de segurança é corrigida por atualizações que já existem, mas ainda não foram instaladas. E um computador recém-instalado costuma estar semanas atrás, porque a imagem de instalação foi gerada antes."),
        ("Por que <code>--with-new-pkgs</code>?", "O <code>upgrade</code> comum deixa de lado as atualizações que pedem um pacote novo, como um kernel novo. Com essa opção, elas entram. E, diferente do <code>dist-upgrade</code>, ela nunca remove pacotes."),
        ("O que as atualizações automáticas instalam?", "Só o que vem dos repositórios de segurança da distro. Elas não trocam a versão da distro e não instalam programas novos, então o computador não muda de cara de um dia para o outro."),
        ("Por que o desfazer não volta as versões?", "O apt não guarda as versões antigas dos pacotes, e voltar uma versão de segurança deixaria o computador vulnerável de novo. Se uma atualização trouxer problema, o snapshot volta o sistema inteiro."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "Pacotes atualizados", "Todos os que o apt tiver para atualizar, mais as dependências novas. Nenhum é removido."),
        ("pacote", "unattended-upgrades", "Instalado só se ainda não estiver. É ele que instala as atualizações de segurança sozinho."),
        ("arquivo", "/etc/apt/apt.conf.d/20auto-upgrades", "Liga <code>APT::Periodic::Update-Package-Lists</code> e <code>APT::Periodic::Unattended-Upgrade</code>, se ainda não estiverem ligadas."),
        ("relogio", "apt-daily.timer e apt-daily-upgrade.timer", "Os agendamentos do systemd que buscam e instalam as atualizações. Se um estiver mascarado, a receita só avisa."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos que o teste roda", "Rode no terminal para ver com os próprios olhos. Nenhum deles muda nada.", comandos([
        ("dpkg --audit", "Lista pacotes instalados pela metade. Não pode mostrar nada."),
        ("apt-get -s upgrade --with-new-pkgs", "Simula a atualização. Não pode sobrar nenhum pacote para atualizar."),
        ("apt-config dump | grep Periodic", "Mostra as opções das atualizações automáticas. As duas precisam valer \"1\"."),
        ("systemctl list-timers 'apt-daily*'", "Mostra quando as atualizações vão rodar de novo."),
        ("ls /var/run/reboot-required", "Se o arquivo existir, reinicie quando puder para usar o kernel novo."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("Atualizações automáticas", "Documentação do Ubuntu Server", "https://documentation.ubuntu.com/server/how-to/software/automatic-updates/"),
        ("UnattendedUpgrades", "Wiki do Debian", "https://wiki.debian.org/UnattendedUpgrades"),
        ("Manual do apt-get", "A opção --with-new-pkgs", "https://manpages.debian.org/trixie/apt/apt-get.8.en.html"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- sistema/snapshot

def _foto(x, y, r, i, vence, rotulo, cor="azul"):
    return f'''<g class="foto{' vence' if vence else ''}" style="--i:{i}">
              <circle cx="{x}" cy="{y}" r="{r}" class="{cor}"/>
              <rect x="{x - r * 0.5}" y="{y - r * 0.28}" width="{r}" height="{r * 0.66}" rx="{r * 0.12}" fill="none" stroke="#fff" stroke-width="1.8"/>
              <circle cx="{x}" cy="{y + r * 0.05}" r="{r * 0.2}" fill="none" stroke="#fff" stroke-width="1.8"/>
              <text x="{x}" y="{y + r + 17}" font-size="12" text-anchor="middle" class="t2">{rotulo}</text>
            </g>'''


ILUSTRA_SNAPSHOT = '''          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="is-t">
            <title id="is-t">Uma linha do tempo: o Timeshift tira uma foto por dia e uma por semana, apaga as mais velhas para manter 5 diárias e 3 semanais, e no dia em que algo quebra, uma seta volta o sistema para a foto de ontem.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Diários</text><text x="82" y="28" font-size="13" class="t2">guarda os 5 mais novos</text>
            <path d="M20 66H460" class="traco tracejado"/>
            ''' + "".join(_foto(48 + i * 60, 66, 17, i, i < 2, d) for i, d in enumerate(["qua", "qui", "sex", "sáb", "dom", "seg", "ter"])) + '''
            <text x="20" y="136" font-size="14" font-weight="600">Semanais</text><text x="96" y="136" font-size="13" class="t2">guarda os 3 mais novos</text>
            <path d="M20 176H460" class="traco tracejado"/>
            ''' + "".join(_foto(70 + i * 110, 176, 21, 7 + i, i == 0, s, "laranja") for i, s in enumerate(["4 sem.", "3 sem.", "2 sem.", "1 sem."])) + '''
            <g class="volta">
              <rect x="20" y="236" width="440" height="92" rx="14" class="caixa-svg"/>
              <path d="M440 262l-9 16h7l-5 14 14-19h-8l6-11z" class="laranja"/>
              <text x="40" y="266" font-size="14" font-weight="600">Hoje, uma atualização quebrou o som.</text>
              <text x="40" y="290" font-size="13" class="t2">Você volta o sistema para a foto de ontem:</text>
              <text x="40" y="314" font-size="13.5" class="mono" font-weight="600">sudo timeshift --restore</text>
            </g>
            <path class="volta-seta" d="M430 238 C 425 150, 390 112, 356 90" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round"/>
            <path class="volta" d="M354 102l1-13 12 3" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>'''


def pagina_snapshot():
    rid = "sistema/snapshot"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_SNAPSHOT, "Com o padrão de 5 diários e 3 semanais, as fotos mais velhas vão sendo apagadas sozinhas, e o disco não enche.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Instala e configura o Timeshift</strong>, a ferramenta de snapshot que as distros da família Ubuntu e Debian recomendam.",
         "<strong>Guarda uma foto por dia e uma por semana</strong> dos arquivos do sistema, e apaga as mais velhas sozinha.",
         "<strong>Cria o primeiro snapshot</strong> logo depois de configurar.",
         "<strong>Faz o bora tirar uma foto antes de cada plano</strong>, daqui em diante.",
         "<strong>Usa o modo btrfs</strong> quando a raiz é btrfs com o subvolume <code>@</code>, que é instantâneo."],
        ["Não guarda os seus arquivos pessoais: <code>/home</code> e <code>/root</code> ficam de fora de propósito. Para eles, existe o backup da pasta pessoal.",
         "Não copia nada para outro disco, a não ser que você escolha um em <code>dispositivo</code>.",
         "Não serve como backup se o disco do computador morrer, porque as fotos ficam no mesmo disco.",
         "Não roda se houver menos de 10 GB livres: para antes de mudar qualquer coisa.",
         "Não se aplica ao Fedora imutável, que já volta versões do sistema do jeito dele."])))
    dentro_fora = '''      <div class="duas revelar" style="margin-top:20px">
        <div class="cartao"><h3>Entra na foto</h3><p>Os arquivos do sistema: <code>/etc</code> (as configurações), <code>/usr</code> (os programas), <code>/boot</code> (o kernel), <code>/var</code> e o resto da raiz.</p><p>Voltar uma foto desfaz uma atualização com defeito, um driver que não sobe ou uma configuração que deu errado.</p></div>
        <div class="cartao"><h3>Fica de fora</h3><p>As pastas pessoais em <code>/home</code> e a pasta do <code>root</code>.</p><p>Assim, voltar o sistema nunca apaga o trabalho que você fez depois da foto. O outro lado: os seus arquivos precisam de um backup de verdade, em outro disco.</p></div>
      </div>'''
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Confere se o Timeshift está instalado, se o <code>timeshift.json</code> tem o disco, o modo e os agendamentos certos, e se o <code>bora-snapshot.timer</code> está ligado. Se estiver tudo certo, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Descobre onde guardar: com <code>auto</code>, a própria partição do sistema.</li><li>Para, sem mudar nada, se houver menos de 10 GB livres ou se a raiz for btrfs sem o subvolume <code>@</code>.</li><li>Instala o <code>timeshift</code> sem os pacotes recomendados.</li><li>Escreve <code>/etc/timeshift/timeshift.json</code> com o disco, o modo, 5 diários, 3 semanais e o que fica de fora.</li><li>Cria o <code>bora-snapshot.timer</code>, que de hora em hora pergunta ao Timeshift se uma foto venceu.</li><li>Cria o primeiro snapshot. Na primeira vez, o Timeshift copia o sistema inteiro: de 5 a 30 minutos. As seguintes copiam só o que mudou.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere que o programa está instalado, que a configuração está certa, que o <code>timeshift --list</code> consegue montar o disco e listar as fotos, que o agendamento está ligado e que existe pelo menos um snapshot.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Desliga e remove o timer, apaga o snapshot que esta receita criou, volta o <code>timeshift.json</code> ao que era e remove o Timeshift, se foi ela que instalou. Fotos criadas depois ficam guardadas, e a receita diz onde estão, para você decidir.</p>"),
    ]) + "\n" + dentro_fora))
    corpo.append(f'''    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "A saída de um teste no Ubuntu 26.04, encurtada nas linhas do apt e do Timeshift, com o disco de teste trocado por um disco comum.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("cmd", P + '<span class="c">sudo bora aplicar plano.yaml</span>'),
        ("", ""),
        ("", '<span class="c">[2/3] Snapshot do sistema</span>'),
        ("", '<span class="bar">  │</span> Os snapshots vão para /dev/sda2 (ext4, modo rsync).'),
        ("", '<span class="bar">  │</span> Instalando: timeshift'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /etc/timeshift/timeshift.json'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /etc/systemd/system/bora-snapshot.timer'),
        ("", '<span class="bar">  │</span> Criando o primeiro snapshot. Na primeira vez, o Timeshift copia o sistema inteiro e pode levar de 5 a 30 minutos.'),
        ("", '<span class="bar">  │</span> <span class="d">Creating new snapshot...(RSYNC)</span>'),
        ("", '<span class="bar">  │</span> <span class="d">RSYNC Snapshot saved successfully (19s)</span>'),
        ("", '<span class="bar">  │</span> Pronto. O Timeshift vai guardar 5 snapshots diários e 3 semanais.'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> agendamento ligado (bora-snapshot.timer)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> existe pelo menos um snapshot'),
        ("", '<span class="v">✓</span> Snapshot do sistema: aplicada e testada'),
        ("cmd", P + '<span class="c">sudo timeshift --list</span>'),
        ("", '<span class="d">Num     Name                 Tags  Description</span>'),
        ("", '0    &gt;  2026-11-04_20-56-56  O'),
    ], "Terminal mostrando o bora aplicar a receita Snapshot do sistema: instala o Timeshift, escreve a configuração e o timer, cria o primeiro snapshot e confere os testes.")}
      </figure>
    </section>''')
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que snapshot, se cada receita sabe se desfazer?", "Há coisas que nenhuma receita controla: uma atualização com defeito, um driver que não sobe, uma configuração que você mudou na mão. O snapshot é a rede de segurança para esses casos."),
        ("Por que um timer do systemd, e não o cron?", "O Timeshift só agenda pelo cron quando é configurado pelo aplicativo. Como aqui a configuração vai direto no arquivo, o agendamento fica com o systemd, que toda distro suportada já usa."),
        ("Por que sem os pacotes recomendados?", "Num desktop, eles já estão instalados. Num servidor, seriam centenas de pacotes gráficos que o Timeshift não usa para nada."),
        ("Por que 10 GB livres?", "A primeira foto copia o sistema inteiro, e as seguintes precisam de espaço para o que muda. Com menos que isso, o disco pode encher no meio do caminho, o que é pior do que não ter foto."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "timeshift", "Instalado sem os pacotes recomendados, se ainda não estiver."),
        ("arquivo", "/etc/timeshift/timeshift.json", "O UUID do disco, o modo (rsync ou btrfs), 5 diários, 3 semanais e <code>/root/**</code> e <code>/home/*/**</code> de fora."),
        ("relogio", "bora-snapshot.service e bora-snapshot.timer", "Em <code>/etc/systemd/system</code>. De hora em hora, rodam <code>timeshift --check</code>, que só cria uma foto quando uma vence."),
        ("foto", "O primeiro snapshot", "Em <code>/timeshift</code> na partição escolhida. É o único que o desfazer apaga."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos que o teste roda", "E os que você vai usar no dia em que precisar voltar.", comandos([
        ("sudo timeshift --list", "Lista os snapshots guardados, com data e tipo."),
        ("systemctl list-timers bora-snapshot.timer", "Mostra quando o agendamento roda de novo."),
        ("cat /etc/timeshift/timeshift.json", "A configuração que a receita escreveu."),
        ("sudo timeshift --restore", "Volta o sistema para um snapshot. Também dá para usar o aplicativo Timeshift, no menu."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("Timeshift", "Repositório do Linux Mint", "https://github.com/linuxmint/timeshift"),
        ("Manual do systemd.timer", "Como funcionam os agendamentos do systemd", "https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- seguranca/firewall

def _pacote(caminho, cor, atraso, barrado=False, quando=None):
    q = f' data-quando="{quando}"' if quando else ""
    return f'''<g class="pacote-rede{' barrado' if barrado else ''}"{q} style="--d:{atraso}s"><circle r="6.5" class="{cor}" style="offset-path:path('{caminho}')"/></g>'''


ILUSTRA_FIREWALL = '''          <div class="alternar" role="group" aria-label="Perfil do firewall" data-alternar="fw-palco">
            <button type="button" data-mostrar="desktop" aria-pressed="true">desktop</button>
            <button type="button" data-mostrar="servidor-lan" aria-pressed="false">servidor-lan</button>
            <button type="button" data-mostrar="tailscale" aria-pressed="false">tailscale</button>
          </div>
          <div id="fw-palco">
          <svg class="ilustra" viewBox="0 0 480 360" role="img" aria-labelledby="if-t">
            <title id="if-t">O computador no meio, cercado pelo firewall. O que vem da internet é barrado. O que sai do computador passa. O que vem da rede de casa e da VPN passa ou não conforme o perfil escolhido.</title>
            <path d="M200 52a20 20 0 0 1 33-16 24 24 0 0 1 44 7 16 16 0 0 1 4 31h-77a16 16 0 0 1-4-22z" class="caixa-svg" stroke-width="1.5"/>
            <text x="240" y="64" font-size="15" font-weight="600" text-anchor="middle">Internet</text>
            <circle cx="240" cy="185" r="70" fill="none" stroke="var(--accent)" stroke-width="3" stroke-dasharray="10 7" class="gira" style="animation-duration:30s"/>
            <rect x="196" y="156" width="88" height="56" rx="8" class="caixa-svg" stroke-width="2"/>
            <path d="M222 224h36M240 212v12" class="traco"/>
            <text x="240" y="190" font-size="15" font-weight="600" text-anchor="middle">você</text>
            <rect x="34" y="276" width="84" height="52" rx="6" class="caixa-svg" stroke-width="2"/>
            <path d="M22 334h108" class="traco"/>
            <text x="76" y="354" font-size="14" font-weight="600" text-anchor="middle">rede de casa</text>
            <rect x="398" y="268" width="42" height="68" rx="8" class="caixa-svg" stroke-width="2"/>
            <path d="M413 328h12" class="traco"/>
            <text x="419" y="354" font-size="14" font-weight="600" text-anchor="middle">celular na VPN</text>
            <text x="22" y="106" font-size="14" class="t2">chega: barrado</text>
            <text x="276" y="104" font-size="14" class="t2">sai: liberado</text>
            ''' + _pacote("M240 76 L240 112", "vermelho", 0, True) + _pacote("M40 124 C100 132 148 142 178 152", "vermelho", 1.4, True) + _pacote("M266 156 C266 124 266 96 266 78", "verde", 0.7) + _pacote("M118 296 C160 268 182 240 206 214", "verde", 1.9) + _pacote("M398 298 C352 270 312 242 274 214", "verde", 1.1, quando="tailscale") + _pacote("M398 298 C372 280 336 258 300 230", "vermelho", 1.1, True, "desktop servidor-lan") + '''
          </svg>
          <p class="legenda-palco" data-quando="desktop"><strong>desktop:</strong> uso pessoal. Bloqueia tudo o que chega; o SSH da rede de casa só fica liberado se um servidor SSH já estiver ligado.</p>
          <p class="legenda-palco" data-quando="servidor-lan"><strong>servidor-lan:</strong> servidor da casa. Libera o SSH só para a rede de casa, e cada serviço depois libera a própria porta, também só para a casa.</p>
          <p class="legenda-palco" data-quando="tailscale"><strong>tailscale:</strong> como o desktop, e libera o que chega pela interface da VPN, que só recebe conexões dos seus aparelhos.</p>
          </div>'''


def pagina_firewall():
    rid = "seguranca/firewall"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_FIREWALL, "Toque nos perfis para ver o que cada um libera. As bolinhas verdes passam; as vermelhas param no firewall.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Liga o ufw</strong>, o firewall simples do Ubuntu, e o instala no Debian, que não traz nenhum.",
         "<strong>Bloqueia tudo o que chega</strong> e <strong>libera tudo o que sai</strong>: navegar, baixar e atualizar continua igual.",
         "<strong>Libera só o que o perfil pede</strong>, sempre só para a rede de casa ou para a VPN.",
         "<strong>Protege quem está conectado por SSH</strong>: se alguém estiver conectado de fora da rede local, a receita para antes de cortar o acesso.",
         "<strong>Guarda uma cópia</strong> de <code>/etc/ufw</code> antes de mudar qualquer coisa, e mantém as regras que você já tinha."],
        ["Não abre nenhuma porta para a internet, em nenhum perfil.",
         "Não libera redes públicas nem de CGNAT como se fossem a rede de casa: só valem <code>10.0.0.0/8</code>, <code>172.16.0.0/12</code> e <code>192.168.0.0/16</code>.",
         "Não bloqueia o que sai do computador. Não é um filtro de sites nem um antivírus.",
         "Não mexe no firewall do roteador.",
         "Não apaga as regras que você criou antes."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Confere se o ufw está ligado, se a política é bloquear o que chega e liberar o que sai, e se cada regra do perfil já está na lista. Se estiver tudo lá, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Descobre a rede de casa pela interface da rota padrão, e só aceita as faixas privadas.</li><li>Confere quem está conectado por SSH. Se alguma sessão vier de fora da rede de casa (ou de fora da VPN, no perfil <code>tailscale</code>), para sem mudar nada.</li><li>Instala o <code>ufw</code>, se ainda não estiver instalado.</li><li>Guarda uma cópia de <code>/etc/ufw</code> e de <code>/etc/default/ufw</code>.</li><li>Define a política: <code>deny incoming</code> e <code>allow outgoing</code>.</li><li>Adiciona as regras do perfil, cada uma com um comentário que começa com <code>bora-</code>.</li><li>Liga o firewall e habilita o <code>ufw.service</code>, para ele subir sozinho no boot.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere que o <code>ufw status</code> diz <code>active</code>, que a política é <code>deny (incoming), allow (outgoing)</code>, que cada regra do perfil está na lista e que o firewall sobe no boot.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Desliga o firewall. Se foi a receita que instalou o ufw, remove o pacote e as dependências que vieram com ele. Se o ufw já existia, volta <code>/etc/ufw</code> à cópia guardada e deixa o firewall ligado ou desligado, como estava antes.</p>"),
    ])))
    ssh = f'''    <section id="ssh" class="largura">
{cabeca("Proteção do SSH", "Ninguém fica trancado do lado de fora", "Ligar um firewall por SSH é o jeito clássico de perder o acesso a um servidor. Por isso, antes de ligar, a receita olha quem está conectado.")}
      <div class="alternar" role="group" aria-label="De onde vem a sessão SSH" data-alternar="fw-ssh">
        <button type="button" data-mostrar="casa" aria-pressed="true">SSH vindo de casa</button>
        <button type="button" data-mostrar="fora" aria-pressed="false">SSH vindo de fora</button>
      </div>
      <figure id="fw-ssh" style="margin:0">
        <div data-quando="casa">
{janela("bora aplicar · perfil servidor-lan", [
        ("cmd", P + '<span class="c">sudo bora aplicar plano.yaml</span>'),
        ("", '<span class="c">[1/1] Firewall</span>'),
        ("", '<span class="bar">  │</span> Rede local: 192.168.0.0/24'),
        ("", '<span class="bar">  │</span> Instalando: ufw'),
        ("", '<span class="bar">  │</span> Regra adicionada: allow from 192.168.0.0/24 to any port 22 proto tcp comment bora-ssh-rede-local'),
        ("", '<span class="bar">  │</span> Firewall ligado.'),
        ("", '<span class="bar">  │</span> <span class="d">To          Action      From</span>'),
        ("", '<span class="bar">  │</span> <span class="d">22/tcp      ALLOW IN    192.168.0.0/24   # bora-ssh-rede-local</span>'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> firewall ligado (ufw status)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> bloqueia o que chega e libera o que sai (ufw status verbose)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o firewall liga sozinho no boot (ufw.service)'),
        ("", '<span class="v">✓</span> Firewall: aplicada e testada'),
    ], "Terminal: com a sessão SSH vindo da rede de casa, a receita libera a porta 22 só para a rede local e liga o firewall.")}
        </div>
        <div data-quando="fora">
{janela("bora aplicar · perfil desktop", [
        ("cmd", P + '<span class="c">sudo bora aplicar plano.yaml</span>'),
        ("", '<span class="c">[1/1] Firewall</span>'),
        ("", '<span class="bar">  │</span> Rede local: 192.168.0.0/24'),
        ("", '<span class="bar">  │</span> <span class="x">Erro:</span> há uma sessão SSH vinda de 203.0.113.5, fora da rede local; ligar o firewall cortaria o acesso. Conecte-se pela rede local ou use o perfil tailscale.'),
        ("", '<span class="x">✗</span> Firewall: a etapa aplicar falhou (código 1).'),
        ("", '  Para voltar ao estado anterior: sudo bora desfazer'),
        ("", '  Para pedir ajuda a uma IA: bora ajuda'),
    ], "Terminal: com uma sessão SSH vinda de fora da rede local, a receita para antes de ligar o firewall e explica o motivo.")}
        </div>
        <figcaption class="legenda-palco">Saídas de verdade, dos testes automáticos da receita, com o endereço da rede trocado por um de casa.</figcaption>
      </figure>
    </section>'''
    corpo.append(ssh)
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que firewall num computador de casa?", "Muitos programas abrem portas sem avisar: compartilhamento de tela, servidores de desenvolvimento, impressão. Em casa isso passa despercebido; numa rede de café, de faculdade ou de aeroporto, qualquer pessoa conectada consegue tentar falar com essas portas."),
        ("Por que o ufw?", "Ele já vem no Ubuntu, as regras se leem quase como frases e ele conversa com o nftables por baixo. O Debian não traz firewall nenhum, e o ufw é o mais simples de explicar."),
        ("Por que nenhuma porta para a internet?", "Abrir uma porta depende do roteador, do provedor e do CGNAT, e expõe o computador ao mundo inteiro. Para acessar de fora, o caminho do projeto é a VPN."),
        ("Por que guardar <code>/etc/ufw</code> inteiro?", "Porque o ufw guarda as regras em vários arquivos. Com a cópia, o desfazer volta exatamente ao que você tinha, inclusive regras que o bora não conhece."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "ufw", "Instalado só se ainda não estiver, com as dependências que ele pede, como o nftables."),
        ("copia", "Cópia de /etc/ufw e /etc/default/ufw", "Guardada na pasta da execução, em <code>/var/lib/bora</code>, antes de qualquer mudança."),
        ("escudo", "Política e regras", "<code>deny incoming</code>, <code>allow outgoing</code> e as regras do perfil, com comentários <code>bora-ssh-rede-local</code> e <code>bora-tailscale</code>."),
        ("servico", "ufw.service", "Habilitado, para o firewall subir sozinho no boot."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos que o teste roda", "", comandos([
        ("sudo ufw status verbose", "Mostra se o firewall está ligado, a política padrão e as regras."),
        ("sudo ufw show added", "Lista as regras do jeito que foram adicionadas, com os comentários bora-."),
        ("systemctl is-enabled ufw.service", "Precisa dizer enabled: o firewall sobe no boot."),
        ("ss -tlnp", "Mostra quais programas estão esperando conexões, e em que portas. É o que o firewall protege."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("Firewalls", "Documentação do Ubuntu Server", "https://documentation.ubuntu.com/server/how-to/security/firewalls/"),
        ("Uncomplicated Firewall", "Wiki do Debian", "https://wiki.debian.org/Uncomplicated%20Firewall%20%28ufw%29"),
        ("Manual do ufw", "Todas as opções e a sintaxe das regras", "https://manpages.debian.org/trixie/ufw/ufw.8.en.html"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- desktop/codecs

def _linha_troca(i, nome, antes, depois, y0=44, passo=46):
    y = y0 + i * passo
    return f'''<g class="pacote" style="--i:{i}">
              <rect x="20" y="{y}" width="440" height="38" rx="10" class="caixa-svg"/>
              <text x="36" y="{y + 24}" font-size="14" font-weight="600" class="mono">{nome}</text>
              <rect x="190" y="{y + 15}" width="110" height="8" rx="4" class="caixa-svg"/>
              <rect class="barra-p laranja" x="190" y="{y + 15}" width="110" height="8" rx="4"/>
              <text x="316" y="{y + 24}" font-size="13" class="t2 velha">{antes}</text>
              <text x="316" y="{y + 24}" font-size="13" class="nova" style="fill:var(--ok)">{depois} ✓</text>
            </g>
            '''


ILUSTRA_CODECS = '''          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ic-t">
            <title id="ic-t">Quatro arquivos que não tocavam, um vídeo do celular, uma música, um filme e uma aula gravada, passam a tocar um depois do outro, e o player mostra o vídeo rodando.</title>
            <text x="20" y="26" font-size="14" font-weight="600">Antes, o player só mostrava um erro:</text>
            ''' + "".join(_linha_troca(i, n, "não toca", "toca") for i, n in enumerate(["celular.mp4", "musica.mp3", "filme.mkv", "aula.wmv"])) + '''<g class="volta">
              <rect x="20" y="236" width="440" height="92" rx="14" class="caixa-svg"/>
              <rect x="40" y="252" width="100" height="60" rx="8" class="azul"/>
              <path d="M82 270v24l20-12z" fill="#fff"/>
              <text x="160" y="272" font-size="14" font-weight="600">Os players do GNOME, do KDE e do Xfce</text>
              <text x="160" y="296" font-size="13" class="t2">usam o GStreamer: um conjunto de plugins</text>
              <text x="160" y="316" font-size="13" class="t2">resolve todos de uma vez.</text>
            </g>
          </svg>'''


def pagina_codecs():
    rid = "desktop/codecs"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_CODECS, "Os nomes dos arquivos são exemplos. O teste da receita confere os plugins de cada formato.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Instala os plugins do GStreamer</strong> que tocam MP4, MKV, WebM, MP3, WMV e o áudio AC-3 dos filmes.",
         "<strong>Toca os vídeos do celular</strong>, que vêm em H.264 ou H.265, com os decodificadores do FFmpeg.",
         "<strong>Vale para todos os players</strong> que usam o GStreamer, e para o navegador ler os mesmos formatos.",
         "<strong>Usa só os repositórios oficiais</strong> da distro, sem nenhum repositório de fora."],
        ["Não instala nenhum player novo: usa o que veio com o seu ambiente gráfico.",
         "Não instala as fontes da Microsoft, que pedem para aceitar uma licença e são baixadas de fora dos repositórios.",
         "Não troca a <code>libavcodec</code> pela <code>libavcodec-extra</code>, que só acrescenta codificadores e mexe num pacote que outros programas usam.",
         "Não toca DVD com proteção contra cópia nem vídeo de serviços de streaming."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Confere se os quatro pacotes estão instalados: <code>gstreamer1.0-libav</code>, <code>-plugins-good</code>, <code>-plugins-bad</code> e <code>-plugins-ugly</code>. Se estiverem, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Atualiza a lista de pacotes, se ela tiver mais de uma hora.</li><li>Confere se cada pacote existe nos repositórios configurados. No Ubuntu, eles ficam no <code>universe</code>; se ele estiver desligado, a receita para e explica como ligar.</li><li>Instala os quatro pacotes, com as dependências, e anota tudo o que entrou.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere os quatro pacotes e os arquivos dos plugins principais, cada um com o que ele toca: <code>libav</code> (H.264, H.265, AAC), <code>isomp4</code> (MP4), <code>matroska</code> (MKV), <code>mpg123</code> (MP3), <code>videoparsersbad</code> (H.264 dentro do arquivo), <code>asf</code> (WMV) e <code>a52dec</code> (AC-3).</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Remove só o que a receita instalou, com as dependências que vieram junto. Se outro programa passou a precisar de algum desses pacotes, ele fica, e a receita avisa.</p>"),
    ])))
    corpo.append(f'''    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "A saída de um teste no Ubuntu 26.04, encurtada nas linhas do apt.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("", '<span class="c">[4/6] Codecs de áudio e vídeo</span>'),
        ("", '<span class="bar">  │</span> Instalando: gstreamer1.0-libav gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly'),
        ("", '<span class="bar">  │</span> <span class="d">Setting up gstreamer1.0-plugins-ugly:amd64 (1.28.2-1) ...</span>'),
        ("", '<span class="bar">  │</span> Pronto. Feche e abra de novo o player de vídeo ou o navegador para eles verem os codecs novos.'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> H.264, H.265 e AAC (vídeos do celular e da internet) (plugin libav do GStreamer)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> arquivos MP4 e MOV (plugin isomp4 do GStreamer)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> arquivos MKV e WebM (plugin matroska do GStreamer)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> música em MP3 (plugin mpg123 do GStreamer)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> arquivos WMV e WMA (plugin asf do GStreamer)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> áudio AC-3 (Dolby Digital) de filmes e DVDs (plugin a52dec do GStreamer)'),
        ("", '<span class="bar">  │</span> Tudo conferido.'),
        ("", '<span class="v">✓</span> Codecs de áudio e vídeo: aplicada e testada'),
    ], "Terminal mostrando o bora aplicar a receita Codecs de áudio e vídeo: instala os quatro pacotes do GStreamer e confere um plugin para cada formato, todos ok.")}
      </figure>
    </section>''')
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que a distro não traz isso?", "Alguns desses formatos são cobertos por patentes em certos países. As distros deixam os codecs fora da instalação padrão e a escolha para você. No Brasil, usar esses codecs em casa é o comum."),
        ("Por que GStreamer, e não só instalar o VLC?", "O VLC é ótimo e traz os próprios codecs, mas só ele toca. Com os plugins do GStreamer, o player que já veio com o sistema, as miniaturas do gerenciador de arquivos e outros programas passam a entender os mesmos formatos. Se você preferir o VLC, ele está no Flathub."),
        ("Por que não o <code>ubuntu-restricted-extras</code>?", "Ele traz junto as fontes da Microsoft, que param a instalação para pedir que você aceite uma licença e são baixadas de fora dos repositórios. Uma receita não pode parar para perguntar nada no meio."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "gstreamer1.0-libav", "Os decodificadores do FFmpeg: H.264, H.265, AAC e quase tudo o que vem da internet."),
        ("pacote", "gstreamer1.0-plugins-good", "MP4, MKV, WebM, MP3 e FLAC."),
        ("pacote", "gstreamer1.0-plugins-bad", "Os analisadores que separam o vídeo de dentro do arquivo, e formatos menos comuns."),
        ("pacote", "gstreamer1.0-plugins-ugly", "WMV, WMA, AC-3 e DVD sem proteção."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos para conferir", "Nenhum deles muda nada.", comandos([
        ("dpkg -l 'gstreamer1.0-*'", "Lista os pacotes do GStreamer instalados."),
        ("gst-inspect-1.0 avdec_h264", "Mostra o decodificador de H.264. Precisa do pacote <code>gstreamer1.0-tools</code>."),
        ("gst-play-1.0 video.mp4", "Toca um vídeo direto do terminal, pelo GStreamer. Também vem no <code>gstreamer1.0-tools</code>."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("ubuntu-restricted-extras", "O pacote, no arquivo do Ubuntu", "https://packages.ubuntu.com/noble/ubuntu-restricted-extras"),
        ("Multimedia codecs", "Wiki do Debian", "https://wiki.debian.org/MultimediaCodecs"),
        ("Plugins do GStreamer", "A lista oficial, com o que cada um toca", "https://gstreamer.freedesktop.org/documentation/plugins_doc.html"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- desktop/flatpak

ILUSTRA_FLATPAK = '''          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="if-t">
            <title id="if-t">Quatro aplicativos de estudo e trabalho saem da versão congelada da distro para a versão mais nova do Flathub, e cada um roda numa caixa isolada, separada do sistema.</title>
            <text x="20" y="26" font-size="14" font-weight="600">Os mesmos aplicativos, direto do Flathub:</text>
            ''' + "".join(_linha_troca(i, n, "da distro", "a mais nova") for i, n in enumerate(["LibreOffice", "GIMP", "OBS Studio", "Anki"])) + '''<g class="volta">
              <rect x="20" y="236" width="440" height="92" rx="14" class="caixa-svg"/>
              <rect x="40" y="254" width="56" height="56" rx="10" fill="none" stroke="var(--azul)" stroke-width="2.4" stroke-dasharray="5 4"/>
              <rect x="54" y="268" width="28" height="28" rx="6" class="azul"/>
              <text x="116" y="272" font-size="14" font-weight="600">Cada aplicativo roda na própria caixa,</text>
              <text x="116" y="296" font-size="13" class="t2">com as permissões que declarou. Instalar ou</text>
              <text x="116" y="316" font-size="13" class="t2">remover um nunca mexe nos pacotes do sistema.</text>
            </g>
          </svg>'''


def pagina_flatpak():
    rid = "desktop/flatpak"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_FLATPAK, "Ilustração. A receita só liga o Flathub: os aplicativos você escolhe na loja ou no terminal.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Instala o Flatpak</strong>, o formato de aplicativos que funciona igual em qualquer distro.",
         "<strong>Liga o Flathub para o sistema todo</strong>, pelo endereço oficial e com a assinatura de cada aplicativo conferida.",
         "<strong>Põe o Flathub na loja de aplicativos</strong>, se ela for o GNOME Software ou o Discover.",
         "<strong>Respeita o que já existe:</strong> no Linux Mint, que já vem com o Flathub, só confere."],
        ["Não instala nenhum aplicativo: você escolhe na loja ou no terminal.",
         "Não remove o Snap do Ubuntu. O Flatpak entra ao lado.",
         "Não muda a App Center do Ubuntu, que só mostra Snaps.",
         "Não mexe num repositório <code>flathub</code> que alguém já configurou de outro jeito: para e explica.",
         "Não remove o Flathub no desfazer se você já instalou aplicativos por ele."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Confere se o pacote <code>flatpak</code> está instalado, se o <code>flathub</code> aparece em <code>flatpak remotes --system</code> com o endereço oficial e, com <code>integrar_loja</code>, se o plugin da loja está instalado. Se estiver tudo certo, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Instala o <code>flatpak</code> e, se a loja for o GNOME Software ou o Discover, o plugin dela.</li><li>Se já houver um <code>flathub</code> com outro endereço ou desativado, para sem mudar nada.</li><li>Roda <code>flatpak remote-add --system --if-not-exists flathub</code> com o arquivo oficial do Flathub, que traz o endereço e a chave que confere as assinaturas.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere que o Flatpak responde, que o Flathub está configurado com o endereço oficial e sem <code>no-gpg-verify</code>, que o <code>/etc/profile.d/flatpak.sh</code> existe (é ele que põe os aplicativos no menu a cada login) e que o plugin da loja está instalado.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Remove o Flathub, se foi a receita que o ligou, e os pacotes que ela instalou. Se você já instalou aplicativos pelo Flathub, nada sai: a receita avisa quais são e explica como tirar tudo à mão.</p>"),
    ])))
    corpo.append(f'''    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "A saída de um teste no Ubuntu 26.04, encurtada nas linhas do apt, e o primeiro aplicativo instalado depois.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("", '<span class="c">[5/6] Flatpak e Flathub</span>'),
        ("", '<span class="bar">  │</span> Instalando: flatpak'),
        ("", '<span class="bar">  │</span> <span class="d">Setting up flatpak (1.16.6-1) ...</span>'),
        ("", '<span class="bar">  │</span> Ligando o Flathub.'),
        ("", '<span class="bar">  │</span> Pronto. Os atalhos dos aplicativos do Flathub aparecem no menu depois que você sair e entrar de novo na sessão.'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> Flatpak instalado (flatpak --version)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> Flathub configurado para o sistema todo (flatpak remotes)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o Flathub confere a assinatura dos aplicativos'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> os aplicativos aparecem no menu depois do login'),
        ("", '<span class="bar">  │</span> Tudo conferido.'),
        ("", '<span class="v">✓</span> Flatpak e Flathub: aplicada e testada'),
        ("cmd", P + '<span class="c">flatpak install flathub org.libreoffice.LibreOffice</span>'),
    ], "Terminal mostrando o bora aplicar a receita Flatpak e Flathub: instala o Flatpak, liga o Flathub e confere quatro testes, todos ok. Depois, um comando instala o LibreOffice pelo Flathub.")}
      </figure>
    </section>''')
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que Flatpak, se a distro já tem os programas?", "Os pacotes da distro ficam congelados na versão em que ela saiu. Num Ubuntu LTS ou num Debian, isso pode ser um, dois ou três anos de atraso. No Flathub, muitos aplicativos são publicados pelos próprios autores, na versão mais nova."),
        ("Por que para o sistema todo, e não só para você?", "Com <code>--system</code>, os aplicativos ficam em <code>/var/lib/flatpak</code> e servem para todas as pessoas do computador, sem baixar tudo de novo para cada uma."),
        ("E o Snap do Ubuntu?", "Fica. O Snap e o Flatpak convivem, e a receita não tira nada do sistema. Remover o Snap é uma decisão maior, com outras consequências, e merece uma receita própria."),
        ("É seguro?", "O Flathub confere a assinatura de cada aplicativo baixado, e cada um roda isolado, com as permissões que declarou. Na página de cada aplicativo, o Flathub mostra quem publicou e quais permissões ele pede."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "flatpak", "Instalado se ainda não estiver, com as dependências."),
        ("pacote", "gnome-software-plugin-flatpak ou plasma-discover-backend-flatpak", "Só se a loja correspondente estiver instalada e <code>integrar_loja</code> for sim."),
        ("arquivo", "O repositório flathub", "Em <code>/var/lib/flatpak/repo</code>, com o endereço <code>https://dl.flathub.org/repo/</code> e a chave pública do Flathub."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos que o teste roda", "E os que você vai usar no dia a dia.", comandos([
        ("flatpak remotes --show-details", "Lista os repositórios do Flatpak, com o endereço de cada um."),
        ("flatpak search anki", "Procura um aplicativo no Flathub."),
        ("flatpak install flathub org.libreoffice.LibreOffice", "Instala um aplicativo. O nome completo aparece na página dele no Flathub."),
        ("flatpak update", "Atualiza todos os aplicativos do Flatpak."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("Configurar o Flathub no Ubuntu", "Flathub", "https://flathub.org/setup/Ubuntu"),
        ("Configurar o Flathub no Debian", "Flathub", "https://flathub.org/setup/Debian"),
        ("flatpak remote-add", "Documentação do Flatpak", "https://docs.flatpak.org/en/latest/flatpak-command-reference.html#flatpak-remote-add"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- sistema/backup-pessoal

ILUSTRA_BACKUP = '''          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ib-t">
            <title id="ib-t">Uma linha do tempo de cópias da pasta pessoal num disco externo: uma por dia, guardando as 7 mais novas e apagando a mais velha, e no dia em que um trabalho é apagado sem querer, uma seta busca a cópia de ontem no disco.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Uma cópia por dia</text><text x="148" y="28" font-size="13" class="t2">guarda as 7 mais novas</text>
            <path d="M20 70H460" class="traco tracejado"/>
            ''' + "".join(_foto(42 + i * 56, 70, 16, i, i == 0, d, "laranja") for i, d in enumerate(["ter", "qua", "qui", "sex", "sáb", "dom", "seg", "ter"])) + '''
            <rect x="20" y="128" width="440" height="80" rx="14" class="caixa-svg"/>
            <rect x="40" y="146" width="44" height="44" rx="8" class="azul"/>
            <circle cx="62" cy="168" r="9" fill="none" stroke="#fff" stroke-width="2"/>
            <text x="100" y="164" font-size="14" font-weight="600">O disco externo guarda as cópias</text>
            <text x="100" y="188" font-size="13" class="t2">O que não mudou não ocupa espaço de novo.</text>
            <g class="volta">
              <rect x="20" y="236" width="440" height="92" rx="14" class="caixa-svg"/>
              <text x="40" y="266" font-size="14" font-weight="600">Hoje, o trabalho de história sumiu.</text>
              <text x="40" y="290" font-size="13" class="t2">Conecte o disco e copie de volta, da cópia de ontem:</text>
              <text x="40" y="314" font-size="13" class="mono" font-weight="600">bora-backup/…/você/2026-11-09_…/</text>
            </g>
            <path class="volta-seta" d="M430 238 C 430 160, 420 120, 400 92" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round"/>
            <path class="volta" d="M394 104l5-13 11 6" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>'''


def pagina_backup():
    rid = "sistema/backup-pessoal"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_BACKUP, "Com o padrão de 7 versões, a cópia mais velha é apagada sozinha a cada cópia nova, e o disco não enche.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Copia a pasta pessoal</strong> de cada pessoa do computador para um disco externo.",
         "<strong>Uma vez por dia e logo que o disco é conectado</strong>, sem você lembrar.",
         "<strong>Guarda as últimas versões</strong> (7, por padrão), para buscar um arquivo como ele estava há alguns dias.",
         "<strong>Cada cópia é uma pasta comum</strong>, que abre em qualquer computador com Linux, sem programa especial.",
         "<strong>Não repete o que não mudou:</strong> as versões compartilham os arquivos iguais, então sete costumam ocupar pouco mais do que uma."],
        ["Não formata disco nenhum. O disco precisa estar em ext4, xfs ou btrfs; em exFAT, NTFS ou FAT, a receita para e explica.",
         "Não manda nada para a nuvem: a cópia fica num disco seu.",
         "Não criptografa a cópia. Guarde o disco num lugar seguro, ou use um disco criptografado.",
         "Não copia o sistema: para isso existe o snapshot.",
         "Não apaga as cópias do disco quando você desfaz: são os seus arquivos."])))
    onde = '''      <div class="duas revelar" style="margin-top:20px">
        <div class="cartao"><h3>Onde ficam as cópias</h3><p>Em <code>bora-backup/&lt;computador&gt;/&lt;pessoa&gt;/</code> no disco externo, uma pasta por data, e um atalho <code>ultimo</code> para a mais nova.</p><p>Cada pessoa só consegue abrir a própria pasta.</p></div>
        <div class="cartao"><h3>Fica de fora</h3><p>O <code>.cache</code>, a lixeira e os caches dos aplicativos Flatpak e Snap, que os programas refazem sozinhos.</p><p>Discos e pastas montados dentro da pasta pessoal também ficam de fora.</p></div>
      </div>'''
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Confere se o <code>rsync</code> está instalado, se a configuração aponta para o disco e as pessoas do plano, se o programa e as unidades do systemd estão no lugar e ligados e, com o disco conectado, se cada pessoa já tem uma cópia completa. Se estiver tudo certo, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Descobre o disco: com <code>auto</code>, o único disco USB conectado com um sistema de arquivos do Linux.</li><li>Para, sem mudar nada, se não houver disco, se houver mais de um, se ele estiver em exFAT, NTFS ou FAT, ou se for a partição do próprio sistema.</li><li>Instala o <code>rsync</code>.</li><li>Escreve <code>/etc/bora/backup-pessoal.conf</code> e o programa <code>/usr/local/lib/bora/backup-pessoal</code>.</li><li>Cria o timer que roda de hora em hora e só copia se a última cópia tiver mais de 20 horas, e a unidade que roda quando o disco é conectado.</li><li>Faz a primeira cópia. Ela copia tudo e pode demorar; as seguintes copiam só o que mudou.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere o <code>rsync</code>, o programa e a configuração, os dois gatilhos ligados e, com o disco conectado, que cada pessoa tem uma cópia completa. Para isso, monta o disco só para leitura, se ele não estiver montado.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Desliga e remove as unidades do systemd, apaga a configuração e o programa e remove o <code>rsync</code>, se foi a receita que o instalou. As cópias no disco externo continuam lá, e a receita diz onde.</p>"),
    ]) + "\n" + onde))
    corpo.append(f'''    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "A saída de um teste no Ubuntu 26.04, com o disco de teste trocado por um disco USB comum.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("", '<span class="c">[6/6] Backup da pasta pessoal</span>'),
        ("", '<span class="bar">  │</span> As cópias vão para /dev/sdb1 (ext4, UUID 737d257f-b139-4c78-bb36-94917984426d).'),
        ("", '<span class="bar">  │</span> Pastas pessoais copiadas: ana'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /etc/bora/backup-pessoal.conf'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /usr/local/lib/bora/backup-pessoal'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /etc/systemd/system/bora-backup-pessoal.timer'),
        ("", '<span class="bar">  │</span> Fazendo a primeira cópia. Ela copia tudo e pode demorar; as próximas copiam só o que mudou.'),
        ("", '<span class="bar">  │</span> ana: copiando /home/ana para /media/ana/BACKUP/bora-backup/notebook/ana/2026-11-05_012104'),
        ("", '<span class="bar">  │</span> ana: pronto. 1 cópia(s) guardada(s).'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> agendamento diário ligado (bora-backup-pessoal.timer)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> backup ao conectar o disco ligado (bora-backup-pessoal-conectar.service)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> ana tem 1 cópia(s), a última em 2026-11-05_012104'),
        ("", '<span class="v">✓</span> Backup da pasta pessoal: aplicada e testada'),
    ], "Terminal mostrando o bora aplicar a receita Backup da pasta pessoal: escolhe o disco USB, instala o programa e os agendamentos, faz a primeira cópia e confere os testes.")}
      </figure>
    </section>''')
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que backup, se já tem snapshot?", "O snapshot fica no mesmo disco do computador e deixa as pastas pessoais de fora de propósito. Se o disco morrer, o notebook for roubado ou um arquivo for apagado sem querer, só uma cópia em outro disco salva o trabalho."),
        ("Por que uma pasta comum, e não um arquivo de backup?", "Para recuperar um arquivo sem aprender programa nenhum: conecte o disco, abra a pasta da data e copie. E a cópia abre em qualquer computador com Linux, mesmo sem o <code>bora</code>."),
        ("Por que exigir ext4?", "As versões compartilham os arquivos que não mudaram por hardlinks, e guardam o dono e as permissões de cada arquivo. exFAT, NTFS e FAT não guardam isso, e sete versões ocupariam sete vezes o espaço. Formatar apagaria o que está no disco, então o <code>bora</code> nunca faz isso por você."),
        ("Por que rodar ao conectar o disco?", "Num notebook, o disco externo quase nunca está conectado na hora marcada. Rodando ao conectar, basta plugar o disco de vez em quando para a cópia acontecer."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "rsync", "Instalado se ainda não estiver. É ele que copia só o que mudou."),
        ("arquivo", "/etc/bora/backup-pessoal.conf", "O UUID do disco, o nome do computador, as pessoas copiadas e quantas versões manter."),
        ("arquivo", "/usr/local/lib/bora/backup-pessoal", "O programa do backup. Também dá para rodar na mão, com <code>--agora</code>."),
        ("relogio", "bora-backup-pessoal.timer", "De hora em hora, copia se o disco estiver conectado e a última cópia tiver mais de 20 horas."),
        ("servico", "bora-backup-pessoal-conectar.service", "Roda quando o disco é conectado, depois de esperar a sessão gráfica montá-lo."),
        ("copia", "As cópias", "No disco externo, em <code>bora-backup/</code>. O desfazer não apaga."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos para conferir", "E os que você vai usar no dia em que precisar de um arquivo de volta.", comandos([
        ("systemctl list-timers bora-backup-pessoal.timer", "Mostra quando o backup confere de novo se a cópia venceu."),
        ("journalctl -u bora-backup-pessoal -u bora-backup-pessoal-conectar", "Mostra o que aconteceu nas últimas cópias."),
        ("sudo /usr/local/lib/bora/backup-pessoal --agora", "Faz uma cópia na hora, com o disco conectado."),
        ("sudo /usr/local/lib/bora/backup-pessoal --conferir", "Confere se cada pessoa tem uma cópia completa, sem copiar nada."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("Manual do rsync", "As opções --link-dest e --one-file-system", "https://download.samba.org/pub/rsync/rsync.1"),
        ("Manual do systemd.device", "Unidades que rodam quando um disco aparece", "https://www.freedesktop.org/software/systemd/man/latest/systemd.device.html"),
        ("BackupAndRecovery", "Wiki do Debian", "https://wiki.debian.org/BackupAndRecovery"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)



# ---------------------------------------------------------------- sistema/zram

ILUSTRA_ZRAM = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="iz-t">
            <title id="iz-t">Duas barras de memória. Sem zram, a memória enche e o que sobra vai para o disco rígido, que é lento. Com zram, as páginas paradas ficam comprimidas na própria memória, ocupando um terço do espaço, e sobra lugar para mais abas.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Sem zram</text><text x="94" y="28" font-size="13" class="t2">a memória enche e vai para o disco</text>
            <rect x="20" y="42" width="300" height="44" rx="10" class="caixa-svg"/>
            """ + "".join(f'<rect x="{26 + i * 49}" y="48" width="43" height="32" rx="6" class="laranja" style="opacity:{0.55 + 0.07 * i}"/>' for i in range(6)) + """
            <path d="M330 64h44" class="traco"/><path d="M366 58l8 6-8 6" class="traco"/>
            <rect x="384" y="42" width="76" height="44" rx="10" class="vermelho" style="opacity:.85"/>
            <text x="422" y="69" font-size="12.5" font-weight="600" text-anchor="middle" style="fill:#fff">disco</text>
            <text x="20" y="108" font-size="13" class="t2">O disco rígido é centenas de vezes mais lento que a memória: tudo trava.</text>
            <text x="20" y="160" font-size="14" font-weight="600">Com zram</text><text x="96" y="160" font-size="13" class="t2">o que está parado fica comprimido</text>
            <g class="pacote" style="--i:0">
              <rect x="20" y="174" width="300" height="44" rx="10" class="caixa-svg"/>
              """ + "".join(f'<rect x="{26 + i * 49}" y="180" width="43" height="32" rx="6" class="laranja" style="opacity:{0.55 + 0.07 * i}"/>' for i in range(3)) + """
              """ + "".join(f'<rect x="{173 + i * 17}" y="180" width="13" height="32" rx="4" class="azul"/>' for i in range(3)) + """
              <text x="290" y="201" font-size="12.5" text-anchor="middle" class="t2">livre</text>
            </g>
            <text x="20" y="242" font-size="13" class="t2">As barras azuis são as mesmas páginas, comprimidas com zstd a um terço.</text>
            <g class="volta">
              <rect x="20" y="262" width="440" height="66" rx="14" class="caixa-svg"/>
              <text x="40" y="290" font-size="14" font-weight="600">A swap no disco continua lá, como reserva.</text>
              <text x="40" y="312" font-size="13" class="t2">O kernel só usa ela quando o zram enche.</text>
            </g>
          </svg>"""


def pagina_zram():
    rid = "sistema/zram"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_ZRAM, "Ilustração. A compressão real depende do que está na memória; um terço é o comum com zstd.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Liga uma swap comprimida na memória</strong>, o zram, com até metade da memória e no máximo 8 GB.",
         "<strong>Comprime com zstd</strong>, que costuma reduzir as páginas a um terço do tamanho.",
         "<strong>Passa na frente da swap no disco</strong>, com prioridade 100: o disco só é usado quando o zram enche.",
         "<strong>Ajusta o kernel para o zram</strong>, como o Fedora e o Pop!_OS já fazem.",
         "<strong>Liga na hora</strong>, sem precisar reiniciar, e a cada boot."],
        ["Não apaga a swap que já existe no disco.",
         "Não mexe num zram que já existia, do <code>zram-tools</code>, do <code>zram-config</code> ou de outra configuração: só confere.",
         "Não reserva memória: o zram começa vazio e só cresce quando a memória aperta.",
         "Não faz milagre com 1 GB: abaixo de 2 GB, até o ambiente leve aperta."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Se o computador já tem zram configurado por outro programa, a receita diz qual e não mexe em nada. Senão, confere se o <code>systemd-zram-generator</code> está instalado, se os dois arquivos de configuração estão como a receita escreve e se o <code>/dev/zram0</code> está ligado como swap.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Se o kernel não traz o módulo do zram, como no Ubuntu Server e nas imagens de nuvem, instala os módulos extras do kernel (<code>linux-modules-extra</code>). Em servidor e em nuvem, eles puxam o <code>linux-firmware</code>, com centenas de MB; o LEIAME da receita explica como evitar.</li><li>Instala o <code>systemd-zram-generator</code>, que cria o zram a cada boot.</li><li>Escreve <code>/etc/systemd/zram-generator.conf</code>, com o tamanho, o zstd e a prioridade.</li><li>Guarda os valores de agora dos ajustes do kernel e escreve <code>/etc/sysctl.d/99-bora-zram.conf</code>.</li><li>Liga o zram e aplica os ajustes, sem reiniciar.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere o gerador, os dois arquivos, e que o <code>/dev/zram0</code> aparece em <code>/proc/swaps</code> com prioridade 100 e comprimindo com zstd.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Desliga o zram (o que estava nele volta para a memória), apaga os dois arquivos, volta os ajustes do kernel aos valores de antes e remove o pacote, se foi a receita que o instalou. Se faltar memória para desligar na hora, o zram sai no próximo reinício.</p>"),
    ])))
    corpo.append(f"""    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "Montada com as mensagens da receita numa máquina com systemd, encurtada nas linhas do apt. A saída do zramctl é um exemplo, de uma máquina com 4 GB.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("", '<span class="c">[3/6] Memória comprimida (zram)</span>'),
        ("", '<span class="bar">  │</span> Instalando: systemd-zram-generator'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /etc/systemd/zram-generator.conf'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /etc/sysctl.d/99-bora-zram.conf'),
        ("", '<span class="bar">  │</span> Ligando o zram.'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> gerador do zram instalado (systemd-zram-generator)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> configuração do zram (/etc/systemd/zram-generator.conf)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> ajustes do kernel para o zram (/etc/sysctl.d/99-bora-zram.conf)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> zram ligado como swap (swapon --show)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o zram comprime com zstd (zramctl)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o kernel usa o zram antes da swap no disco (prioridade 100)'),
        ("", '<span class="bar">  │</span> Tudo conferido.'),
        ("", '<span class="v">✓</span> Memória comprimida (zram): aplicada e testada'),
        ("cmd", P + '<span class="c">zramctl</span>'),
        ("", 'NAME       ALGORITHM DISKSIZE  DATA  COMPR TOTAL STREAMS MOUNTPOINT'),
        ("", '/dev/zram0 zstd           1.9G  612M  187M  196M       2 [SWAP]'),
    ], "Terminal mostrando o bora aplicar a receita Memória comprimida: instala o gerador do zram, escreve a configuração, liga o zram e confere seis testes. Depois, o zramctl mostra 612 MB de memória guardados em 196 MB.")}
      </figure>
    </section>""")
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que zram, e não mais swap no disco?", "Num disco rígido, ler e gravar uma página leva milissegundos; comprimir e descomprimir na memória leva microssegundos. É a diferença entre o mouse travar e a máquina seguir respondendo."),
        ("Por que metade da memória?", "É o tamanho máximo, e não o que o zram ocupa de saída. Com a compressão de um terço, metade da memória em zram guarda páginas que ocupariam 1,5 vez a memória inteira. É o padrão do Debian e perto do que o Fedora usa."),
        ("O que são os ajustes do kernel?", "Por padrão, o kernel evita trocar, pensando num disco lento. Com o zram, trocar é barato, então <code>vm.swappiness = 180</code> deixa o kernel comprimir cedo, antes de a memória ficar apertada, e <code>vm.page-cluster = 0</code> faz ele ler uma página por vez, em vez de oito."),
        ("E se a distro já tiver zram?", "O Pop!_OS e algumas outras já ligam zram. A receita encontra a configuração que existe, diz de onde ela vem e não mexe em nada."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "systemd-zram-generator", "Instalado se ainda não estiver. Cria o <code>/dev/zram0</code> a cada boot."),
        ("arquivo", "/etc/systemd/zram-generator.conf", "Tamanho de até 50% da memória (no máximo 8 GB), zstd e prioridade 100."),
        ("arquivo", "/etc/sysctl.d/99-bora-zram.conf", "<code>vm.swappiness</code>, <code>vm.watermark_boost_factor</code>, <code>vm.watermark_scale_factor</code> e <code>vm.page-cluster</code>."),
        ("servico", "systemd-zram-setup@zram0.service e dev-zram0.swap", "As unidades que o gerador cria: uma prepara o zram, a outra liga como swap."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos para conferir", "", comandos([
        ("zramctl", "Mostra o tamanho do zram, quanto ele guarda (DATA) e quanto isso ocupa comprimido (TOTAL)."),
        ("swapon --show", "Lista as swaps com a prioridade de cada uma: o zram com 100, o disco abaixo."),
        ("free -h", "A linha Swap soma o zram e a swap no disco."),
        ("bora diag", "Mostra a memória comprimida ligada, e se o disco do sistema é SSD ou disco rígido."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("zram-generator.conf(5)", "As opções do gerador do systemd", "https://github.com/systemd/zram-generator/blob/main/man/zram-generator.conf.md"),
        ("Zram", "ArchWiki, com os ajustes do kernel", "https://wiki.archlinux.org/title/Zram"),
        ("zram", "Documentação do kernel", "https://docs.kernel.org/admin-guide/blockdev/zram.html"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- desktop/ambiente-leve

def _janela_svg(x, nome, memoria, cor, barra_y):
    return f"""<g>
              <rect x="{x}" y="44" width="210" height="150" rx="12" class="caixa-svg"/>
              <rect x="{x}" y="{barra_y}" width="210" height="22" rx="0" class="{cor}" style="opacity:.9"/>
              <rect x="{x + 16}" y="{70 if barra_y > 100 else 84}" width="90" height="56" rx="6" class="fundo" stroke="var(--line)"/>
              <rect x="{x + 116}" y="{70 if barra_y > 100 else 84}" width="78" height="40" rx="6" class="fundo" stroke="var(--line)"/>
              <text x="{x + 105}" y="222" font-size="14" font-weight="600" text-anchor="middle">{nome}</text>
              <text x="{x + 105}" y="242" font-size="13" text-anchor="middle" class="t2">{memoria}</text>
            </g>"""


ILUSTRA_AMBIENTE = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="iam-t">
            <title id="iam-t">Duas áreas de trabalho lado a lado: a de antes, que gasta uns 1,5 GB de memória, e o Xfce, que gasta uns 500 MB. Embaixo, a tela de login mostra as duas opções de sessão, e a pessoa escolhe qual abrir.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Os dois ficam instalados, lado a lado</text>
            """ + _janela_svg(20, "O ambiente de antes", "uns 1,5 GB de memória", "azul", 44) + """
            """ + _janela_svg(250, "Xfce ou LXQt", "de 400 a 600 MB", "laranja", 172) + """
            <g class="volta">
              <rect x="20" y="262" width="440" height="66" rx="14" class="caixa-svg"/>
              <text x="40" y="288" font-size="14" font-weight="600">Na tela de login, você escolhe:</text>
              <rect x="40" y="298" width="120" height="22" rx="11" class="fundo" stroke="var(--line)"/>
              <text x="100" y="314" font-size="12.5" text-anchor="middle">Ubuntu</text>
              <rect x="170" y="298" width="120" height="22" rx="11" class="laranja"/>
              <text x="230" y="314" font-size="12.5" text-anchor="middle" font-weight="600" style="fill:#fff">Xfce Session</text>
            </g>
          </svg>"""


def pagina_ambiente():
    rid = "desktop/ambiente-leve"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_AMBIENTE, "Ilustração. O consumo de memória é aproximado e muda com os programas abertos.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Instala o Xfce ou o LXQt</strong>, os ambientes leves mais usados, dos repositórios oficiais.",
         "<strong>Fica ao lado do ambiente atual</strong>: você escolhe qual abrir na tela de login.",
         "<strong>Traz o essencial para o dia a dia</strong>: terminal, notificações, bateria, bloqueio de tela, a rede Wi-Fi e a janela que pede a senha de administrador.",
         "<strong>Pode virar o padrão</strong>, com <code>entrar_no_leve</code>, para cada pessoa do computador."],
        ["Não remove o ambiente que você já tem, nem os seus programas e configurações.",
         "Não troca a tela de login: instala sem os pacotes recomendados, que trariam outra.",
         "Não instala jogos, protetores de tela e programas que você não pediu.",
         "Não desfaz com você dentro do ambiente leve: pede para sair dessa sessão primeiro."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Confere se cada pacote do ambiente escolhido está instalado e, com <code>entrar_no_leve</code>, se cada pessoa já entra nele por padrão. Se estiver tudo certo, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Instala os pacotes do ambiente com <code>--no-install-recommends</code>.</li><li>Instala o Xorg, se o computador não tiver, e o applet de rede, se ele usar o NetworkManager.</li><li>Com <code>entrar_no_leve</code>, grava a sessão de cada pessoa em <code>/var/lib/AccountsService/users</code>, guardando antes uma cópia.</li><li>Explica como escolher o ambiente na tela de login.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere os pacotes, o arquivo que põe o ambiente na tela de login (<code>/usr/share/xsessions/xfce.desktop</code> ou <code>lxqt.desktop</code>), o programa que abre a sessão e o Xorg e, com <code>entrar_no_leve</code>, a sessão gravada de cada pessoa.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Volta os arquivos do AccountsService ao que eram e remove os pacotes que a receita instalou, com as dependências que vieram junto. Se alguém estiver dentro do ambiente leve, para antes de mudar qualquer coisa.</p>"),
    ])))
    corpo.append(f"""    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "A saída de um teste no Ubuntu 26.04, com o Xfce e <code>entrar_no_leve: sim</code>, encurtada nas linhas do apt.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("", '<span class="c">[4/6] Ambiente gráfico leve</span>'),
        ("", '<span class="bar">  │</span> Instalando: xfce4 xfce4-terminal xfce4-notifyd xfce4-power-manager xfce4-screensaver mate-polkit tango-icon-theme network-manager-applet'),
        ("", '<span class="bar">  │</span> <span class="d">0 upgraded, 265 newly installed, 0 to remove and 0 not upgraded.</span>'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /var/lib/AccountsService/users/ana'),
        ("", '<span class="bar">  │</span> ana passa a entrar no Xfce por padrão.'),
        ("", '<span class="bar">  │</span> Pronto. Na próxima vez que você entrar, o Xfce abre direto. O ambiente antigo continua na tela de login.'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> pacote xfce4 instalado'),
        ("", '<span class="bar">  │</span> <span class="d">…</span>'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o Xfce aparece na tela de login (/usr/share/xsessions/xfce.desktop)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o programa que abre a sessão existe (startxfce4)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> servidor gráfico instalado (Xorg)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> ana entra no Xfce por padrão (/var/lib/AccountsService/users/ana)'),
        ("", '<span class="bar">  │</span> Tudo conferido.'),
        ("", '<span class="v">✓</span> Ambiente gráfico leve: aplicada e testada'),
    ], "Terminal mostrando o bora aplicar a receita Ambiente gráfico leve: instala o Xfce, faz ele abrir por padrão para a pessoa do computador e confere os testes.")}
      </figure>
    </section>""")
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Xfce ou LXQt?", "O Xfce é o mais completo dos leves, com o jeito de sempre: menu, barra de tarefas e ícones na área de trabalho. É o padrão. O LXQt gasta ainda menos, e é a escolha para 2 GB de memória ou menos."),
        ("Por que ao lado, e não no lugar?", "Para testar sem perder nada. Se não gostar, escolha o antigo na tela de login. Os seus arquivos e programas são os mesmos nos dois."),
        ("Por que sem os recomendados?", "Junto com o Xfce, o apt recomenda outra tela de login, o LightDM, que trocaria a que você já tem e mudaria o jeito de entrar no computador. Também viriam programas que pesam. A receita escolhe à mão o que faz falta."),
        ("E o Wayland?", "O Xfce e o LXQt rodam no Xorg, que é o que funciona melhor com placas de vídeo antigas. Se o computador veio só com Wayland, a receita instala o Xorg junto."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("pacote", "xfce4 e companhia, ou lxqt-core e companhia", "O ambiente, o terminal, as notificações, a bateria, o bloqueio de tela e a janela da senha de administrador."),
        ("pacote", "xserver-xorg e network-manager-applet", "Só se faltarem: o Xorg, e o applet para escolher a rede Wi-Fi."),
        ("arquivo", "/var/lib/AccountsService/users/&lt;pessoa&gt;", "Só com <code>entrar_no_leve</code>: a sessão que abre por padrão. O GDM e o LightDM leem daqui."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos para conferir", "", comandos([
        ("ls /usr/share/xsessions", "Lista as sessões que aparecem na tela de login."),
        ("sudo cat /var/lib/AccountsService/users/$USER", "Mostra a sessão que abre por padrão para você."),
        ("free -h", "Abra no ambiente antigo e no leve, com os mesmos programas, e compare a memória usada."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("Xfce", "Wiki do Debian", "https://wiki.debian.org/Xfce"),
        ("LXQt", "Wiki do Debian", "https://wiki.debian.org/LXQt"),
        ("Documentação do Xfce", "docs.xfce.org", "https://docs.xfce.org/"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- desktop/navegador-leve

ILUSTRA_NAVEGADOR = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="in-t">
            <title id="in-t">Quatro coisas que pesam no Firefox de uma máquina antiga mudam, uma depois da outra: os anúncios passam a ser bloqueados, as abas paradas saem da memória quando ela acaba, a sessão é gravada no disco a cada minuto em vez de a cada 15 segundos, e a telemetria é desligada.</title>
            <text x="20" y="26" font-size="14" font-weight="600">O mesmo Firefox, com menos peso:</text>
            """ + "".join(_linha_troca(i, n, a, d) for i, (n, a, d) in enumerate([("anúncios", "carregam", "bloqueados"), ("abas paradas", "na memória", "descarregam"), ("sessão no disco", "a cada 15 s", "a cada 60 s"), ("telemetria", "ligada", "desligada")])) + """<g class="volta">
              <rect x="20" y="236" width="440" height="92" rx="14" class="caixa-svg"/>
              <rect x="40" y="254" width="56" height="56" rx="12" class="vermelho"/>
              <path d="M68 266l14 6v8c0 8-6 13-14 17-8-4-14-9-14-17v-8z" fill="#fff"/>
              <text x="114" y="276" font-size="14" font-weight="600">uBlock Origin</text>
              <text x="114" y="298" font-size="13" class="t2">Baixado da loja da Mozilla na primeira vez</text>
              <text x="114" y="316" font-size="13" class="t2">que o Firefox abrir, e atualizado sozinho.</text>
            </g>
          </svg>"""


def pagina_navegador():
    rid = "desktop/navegador-leve"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_NAVEGADOR, "Ilustração. As mudanças valem para o Firefox da distro, inclusive o Snap do Ubuntu.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Instala o uBlock Origin</strong>, o bloqueador de anúncios mais usado, pela loja oficial da Mozilla.",
         "<strong>Tira da memória as abas paradas</strong> quando ela acaba. Elas recarregam quando você clica.",
         "<strong>Abre mais rápido</strong>: as abas da última vez só carregam quando você clica nelas.",
         "<strong>Grava menos no disco</strong>: a sessão é salva a cada minuto, e não a cada 15 segundos.",
         "<strong>Desliga a telemetria, os estudos e os atalhos patrocinados</strong> da página inicial."],
        ["Não troca de navegador: os seus favoritos, senhas e extensões continuam lá.",
         "Não instala o Firefox. Se ele não estiver instalado, as configurações ficam prontas para quando ele for.",
         "Não trava as preferências: você muda qualquer uma em <code>about:config</code>.",
         "Não mexe no Firefox do Flatpak, que não lê o arquivo de políticas: a receita avisa se encontrar um.",
         "Não tira nada de um <code>policies.json</code> que já existia: só acrescenta."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Confere se <code>/etc/firefox/policies/policies.json</code> já tem cada política e preferência da receita, com os mesmos valores. Se tiver, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Se o arquivo de políticas existir e não for um JSON válido, para e explica: o Firefox também não consegue ler.</li><li>Guarda uma cópia do arquivo e junta a ele as políticas da receita, sem tirar nada.</li><li>Avisa se o Firefox não estiver instalado, ou se for o do Flatpak.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere que o arquivo é um JSON válido, que tem todas as políticas e preferências da receita e, com <code>bloquear_anuncios</code>, o uBlock Origin.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Volta o <code>policies.json</code> ao que era, ou apaga, se foi a receita que criou. O uBlock Origin, se já tiver sido instalado, fica como uma extensão comum, que você remove em <code>about:addons</code>.</p>"),
    ])))
    corpo.append(f"""    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "A saída de um teste no Ubuntu 26.04.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("", '<span class="c">[5/6] Navegador enxuto</span>'),
        ("", '<span class="bar">  │</span> Arquivo atualizado: /etc/firefox/policies/policies.json'),
        ("", '<span class="bar">  │</span> Pronto. Feche e abra o Firefox para valer. O uBlock Origin é baixado da loja de extensões da Mozilla na primeira vez que ele abrir.'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o arquivo de políticas é um JSON que o Firefox lê (/etc/firefox/policies/policies.json)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> telemetria, estudos e atalhos patrocinados desligados'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> abas paradas saem da memória quando ela acaba (browser.tabs.unloadOnLowMemory)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> o uBlock Origin é instalado na próxima vez que o Firefox abrir'),
        ("", '<span class="bar">  │</span> Para ver no Firefox: abra about:policies e confira a lista de políticas ativas.'),
        ("", '<span class="bar">  │</span> Tudo conferido.'),
        ("", '<span class="v">✓</span> Navegador enxuto: aplicada e testada'),
    ], "Terminal mostrando o bora aplicar a receita Navegador enxuto: escreve as políticas do Firefox e confere quatro testes, todos ok.")}
      </figure>
    </section>""")
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Por que bloquear anúncios?", "Numa página de notícias comum, os anúncios e os rastreadores são boa parte do que é baixado e do processador gasto. Bloqueados, a página carrega mais rápido, gasta menos memória e fica mais segura."),
        ("Por que o Firefox, e não outro navegador?", "Ele já vem no Ubuntu, no Mint e no Debian, então nada muda para quem usa. E é dos poucos em que o uBlock Origin completo ainda funciona: nos navegadores baseados no Chromium, só a versão limitada."),
        ("Por que pela loja da Mozilla, e não por um pacote?", "O uBlock Origin precisa de atualizações frequentes para acompanhar os sites. Pela loja oficial da Mozilla, ele se atualiza sozinho, no Firefox do Snap e no do apt. O pacote do Debian demora a chegar e não serve para o Snap."),
        ("Por que um arquivo de políticas?", "É o jeito oficial de configurar o Firefox para o computador todo, para todas as pessoas, sem mexer no perfil de ninguém. Em <code>about:policies</code>, o próprio Firefox mostra o que está valendo."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("arquivo", "/etc/firefox/policies/policies.json", "Criado, ou completado se já existir. O Firefox lê daqui em qualquer distro, inclusive o Snap do Ubuntu."),
        ("escudo", "uBlock Origin", "Com <code>bloquear_anuncios</code>, instalado pelo próprio Firefox na primeira vez que ele abrir."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos para conferir", "No Firefox, digite na barra de endereços:", comandos([
        ("about:policies", "Lista as políticas ativas e mostra se alguma tem erro."),
        ("about:addons", "Mostra o uBlock Origin, depois da primeira abertura."),
        ("about:unloads", "Mostra as abas na ordem em que o Firefox descarrega quando a memória acaba."),
        ("about:processes", "Mostra quanta memória e processador cada aba está usando."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("Políticas do Firefox", "Mozilla, a lista completa", "https://mozilla.github.io/policy-templates/"),
        ("uBlock Origin", "O projeto, no GitHub", "https://github.com/gorhill/uBlock"),
        ("Descarregar abas para economizar memória", "Suporte da Mozilla", "https://support.mozilla.org/kb/unload-inactive-tabs-save-system-memory-firefox"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- sistema/servicos-enxutos

ILUSTRA_SERVICOS = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="is-t">
            <title id="is-t">Três serviços que ligavam no boot sem ter o que fazer são desligados, um depois do outro: o Bluetooth numa máquina sem Bluetooth, o ModemManager sem modem de celular, e a espera pela rede no boot.</title>
            <text x="20" y="26" font-size="14" font-weight="600">Só sai o que a máquina não tem:</text>
            """ + "".join(_linha_troca(i, n, a, d) for i, (n, a, d) in enumerate([("bluetooth", "ligado", "desligado"), ("ModemManager", "ligado", "desligado"), ("wait-online", "boot espera", "não espera")])) + """<g class="volta">
              <rect x="20" y="190" width="440" height="138" rx="14" class="caixa-svg"/>
              <text x="40" y="220" font-size="14" font-weight="600">Antes de desligar, a receita confere:</text>
              <text x="40" y="246" font-size="13" class="t2">• nenhuma placa em /sys/class/bluetooth</text>
              <text x="40" y="270" font-size="13" class="t2">• nenhum modem 3G, 4G ou 5G</text>
              <text x="40" y="294" font-size="13" class="t2">• nenhuma pasta da rede no /etc/fstab</text>
              <text x="40" y="318" font-size="13" class="t2">Impressão, som e atualizações não são mexidos.</text>
            </g>
          </svg>"""


def pagina_servicos():
    rid = "sistema/servicos-enxutos"
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ILUSTRA_SERVICOS, "Ilustração. Numa máquina com Bluetooth ou modem, esses serviços continuam ligados.")]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(
        ["<strong>Desliga o Bluetooth</strong> se a máquina não tiver placa de Bluetooth.",
         "<strong>Desliga o ModemManager</strong> se ela não tiver modem de celular.",
         "<strong>Faz o boot parar de esperar a rede</strong>, se nada no <code>/etc/fstab</code> precisar dela.",
         "<strong>Confere antes de cada um</strong>: só sai o que a máquina comprovadamente não usa."],
        ["Não mexe na impressão, no som, nas atualizações automáticas nem na busca de arquivos.",
         "Não remove nenhum pacote: os serviços continuam instalados.",
         "Não usa <code>mask</code>: um <code>systemctl enable --now</code> liga qualquer um de volta.",
         "Não liga de novo sozinho se você conectar um adaptador Bluetooth depois: para isso, desfaça ou ligue à mão."])))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?",
         "<p>Monta a lista do que esta máquina não usa (Bluetooth sem placa, ModemManager sem modem, espera da rede sem pastas da rede) e confere se algum desses serviços está habilitado. Se nenhum estiver, pula a receita.</p>"),
        ("aplicar", "", "Aplicar", "faz a mudança",
         "<ul><li>Roda <code>systemctl disable --now</code> em cada serviço da lista que estiver habilitado.</li><li>Anota cada um, para o desfazer ligar exatamente esses de volta.</li></ul>"),
        ("testar", "verde", "Testar", "funcionou?",
         "<p>Confere, com <code>systemctl is-enabled</code> e <code>systemctl is-active</code>, que nenhum serviço da lista liga no boot nem está rodando.</p>"),
        ("desfazer", "cinza", "Desfazer", "quando você pedir",
         "<p>Liga de novo, com <code>systemctl enable --now</code>, os serviços que a receita desligou, e só eles.</p>"),
    ])))
    corpo.append(f"""    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", "A saída de um teste no Ubuntu 26.04, num computador sem Bluetooth e sem modem.")}
      <figure style="margin:0">
{janela("bora aplicar", [
        ("", '<span class="c">[6/6] Serviços enxutos</span>'),
        ("", '<span class="bar">  │</span> Desligado: bluetooth.service (este computador não tem Bluetooth).'),
        ("", '<span class="bar">  │</span> Desligado: ModemManager.service (este computador não tem modem de celular).'),
        ("", '<span class="bar">  │</span> Desligado: NetworkManager-wait-online.service (o boot não precisa esperar a rede conectar).'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> bluetooth.service não liga no boot (este computador não tem Bluetooth)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> ModemManager.service não liga no boot (este computador não tem modem de celular)'),
        ("", '<span class="bar">  │</span> <span class="v">ok:</span> NetworkManager-wait-online.service não liga no boot (o boot não precisa esperar a rede conectar)'),
        ("", '<span class="bar">  │</span> Tudo conferido.'),
        ("", '<span class="v">✓</span> Serviços enxutos: aplicada e testada'),
    ], "Terminal mostrando o bora aplicar a receita Serviços enxutos: desliga o Bluetooth, o ModemManager e a espera da rede no boot, e confere que nenhum dos três liga mais.")}
      </figure>
    </section>""")
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques([
        ("Faz diferença mesmo?", "Numa máquina nova, quase nada. Numa de 2 GB com disco rígido, cada serviço que não sobe é um programa a menos para ler do disco no boot e um pouco menos de memória ocupada. A espera da rede é a que mais se nota: com Wi-Fi, ela pode segurar o boot por vários segundos."),
        ("Por que só esses três?", "São os que dá para saber, de fora, que a máquina não usa: não há placa, não há modem, não há pasta da rede. Impressão, som e busca de arquivos dependem do que você faz, e desligar errado quebraria algo sem aviso."),
        ("Por que disable, e não mask?", "Com <code>mask</code>, o serviço não liga nem se alguém pedir, e isso confunde quem tenta usar depois. Com <code>disable</code>, ele só não sobe no boot, e volta com um comando."),
    ])))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas([
        ("servico", "bluetooth.service", "Desabilitado só se não houver nenhuma placa em <code>/sys/class/bluetooth</code>."),
        ("servico", "ModemManager.service", "Desabilitado só se não houver modem de celular."),
        ("servico", "NetworkManager-wait-online.service", "Desabilitado se o <code>/etc/fstab</code> não montar pastas da rede e <code>esperar_rede</code> for não."),
    ])))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos para conferir", "", comandos([
        ("systemctl list-unit-files --state=enabled", "Lista o que liga no boot."),
        ("systemd-analyze blame", "Mostra quanto tempo cada serviço levou no último boot."),
        ("systemd-analyze", "Mostra quanto o boot levou, no total."),
        ("sudo systemctl enable --now bluetooth", "Liga o Bluetooth de volta, se um dia você conectar um adaptador."),
    ])))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes([
        ("systemctl(1)", "Manual do systemd", "https://www.freedesktop.org/software/systemd/man/latest/systemctl.html"),
        ("Serviços que esperam a rede", "systemd.io", "https://systemd.io/NETWORK_ONLINE/"),
        ("Melhorar o boot", "ArchWiki", "https://wiki.archlinux.org/title/Improving_performance/Boot_process"),
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"),
    ])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


PAGINAS = {
    "base/atualizar": pagina_atualizar,
    "sistema/snapshot": pagina_snapshot,
    "seguranca/firewall": pagina_firewall,
    "desktop/codecs": pagina_codecs,
    "desktop/flatpak": pagina_flatpak,
    "sistema/backup-pessoal": pagina_backup,
    "sistema/zram": pagina_zram,
    "desktop/ambiente-leve": pagina_ambiente,
    "desktop/navegador-leve": pagina_navegador,
    "sistema/servicos-enxutos": pagina_servicos,
}


# ---------------------------------------------------------------- rolê 3: programação

def _saida(titulo, linhas, final):
    """Linhas de uma receita no bora aplicar: texto comum, ou ("ok", texto)."""
    out = [("", f'<span class="c">{titulo}</span>')]
    for l in linhas:
        if isinstance(l, tuple):
            out.append(("", f'<span class="bar">  │</span> <span class="v">ok:</span> {l[1]}'))
        else:
            out.append(("", f'<span class="bar">  │</span> {l}'))
    out.append(("", f'<span class="v">✓</span> {final}: aplicada e testada'))
    return out


def _no_terminal(texto, linhas, alt):
    return f'''    <section class="largura" aria-label="Uma aplicação de verdade">
{cabeca("No terminal", "Uma aplicação de verdade", texto)}
      <figure style="margin:0">
{janela("bora aplicar", linhas, alt)}
      </figure>
    </section>'''


def _pagina(rid, ilustra, legenda, faz, nao, passos, terminal, porq, muda, conferir_, fontes_):
    r = ler_receita(rid)
    corpo = [abertura(rid, r, ilustra, legenda)]
    corpo.append(secao("resumo", "Em resumo", "O que faz e o que não faz", "", faz_nao(faz, nao)))
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora aplica esta receita", "As mesmas quatro etapas de toda receita, com o que esta confere em cada uma.", etapas([
        ("verificar", "azul", "Verificar", "já está aplicada?", passos[0]),
        ("aplicar", "", "Aplicar", "faz a mudança", passos[1]),
        ("testar", "verde", "Testar", "funcionou?", passos[2]),
        ("desfazer", "cinza", "Desfazer", "quando você pedir", passos[3]),
    ])))
    corpo.append(terminal)
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques(porq)))
    corpo.append(secao("o-que-muda", "Como", "O que muda no sistema", "", mudancas(muda)))
    corpo.append(secao("parametros", "Parâmetros", "O que dá para escolher", "", parametros(rid, r)))
    corpo.append(secao("conferir", "Confira você mesmo", "Os comandos para conferir", "", comandos(conferir_)))
    corpo.append(secao("onde-testada", "Onde funciona", "Distros e testes", "", onde_testada(r)))
    corpo.append(secao("roles", "Onde ela entra", "Rolês que usam esta receita", "", roles_que_usam(rid)))
    corpo.append(secao("fontes", "Fontes", "Para ler mais", "", fontes(fontes_ + [
        ("LEIAME da receita", "O mesmo conteúdo, junto do código", f"{REPO}/blob/main/receitas/{rid}/LEIAME.md")])))
    corpo.append(bloco_pedidos(rid, "esta receita", "nesta receita", editar=f"{REPO}/blob/main/receitas/{rid}/LEIAME.md"))
    return "\n\n".join(corpo)


def _commit(x, y, i, texto, cor="laranja"):
    return f'''<g class="pacote" style="--i:{i}">
              <circle cx="{x}" cy="{y}" r="13" class="{cor}"/>
              <text x="{x}" y="{y + 36}" font-size="12.5" text-anchor="middle" class="t2">{texto}</text>
            </g>'''


ILUSTRA_GIT = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ig-t">
            <title id="ig-t">Uma linha do tempo de commits no ramo main, cada um com o nome e o e-mail de quem fez, e uma chave que liga o computador ao GitHub sem senha.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Cada commit guarda quem fez, quando e por quê</text>
            <path d="M50 92H430" class="traco"/>
            """ + "".join(_commit(50 + i * 95, 92, i, t) for i, t in enumerate(["início", "menu", "cores", "conserto", "versão 1"])) + """
            <text x="20" y="160" font-size="13" class="t2 mono">main · Ana Aluna &lt;ana@exemplo.com.br&gt;</text>
            <g class="volta">
              <rect x="20" y="196" width="440" height="128" rx="14" class="caixa-svg"/>
              <circle cx="66" cy="246" r="14" fill="none" stroke="var(--accent)" stroke-width="3"/>
              <path d="M80 246h46M110 246v14M122 246v10" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
              <text x="150" y="232" font-size="14" font-weight="600">Uma chave SSH ed25519</text>
              <text x="150" y="254" font-size="13" class="t2">A parte pública vai para o GitHub ou o GitLab;</text>
              <text x="150" y="274" font-size="13" class="t2">a privada nunca sai do seu computador.</text>
              <text x="150" y="304" font-size="13" class="t2 mono">git push, sem digitar senha</text>
            </g>
          </svg>"""


def pagina_git():
    return _pagina(
        "dev/git", ILUSTRA_GIT, "Ilustração. O nome e o e-mail vão em cada commit; a chave é o seu crachá para o GitHub e o GitLab.",
        ["<strong>Instala o Git</strong>, se ainda não estiver instalado.",
         "<strong>Põe o seu nome e o seu e-mail</strong> nos commits, para o primeiro <code>git commit</code> não parar pedindo.",
         "<strong>Começa os repositórios no ramo <code>main</code></strong>, o mesmo nome do GitHub e do GitLab.",
         "<strong>Deixa o <code>git pull</code> juntar as mudanças</strong> sozinho, sem parar com uma pergunta que quem começa ainda não sabe responder.",
         "<strong>Cria uma chave SSH</strong> e mostra a linha para colar no GitHub ou no GitLab."],
        ["Não cria conta no GitHub nem no GitLab, e não cadastra a chave por você.",
         "Não apaga o que já estava no seu <code>.gitconfig</code>: só acrescenta.",
         "Não cria outra chave SSH se você já tiver uma.",
         "Não apaga a chave no desfazer: ela pode já estar cadastrada no site."],
        ["<p>Confere se o Git está instalado e se o nome, o e-mail, o ramo inicial e o jeito de juntar do <code>git pull</code> já estão como a receita pede, e se a pessoa já tem uma chave SSH.</p>",
         "<ul><li>Instala <code>git</code> e <code>openssh-client</code>, se faltarem.</li><li>Guarda uma cópia do <code>~/.gitconfig</code> e grava <code>user.name</code>, <code>user.email</code> e, se não existirem, <code>init.defaultBranch</code> e <code>pull.rebase</code>, como a própria pessoa.</li><li>Cria <code>~/.ssh/id_ed25519</code>, se não houver chave, e mostra a parte pública.</li></ul>",
         "<p>Confere cada configuração, faz um commit de verdade num repositório de teste, apagado no fim, e confere a chave com <code>ssh-keygen -l</code>.</p>",
         "<p>Volta o <code>~/.gitconfig</code> ao que era, ou apaga o arquivo, se foi a receita que o criou, e remove os pacotes que ela instalou. A chave SSH fica.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 26.04, numa conta que nunca tinha usado o Git, encurtada nas linhas do apt.", _saida("[1/4] Git", [
            "Instalando: git openssh-client",
            "Git: user.name = Ana Aluna", "Git: user.email = ana@exemplo.com.br",
            "Git: init.defaultBranch = main", "Git: pull.rebase = false",
            "Chave SSH criada: /home/aluna/.ssh/id_ed25519",
            "Para usar a chave no GitHub, abra https://github.com/settings/ssh/new e cole esta linha:",
            '  <span class="d">ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDvQF3u0… ana@exemplo.com.br</span>',
            ("ok", "Git instalado (git --version)"), ("ok", "nome nos commits de aluna (git config user.name)"),
            ("ok", "e-mail nos commits de aluna (git config user.email)"), ("ok", "repositórios novos começam no ramo main (init.defaultBranch)"),
            ("ok", "o git pull sabe juntar as mudanças (pull.rebase)"), ("ok", "um commit de teste funciona"),
            ("ok", "aluna tem uma chave SSH válida (ssh-keygen -l)"), "Tudo conferido."], "Git"),
            "Terminal mostrando o bora aplicar a receita Git: instala o Git, grava o nome, o e-mail e dois padrões, cria a chave SSH, mostra a linha para colar no GitHub e confere sete testes."),
        [("Por que o nome e o e-mail?", "Cada commit leva o nome e o e-mail de quem fez. O GitHub e o GitLab usam o e-mail para ligar o commit à sua conta, por isso vale usar o mesmo de lá. Sem eles, o Git se recusa a fazer o commit."),
         ("Por que <code>main</code>?", "É o nome que o GitHub e o GitLab dão ao ramo principal. Com outro nome no seu computador, o primeiro <code>git push</code> cria um ramo a mais, e os tutoriais deixam de bater com o que você vê."),
         ("Por que <code>pull.rebase = false</code>?", "Quando você e outra pessoa mudam o mesmo repositório, o <code>git pull</code> precisa juntar as duas versões. Sem essa configuração, o Git para e pede que você escolha entre merge, rebase e fast-forward. O merge é o comportamento clássico e o que os tutoriais esperam."),
         ("Por que uma chave SSH, e sem senha?", "O GitHub não aceita mais a senha da conta no <code>git push</code>. A chave é o jeito recomendado e não expira. Ela é criada sem senha porque a receita não faz perguntas no meio; para pôr uma, rode <code>ssh-keygen -p -f ~/.ssh/id_ed25519</code>.")],
        [("pacote", "git e openssh-client", "Instalados se ainda não estiverem."),
         ("arquivo", "~/.gitconfig", "<code>user.name</code>, <code>user.email</code>, <code>init.defaultBranch</code> e <code>pull.rebase</code>. O que já estava lá fica."),
         ("arquivo", "~/.ssh/id_ed25519 e id_ed25519.pub", "A chave SSH, só se a pessoa ainda não tiver uma.")],
        [("git config --global --list", "Mostra tudo o que está configurado no seu Git."),
         ("cat ~/.ssh/id_ed25519.pub", "Mostra a parte pública da chave, para colar no GitHub ou no GitLab."),
         ("ssh -T git@github.com", "Depois de cadastrar a chave, responde com o seu usuário do GitHub.")],
        [("Configuração inicial do Git", "Pro Git, em português", "https://git-scm.com/book/pt-br/v2/Primeiros-Passos-Configura%C3%A7%C3%A3o-inicial-do-Git"),
         ("Gerar uma chave SSH", "Documentação do GitHub", "https://docs.github.com/pt/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent"),
         ("Chaves SSH no GitLab", "Documentação do GitLab", "https://docs.gitlab.com/user/ssh/")])


ILUSTRA_COMPILACAO = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="icp-t">
            <title id="icp-t">Um pip install e um npm install encontram um pedaço em C. Sem compilador, a instalação para com erro; com as ferramentas de compilação, o pedaço é compilado e a instalação termina.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Um pacote com um pedaço em C</text>
            <g class="pacote" style="--i:0">
              <rect x="20" y="44" width="440" height="56" rx="12" class="caixa-svg"/>
              <text x="40" y="78" font-size="14" class="mono">pip install um-pacote</text>
              <rect x="300" y="60" width="140" height="24" rx="8" class="vermelho"/>
              <text x="370" y="77" font-size="12.5" font-weight="600" text-anchor="middle" style="fill:#fff">gcc: not found</text>
            </g>
            <text x="20" y="128" font-size="13" class="t2">Sem compilador, a instalação para no meio.</text>
            <g class="pacote" style="--i:1">
              <rect x="20" y="150" width="440" height="56" rx="12" class="caixa-svg"/>
              <text x="40" y="184" font-size="14" class="mono">npm install outro-pacote</text>
              <rect x="300" y="166" width="140" height="24" rx="8" class="verde"/>
              <text x="370" y="183" font-size="12.5" font-weight="600" text-anchor="middle" style="fill:#fff">compilado ✓</text>
            </g>
            <g class="volta">
              <rect x="20" y="230" width="440" height="94" rx="14" class="caixa-svg"/>
              <text x="40" y="262" font-size="14" font-weight="600">build-essential e pkg-config</text>
              <text x="40" y="286" font-size="13" class="t2 mono">gcc · g++ · make · libc-dev · pkg-config</text>
              <text x="40" y="308" font-size="13" class="t2">O que o pip e o npm chamam por baixo, sem avisar.</text>
            </g>
          </svg>"""


def pagina_compilacao():
    return _pagina(
        "dev/compilacao", ILUSTRA_COMPILACAO, "Ilustração. A maioria dos pacotes vem pronta; os que não vêm são compilados na hora.",
        ["<strong>Instala o compilador de C e de C++</strong>, o <code>gcc</code> e o <code>g++</code>.",
         "<strong>Instala o <code>make</code></strong> e as bibliotecas básicas do C, pelo <code>build-essential</code>.",
         "<strong>Instala o <code>pkg-config</code></strong>, que os scripts de compilação usam para achar as bibliotecas do sistema."],
        ["Não configura nada: são só programas novos.",
         "Não instala bibliotecas de projetos específicos, como as de banco de dados ou de imagem.",
         "Não remove no desfazer o que outro programa passou a usar."],
        ["<p>Confere se os pacotes <code>build-essential</code> e <code>pkg-config</code> estão instalados.</p>",
         "<p>Instala os dois, com as dependências que faltarem, e anota tudo o que entrou.</p>",
         "<p>Roda <code>gcc</code>, <code>g++</code>, <code>make</code> e <code>pkg-config</code>, e compila e roda um programa de uma linha em C e outro em C++, numa pasta temporária.</p>",
         "<p>Remove os pacotes que a receita instalou, com as dependências que vieram junto, menos o que outro programa passou a usar.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 26.04, encurtada nas linhas do apt.", _saida("[2/4] Ferramentas de compilação", [
            "Instalando: build-essential pkg-config", '<span class="d">0 upgraded, 95 newly installed, 0 to remove and 0 not upgraded.</span>',
            "Pronto: gcc, g++, make e pkg-config instalados.",
            ("ok", "compilador de C (gcc --version)"), ("ok", "compilador de C++ (g++ --version)"), ("ok", "make (make --version)"),
            ("ok", "pkg-config acha as bibliotecas do sistema"), ("ok", "um programa em C compila e roda"),
            ("ok", "um programa em C++ compila e roda"), "Tudo conferido."], "Ferramentas de compilação"),
            "Terminal mostrando o bora aplicar a receita Ferramentas de compilação: instala o build-essential e o pkg-config e confere seis testes, dois deles compilando e rodando programas de verdade."),
        [("Por que, se eu vou programar em Python ou JavaScript?", "Muitos pacotes do pip e do npm têm um pedaço em C ou C++, por velocidade. Quando não há uma versão pronta para a sua máquina, eles são compilados na hora da instalação. Sem o compilador, o erro aparece no meio de um monte de texto em inglês."),
         ("O que é o <code>build-essential</code>?", "Um pacote que não tem nada dentro: ele só puxa o <code>gcc</code>, o <code>g++</code>, o <code>make</code> e as bibliotecas do C. É o jeito que o Debian e o Ubuntu fazem para instalar o kit básico de uma vez.")],
        [("pacote", "build-essential", "O gcc, o g++, o make e as bibliotecas básicas do C."),
         ("pacote", "pkg-config", "Acha as bibliotecas instaladas para os scripts de compilação.")],
        [("gcc --version", "Mostra a versão do compilador de C."),
         ("make --version", "Mostra a versão do make.")],
        [("O pacote build-essential", "Debian", "https://packages.debian.org/stable/build-essential"),
         ("pkg-config", "freedesktop.org", "https://www.freedesktop.org/wiki/Software/pkg-config/")])


ILUSTRA_PYTHON = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ipy-t">
            <title id="ipy-t">O Python da distro fica intocado, no meio, usado pelo sistema. Cada projeto tem a sua caixa, um ambiente virtual, com as próprias bibliotecas, em versões que podem ser diferentes.</title>
            <rect x="140" y="24" width="200" height="70" rx="14" class="caixa-svg"/>
            <text x="240" y="54" font-size="14" font-weight="600" text-anchor="middle">Python da distro</text>
            <text x="240" y="76" font-size="12.5" text-anchor="middle" class="t2">o sistema usa; ninguém mexe</text>
            <path d="M190 94v30M290 94v30" class="traco tracejado"/>
            <g class="pacote" style="--i:0">
              <rect x="40" y="128" width="190" height="120" rx="14" fill="none" stroke="var(--azul)" stroke-width="2.4" stroke-dasharray="6 4"/>
              <text x="60" y="156" font-size="14" font-weight="600">site/.venv</text>
              <text x="60" y="184" font-size="13" class="t2 mono">flask 3.1</text>
              <text x="60" y="206" font-size="13" class="t2 mono">requests 2.32</text>
            </g>
            <g class="pacote" style="--i:1">
              <rect x="250" y="128" width="190" height="120" rx="14" fill="none" stroke="var(--azul)" stroke-width="2.4" stroke-dasharray="6 4"/>
              <text x="270" y="156" font-size="14" font-weight="600">dados/.venv</text>
              <text x="270" y="184" font-size="13" class="t2 mono">pandas 2.3</text>
              <text x="270" y="206" font-size="13" class="t2 mono">requests 2.28</text>
            </g>
            <g class="volta">
              <rect x="40" y="268" width="400" height="56" rx="14" class="caixa-svg"/>
              <text x="240" y="301" font-size="11.5" text-anchor="middle" class="mono">python3 -m venv .venv &amp;&amp; source .venv/bin/activate</text>
            </g>
          </svg>"""


def pagina_python():
    return _pagina(
        "dev/python", ILUSTRA_PYTHON, "Ilustração. Cada projeto tem o seu ambiente, e as versões das bibliotecas não brigam entre si.",
        ["<strong>Instala o módulo de ambientes virtuais</strong> e o <code>pip</code>, para cada projeto ter as suas bibliotecas.",
         "<strong>Instala os cabeçalhos do Python</strong>, que os pacotes com partes em C pedem para compilar.",
         "<strong>Instala o <code>pipx</code></strong>, para programas de linha de comando escritos em Python.",
         "<strong>Faz o comando <code>python</code> abrir o Python 3</strong>, como os tutoriais escrevem.",
         "<strong>Cria a pasta <code>~/.local/bin</code></strong>, onde o pipx põe os programas, para ela entrar no PATH."],
        ["Não troca a versão do Python da distro.",
         "Não instala nada com <code>sudo pip</code>, que pode quebrar programas do sistema.",
         "Não cria projetos nem ambientes por você.",
         "Não apaga os ambientes virtuais dos seus projetos no desfazer."],
        ["<p>Confere se <code>python3-venv</code>, <code>python3-pip</code>, <code>python3-dev</code>, <code>pipx</code> e <code>python-is-python3</code> estão instalados, e se a pasta <code>~/.local/bin</code> existe.</p>",
         "<p>Instala os pacotes que faltarem e cria <code>~/.local/bin</code>, como a própria pessoa. O <code>~/.profile</code> põe essa pasta no PATH a cada login.</p>",
         "<p>Confere que <code>python</code> e <code>python3</code> mostram a mesma versão, cria um ambiente virtual de verdade numa pasta temporária e roda o <code>pip</code> de dentro dele, e confere o <code>Python.h</code> e o <code>pipx</code>.</p>",
         "<p>Remove os pacotes que a receita instalou e a pasta <code>~/.local/bin</code>, se ainda estiver vazia. Os ambientes dos projetos ficam.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 26.04, encurtada nas linhas do apt.", _saida("[3/4] Python com ambientes virtuais", [
            "Instalando: python3-venv python3-pip python3-dev pipx python-is-python3",
            "Pasta criada: /home/aluna/.local/bin (entra no PATH no próximo login)",
            "Pronto: Python 3.14.4. Para cada projeto, crie um ambiente com: python3 -m venv .venv &amp;&amp; source .venv/bin/activate",
            ("ok", "Python 3 instalado (Python 3.14.4)"), ("ok", "o comando python abre o Python 3"),
            ("ok", "um ambiente virtual novo funciona, com o pip dentro (python3 -m venv)"),
            ("ok", "cabeçalhos para compilar pacotes com partes em C (Python.h)"), ("ok", "pipx instalado (pipx --version)"),
            ("ok", "a pasta dos programas do pipx existe (/home/aluna/.local/bin)"), "Tudo conferido."], "Python com ambientes virtuais"),
            "Terminal mostrando o bora aplicar a receita Python com ambientes virtuais: instala cinco pacotes, cria a pasta dos programas do pipx e confere seis testes, um deles criando um ambiente virtual."),
        [("Por que não <code>sudo pip install</code>?", "O Python da distro é usado por programas do próprio sistema. Trocar uma biblioteca dele pode quebrar esses programas. Por isso, desde o Debian 12 e o Ubuntu 23.04, o pip fora de um ambiente virtual recusa instalar, com o erro <code>externally-managed-environment</code>."),
         ("O que é um ambiente virtual?", "Uma pasta, em geral <code>.venv</code>, dentro do projeto, com um Python e as bibliotecas só daquele projeto. Dois projetos podem usar versões diferentes da mesma biblioteca. Apagar a pasta apaga tudo, sem rastro no sistema."),
         ("E o pipx?", "É para programas, e não para bibliotecas: <code>pipx install ruff</code> cria um ambiente só para o ruff e põe o comando em <code>~/.local/bin</code>. Atualizar ou remover um não mexe nos outros.")],
        [("pacote", "python3-venv, python3-pip e python3-dev", "Os ambientes virtuais, o pip dentro deles e os cabeçalhos para compilar."),
         ("pacote", "pipx e python-is-python3", "Programas em Python em ambientes próprios, e o comando <code>python</code>."),
         ("arquivo", "~/.local/bin", "Criada vazia, se ainda não existir. Entra no PATH no próximo login.")],
        [("python3 -m venv .venv", "Cria um ambiente virtual na pasta do projeto."),
         ("source .venv/bin/activate", "Entra no ambiente. O prompt passa a mostrar <code>(.venv)</code>; para sair, <code>deactivate</code>."),
         ("pipx install ruff", "Instala um programa de linha de comando no seu próprio ambiente.")],
        [("venv: ambientes virtuais", "Documentação do Python, em português", "https://docs.python.org/pt-br/3/library/venv.html"),
         ("PEP 668", "Ambientes gerenciados pela distro", "https://peps.python.org/pep-0668/"),
         ("pipx", "Documentação oficial", "https://pipx.pypa.io/")])


ILUSTRA_NODE = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ino-t">
            <title id="ino-t">O arquivo do Node.js sai de nodejs.org, passa pela conferência da soma SHA256 gravada na receita e só então é instalado. Os pacotes do npm install -g vão para a pasta pessoal, sem sudo.</title>
            <g class="pacote" style="--i:0">
              <rect x="20" y="30" width="130" height="64" rx="12" class="caixa-svg"/>
              <text x="85" y="58" font-size="14" font-weight="600" text-anchor="middle">nodejs.org</text>
              <text x="85" y="80" font-size="12" text-anchor="middle" class="t2">26.13.0 LTS</text>
            </g>
            <path d="M156 62h42" class="traco"/><path d="M190 56l8 6-8 6" class="traco"/>
            <g class="pacote" style="--i:1">
              <rect x="206" y="30" width="120" height="64" rx="12" class="azul"/>
              <text x="266" y="58" font-size="14" font-weight="600" text-anchor="middle" style="fill:#fff">SHA256</text>
              <text x="266" y="80" font-size="12" text-anchor="middle" style="fill:#fff">bate? ✓</text>
            </g>
            <path d="M332 62h42" class="traco"/><path d="M366 56l8 6-8 6" class="traco"/>
            <g class="pacote" style="--i:2">
              <rect x="382" y="30" width="78" height="64" rx="12" class="verde"/>
              <text x="421" y="67" font-size="13" font-weight="600" text-anchor="middle" style="fill:#fff">instala</text>
            </g>
            <text x="20" y="128" font-size="13" class="t2">Se o arquivo não for exatamente o testado, nada é instalado.</text>
            <g class="volta">
              <rect x="20" y="158" width="440" height="166" rx="14" class="caixa-svg"/>
              <text x="40" y="190" font-size="14" font-weight="600">npm install -g, sem sudo</text>
              <text x="40" y="222" font-size="13" class="mono">/usr/local/lib/nodejs/</text>
              <text x="280" y="222" font-size="13" class="t2">o Node.js, do root</text>
              <text x="40" y="252" font-size="13" class="mono">~/.local/lib/node_modules/</text>
              <text x="280" y="252" font-size="13" class="t2">os seus pacotes</text>
              <text x="40" y="282" font-size="13" class="mono">~/.local/bin/</text>
              <text x="280" y="282" font-size="13" class="t2">os seus comandos</text>
              <text x="40" y="308" font-size="12.5" class="t2">Nada do root na sua pasta, nada seu na do root.</text>
            </g>
          </svg>"""


def pagina_node():
    return _pagina(
        "dev/node", ILUSTRA_NODE, "Ilustração. A versão e as somas ficam gravadas na receita, e sobem junto com o bora.",
        ["<strong>Instala o Node.js LTS oficial</strong>, com o <code>npm</code> e o <code>npx</code>, igual em todas as distros.",
         "<strong>Confere a soma SHA256</strong> do arquivo baixado antes de instalar.",
         "<strong>Faz o <code>npm install -g</code> funcionar sem sudo</strong>, instalando na sua pasta pessoal.",
         "<strong>Cria a pasta <code>~/.local/bin</code></strong>, onde aparecem os comandos instalados pelo npm."],
        ["Não usa o Node.js da distro, que no Ubuntu 24.04 é a versão 18, já fora de suporte.",
         "Não remove o Node.js da distro, se ele estiver instalado: só passa na frente no PATH.",
         "Não atualiza sozinho pelo <code>apt</code>: a versão sobe com o <code>bora</code>.",
         "Não passa por cima de um <code>node</code> que você instalou à mão em <code>/usr/local/bin</code>.",
         "Não apaga os pacotes que você instalou com <code>npm install -g</code> no desfazer."],
        ["<p>Confere se o Node.js da versão da receita está em <code>/usr/local/lib/nodejs</code>, se <code>node</code>, <code>npm</code> e <code>npx</code> em <code>/usr/local/bin</code> apontam para ele, se o <code>npmrc</code> está como a receita escreve e se <code>~/.local/bin</code> existe.</p>",
         "<ul><li>Para, sem mudar nada, se já houver um <code>node</code> em <code>/usr/local/bin</code> que não veio do <code>bora</code>.</li><li>Baixa o arquivo de nodejs.org, confere a soma SHA256 gravada na receita e abre em <code>/usr/local/lib/nodejs</code>.</li><li>Cria os links em <code>/usr/local/bin</code>, escreve <code>prefix=${HOME}/.local</code> no <code>npmrc</code> do Node.js e cria <code>~/.local/bin</code>.</li></ul>",
         "<p>Como a pessoa: confere a versão do <code>node</code>, o <code>npm</code> e o <code>npx</code>, roda um programa e confere que o <code>npm prefix -g</code> é <code>~/.local</code>.</p>",
         "<p>Apaga os links e a pasta do Node.js, remove os pacotes que a receita instalou e a pasta <code>~/.local/bin</code>, se ainda estiver vazia.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 26.04, encurtada nas linhas do apt.", _saida("[3/4] Node.js", [
            "Baixando o Node.js 26.13.0 de https://nodejs.org/dist/v26.13.0/node-v26.13.0-linux-x64.tar.xz",
            "Soma SHA256 conferida.", "Node.js instalado em /usr/local/lib/nodejs/node-v26.13.0-linux-x64",
            "Arquivo atualizado: /usr/local/lib/nodejs/node-v26.13.0-linux-x64/etc/npmrc",
            "Pasta criada: /home/aluna/.local/bin (entra no PATH no próximo login)",
            "Pronto: Node.js 26.13.0 e npm 11.20.0.",
            ("ok", "Node.js 26.13.0 (node --version)"), ("ok", "npm (npm --version)"), ("ok", "npx (npx --version)"),
            ("ok", "o Node.js roda um programa"), ("ok", "npm install -g instala em ~/.local, sem sudo (npm prefix -g)"),
            ("ok", "a pasta dos programas do npm existe (/home/aluna/.local/bin)"), "Tudo conferido."], "Node.js"),
            "Terminal mostrando o bora aplicar a receita Node.js: baixa o Node.js 26.13.0, confere a soma SHA256, instala, configura o npm e confere seis testes."),
        [("Por que não o Node.js da distro?", "No Ubuntu 24.04 e nas derivadas, como o Linux Mint 22, o Pop!_OS e o Zorin OS, ele é a versão 18, que saiu de suporte em 2025. As ferramentas de hoje, como o Vite, pedem uma versão mais nova, e o primeiro tutorial já quebraria."),
         ("É seguro baixar de fora da distro?", "O arquivo vem de nodejs.org, do próprio projeto, e a receita traz a soma SHA256 do arquivo que foi testado. Se o que chegar não bater, nada é instalado. É a regra do projeto para instaladores oficiais."),
         ("Por que o npm sem sudo?", "Com <code>sudo npm install -g</code>, os arquivos ficam do root, e o próximo <code>npm</code> sem sudo falha com <code>EACCES</code>. Com o <code>prefix</code> em <code>~/.local</code>, cada pessoa instala na própria pasta."),
         ("Como atualizar?", "Quando sair um <code>bora</code> com uma versão nova do Node.js, aplique a receita de novo. Ela instala a nova ao lado e troca os links.")],
        [("pacote", "curl, xz-utils e ca-certificates", "Para baixar e abrir o arquivo, se faltarem."),
         ("arquivo", "/usr/local/lib/nodejs/node-v26.13.0-linux-x64", "O Node.js, com o npm e o npx, e o <code>etc/npmrc</code> com o <code>prefix</code>."),
         ("arquivo", "/usr/local/bin/node, npm e npx", "Links para a versão instalada."),
         ("arquivo", "~/.local/bin", "Criada vazia, se ainda não existir. Entra no PATH no próximo login.")],
        [("node --version", "Mostra a versão do Node.js."),
         ("npm prefix -g", "Mostra onde o <code>npm install -g</code> instala: a sua <code>~/.local</code>."),
         ("npm create vite@latest meu-site", "Começa um projeto web com o Vite.")],
        [("Downloads do Node.js", "nodejs.org", "https://nodejs.org/pt/download"),
         ("Versões LTS do Node.js", "nodejs.org", "https://nodejs.org/pt/about/previous-releases"),
         ("A configuração prefix", "Documentação do npm", "https://docs.npmjs.com/cli/using-npm/config#prefix")])


ILUSTRA_PODMAN = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ipo-t">
            <title id="ipo-t">À esquerda, o Docker, com um serviço rodando como root por trás de todos os contêineres. À direita, o Podman, em que cada pessoa roda os próprios contêineres na sua conta, e o root de dentro do contêiner é um usuário sem poder do lado de fora.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Docker</text>
            <rect x="20" y="42" width="200" height="40" rx="10" class="vermelho"/>
            <text x="120" y="67" font-size="13" font-weight="600" text-anchor="middle" style="fill:#fff">serviço como root</text>
            """ + "".join(f'<rect x="{30 + i * 64}" y="100" width="52" height="40" rx="8" class="caixa-svg"/>' for i in range(3)) + """
            <path d="M120 82v18" class="traco"/>
            <text x="20" y="166" font-size="12.5" class="t2">o grupo docker vale o root</text>
            <text x="260" y="28" font-size="14" font-weight="600">Podman</text>
            <g class="pacote" style="--i:0">
              <rect x="260" y="42" width="200" height="40" rx="10" class="verde"/>
              <text x="360" y="67" font-size="13" font-weight="600" text-anchor="middle" style="fill:#fff">a sua conta</text>
              """ + "".join(f'<rect x="{270 + i * 64}" y="100" width="52" height="40" rx="8" fill="none" stroke="var(--ok)" stroke-width="2.2"/>' for i in range(3)) + """
              <path d="M360 82v18" class="traco"/>
              <text x="260" y="166" font-size="12.5" class="t2">sem serviço, sem root</text>
            </g>
            <g class="volta">
              <rect x="20" y="196" width="440" height="128" rx="14" class="caixa-svg"/>
              <text x="40" y="226" font-size="14" font-weight="600">O root de dentro é você do lado de fora</text>
              <text x="40" y="252" font-size="13" class="mono">dentro: root (0)  →  fora: 165536</text>
              <text x="40" y="278" font-size="13" class="t2">A faixa de IDs vem de /etc/subuid e /etc/subgid.</text>
              <text x="40" y="304" font-size="13" class="mono">podman run --rm -it python:3.13</text>
            </g>
          </svg>"""


def pagina_podman():
    return _pagina(
        "containers/podman", ILUSTRA_PODMAN, "Ilustração. Os comandos são os mesmos do Docker; muda quem roda os contêineres.",
        ["<strong>Instala o Podman</strong>, que aceita os mesmos comandos do Docker na maioria dos casos.",
         "<strong>Deixa os contêineres rodarem na sua conta</strong>, sem serviço como root e sem sudo.",
         "<strong>Cria a faixa de IDs</strong> que os contêineres sem root precisam, se a conta ainda não tiver.",
         "<strong>Acha as imagens pelo nome curto</strong>, como <code>python</code> ou <code>nginx</code>, no Docker Hub."],
        ["Não instala o Docker nem cria o grupo <code>docker</code>.",
         "Não deixa nenhum serviço rodando: o Podman só roda quando você chama.",
         "Não baixa imagem nenhuma: você escolhe o que rodar.",
         "Não apaga as suas imagens e contêineres no desfazer: eles ficam em <code>~/.local/share/containers</code>."],
        ["<p>Confere se <code>podman</code> e <code>uidmap</code> estão instalados, se a configuração dos registros está como a receita escreve e se a conta tem a faixa de IDs em <code>/etc/subuid</code> e <code>/etc/subgid</code>.</p>",
         "<ul><li>Instala <code>podman</code> e <code>uidmap</code>.</li><li>Escreve <code>/etc/containers/registries.conf.d/50-bora-docker-hub.conf</code>, com o Docker Hub para os nomes curtos.</li><li>Se a conta não tiver faixa de IDs, guarda uma cópia de <code>/etc/subuid</code> e <code>/etc/subgid</code> e acrescenta 65536 IDs depois das faixas que já existem.</li></ul>",
         "<p>Confere o <code>podman --version</code>, a faixa de IDs, a permissão do <code>newuidmap</code>, que o <code>podman info</code> da pessoa diz <code>rootless: true</code> e que o Docker Hub está nos registros.</p>",
         "<p>Apaga a configuração dos registros, volta <code>/etc/subuid</code> e <code>/etc/subgid</code> ao que eram e remove os pacotes que a receita instalou.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 26.04, numa conta sem faixa de IDs, encurtada nas linhas do apt.", _saida("[4/4] Contêineres com Podman", [
            "Instalando: podman uidmap",
            "Arquivo atualizado: /etc/containers/registries.conf.d/50-bora-docker-hub.conf",
            "Faixa de IDs para os contêineres de aluna: 165536 a 231071",
            "Pronto: podman version 5.7.0. Para testar: podman run --rm hello-world",
            ("ok", "Podman instalado (podman --version)"), ("ok", "faixa de IDs de aluna para os contêineres (/etc/subuid e /etc/subgid)"),
            ("ok", "o newuidmap pode mapear os IDs (uidmap)"), ("ok", "aluna roda o Podman sem ser root (podman info)"),
            ("ok", "imagens com nome curto vêm do Docker Hub"), "Tudo conferido."], "Contêineres com Podman"),
            "Terminal mostrando o bora aplicar a receita Contêineres com Podman: instala o Podman, configura o Docker Hub, cria a faixa de IDs da conta e confere cinco testes."),
        [("Por que Podman, e não Docker?", "No Docker, um serviço roda como root, e quem está no grupo <code>docker</code> consegue, na prática, fazer qualquer coisa no sistema. O Podman roda cada contêiner na conta de quem chamou, e aceita os mesmos comandos na maioria dos casos."),
         ("O que é a faixa de IDs?", "Dentro do contêiner, os programas costumam rodar como root. Do lado de fora, esse root vira um ID da faixa da sua conta, sem poder nenhum no sistema. O <code>adduser</code> já cria a faixa para contas novas; contas antigas podem não ter."),
         ("Por que o Docker Hub?", "Os tutoriais escrevem <code>podman run python</code>, com o nome curto. Sem dizer onde procurar, o Podman do Ubuntu não acha a imagem. Com um registro só na lista, ele procura lá, como o Docker faz.")],
        [("pacote", "podman e uidmap", "O Podman e o <code>newuidmap</code>, que os contêineres sem root usam."),
         ("arquivo", "/etc/containers/registries.conf.d/50-bora-docker-hub.conf", "<code>unqualified-search-registries = [\"docker.io\"]</code>."),
         ("arquivo", "/etc/subuid e /etc/subgid", "Uma faixa de 65536 IDs para a conta, só se ela ainda não tiver.")],
        [("podman run --rm hello-world", "Baixa e roda o contêiner de teste, que imprime uma mensagem e sai."),
         ("podman info", "Mostra a configuração; <code>rootless: true</code> quer dizer que roda sem root."),
         ("podman images", "Lista as imagens baixadas. Para apagar tudo: <code>podman system reset</code>.")],
        [("Podman sem root", "Tutorial oficial", "https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md"),
         ("registries.conf", "containers/image", "https://github.com/containers/image/blob/main/docs/containers-registries.conf.5.md"),
         ("Podman", "Wiki do Debian", "https://wiki.debian.org/Podman")])


PAGINAS.update({
    "dev/git": pagina_git,
    "dev/compilacao": pagina_compilacao,
    "dev/python": pagina_python,
    "dev/node": pagina_node,
    "containers/podman": pagina_podman,
})


# ---------------------------------------------------------------- capacidades novas: etckeeper, sem-snap e ssh

ILUSTRA_ETCKEEPER = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="iet-t">
            <title id="iet-t">A pasta /etc com uma linha do tempo de registros do Git: a instalação, a instalação do firewall, a mudança do dia, cada um mostrando o que mudou na configuração.</title>
            <rect x="20" y="24" width="440" height="64" rx="14" class="caixa-svg"/>
            <text x="44" y="52" font-size="14" font-weight="600" class="mono">/etc</text>
            <text x="44" y="74" font-size="12.5" class="t2">a configuração do sistema, num repositório do Git</text>
            <path d="M60 140H420" class="traco"/>
            """ + "".join(_commit(60 + i * 120, 140, i, t) for i, t in enumerate(["instalação", "apt: ufw", "apt: codecs", "dia 12"])) + """
            <g class="volta">
              <rect x="20" y="210" width="440" height="110" rx="14" class="caixa-svg"/>
              <text x="44" y="240" font-size="13" class="mono">$ sudo git -C /etc log --oneline</text>
              <text x="44" y="266" font-size="12.5" class="t2 mono">a1c3e9f commit diário</text>
              <text x="44" y="288" font-size="12.5" class="t2 mono">7d20b14 saving changes after apt run</text>
              <text x="44" y="310" font-size="12.5" class="t2 mono">3f9e002 Initial commit</text>
            </g>
          </svg>"""


def pagina_etckeeper():
    return _pagina(
        "sistema/etckeeper", ILUSTRA_ETCKEEPER, "Ilustração. Cada instalação e cada dia viram um registro no histórico do /etc.",
        ["<strong>Guarda a pasta <code>/etc</code> num repositório do Git</strong>, com o primeiro registro na hora.",
         "<strong>Registra cada instalação do apt</strong>, antes e depois, e o que mudou por fora dele uma vez por dia.",
         "<strong>Fecha o histórico</strong> com permissão só do root, porque o <code>/etc</code> tem as senhas cifradas."],
        ["Não manda o histórico para lugar nenhum: ele fica no próprio computador.",
         "Não substitui o snapshot nem o backup: guarda só a configuração.",
         "Não mexe num histórico do <code>/etc</code> que já existia antes do <code>bora</code>."],
        ["<p>Confere se o pacote <code>etckeeper</code> está instalado e se o <code>/etc</code> tem um histórico com pelo menos um registro.</p>",
         "<p>Instala o <code>etckeeper</code>, que cria o histórico e o primeiro registro, registra o que tiver mudado desde então e fecha a pasta <code>/etc/.git</code> para o root.</p>",
         "<p>Confere o histórico, o gancho do apt, a permissão 700 de <code>/etc/.git</code> e o arquivo onde ficam o dono e as permissões de cada arquivo.</p>",
         "<p>Guarda uma cópia do histórico em <code>/var/backups</code>, remove o repositório com <code>etckeeper uninit</code> e tira o pacote. Os arquivos do <code>/etc</code> ficam como estão.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04, encurtada nas linhas do apt.", _saida("[2/8] Histórico do /etc", [
            "Instalando: etckeeper", '<span class="d">0 upgraded, 3 newly installed, 0 to remove and 0 not upgraded.</span>',
            "Pronto. Para ver o histórico: sudo git -C /etc log --oneline",
            ("ok", "etckeeper instalado"), ("ok", "o /etc tem um histórico com pelo menos um registro (git -C /etc log)"),
            ("ok", "o apt registra cada instalação no histórico (/etc/apt/apt.conf.d/05etckeeper)"),
            ("ok", "só o root lê o histórico (/etc/.git com permissão 700)"),
            ("ok", "dono e permissões de cada arquivo guardados à parte (/etc/.etckeeper)"), "Tudo conferido."], "Histórico do /etc"),
            "Terminal mostrando o bora aplicar a receita Histórico do /etc: instala o etckeeper e confere cinco testes."),
        [("Já tenho o snapshot. Para que outro?", "O snapshot volta o sistema inteiro a como estava ontem. O histórico do <code>/etc</code> responde a uma pergunta menor: o que mudou na configuração desde que o Wi-Fi parou? Com ele, dá para ver a diferença de um arquivo e voltar só aquele, sem desfazer o resto."),
         ("Por que o Git?", "É a ferramenta que todo mundo que programa usa para guardar versões, e o <code>git log -p</code> mostra, linha por linha, o que cada programa e cada receita do <code>bora</code> mudou. Para quem está aprendendo, é um jeito de ver o sistema por dentro.")],
        [("pacote", "etckeeper", "Guarda o /etc no Git e avisa o apt antes e depois de cada instalação. Traz o git, se faltar."),
         ("arquivo", "/etc/.git e /etc/.etckeeper", "O histórico, com permissão só do root, e o dono e as permissões de cada arquivo."),
         ("relogio", "etckeeper.timer", "Um registro por dia do que mudou por fora do apt.")],
        [("sudo git -C /etc log --oneline", "A lista de registros, do mais novo para o mais velho."),
         ("sudo git -C /etc log -p -- fstab", "O histórico de um arquivo, com as linhas que mudaram."),
         ("sudo git -C /etc diff", "O que mudou desde o último registro.")],
        [("etckeeper", "Site do projeto", "https://etckeeper.branchable.com/"),
         ("etckeeper, na ArchWiki", "ArchWiki", "https://wiki.archlinux.org/title/Etckeeper")])


ILUSTRA_SEM_SNAP = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="isn-t">
            <title id="isn-t">À esquerda, o Firefox e o Thunderbird do Snap; à direita, o Firefox da Mozilla e o Thunderbird do Flathub, com os perfis levados de um lado para o outro.</title>
            <g class="pacote" style="--i:0">
              <rect x="20" y="30" width="190" height="200" rx="14" fill="none" stroke="var(--text-2)" stroke-width="2.2" stroke-dasharray="6 4"/>
              <text x="115" y="60" font-size="14" font-weight="600" text-anchor="middle">Snap</text>
              <text x="115" y="104" font-size="13" text-anchor="middle" class="t2">Firefox</text>
              <text x="115" y="134" font-size="13" text-anchor="middle" class="t2">Thunderbird</text>
              <text x="115" y="164" font-size="13" text-anchor="middle" class="t2">loja de aplicativos</text>
              <text x="115" y="206" font-size="12" text-anchor="middle" class="t2 mono">snapd sempre rodando</text>
            </g>
            <path d="M222 130h36" class="traco"/>
            <path d="M250 122l10 8-10 8" class="traco"/>
            <g class="pacote" style="--i:1">
              <rect x="270" y="30" width="190" height="200" rx="14" class="caixa-svg"/>
              <text x="365" y="60" font-size="14" font-weight="600" text-anchor="middle">No lugar</text>
              <text x="365" y="104" font-size="13" text-anchor="middle">Firefox da Mozilla</text>
              <text x="365" y="134" font-size="13" text-anchor="middle">Thunderbird do Flathub</text>
              <text x="365" y="164" font-size="13" text-anchor="middle">GNOME Software</text>
              <text x="365" y="206" font-size="12" text-anchor="middle" class="t2 mono">com os seus dados</text>
            </g>
            <g class="volta">
              <rect x="20" y="256" width="440" height="64" rx="14" class="caixa-svg"/>
              <text x="240" y="284" font-size="12.5" text-anchor="middle" class="mono">Package: snapd · Pin-Priority: -10</text>
              <text x="240" y="306" font-size="12.5" text-anchor="middle" class="t2">o apt não traz o Snap de volta</text>
            </g>
          </svg>"""


def pagina_sem_snap():
    return _pagina(
        "desktop/sem-snap", ILUSTRA_SEM_SNAP, "Ilustração. Os mesmos programas, de outra fonte, com os seus dados.",
        ["<strong>Tira o Snap do Ubuntu</strong> e impede que o apt o traga de volta.",
         "<strong>Troca o Firefox do Snap pelo da Mozilla</strong>, do repositório oficial, com a chave conferida, levando favoritos, senhas e extensões.",
         "<strong>Troca o Thunderbird do Snap pelo do Flathub</strong>, com os seus e-mails, e a loja do Snap pelo GNOME Software."],
        ["Só entra se você pedir: o padrão do rolê é deixar o Snap como está.",
         "Não tira um snap que não sabe trocar: ela para e diz qual é, sem mudar nada.",
         "Não apaga os seus perfis: as cópias ficam, mesmo depois do desfazer.",
         "Não mexe no Debian nem no Linux Mint, que já não usam o Snap: nelas, só bloqueia o apt."],
        ["<p>Confere se o pacote <code>snapd</code> e algum snap estão instalados, e se o apt ainda poderia trazer o <code>snapd</code> de volta.</p>",
         "<p>Recusa se houver um snap sem substituto. Liga o repositório da Mozilla antes de tirar qualquer coisa, copia os perfis para os lugares novos, remove os snaps e o <code>snapd</code>, bloqueia o <code>snapd</code> no apt e instala o Firefox e o Thunderbird no lugar.</p>",
         "<p>Confere que o <code>snapd</code> e os snaps saíram, que o apt recusa o <code>snapd</code>, que o Firefox vem de <code>packages.mozilla.org</code> e que os perfis estão nos lugares novos.</p>",
         "<p>Remove o que a receita instalou, apaga os arquivos do apt que ela criou, instala de volta o <code>snapd</code>, os metapacotes e os snaps de programas, e devolve os perfis para a pasta do Snap.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04, com um snap do Firefox, encurtada nas linhas do apt.", _saida("[7/8] Sem Snap", [
            "Atualizando a lista de pacotes, com o repositório da Mozilla.",
            "Perfil copiado para /home/aluno/.mozilla/firefox", "Removendo o snapd: snapd",
            "Arquivo atualizado: /etc/apt/preferences.d/bora-sem-snap.pref", "Instalando: firefox firefox-l10n-pt-br",
            "Pronto. O Snap saiu e não volta pelo apt.",
            ("ok", "o snapd não está instalado (dpkg -l snapd)"), ("ok", "nenhum snap ficou em /var/lib/snapd/snaps"),
            ("ok", "o apt não instala o snapd de volta (apt-cache policy snapd)"),
            ("ok", "o Firefox é o pacote da Mozilla (apt-cache policy firefox)"), ("ok", "os perfis copiados estão no lugar novo"),
            "Tudo conferido."], "Sem Snap"),
            "Terminal mostrando o bora aplicar a receita Sem Snap: liga o repositório da Mozilla, copia o perfil do Firefox, remove o snapd, bloqueia a volta dele e instala o Firefox da Mozilla, conferindo cinco testes."),
        [("O Snap é ruim?", "Não. Ele funciona e é o jeito do Ubuntu de entregar aplicativos. Mas cada snap é uma imagem montada no boot, os programas demoram mais para abrir na primeira vez e o <code>snapd</code> fica rodando o tempo todo. Com o Flatpak já ligado pelo rolê, são duas lojas fazendo o mesmo trabalho. Por isso é uma escolha sua, e não um conserto."),
         ("Por que o Firefox da Mozilla, e não o do Flathub?", "O repositório da Mozilla é o caminho que ela mesma recomenda para Debian e Ubuntu, entrega as atualizações no mesmo dia e continua lendo as políticas de <code>/etc/firefox/policies</code>, que o navegador enxuto usa. A chave é conferida pela impressão digital que a Mozilla publica."),
         ("Por que o risco alto?", "A receita mexe no navegador e nos metapacotes do Ubuntu. Ela para antes de mudar qualquer coisa quando encontra um snap sem substituto, quando tirar o <code>snapd</code> levaria um pacote que não é do Snap, ou quando o repositório da Mozilla não responde.")],
        [("pacote", "snapd (sai)", "Junto com os snaps e os pacotes de transição. Os metapacotes do Ubuntu saem, mas o que eles puxavam fica."),
         ("arquivo", "/etc/apt/preferences.d/bora-sem-snap.pref", "Prioridade -10 para o snapd: o apt não instala de volta."),
         ("arquivo", "/etc/apt/sources.list.d/mozilla.sources", "O repositório da Mozilla, com a chave em /etc/apt/keyrings e prioridade 1000 em preferences.d/mozilla.pref."),
         ("pacote", "firefox e firefox-l10n-pt-br", "O Firefox da Mozilla, em português."),
         ("copia", "~/.mozilla/firefox", "O perfil do Firefox, copiado de ~/snap/firefox antes de o Snap sair.")],
        [("snap list", "Depois da receita, responde que o comando não existe."),
         ("apt-cache policy snapd", "O candidato é (none): o apt não instala o snapd."),
         ("apt-cache policy firefox", "A versão instalada vem de packages.mozilla.org.")],
        [("Instalar o Firefox no Linux", "Mozilla", "https://support.mozilla.org/kb/install-firefox-linux"),
         ("apt_preferences(5)", "Manual do apt", "https://manpages.debian.org/stable/apt/apt_preferences.5.en.html")])


ILUSTRA_SSH = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="issh-t">
            <title id="issh-t">Um notebook da casa conecta por SSH na máquina antiga, pela rede local. Uma conexão vinda da internet fica de fora, barrada no firewall.</title>
            <rect x="20" y="40" width="170" height="110" rx="14" class="caixa-svg"/>
            <text x="105" y="76" font-size="14" font-weight="600" text-anchor="middle">Notebook</text>
            <text x="105" y="100" font-size="12" text-anchor="middle" class="t2 mono">ssh ana@192.168.0.20</text>
            <rect x="290" y="40" width="170" height="110" rx="14" class="caixa-svg"/>
            <text x="375" y="76" font-size="14" font-weight="600" text-anchor="middle">Máquina antiga</text>
            <text x="375" y="100" font-size="12" text-anchor="middle" class="t2">sem tela, num canto</text>
            <g class="pacote" style="--i:0">
              <path d="M190 95h100" class="traco"/>
              <text x="240" y="86" font-size="12" text-anchor="middle" class="t2">rede de casa</text>
            </g>
            <g class="volta">
              <rect x="20" y="190" width="440" height="130" rx="14" class="caixa-svg"/>
              <text x="44" y="220" font-size="12.5" class="mono">PermitRootLogin no</text>
              <text x="44" y="244" font-size="12.5" class="mono">PasswordAuthentication yes (ou no, só chave)</text>
              <text x="44" y="268" font-size="12.5" class="mono">MaxAuthTries 4</text>
              <text x="44" y="300" font-size="12.5" class="t2">firewall: porta 22 só para a rede local</text>
            </g>
          </svg>"""


def pagina_ssh():
    return _pagina(
        "seguranca/ssh", ILUSTRA_SSH, "Ilustração. A máquina da casa atende pelo terminal de outro computador, só pela rede local.",
        ["<strong>Liga o servidor SSH</strong>, para entrar nesta máquina pelo terminal de outro computador da casa.",
         "<strong>Fecha o que uma máquina de casa não precisa</strong>: o login do root, as senhas vazias e o encaminhamento de janelas.",
         "<strong>Libera só a rede local no firewall</strong>, quando ele está ligado.",
         "<strong>Aceita só chave, se você pedir</strong>, e só depois de conferir que a conta já tem uma."],
        ["Só entra se você pedir: o padrão do rolê é não ligar o SSH.",
         "Não abre porta para a internet. Para entrar de fora de casa, o caminho é uma VPN.",
         "Não desliga a senha numa conta sem chave, para ninguém ficar trancado do lado de fora.",
         "Não cria contas nem chaves por você."],
        ["<p>Confere se o <code>openssh-server</code> está instalado, se a configuração do <code>bora</code> está no lugar e, com o firewall ligado, se a rede local está liberada.</p>",
         "<p>Instala o servidor, escreve <code>/etc/ssh/sshd_config.d/10-bora.conf</code>, confere com <code>sshd -t</code> antes de recarregar, liga o SSH no boot e acrescenta a regra do firewall para a rede local.</p>",
         "<p>Confere a configuração válida, os valores que valem de verdade com <code>sshd -T</code>, o SSH ligado no boot, a porta 22 esperando conexões e a regra do firewall.</p>",
         "<p>Remove a regra do firewall e o arquivo da receita, desliga o que ela ligou e tira o <code>openssh-server</code>, se foi ela que instalou. Quem está conectado na hora continua.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04 com o firewall ligado, encurtada nas linhas do apt.", _saida("[7/7] Acesso por SSH na rede de casa", [
            "Instalando: openssh-server", "Arquivo atualizado: /etc/ssh/sshd_config.d/10-bora.conf",
            "Firewall: SSH liberado só para a rede local (192.168.0.0/24).", "Pronto. De outro computador da casa: ssh ana@192.168.0.20",
            ("ok", "servidor SSH instalado (openssh-server)"), ("ok", "o sshd aceita a configuração (sshd -t)"),
            ("ok", "o root não entra por SSH (PermitRootLogin no)"), ("ok", "entra com a senha da conta ou com chave (PasswordAuthentication yes)"),
            ("ok", "no máximo 4 tentativas por conexão (MaxAuthTries 4)"), ("ok", "o SSH liga junto com o computador (ssh.socket)"),
            ("ok", "o firewall libera o SSH só para a rede local"), "Tudo conferido."], "Acesso por SSH na rede de casa"),
            "Terminal mostrando o bora aplicar a receita Acesso por SSH: instala o servidor, escreve a configuração, libera a rede local no firewall e confere sete testes."),
        [("Para que SSH numa máquina antiga?", "Uma máquina antiga que vira servidor da casa costuma ficar num canto, sem tela nem teclado. O SSH é o jeito de cuidar dela de outro computador: atualizar, ver o espaço em disco, reiniciar um serviço."),
         ("Senha ou chave?", "A senha funciona na hora e serve para começar. A chave não dá para adivinhar e é o recomendado depois que você copiar a sua com <code>ssh-copy-id</code>. Aí é só rodar o <code>bora</code> de novo com <code>so_chave</code> em sim."),
         ("Por que só a rede local?", "Nenhuma receita do <code>bora</code> abre porta para a internet: depende do roteador, do provedor e do CGNAT, e uma porta de SSH aberta recebe tentativas de senha o dia inteiro. De fora de casa, use uma VPN, como o Tailscale.")],
        [("pacote", "openssh-server", "O servidor SSH. Cria as chaves do servidor na instalação."),
         ("arquivo", "/etc/ssh/sshd_config.d/10-bora.conf", "Sem login do root, sem senha vazia, no máximo 4 tentativas e, se você pedir, só chave."),
         ("servico", "ssh.socket ou ssh.service", "O SSH liga junto com o computador."),
         ("escudo", "Regra do ufw bora-ssh", "A porta 22 liberada só para a rede local, quando o firewall está ligado.")],
        [("ssh pessoa@endereço", "De outro computador da casa, com o endereço que ip -4 addr mostra."),
         ("sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication'", "Os valores que valem de verdade."),
         ("ssh-copy-id pessoa@endereço", "Copia a sua chave para a máquina, para depois usar só chave.")],
        [("sshd_config(5)", "OpenBSD", "https://man.openbsd.org/sshd_config"),
         ("SSH", "Wiki do Debian", "https://wiki.debian.org/SSH")])


PAGINAS.update({
    "sistema/etckeeper": pagina_etckeeper,
    "desktop/sem-snap": pagina_sem_snap,
    "seguranca/ssh": pagina_ssh,
})


# ---------------------------------------------------------------- rolê 4: vibecodar

ILUSTRA_FERRAMENTAS = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ife-t">
            <title id="ife-t">Quatro comandos que os agentes usam para entender um projeto: rg procura um texto, fd acha um arquivo, jq lê um JSON e gh fala com o GitHub.</title>
            <text x="20" y="28" font-size="14" font-weight="600">O que o agente roda para entender um projeto</text>
            """ + "".join(f'''<g class="pacote" style="--i:{i}">
              <rect x="20" y="{48 + i * 70}" width="440" height="56" rx="12" class="caixa-svg"/>
              <text x="40" y="{82 + i * 70}" font-size="14" font-weight="600" class="mono">{c}</text>
              <text x="200" y="{82 + i * 70}" font-size="13" class="t2">{d}</text>
            </g>''' for i, (c, d) in enumerate([("rg TODO", "procura um texto em tudo"), ("fd -e py", "acha os arquivos .py"),
                                                ("jq .versao", "lê um campo de um JSON"), ("gh pr create", "abre um pull request")])) + """
          </svg>"""


def pagina_ferramentas():
    return _pagina(
        "dev/ferramentas", ILUSTRA_FERRAMENTAS, "Ilustração. Sem essas ferramentas, o agente gasta tempo e tokens procurando outro caminho.",
        ["<strong>Instala o <code>ripgrep</code></strong>, o comando <code>rg</code>, que procura um texto em todos os arquivos de um projeto.",
         "<strong>Instala o <code>fd</code></strong>, que acha arquivos pelo nome, e cria o comando <code>fd</code>, que no Debian se chama <code>fdfind</code>.",
         "<strong>Instala o <code>jq</code></strong>, que lê e filtra JSON.",
         "<strong>Instala o GitHub CLI</strong>, o <code>gh</code>, para clonar, abrir pull requests e entrar no GitHub pelo terminal."],
        ["Não entra no GitHub por você: o <code>gh auth login</code> é seu.",
         "Não passa por cima de um <code>fd</code> que já exista em <code>/usr/local/bin</code>.",
         "Não vem de fora da distro: os quatro estão nos repositórios do Ubuntu e do Debian."],
        ["<p>Confere se os pacotes <code>ripgrep</code>, <code>fd-find</code>, <code>jq</code> e <code>gh</code> estão instalados e se existe o comando <code>fd</code>.</p>",
         "<p>Instala os pacotes que faltarem e cria o link <code>/usr/local/bin/fd</code> para o <code>fdfind</code>.</p>",
         "<p>Numa pasta de teste, procura um texto com <code>rg</code>, acha um arquivo com <code>fd</code>, lê um JSON com <code>jq</code> e roda <code>gh --version</code>.</p>",
         "<p>Apaga o link do <code>fd</code> e remove os pacotes que a receita instalou, menos o que outro programa passou a usar.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04, encurtada nas linhas do apt.", _saida("[6/11] Ferramentas do terminal", [
            "Instalando: ripgrep fd-find jq gh", "Comando criado: fd (o fdfind do Debian)",
            "Pronto: rg, fd, jq e gh instalados. Para entrar no GitHub pelo terminal: gh auth login",
            ("ok", "ripgrep acha um texto num projeto (rg)"), ("ok", "fd acha um arquivo pelo nome (fd)"),
            ("ok", "jq lê um JSON (jq)"), ("ok", "GitHub CLI (gh --version)"), "Tudo conferido."], "Ferramentas do terminal"),
            "Terminal mostrando o bora aplicar a receita Ferramentas do terminal: instala o ripgrep, o fd, o jq e o GitHub CLI e confere quatro testes."),
        [("Por que o agente precisa delas?", "Para entender um projeto, o agente procura textos e arquivos o tempo todo. O <code>rg</code> é muito mais rápido que o <code>grep -r</code> e pula o que está no <code>.gitignore</code>, como a pasta <code>node_modules</code>. Vários agentes procuram o <code>rg</code> primeiro."),
         ("Por que o <code>fd</code> se chama <code>fdfind</code>?", "No Debian, já existia outro programa com o nome <code>fd</code>. O pacote usa <code>fdfind</code>, e a receita cria o nome curto, que é o que os tutoriais e os agentes usam.")],
        [("pacote", "ripgrep, fd-find, jq e gh", "Dos repositórios da distro."),
         ("arquivo", "/usr/local/bin/fd", "Link para <code>/usr/bin/fdfind</code>.")],
        [("rg -n 'TODO'", "Mostra cada linha com TODO no projeto, com o número da linha."),
         ("fd -e py", "Lista os arquivos Python da pasta."),
         ("gh auth login", "Entra no GitHub pelo terminal, sem senha no Git.")],
        [("ripgrep", "GitHub", "https://github.com/BurntSushi/ripgrep"),
         ("fd", "GitHub", "https://github.com/sharkdp/fd"),
         ("GitHub CLI", "Manual", "https://cli.github.com/manual/")])


ILUSTRA_SEGREDOS = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ise-t">
            <title id="ise-t">Três arquivos indo para um commit. O .env nem entra, porque o Git ignora. O config.py com um token é barrado pelo gitleaks. O ola.py passa.</title>
            <text x="20" y="28" font-size="14" font-weight="600">git add . &amp;&amp; git commit</text>
            <g class="pacote" style="--i:0">
              <rect x="20" y="48" width="200" height="50" rx="12" class="caixa-svg"/>
              <text x="40" y="79" font-size="13.5" class="mono">.env</text>
              <text x="250" y="79" font-size="13" class="t2">ignorado pelo Git</text>
            </g>
            <g class="pacote" style="--i:1">
              <rect x="20" y="114" width="200" height="50" rx="12" fill="none" stroke="var(--vermelho)" stroke-width="2.4"/>
              <text x="40" y="145" font-size="13.5" class="mono">config.py</text>
              <text x="250" y="145" font-size="13" class="t2">barrado: tem um token</text>
            </g>
            <g class="pacote" style="--i:2">
              <rect x="20" y="180" width="200" height="50" rx="12" fill="none" stroke="var(--ok)" stroke-width="2.4"/>
              <text x="40" y="211" font-size="13.5" class="mono">ola.py</text>
              <text x="250" y="211" font-size="13" class="t2">passa</text>
            </g>
            <g class="volta">
              <rect x="20" y="252" width="440" height="72" rx="14" class="caixa-svg"/>
              <text x="40" y="282" font-size="13" class="mono">gitleaks protect --staged</text>
              <text x="40" y="306" font-size="12.5" class="t2">roda antes de cada commit, em todos os projetos</text>
            </g>
          </svg>"""


def pagina_segredos():
    return _pagina(
        "seguranca/segredos", ILUSTRA_SEGREDOS, "Ilustração. Duas barreiras: o Git nem oferece o .env, e o gitleaks confere o resto.",
        ["<strong>Confere cada commit com o gitleaks</strong> e barra o que leva uma chave de API, um token ou uma senha.",
         "<strong>Faz o Git ignorar os arquivos <code>.env</code></strong> e as chaves privadas em todos os projetos, inclusive os que você clonar depois.",
         "<strong>Mantém os ganchos de cada projeto</strong> funcionando: o gancho do bora chama o do projeto depois do gitleaks."],
        ["Não apaga segredos que já foram para o histórico: para isso, troque a chave no site do provedor.",
         "Não passa por cima de um <code>core.hooksPath</code> que você já tinha.",
         "Não roda nos projetos que definem os próprios ganchos com o husky ou o <code>core.hooksPath</code> do projeto.",
         "Não impede um <code>git commit --no-verify</code>, para quando o gitleaks errar."],
        ["<p>Confere se o <code>git</code> e o <code>gitleaks</code> estão instalados, se o arquivo de exclusões globais tem o bloco do bora e se o <code>core.hooksPath</code> aponta para os ganchos do bora.</p>",
         "<ul><li>Para, sem mudar nada, se a conta já usar outro <code>core.hooksPath</code>.</li><li>Acrescenta o bloco do bora ao <code>~/.config/git/ignore</code> (ou ao arquivo do <code>core.excludesFile</code>).</li><li>Cria <code>~/.config/git/ganchos-bora</code>, com o gancho e um link para cada nome de gancho, e configura o <code>core.hooksPath</code>.</li></ul>",
         "<p>Num repositório de teste, como a pessoa: um <code>.env</code> fica fora do Git, um commit com um token do GitHub inventado é barrado, um commit sem segredo passa e um gancho do próprio projeto continua rodando.</p>",
         "<p>Tira o <code>core.hooksPath</code> e o bloco do bora, apaga os ganchos e remove os pacotes que a receita instalou. As suas outras linhas ficam.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04, encurtada nas linhas do apt.", _saida("[7/11] Verificação de segredos", [
            "Instalando: gitleaks",
            "O Git de dani passa a ignorar .env e chaves em todos os projetos (/home/dani/.config/git/ignore).",
            "O gitleaks passa a conferir cada commit de dani (ganchos em /home/dani/.config/git/ganchos-bora).",
            ("ok", "gitleaks instalado (gitleaks version)"), ("ok", "um arquivo .env fica fora do Git (git check-ignore .env)"),
            ("ok", "um commit com um token do GitHub é barrado"), ("ok", "um commit sem segredo passa"),
            ("ok", "os ganchos do próprio projeto continuam rodando"), "Tudo conferido."], "Verificação de segredos"),
            "Terminal mostrando o bora aplicar a receita Verificação de segredos: instala o gitleaks, configura o Git e confere cinco testes, um deles barrando um commit com um token."),
        [("Por que não basta apagar o arquivo depois?", "A chave continua no histórico do Git, e num repositório público robôs acham em minutos. O único conserto é trocar a chave no site do provedor. Por isso o melhor é não deixar entrar."),
         ("Por que nos ganchos da conta, e não em cada projeto?", "Assim vale para todo projeto, inclusive os que você clonar amanhã, sem lembrar de instalar nada. O gancho do bora chama o <code>.git/hooks</code> de cada projeto depois, para não quebrar o que já existia."),
         ("E se o gitleaks errar?", "Ele às vezes acha que um texto de exemplo é uma chave. Confira o que ele apontou e, se for alarme falso, faça o commit com <code>git commit --no-verify</code>.")],
        [("pacote", "git e gitleaks", "Dos repositórios da distro."),
         ("arquivo", "~/.config/git/ignore", "Um bloco do bora com <code>.env</code>, <code>*.pem</code>, <code>*.key</code> e as chaves SSH."),
         ("arquivo", "~/.config/git/ganchos-bora", "O gancho e os links; o <code>core.hooksPath</code> aponta para cá.")],
        [("gitleaks detect", "Confere o projeto inteiro, com todo o histórico."),
         ("git check-ignore -v .env", "Mostra qual regra faz o Git ignorar o arquivo."),
         ("git config --global core.hooksPath", "Mostra a pasta dos ganchos da sua conta.")],
        [("gitleaks", "GitHub", "https://github.com/gitleaks/gitleaks"),
         ("Ganchos do Git", "Documentação do Git", "https://git-scm.com/docs/githooks"),
         ("gitignore", "Documentação do Git", "https://git-scm.com/docs/gitignore")])


ILUSTRA_CHAVES = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ich-t">
            <title id="ich-t">O arquivo de chaves fica em ~/.config, fora dos projetos, com permissão só da dona. Cada terminal novo carrega as chaves, e os agentes as encontram nas variáveis de ambiente.</title>
            <rect x="20" y="24" width="440" height="110" rx="14" class="caixa-svg"/>
            <text x="44" y="54" font-size="13" class="mono">~/.config/chaves-de-api/chaves.env</text>
            <text x="44" y="80" font-size="12.5" class="t2 mono">-rw------- dani</text>
            <text x="44" y="108" font-size="12.5" class="mono">OPENROUTER_API_KEY=sk-or-…</text>
            <path d="M240 134v34" class="traco"/>
            <g class="pacote" style="--i:0">
              <rect x="20" y="170" width="440" height="56" rx="12" class="caixa-svg"/>
              <text x="44" y="204" font-size="13" class="t2">cada terminal novo carrega as chaves (~/.bashrc)</text>
            </g>
            <g class="volta">
              <rect x="20" y="246" width="210" height="74" rx="14" fill="none" stroke="var(--ok)" stroke-width="2.4"/>
              <text x="125" y="290" font-size="13" text-anchor="middle">os agentes acham</text>
              <rect x="250" y="246" width="210" height="74" rx="14" fill="none" stroke="var(--vermelho)" stroke-width="2.4"/>
              <text x="355" y="282" font-size="13" text-anchor="middle">fora do Git</text>
              <text x="355" y="302" font-size="12.5" text-anchor="middle" class="t2">e de outras contas</text>
            </g>
          </svg>"""


def pagina_chaves():
    return _pagina(
        "ia/chaves-de-api", ILUSTRA_CHAVES, "Ilustração. A chave fica num lugar só, longe dos projetos.",
        ["<strong>Cria um arquivo para as chaves de API</strong> em <code>~/.config/chaves-de-api</code>, que só a sua conta abre.",
         "<strong>Carrega as chaves em cada terminal novo</strong>, onde os agentes as procuram.",
         "<strong>Diz onde criar cada chave</strong>, com o provedor que você escolheu no topo do arquivo."],
        ["Não recebe a sua chave pelo bora: o plano pode ir para o Git ou para uma IA, então você cola a chave no arquivo, depois.",
         "Não manda as chaves para lugar nenhum.",
         "Não apaga o arquivo no desfazer se você já colou alguma chave."],
        ["<p>Confere se a pasta e o arquivo existem, com as permissões 700 e 600 e a sua conta como dona, e se o <code>.bashrc</code> tem o bloco do bora.</p>",
         "<ul><li>Cria a pasta e o arquivo, se não existirem, já com a permissão só da pessoa.</li><li>Acrescenta ao <code>.bashrc</code> o bloco que carrega o arquivo.</li></ul>",
         "<p>Confere as permissões, que outra conta não lê o arquivo, que ele não tem erro de sintaxe e, com uma chave de teste num arquivo temporário, que a chave chega ao terminal.</p>",
         "<p>Tira o bloco do <code>.bashrc</code>. O arquivo só sai se continuar sem nenhuma chave.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04, com o OpenRouter escolhido.", _saida("[8/11] Chaves de API guardadas", [
            "Arquivo de chaves criado: /home/dani/.config/chaves-de-api/chaves.env",
            "Cada terminal novo de dani passa a carregar as chaves (/home/dani/.bashrc).",
            "Para usar a sua chave, abra o arquivo num editor, tire o # da linha OPENROUTER_API_KEY= e cole a chave depois do =.",
            ("ok", "a pasta das chaves só abre para dani (700)"), ("ok", "o arquivo das chaves só abre para dani (600)"),
            ("ok", "outra conta não consegue ler as chaves"), ("ok", "o arquivo das chaves não tem erro"),
            ("ok", "o .bashrc carrega as chaves em cada terminal novo"), ("ok", "uma chave do arquivo chega ao terminal (printenv)"),
            "Tudo conferido."], "Chaves de API guardadas"),
            "Terminal mostrando o bora aplicar a receita Chaves de API guardadas: cria o arquivo de chaves, liga o carregamento no .bashrc e confere seis testes."),
        [("Por que não no próprio projeto?", "Um <code>.env</code> no projeto é o caminho mais curto para a chave ir parar no GitHub. Fora de qualquer projeto, nenhum <code>git add</code> alcança."),
         ("Por que o bora não pergunta a chave?", "O plano do bora é um arquivo que pode ir para o Git, ser mostrado a uma IA ou aplicado em outra máquina. Uma chave ali vazaria. Você cola a chave direto no arquivo, num editor."),
         ("Qual provedor escolher?", "O OpenRouter dá acesso a vários modelos com uma chave só, alguns gratuitos. A DeepSeek costuma ser das mais baratas. Os planos mudam o tempo todo; confira na página de cada um.")],
        [("arquivo", "~/.config/chaves-de-api/chaves.env", "Permissão 600, com uma linha comentada por provedor."),
         ("arquivo", "~/.bashrc", "Um bloco do bora que carrega o arquivo em cada terminal novo.")],
        [("ls -l ~/.config/chaves-de-api", "Mostra que só você lê o arquivo (<code>-rw-------</code>)."),
         ("printenv OPENROUTER_API_KEY", "Num terminal novo, mostra se a chave chegou.")],
        [("Provedores no OpenCode", "Documentação do OpenCode", "https://opencode.ai/docs/providers/"),
         ("Chaves de API", "OpenRouter", "https://openrouter.ai/docs/api-keys")])


ILUSTRA_AGENTES = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="iag-t">
            <title id="iag-t">Cinco agentes, cada um com o seu comando, instalados na pasta ~/.local/bin da pessoa, sem sudo. Todos leem a skill do bora.</title>
            <text x="20" y="28" font-size="14" font-weight="600">~/.local/bin, na sua conta, sem sudo</text>
            """ + "".join(f'''<g class="pacote" style="--i:{i}">
              <rect x="{20 + (i % 3) * 150}" y="{48 + (i // 3) * 76}" width="136" height="60" rx="12" class="caixa-svg"/>
              <text x="{88 + (i % 3) * 150}" y="{75 + (i // 3) * 76}" font-size="13.5" font-weight="600" text-anchor="middle" class="mono">{c}</text>
              <text x="{88 + (i % 3) * 150}" y="{96 + (i // 3) * 76}" font-size="11.5" text-anchor="middle" class="t2">{d}</text>
            </g>''' for i, (c, d) in enumerate([("claude", "Anthropic"), ("codex", "OpenAI"), ("copilot", "GitHub"), ("opencode", "livre"), ("vibe", "Mistral")])) + """
            <g class="volta">
              <rect x="20" y="220" width="440" height="104" rx="14" class="caixa-svg"/>
              <text x="40" y="250" font-size="14" font-weight="600">A skill do bora</text>
              <text x="40" y="276" font-size="13" class="t2">O agente monta e valida o plano; quem aplica é você:</text>
              <text x="40" y="304" font-size="13" class="mono">sudo bora aplicar plano.yaml</text>
            </g>
          </svg>"""


def pagina_agentes():
    return _pagina(
        "ia/agentes", ILUSTRA_AGENTES, "Ilustração. Cada agente funciona com um tipo de conta; o rolê não depende de nenhum fabricante.",
        ["<strong>Instala os agentes que você escolher</strong>: Claude Code, Codex, Copilot CLI, OpenCode e Mistral Vibe.",
         "<strong>Na sua conta, sem sudo</strong>, pelos pacotes oficiais de cada fabricante no npm e no PyPI, que conferem a soma de cada arquivo.",
         "<strong>Ensina o bora aos agentes</strong>, com uma skill que mostra como montar e validar um plano sem rodar nada como root."],
        ["Não cria contas nem assina planos por você.",
         "Não roda instaladores do tipo <code>curl | sh</code>: por isso o Antigravity CLI, que só tem esse, ainda não entra.",
         "Não mexe num agente que você já instalou de outro jeito.",
         "Não apaga as configurações e os logins dos agentes no desfazer."],
        ["<p>Confere se o comando de cada agente escolhido existe na sessão da pessoa e se a skill do bora está nas duas pastas de skills.</p>",
         "<ul><li>Para cada agente que falta, roda como a pessoa <code>npm install -g</code> ou <code>pipx install</code>, e anota o que instalou.</li><li>Escreve a skill em <code>~/.claude/skills/bora</code> e em <code>~/.agents/skills/bora</code>.</li></ul>",
         "<p>Para cada agente: o comando responde a <code>--version</code> e está na conta da pessoa, e não na do root. A conversa de verdade precisa da sua conta, e fica com você.</p>",
         "<p>Desinstala os agentes que a receita instalou e apaga a skill, se ela não mudou.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04, com os cinco agentes, encurtada nas linhas do npm.", _saida("[9/11] Agentes de IA no terminal", [
            "Instalando @anthropic-ai/claude-code, do npm, em /home/dani/.local", "Instalado: claude (2.1.319 (Claude Code))",
            "Instalando @openai/codex, do npm, em /home/dani/.local", "Instalado: codex (codex-cli 0.167.0)",
            "Instalando mistral-vibe, do PyPI, com o pipx", "Instalado: vibe (vibe 3.1.0)",
            "Skill do bora instalada: /home/dani/.claude/skills/bora/SKILL.md",
            ("ok", "claude responde (claude --version)"), ("ok", "codex responde (codex --version)"),
            ("ok", "copilot responde (copilot --version)"), ("ok", "opencode responde (opencode --version)"),
            ("ok", "vibe responde (vibe --version)"), ("ok", "a skill do bora está em /home/dani/.claude/skills/bora"),
            "Tudo conferido."], "Agentes de IA no terminal"),
            "Terminal mostrando o bora aplicar a receita Agentes de IA no terminal: instala cinco agentes na conta da pessoa e a skill do bora, e confere que cada um responde."),
        [("Qual agente escolher?", "O OpenCode funciona com modelos gratuitos e com a chave de qualquer provedor, e é o padrão. O Codex funciona com a conta gratuita do ChatGPT, e o Copilot CLI, com o plano gratuito do Copilot. O Claude Code pede um plano pago do Claude ou crédito na API. Dá para instalar vários e testar."),
         ("Por que na minha conta, e não para o sistema?", "Assim nenhum agente roda como root, e eles conseguem se atualizar sozinhos, sem sudo, como vários fazem."),
         ("Por que a versão mais nova, e não uma fixa?", "Os agentes mudam toda semana, e uma versão antiga costuma parar de funcionar com o serviço do fabricante. A máquina virtual do CI confere os cinco toda semana."),
         ("O que é a skill do bora?", "Um arquivo que o agente lê quando o assunto aparece. Ela ensina a ver a máquina, montar e validar um plano, e sempre pedir para você aplicar. É a terceira porta do bora, a do agente.")],
        [("arquivo", "~/.local/bin", "Os comandos <code>claude</code>, <code>codex</code>, <code>copilot</code>, <code>opencode</code> e <code>vibe</code>, conforme a escolha."),
         ("arquivo", "~/.claude/skills/bora e ~/.agents/skills/bora", "A skill do bora, um <code>SKILL.md</code>.")],
        [("opencode", "Abre o OpenCode na pasta do projeto. Na primeira vez, escolha um modelo."),
         ("codex", "Abre o Codex; na primeira vez, ele pede para entrar com a conta do ChatGPT."),
         ("npm ls -g", "Lista os agentes instalados pelo npm na sua conta.")],
        [("Claude Code", "Anthropic", "https://docs.claude.com/en/docs/claude-code/setup"),
         ("Codex CLI", "OpenAI", "https://github.com/openai/codex"),
         ("Copilot CLI", "GitHub Docs", "https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli"),
         ("OpenCode", "Documentação", "https://opencode.ai/docs/"),
         ("Mistral Vibe", "GitHub", "https://github.com/mistralai/mistral-vibe")])


ILUSTRA_CAIXA = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ica-t">
            <title id="ica-t">O agente dentro de uma caixa: escreve na pasta do projeto, lê o sistema sem mudar nada, e não alcança as chaves SSH, o login do GitHub nem o sudo.</title>
            <rect x="20" y="24" width="440" height="190" rx="16" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-dasharray="8 5"/>
            <text x="44" y="54" font-size="13" class="mono">caixa opencode</text>
            <g class="pacote" style="--i:0">
              <rect x="44" y="72" width="190" height="56" rx="12" fill="none" stroke="var(--ok)" stroke-width="2.4"/>
              <text x="139" y="98" font-size="13" text-anchor="middle">~/projetos/site</text>
              <text x="139" y="118" font-size="12" text-anchor="middle" class="t2">escreve</text>
            </g>
            <g class="pacote" style="--i:1">
              <rect x="246" y="72" width="190" height="56" rx="12" class="caixa-svg"/>
              <text x="341" y="98" font-size="13" text-anchor="middle">o resto do sistema</text>
              <text x="341" y="118" font-size="12" text-anchor="middle" class="t2">só lê</text>
            </g>
            <text x="44" y="166" font-size="12.5" class="t2">sem sudo · sem /run · com internet, para falar com o modelo</text>
            <g class="volta">
              """ + "".join(f'''<rect x="{20 + i * 150}" y="240" width="140" height="80" rx="12" fill="none" stroke="var(--vermelho)" stroke-width="2.2"/>
              <text x="{90 + i * 150}" y="276" font-size="13" text-anchor="middle" class="mono">{c}</text>
              <text x="{90 + i * 150}" y="298" font-size="12" text-anchor="middle" class="t2">invisível</text>''' for i, c in enumerate(["~/.ssh", "~/.config/gh", "chaves.env"])) + """
            </g>
          </svg>"""


def pagina_caixa():
    return _pagina(
        "ia/caixa-de-areia", ILUSTRA_CAIXA, "Ilustração. Um comando errado do agente estraga, no máximo, a pasta do projeto, que está no Git.",
        ["<strong>Instala o comando <code>caixa</code></strong>, que roda qualquer agente dentro de uma caixa de areia do <code>bubblewrap</code>.",
         "<strong>Dentro dela, o agente escreve só na pasta do projeto</strong> e nas pastas dele, e lê o resto sem mudar nada.",
         "<strong>Esconde as suas chaves SSH</strong>, o GnuPG, o login do GitHub CLI e o arquivo de chaves de API, e não deixa usar sudo.",
         "<strong>Liga a caixa de areia do próprio Claude Code</strong>, se ele estiver instalado, e deixa a do Claude Code e a do Codex funcionarem no Ubuntu 24.04."],
        ["Não corta a internet: o agente precisa dela para falar com o modelo.",
         "Não abre na pasta pessoal inteira nem fora dela.",
         "Não usa o distrobox nem o toolbox, que montam a pasta pessoal inteira e não isolam.",
         "Não é uma máquina virtual: um defeito no kernel ainda alcançaria o sistema."],
        ["<p>Confere se o <code>bubblewrap</code> e o <code>socat</code> estão instalados, se o comando <code>caixa</code> é o da receita, se o perfil do AppArmor está lá (quando o sistema restringe os user namespaces) e se a caixa de areia do Claude Code está ligada (quando ele está instalado).</p>",
         "<ul><li>Instala os pacotes e escreve <code>/usr/local/bin/caixa</code>.</li><li>No Ubuntu 24.04 em diante, escreve e carrega o perfil <code>/etc/apparmor.d/bora-bwrap</code>.</li><li>Liga <code>sandbox.enabled</code> em <code>~/.claude/settings.json</code>, sem mexer no resto.</li></ul>",
         "<p>Como a pessoa, numa pasta de teste: dentro da caixa, escreve no projeto, não escreve fora, não lê um arquivo de mentira em <code>~/.ssh</code>, não usa sudo, e a caixa recusa abrir na pasta pessoal.</p>",
         "<p>Apaga o comando e o perfil, volta o <code>settings.json</code> do Claude Code e remove os pacotes que a receita instalou.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04.", _saida("[10/11] Caixa de areia para os agentes", [
            "Instalando: bubblewrap socat", "Arquivo atualizado: /usr/local/bin/caixa",
            "A caixa de areia do Claude Code foi ligada (/home/dani/.claude/settings.json).",
            ("ok", "o bubblewrap abre uma caixa de areia sem root"), ("ok", "dentro da caixa, o agente escreve na pasta do projeto"),
            ("ok", "dentro da caixa, ele não escreve fora do projeto"), ("ok", "dentro da caixa, ele não lê as chaves SSH"),
            ("ok", "dentro da caixa, o sudo não funciona"), ("ok", "a caixa não abre com a pasta pessoal inteira"),
            "Tudo conferido."], "Caixa de areia para os agentes"),
            "Terminal mostrando o bora aplicar a receita Caixa de areia para os agentes: instala o bubblewrap, o comando caixa, liga a caixa do Claude Code e confere sete testes."),
        [("Por que isolar um agente?", "Um modelo erra, entende mal, ou lê num arquivo do projeto uma instrução escondida para apagar algo ou mandar as suas chaves para fora. Na caixa, o estrago fica na pasta do projeto, que está no Git."),
         ("Por que o bubblewrap, e não um contêiner?", "O distrobox e o toolbox montam a pasta pessoal inteira e o sistema dentro do contêiner, então não isolam. O bubblewrap é a peça que o Flatpak usa para isolar os aplicativos, e a mesma que o Claude Code e o Codex usam no Linux."),
         ("E o <code>git push</code>?", "Dentro da caixa, o agente não vê a sua chave SSH. Faça o push fora, depois de conferir o que ele fez. É de propósito."),
         ("O que é o perfil do AppArmor?", "Do Ubuntu 24.04 em diante, só programas com um perfil podem criar o espaço isolado que a caixa usa. A receita escreve um para o bubblewrap, como o Ubuntu faz com o Flatpak, e só quando o sistema tem essa restrição.")],
        [("pacote", "bubblewrap e socat", "A caixa de areia e a ponte de rede que o Claude Code usa."),
         ("arquivo", "/usr/local/bin/caixa", "O comando que monta a caixa."),
         ("arquivo", "/etc/apparmor.d/bora-bwrap", "Só no Ubuntu 24.04 em diante."),
         ("arquivo", "~/.claude/settings.json", "<code>sandbox.enabled: true</code>, se o Claude Code estiver instalado.")],
        [("caixa --help", "Mostra o que fica dentro e fora da caixa."),
         ("cd ~/projetos/site && caixa opencode", "Roda o OpenCode isolado na pasta do projeto."),
         ("caixa bash", "Abre um terminal dentro da caixa, para ver com os próprios olhos.")],
        [("bubblewrap", "GitHub", "https://github.com/containers/bubblewrap"),
         ("Caixa de areia do Claude Code", "Anthropic", "https://docs.claude.com/en/docs/claude-code/sandboxing"),
         ("Restrição de user namespaces", "Ubuntu", "https://ubuntu.com/blog/ubuntu-23-10-restricted-unprivileged-user-namespaces")])


ILUSTRA_EDITOR = """          <svg class="ilustra" viewBox="0 0 480 340" role="img" aria-labelledby="ied-t">
            <title id="ied-t">Quatro opções de editor: só o terminal, o VS Code do repositório da Microsoft, e o VSCodium e o Zed do Flathub.</title>
            <text x="20" y="28" font-size="14" font-weight="600">Qual editor?</text>
            """ + "".join(f'''<g class="pacote" style="--i:{i}">
              <rect x="20" y="{48 + i * 70}" width="440" height="56" rx="12" class="caixa-svg"/>
              <text x="40" y="{82 + i * 70}" font-size="14" font-weight="600">{c}</text>
              <text x="200" y="{82 + i * 70}" font-size="13" class="t2">{d}</text>
            </g>''' for i, (c, d) in enumerate([("Só o terminal", "nada novo para instalar"), ("VS Code", "repositório da Microsoft"),
                                                ("VSCodium", "Flathub, sem telemetria"), ("Zed", "Flathub, leve e rápido")])) + """
          </svg>"""


def pagina_editor():
    return _pagina(
        "dev/editor", ILUSTRA_EDITOR, "Ilustração. Dá para vibecodar só no terminal; o editor ajuda a ler o que o agente escreveu.",
        ["<strong>Instala o VS Code</strong> do repositório oficial da Microsoft, com a chave conferida pela impressão digital publicada.",
         "<strong>Ou o VSCodium ou o Zed</strong>, do Flathub, publicados pelos próprios projetos.",
         "<strong>Ou nada</strong>, se você escolher ficar só no terminal."],
        ["Não instala extensões: as dos agentes você escolhe dentro do editor.",
         "Não usa o VS Code do Flathub, que não é da Microsoft e cujo terminal não enxerga os agentes.",
         "Não apaga as suas configurações e extensões no desfazer."],
        ["<p>Com o VS Code, confere se o pacote <code>code</code> está instalado e se o repositório da Microsoft está como a receita escreve. Com o VSCodium ou o Zed, se o aplicativo está instalado pelo Flathub.</p>",
         "<ul><li>VS Code: baixa a chave, confere a impressão digital, escreve <code>/etc/apt/sources.list.d/vscode.sources</code> e instala o <code>code</code>. Se a chave não for a publicada, nada muda.</li><li>VSCodium ou Zed: instala do Flathub, que precisa estar ligado.</li></ul>",
         "<p>VS Code: o pacote veio da Microsoft, a chave é a publicada e <code>code --version</code> responde. VSCodium ou Zed: o <code>flatpak info</code> acha o aplicativo.</p>",
         "<p>Remove o editor e, no VS Code, o repositório e a chave da Microsoft.</p>"],
        _no_terminal("A saída de um teste no Ubuntu 24.04, com o VS Code, encurtada nas linhas do apt.", _saida("[11/11] Editor de código", [
            "Arquivo atualizado: /etc/apt/keyrings/packages.microsoft.asc", "Arquivo atualizado: /etc/apt/sources.list.d/vscode.sources",
            "Atualizando a lista de pacotes, com o repositório da Microsoft.", "Instalando: code",
            ("ok", "VS Code instalado pelo repositório da Microsoft"), ("ok", "a chave da Microsoft é a publicada (BC528686B50D79E339D3721CEB3E94ADBE1229CF)"),
            ("ok", "o VS Code responde (code --version)"), "Tudo conferido."], "Editor de código"),
            "Terminal mostrando o bora aplicar a receita Editor de código com o VS Code: confere a chave da Microsoft, liga o repositório, instala e confere três testes."),
        [("Por que o VS Code vem da Microsoft, e não do Flathub?", "O do Flathub é empacotado por voluntários, e o terminal dele roda dentro do Flatpak, sem enxergar os agentes instalados na sua conta. O repositório da Microsoft é o caminho que ela recomenda, e a receita confere a chave como faz com o Firefox da Mozilla."),
         ("VS Code ou VSCodium?", "O código é o mesmo. O VSCodium tira a telemetria e a marca da Microsoft, mas usa outra loja de extensões, que nem sempre tem as extensões oficiais dos agentes."),
         ("E o terminal no VSCodium e no Zed?", "No Flathub, o terminal integrado pode rodar dentro do Flatpak. Se o agente não aparecer nele, use o terminal do sistema, ao lado do editor.")],
        [("arquivo", "/etc/apt/keyrings/packages.microsoft.asc", "A chave da Microsoft, só com o VS Code."),
         ("arquivo", "/etc/apt/sources.list.d/vscode.sources", "O repositório do VS Code."),
         ("pacote", "code, com.vscodium.codium ou dev.zed.Zed", "O editor escolhido.")],
        [("code .", "Abre o VS Code na pasta do projeto."),
         ("apt-cache policy code", "Mostra que o VS Code vem de packages.microsoft.com.")],
        [("VS Code no Linux", "Microsoft", "https://code.visualstudio.com/docs/setup/linux"),
         ("VSCodium", "Flathub", "https://flathub.org/apps/com.vscodium.codium"),
         ("Zed", "Flathub", "https://flathub.org/apps/dev.zed.Zed")])


PAGINAS.update({
    "dev/ferramentas": pagina_ferramentas,
    "seguranca/segredos": pagina_segredos,
    "ia/chaves-de-api": pagina_chaves,
    "ia/agentes": pagina_agentes,
    "ia/caixa-de-areia": pagina_caixa,
    "dev/editor": pagina_editor,
})
