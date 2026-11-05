# Páginas das receitas prontas.
from comum import REPO, ladrilho, cabeca, janela, bloco_pedidos, P
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
        if p.get("tipo") == "escolha":
            rot = p.get("rotulos") or {}
            ops = "".join(f"<li><code>{o}</code>{': ' + rot[o] if o in rot else ''}</li>" for o in p["opcoes"])
            o_que += f'<ul style="margin:8px 0 0;padding-left:18px">{ops}</ul>'
        linhas.append(f"<tr><td><code>{nome}</code></td><td><code>{padrao}</code></td><td>{o_que}</td></tr>")
    ps = list((r.get("parametros") or {}).items())
    ordem = {"escolha": 0, "booleano": 1, "inteiro": 2}
    exemplo_nome, exemplo_valor = sorted(ps, key=lambda kv: ordem.get(kv[1].get("tipo"), 9))[0]
    tipo = exemplo_valor.get("tipo")
    valor = {"escolha": (exemplo_valor.get("opcoes") or ["", ""])[1], "booleano": "nao", "inteiro": "7"}.get(tipo, "auto")
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
        <p class="nota"><strong>Testada</strong> quer dizer que a receita passou em teste automático nessa família. Ela ainda não rodou numa máquina virtual nem num computador de verdade; o <code>bora</code> avisa isso quando monta o plano. <a href="{REPO}/blob/main/CONTRIBUTING.md#antes-de-abrir-um-pull-request">Testar numa máquina sua</a> é uma das ajudas mais valiosas.</p>
      </div>'''


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
            <span class="ficha feito testada">Testada no Ubuntu e no Debian</span>
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
        ("Restricted formats", "Documentação do Ubuntu", "https://help.ubuntu.com/community/RestrictedFormats"),
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



PAGINAS = {
    "base/atualizar": pagina_atualizar,
    "sistema/snapshot": pagina_snapshot,
    "seguranca/firewall": pagina_firewall,
    "desktop/codecs": pagina_codecs,
    "desktop/flatpak": pagina_flatpak,
    "sistema/backup-pessoal": pagina_backup,
}
