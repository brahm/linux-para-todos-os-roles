# Páginas dos rolês e a página do catálogo.
import math
from comum import REPO, ICONES, ladrilho, cabeca, janela, bloco_pedidos, P, pedido
from dados import RECEITAS, PRONTAS, ROLES, PUBLICOS, AREAS
from receitas import etapas, faz_nao, porques, secao, ICONE_ETAPA

ICONE_ETAPA.update({
    "menu": '<path d="M4 6.5h16M4 12h16M4 17.5h16"/>',
    "pergunta": '<path d="M4.5 5h15a1 1 0 0 1 1 1v9.5a1 1 0 0 1-1 1H10l-4.5 3.5v-3.5h-1a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/><path d="M10 9a2 2 0 1 1 2.6 1.9c-.4.2-.6.5-.6.9v.4M12 14h.01"/>',
    "plano": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h4"/>',
    "foto": '<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M8.5 7l1.5-3h4l1.5 3"/><circle cx="12" cy="13.5" r="3.6"/>',
    "receitas": '<path d="M9 6.5h11M9 12h11M9 17.5h11M4.5 6.5l1 1 2-2M4.5 12l1 1 2-2M4.5 17.5l1 1 2-2"/>',
    "pronto": '<path d="M5 21V4M5 4h12l-2.5 4L17 12H5"/>',
})


def link_receita(rid):
    return "../receitas/" + rid.replace("/", "-") + ".html"


def trilha(r):
    """Ilustração: pegadas passando por cada receita do rolê, em ordem."""
    itens = r["receitas"]
    n = len(itens)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = 50 + t * 380
        y = 196 - t * 104 + (30 if i % 2 else -30) * (1 if n > 4 else 0.6)
        pts.append((x, y))
    partes = []
    k = 0
    for i in range(n - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) + 90
        dist = math.hypot(x2 - x1, y2 - y1)
        livre = dist - 64
        passos = max(2, int(livre / 15))
        for j in range(passos):
            f = (32 + livre * (j + 0.5) / passos) / dist
            px, py = x1 + (x2 - x1) * f, y1 + (y2 - y1) * f
            lado = 5 if j % 2 else -5
            nx, ny = -math.sin(math.radians(ang - 90)) * lado, math.cos(math.radians(ang - 90)) * lado
            partes.append(f'<use href="#pegada" class="pe" style="--i:{k}; color:color-mix(in srgb, var(--accent) 50%, transparent)" x="{px + nx - 7:.1f}" y="{py + ny - 7:.1f}" width="14" height="14" transform="rotate({ang:.1f} {px + nx:.1f} {py + ny:.1f})"/>')
            k += 1
        partes.append("")
    paradas = []
    kk = 0
    for i, ((x, y), (rid, nota)) in enumerate(zip(pts, itens)):
        nome, icone, cor, _ = RECEITAS[rid]
        pronta = rid in PRONTAS
        atraso = int(i * (k / max(1, n - 1))) if n > 1 else 0
        traco = "var(--accent)" if pronta else "var(--text-2)"
        dash = "" if pronta else ' stroke-dasharray="4 4"'
        fundo = "var(--accent-soft)" if pronta else "var(--surface-2)"
        paradas.append(f'''<g class="parada" style="--i:{atraso}">
              <circle cx="{x:.1f}" cy="{y:.1f}" r="25" fill="{fundo}" stroke="{traco}" stroke-width="2.2"{dash}/>
              <svg x="{x - 13:.1f}" y="{y - 13:.1f}" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="{traco}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ICONES[icone]}</svg>
              <circle cx="{x + 19:.1f}" cy="{y - 19:.1f}" r="10" fill="{traco}"/>
              <text x="{x + 19:.1f}" y="{y - 15:.1f}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:var(--surface)">{i + 1}</text>
            </g>''')
    x0, y0 = pts[0]
    xn, yn = pts[-1]
    return f'''          <svg class="ilustra trilha-role" viewBox="0 0 480 270" role="img" aria-labelledby="tr-t">
            <title id="tr-t">Uma trilha de pegadas que passa, em ordem, pelas {n} receitas do rolê. As de contorno cheio já estão prontas; as tracejadas ainda estão planejadas.</title>
            {"".join(partes)}
            {"".join(paradas)}
            <text x="{x0:.1f}" y="{y0 + 44:.1f}" font-size="12.5" font-weight="600" text-anchor="middle" class="t2">sudo bora</text>
            <g class="parada" style="--i:{k}"><path d="M{xn - 4:.1f} {yn - 34:.1f}v-34l20 8-20 8" fill="var(--accent)" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"/></g>
          </svg>'''


def estacoes(r):
    itens = []
    for i, (rid, nota) in enumerate(r["receitas"]):
        nome, icone, cor, desc = RECEITAS[rid]
        pronta = rid in PRONTAS
        nota_html = f" · {nota}" if nota else ""
        ficha = '<span class="ficha feito">Pronta</span>' if pronta else '<span class="ficha planejado">Planejada</span>'
        conteudo = f'''{ladrilho(icone, cor)}
          <span><strong>{i + 1}. {nome}</strong><span class="d">{desc} <code>{rid}</code>{nota_html}</span></span>
          {ficha}'''
        if pronta:
            itens.append(f'        <li><a class="cartao estacao revelar" href="{link_receita(rid)}">\n          {conteudo}\n        </a></li>')
        else:
            itens.append(f'        <li><div class="cartao estacao planejada revelar">\n          {conteudo}\n        </div></li>')
    return '      <ol class="estacoes">\n' + "\n".join(itens) + "\n      </ol>"


def status_ficha(r):
    prontas = sum(1 for rid, _ in r["receitas"] if rid in PRONTAS)
    total = len(r["receitas"])
    if prontas == total:
        return f'<span class="ficha agora">Para testar · {total} de {total} receitas prontas</span>'
    if r["status"] == "em-construcao":
        return f'<span class="ficha agora">Em construção · {prontas} de {total} prontas</span>'
    if prontas:
        return f'<span class="ficha planejado">Planejado · {prontas} de {total} prontas</span>'
    return '<span class="ficha planejado">Planejado</span>'


def pagina_role(r):
    rid = r["id"]
    prontas = [x for x, _ in r["receitas"] if x in PRONTAS]
    publicos = "".join(f'<span class="ficha">{PUBLICOS[p]}</span>' for p in r["para_quem"])
    corpo = [f'''    <div class="abertura interna">
      <div class="largura">
        <div>
          <ol class="migalhas" aria-label="Onde você está">
            <li><a href="../">Rolês e receitas</a></li>
            <li><a href="../#roles">Rolês</a></li>
            <li aria-current="page">{r['nome']}</li>
          </ol>
          <h1>{ladrilho(r['icone'], r['cor'])}<span>{r['nome']}</span></h1>
          <p class="lema">{r['resumo']}</p>
          <div class="fichas">
            {status_ficha(r)}
            {publicos}
            <span class="ficha">{r['hardware']}</span>
          </div>
          <div class="acoes">
            <a class="botao principal" href="#receitas">Ver as receitas</a>
            <a class="botao secundario" href="#passo-a-passo">Como o bora leva você até lá</a>
          </div>
        </div>
        <figure class="palco" style="margin:0" data-anima>
{trilha(r)}
          <figcaption>Cada parada é uma receita, aplicada nesta ordem.{"" if len(prontas) == len(r["receitas"]) else " As tracejadas ainda não existem."}</figcaption>
        </figure>
      </div>
    </div>''']

    if r["status"] == "planejado":
        aviso = ("Este rolê ainda está no papel. As receitas tracejadas não existem, e os detalhes podem mudar."
                 + (f" As receitas prontas ({', '.join(RECEITAS[x][0] for x in prontas)}) já funcionam hoje, como receitas avulsas no menu do <code>bora</code>." if prontas else ""))
    elif len(prontas) == len(r["receitas"]):
        aviso = ("Todas as receitas deste rolê existem, e ele já aparece no menu do <code>bora</code>. "
                 "Elas passaram nos testes automáticos em contêiner, mas ainda não numa máquina virtual nem num computador de verdade. Use numa máquina que possa ser formatada sem dor.")
    else:
        aviso = (f"Faltam {len(r['receitas']) - len(prontas)} receitas para este rolê aparecer completo no menu. "
                 f"As {len(prontas)} prontas já funcionam hoje, como receitas avulsas no menu do <code>bora</code>.")
    corpo.append(f'''    <section id="resumo" class="largura">
{cabeca("Em resumo", "O que faz e o que não faz", aviso)}
{faz_nao(r['faz'], r['nao_faz'], "O que o rolê faz", "O que ele não faz")}
    </section>''')

    perguntas = ""
    if r["perguntas"]:
        perguntas = "<p>Para este rolê, o <code>bora</code> pergunta:</p><ul>" + "".join(f"<li>{q}</li>" for q in r["perguntas"]) + "</ul>"
    else:
        perguntas = "<p>Este rolê não faz perguntas além das que cada receita precisa, e todas têm um padrão pensado para quem está começando.</p>"
    lista = [
        ("menu", "azul", "Escolha o rolê", "no menu",
         "<p>Rode <code>sudo bora</code> no terminal. O menu mostra só os rolês que cabem na sua máquina e na sua distro, e você escolhe pelo número.</p>"),
        ("pergunta", "azul", "Responda o que for preciso", "em português", perguntas),
        ("plano", "", "Revise o plano", "nada mudou ainda",
         "<p>O <code>bora</code> mostra o plano: as receitas, na ordem, com os parâmetros. Você pode aplicar agora, só simular, ou salvar o plano para revisar com calma, versionar ou aplicar em outra máquina.</p>"),
        ("foto", "", "Snapshot antes de mudar", "o ponto de volta",
         "<p>Se o snapshot do sistema já estiver configurado, o <code>bora</code> tira uma foto do sistema antes da primeira mudança. Se o próprio rolê configura o snapshot, as próximas mudanças já ganham o ponto de volta.</p>"),
        ("receitas", "", "Uma receita de cada vez", "verificar, aplicar, testar",
         f"<p>Cada receita primeiro verifica se já está aplicada, e pula se estiver. Depois aplica e testa. Se uma falhar, o <code>bora</code> para ali, diz o que aconteceu e como voltar. As {len(r['receitas'])} receitas deste rolê estão logo abaixo.</p>"),
        ("pronto", "verde", "Pronto quando", "o teste que qualquer pessoa faz", f"<p>{r['pronto_quando']}</p>"),
        ("desfazer", "cinza", "Para voltar atrás", "sudo bora desfazer", f"<p>{r['como_desfazer']}</p>"),
    ]
    corpo.append(secao("passo-a-passo", "Passo a passo", "Como o bora leva você até lá", "", etapas(lista)))

    if rid == "pronto-para-estudar":
        corpo.append(f'''    <section class="largura" aria-label="O menu de verdade">
{cabeca("No terminal", "O menu, hoje", "O rolê aparece no menu, faz as duas perguntas que precisa e mostra o plano antes de mudar qualquer coisa. Esta é a saída de verdade do bora, encurtada nas descrições.")}
      <figure style="margin:0">
{janela("sudo bora", [
            ("cmd", P + '<span class="c">sudo bora</span>'),
            ("", '<span class="c">bora 0.3.0 · Linux para todos os rolês</span>'),
            ("", '<span class="d">Ubuntu 26.04.1 LTS, família ubuntu, 8 GB de RAM, 120 GB livres</span>'),
            ("", ""),
            ("", 'O que você quer fazer com este computador?'),
            ("", '   1. Dar vida nova a uma máquina antiga  <span class="d">Um computador de dez anos atrás voltando a abrir o navegador…</span>'),
            ("", '   2. Pronto para estudar e trabalhar  <span class="d">O computador atualizado, protegido e com um jeito fácil de voltar atrás se algo der errado.</span>'),
            ("", '   3. Receitas avulsas  <span class="d">escolher uma ou mais receitas do catálogo</span>'),
            ("", '   4. Ver o diagnóstico completo'),
            ("", '   5. Desfazer a última aplicação'),
            ("", '   6. Montar uma pergunta para a IA  <span class="d">bora ajuda</span>'),
            ("", '   7. Sair'),
            ("cmd", 'Número: <span class="c">2</span>'),
            ("", 'Sistema atualizado: Instalar as atualizações de segurança sozinho, todo dia? [S/n] <span class="c">s</span>'),
            ("", 'Backup da pasta pessoal: Em que disco externo guardar a cópia? "auto" usa o disco USB conectado agora; ou informe a partição, como /dev/sdb1. [auto]: <span class="c">auto</span>'),
            ("", ""),
            ("", 'Plano: pronto-para-estudar'),
            ("", '  1. Sistema atualizado'),
            ("", '  2. Firewall · risco médio  <span class="d">perfil=desktop</span>'),
            ("", '  3. Snapshot do sistema · risco médio'),
            ("", '  4. Codecs de áudio e vídeo'),
            ("", '  5. Flatpak e Flathub'),
            ("", '  6. Backup da pasta pessoal · risco médio  <span class="d">destino=auto, manter=7</span>'),
            ("", ""),
            ("", 'O que fazer com o plano?'),
            ("", '   1. Aplicar agora  <span class="d">pede a senha de administrador</span>'),
            ("", '   2. Só simular  <span class="d">mostra o que mudaria, sem mudar nada</span>'),
            ("", '   3. Salvar para depois  <span class="d">para revisar, versionar ou aplicar em outra máquina</span>'),
            ("", '   4. Voltar'),
            ("", 'Número [1]: <span class="cursor"></span>'),
        ], "Terminal mostrando o menu do bora: o rolê Pronto para estudar e trabalhar é escolhido, o bora faz duas perguntas e mostra o plano com as seis receitas.")}
      </figure>
    </section>''')

    if rid == "maquina-antiga":
        corpo.append(f'''    <section class="largura" aria-label="O menu de verdade">
{cabeca("No terminal", "O menu, hoje", "O rolê aparece no menu, faz quatro perguntas, todas com um padrão, e mostra o plano antes de mudar qualquer coisa. Esta é a saída de verdade do bora, encurtada nas descrições, numa máquina de 4 GB.")}
      <figure style="margin:0">
{janela("sudo bora", [
            ("cmd", P + '<span class="c">sudo bora</span>'),
            ("", '<span class="c">bora 0.3.0 · Linux para todos os rolês</span>'),
            ("", '<span class="d">Debian GNU/Linux 13 (trixie), família debian, 3.8 GB de RAM, 96 GB livres</span>'),
            ("", ""),
            ("", 'O que você quer fazer com este computador?'),
            ("", '   1. Dar vida nova a uma máquina antiga  <span class="d">Um computador de dez anos atrás voltando a abrir o navegador e os vídeos sem travar.</span>'),
            ("", '   2. Pronto para estudar e trabalhar  <span class="d">O computador atualizado, protegido e com um jeito fácil de voltar atrás…</span>'),
            ("", '   <span class="d">…</span>'),
            ("cmd", 'Número: <span class="c">1</span>'),
            ("", 'Sistema atualizado: Instalar as atualizações de segurança sozinho, todo dia? [S/n] <span class="c">s</span>'),
            ("", 'Ambiente gráfico leve: Qual ambiente leve você quer?'),
            ("", '   1. xfce  <span class="d">Xfce. Leve, completo e com cara de sempre; o mais fácil para quem vem do Windows.</span>'),
            ("", '   2. lxqt  <span class="d">LXQt. Ainda mais leve, para máquinas com 2 GB de memória ou menos.</span>'),
            ("", 'Número [1]: <span class="c">1</span>'),
            ("", 'Ambiente gráfico leve: Passar a entrar no ambiente leve por padrão? Com não, ele só aparece como opção na tela de login. [s/N] <span class="c">s</span>'),
            ("", 'Navegador enxuto: Instalar o bloqueador de anúncios uBlock Origin no Firefox? [S/n] <span class="c">s</span>'),
            ("", 'Serviços enxutos: Manter o boot esperando a rede conectar? Só faz falta em quem monta pastas da rede ao ligar. [s/N] <span class="c">n</span>'),
            ("", ""),
            ("", 'Plano: maquina-antiga'),
            ("", '  1. Sistema atualizado  <span class="d">automaticas=sim</span>'),
            ("", '  2. Snapshot do sistema · risco médio  <span class="d">dispositivo=auto, diarios=5, semanais=3</span>'),
            ("", '  3. Memória comprimida (zram)  <span class="d">porcentagem=50</span>'),
            ("", '  4. Ambiente gráfico leve  <span class="d">ambiente=xfce, entrar_no_leve=sim</span>'),
            ("", '  5. Navegador enxuto  <span class="d">bloquear_anuncios=sim</span>'),
            ("", '  6. Serviços enxutos  <span class="d">esperar_rede=não</span>'),
            ("", ""),
            ("", 'O que fazer com o plano?'),
            ("", '   1. Aplicar agora  <span class="d">pede a senha de administrador</span>'),
            ("", '   2. Só simular  <span class="d">mostra o que mudaria, sem mudar nada</span>'),
            ("", '   3. Salvar para depois  <span class="d">para revisar, versionar ou aplicar em outra máquina</span>'),
            ("", '   4. Voltar'),
            ("", 'Número [1]: <span class="cursor"></span>'),
        ], "Terminal mostrando o menu do bora: o rolê Dar vida nova a uma máquina antiga é escolhido, o bora faz quatro perguntas e mostra o plano com as seis receitas.")}
      </figure>
    </section>''')

    corpo.append(secao("receitas", "As receitas", f"{len(r['receitas'])} receitas, nesta ordem", "Toque numa receita pronta para ver o passo a passo dela. Os ids das planejadas são provisórios.", estacoes(r)))
    corpo.append(secao("porques", "Os porquês", "Por que assim", "", porques(r["porques"])))
    corpo.append(bloco_pedidos(rid, "este rolê", "neste rolê", editar=f"{REPO}/blob/main/objetivos/README.md"))
    return "\n\n".join(corpo)


# ---------------------------------------------------------------- catálogo

CICLO = '''          <svg class="ilustra ciclo" viewBox="0 0 500 220" role="img" aria-labelledby="ci-t">
            <title id="ci-t">As quatro etapas de toda receita: verificar, aplicar, testar e, quando você pedir, desfazer.</title>
            <path d="M70 110 C70 40, 190 40, 190 110 C190 40, 310 40, 310 110 C310 40, 430 40, 430 110" class="traco tracejado"/>
            <path d="M430 150 C 430 200, 70 200, 70 150" class="traco tracejado" style="stroke:var(--text-2);opacity:.6"/>
            <text x="250" y="212" font-size="12.5" text-anchor="middle" class="t2">desfazer volta pelo mesmo caminho, na ordem contrária</text>
            ''' + "".join(
    f'''<g class="no" style="--i:{i}">
              <circle cx="{x}" cy="110" r="36" fill="{f}" />
              <svg x="{x - 16}" y="{94}" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ICONE_ETAPA[k]}</svg>
              <text x="{x}" y="166" font-size="14" font-weight="600" text-anchor="middle">{t}</text>
            </g>''' for i, (x, k, t, f, c) in enumerate([
        (70, "verificar", "Verificar", "var(--azul-soft)", "var(--azul)"),
        (190, "aplicar", "Aplicar", "var(--accent-soft)", "var(--link)"),
        (310, "testar", "Testar", "var(--ok-soft)", "var(--ok)"),
        (430, "desfazer", "Desfazer", "var(--surface-2)", "var(--text-2)"),
    ])) + '''
            <circle r="7" class="bolinha laranja"/>
          </svg>'''


def cartao_role(r):
    return f'''        <a class="cartao role revelar" href="roles/{r['id']}.html">
          {ladrilho(r['icone'], r['cor'])}
          <h3>{r['nome']}</h3>
          <p>{r['resumo']}</p>
          <div class="rodape"><span class="num">{r['num']}</span>{status_ficha(r)}</div>
        </a>'''


def pagina_catalogo():
    usos = {}
    for r in ROLES:
        for rid, _ in r["receitas"]:
            usos.setdefault(rid, []).append(r)
    por_area = {}
    for rid in RECEITAS:
        por_area.setdefault(rid.split("/")[0], []).append(rid)
    areas = []
    for area, nome_area in AREAS.items():
        ids = sorted(por_area.get(area, []), key=lambda x: (x not in PRONTAS, x))
        if not ids:
            continue
        itens = []
        for rid in ids:
            nome, icone, cor, desc = RECEITAS[rid]
            nomes_roles = ", ".join(r["nome"] for r in usos.get(rid, []))
            em = f' Entra em: {nomes_roles}.' if nomes_roles else ""
            if rid in PRONTAS:
                itens.append(f'''          <li><a class="cartao estacao revelar" href="receitas/{rid.replace('/', '-')}.html">
            {ladrilho(icone, cor)}
            <span><strong>{nome}</strong><span class="d">{desc} <code>{rid}</code></span></span>
            <span class="ficha feito">Pronta</span>
          </a></li>''')
            else:
                itens.append(f'''          <li><div class="cartao estacao planejada">
            {ladrilho(icone, cor)}
            <span><strong>{nome}</strong><span class="d">{desc}{em}</span></span>
            <span class="ficha planejado">Planejada</span>
          </div></li>''')
        areas.append(f'''        <div class="area">
          <h3>{nome_area} <code>{area}/</code></h3>
          <ol class="estacoes">
{chr(10).join(itens)}
          </ol>
        </div>''')
    prontas = len(PRONTAS)
    planejadas = len(RECEITAS) - prontas
    corpo = [f'''    <div class="abertura interna">
      <div class="largura">
        <div>
          <ol class="migalhas" aria-label="Onde você está">
            <li><a href="../">Início</a></li>
            <li aria-current="page">Rolês e receitas</li>
          </ol>
          <h1>Rolês e receitas</h1>
          <p class="lema">Um <strong>rolê</strong> é o que você quer fazer com o computador. Ele é feito de <strong>receitas</strong>: mudanças pequenas que o <code>bora</code> sabe verificar, aplicar, testar e desfazer.</p>
          <div class="fichas">
            <span class="ficha">7 rolês na primeira versão</span>
            <span class="ficha feito">{prontas} receitas prontas</span>
            <span class="ficha planejado">{planejadas} planejadas</span>
          </div>
          <div class="acoes">
            <a class="botao principal" href="#roles">Ver os rolês</a>
            <a class="botao secundario" href="#receitas">Ver as receitas</a>
          </div>
        </div>
        <figure class="palco" style="margin:0" data-anima>
{CICLO}
          <figcaption>Toda receita passa por essas etapas, na mesma ordem. Cada página de receita mostra o que acontece em cada uma.</figcaption>
        </figure>
      </div>
    </div>''']
    corpo.append(f'''    <section id="roles" class="largura">
{cabeca("Rolês", "Sete rolês para começar", "Cada página mostra o que o rolê faz e o que ele não faz, as receitas, o passo a passo e os porquês. O <code>bora</code> mostra no menu só os rolês que cabem na sua máquina.")}
      <div class="grade">
{chr(10).join(cartao_role(r) for r in ROLES)}
      </div>
    </section>''')
    corpo.append(f'''    <section id="receitas" class="largura">
{cabeca("Receitas", "As receitas, por área", "As prontas têm uma página com o passo a passo, ilustrado. As planejadas aparecem com o rolê em que vão entrar; os ids delas são provisórios.")}
      <div class="receitas-area">
{chr(10).join(areas)}
      </div>
    </section>''')
    corpo.append(f'''    <section id="como-ler" class="largura">
{cabeca("Como ler", "O que cada página traz", "")}
      <div class="principios">
        <div class="cartao principio"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg><div><strong>O que faz e o que não faz.</strong><span>Os limites ficam tão claros quanto o que a receita entrega.</span></div></div>
        <div class="cartao principio"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6.5h11M9 12h11M9 17.5h11M4.5 6.5h.01M4.5 12h.01M4.5 17.5h.01"/></svg><div><strong>O passo a passo.</strong><span>O que o <code>bora</code> confere e muda em cada etapa.</span></div></div>
        <div class="cartao principio"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M10 9a2 2 0 1 1 2.6 1.9c-.4.2-.6.5-.6.9v.4M12 15.5h.01"/></svg><div><strong>Os porquês.</strong><span>Por que esse jeito, e não outro.</span></div></div>
        <div class="cartao principio"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7.5 9.5l3 2.5-3 2.5M12.5 15h4"/></svg><div><strong>Os comandos para conferir.</strong><span>Para ver com os próprios olhos, sem mudar nada.</span></div></div>
        <div class="cartao principio"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 14L4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/></svg><div><strong>Como desfazer.</strong><span>O que volta, o que fica e por quê.</span></div></div>
        <div class="cartao principio"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg><div><strong>Um jeito de pedir mais.</strong><span>No fim de cada página, os pedidos viram issues no GitHub.</span></div></div>
      </div>
    </section>''')
    corpo.append(pedidos_catalogo())
    return "\n\n".join(corpo)


def pedidos_catalogo():
    cartoes = [
        (pedido("3-novo-role.yml", "Rolê: "), '<path d="M9.5 18h5M10.5 21h3"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.5 1.1 1.3 1.1 2.2h5c0-.9.4-1.7 1.1-2.2A6 6 0 0 0 12 3z"/>', "Propor um rolê", "Conte o objetivo em linguagem de gente, para quem ele serve e em que máquina você pensou.", "Propor"),
        (pedido("2-nova-receita.yml", "Receita: "), '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13 7l4 4"/>', "Pedir uma receita nova", "Uma mudança que o bora ainda não sabe fazer.", "Pedir uma receita"),
        (pedido("1-pedido-de-recurso.yml", "Pedido: "), '<path d="M12 5v14M5 12h14"/>', "Pedir um recurso", "Algo novo num rolê ou numa receita que já existe, ou outra distro.", "Fazer um pedido"),
        (pedido("4-problema.yml", "Problema: "), '<path d="M12 4l9 16H3z"/><path d="M12 10v4.5M12 17.3h.01"/>', "Relatar um problema", "Algo não funcionou como a página diz? O formulário já vem com o roteiro.", "Relatar"),
    ]
    itens = "\n".join(
        f'''        <a class="cartao convite" href="{h}">
          <span class="bolha" aria-hidden="true"><svg viewBox="0 0 24 24">{ic}</svg></span>
          <h3>{t}</h3>
          <p>{d}</p>
          <span class="seta">{s}</span>
        </a>''' for h, ic, t, d, s in cartoes)
    return f'''    <section id="pedidos" class="largura pedidos">
{cabeca("Bora melhorar", "Falta alguma coisa?", "Os pedidos viram issues no GitHub, onde qualquer pessoa pode comentar, votar com um 👍 ou se oferecer para fazer.")}
      <div class="convites">
{itens}
      </div>
    </section>'''
