# docs

O site do projeto, publicado em <https://brahm.github.io/linux-para-todos-os-roles/>, e os documentos que explicam como o projeto pensa e escreve.

| Arquivo | O que é |
|---|---|
| [`decisoes.md`](decisoes.md) | As decisões que definem o projeto, com o porquê de cada uma |
| [`estilo.md`](estilo.md) | O guia de estilo: como escrever qualquer texto do projeto |
| `index.html`, `estilo.css` e `site.js` | A página inicial do site |
| `404.html` | A página de "não encontrado" |
| `distro/` | Escolher e instalar a distro: o questionário, as distros recomendadas e o caminho do pendrive até o `bora diag`, com `distro.css` e `distro.js` |
| `catalogo/` | Rolês e receitas: a página do catálogo, uma página por receita pronta e uma por rolê, com `catalogo.css` e `catalogo.js` |
| `imagens/` | Ícone e imagem social, copiados de [`marca/`](../marca/README.md) |
| `fontes/` | A Inter em WOFF2, só com os caracteres do português, sob a [SIL OFL 1.1](fontes/OFL.txt) |

## Como é publicado

O workflow [`site.yml`](../.github/workflows/site.yml) publica a pasta no GitHub Pages a cada mudança em `docs/` na `main`. Ele envia só os arquivos do site: os `.md` desta pasta ficam no repositório. Também dá para publicar à mão em Actions, Site, Run workflow.

## Como ver localmente

O site é HTML, CSS e um pouco de JavaScript. Sem etapa de build, sem `node_modules` do tamanho de um sistema operacional:

```sh
python3 -m http.server -d docs 8000
```

Abra <http://localhost:8000>. A lista de últimas mudanças vem da API pública do GitHub; se ela falhar, a página mostra o link para o histórico.

## Como manter

Todo texto novo segue o [guia de estilo](estilo.md). Rode `ferramentas/estilo/conferir.sh` antes do pull request.

- **Status de um rolê:** quando um rolê mudar de `planejado` para `rascunho` ou `testado` em [`objetivos/`](../objetivos/README.md), troque a ficha dele no `index.html` (classe `ficha`).
- **Versão e instalação:** quando sair uma versão nova, troque o selo da abertura no `index.html` (classe `selo`) e confira as transcrições do `bora` em `ferramentas/catalogo/roles.py`. Os comandos de instalação ficam em `ferramentas/catalogo/distro.py` e no README; mantenha os dois iguais.
- **Trilha do status:** cada etapa é um `<li class="passo">`. Use `feito` nas concluídas e `agora` na que está em andamento.
- **Marca:** o ícone e a imagem social vêm de `marca/`. Se a marca mudar, copie de novo `marca/icones/hicolor/scalable/apps/br.com.brahm.Bora.svg` para `imagens/icone.svg`, `marca/png/icone-256.png` para `imagens/icone-256.png` e `marca/png/imagem-social.png` para `imagens/imagem-social.png`.
- **Domínio próprio:** a `404.html` usa caminhos absolutos começando em `/linux-para-todos-os-roles/`. Se o site ganhar um domínio próprio, troque esse prefixo por `/`, e ajuste também os endereços completos no `<head>` do `index.html`.

## O catálogo

As páginas em `catalogo/` são geradas. Não edite o HTML: ele é sobrescrito na próxima geração.

O gerador, [`ferramentas/catalogo/gerar.py`](../ferramentas/catalogo/gerar.py), lê:

- os `receita.yaml`: parâmetros, famílias e registro de testes;
- `ferramentas/catalogo/dados.py`: rolês e receitas planejadas;
- `ferramentas/catalogo/roles.py`: as páginas dos rolês e a do catálogo;
- `ferramentas/catalogo/receitas.py`: o passo a passo e as ilustrações de cada receita pronta.

Depois de mudar uma receita ou um rolê, gere de novo e confira:

```sh
python3 ferramentas/catalogo/gerar.py      # precisa do PyYAML (pacote python3-yaml)
python3 -m http.server -d docs 8000
```

As ilustrações são SVG com animações em CSS. O `catalogo.js` só as dispara quando aparecem na tela, faz o terminal se escrever sozinho e troca os perfis do firewall. Sem JavaScript, ou com "reduzir movimento" ligado no sistema, tudo aparece parado e completo.

Os links "Falta alguma coisa?" no fim de cada página abrem os formulários de [`.github/ISSUE_TEMPLATE/`](../.github/ISSUE_TEMPLATE), já preenchidos com o rolê ou a receita.

A página `distro/` sai do mesmo gerador, a partir de [`ferramentas/catalogo/distro.py`](../ferramentas/catalogo/distro.py): é lá que ficam as distros, os links oficiais e os textos. O questionário (as regras de qual distro sugerir) fica em `distro/distro.js`. Quando mudar uma distro de onda, troque o campo `suporte` dela no `distro.py` e gere de novo.

A página inicial ainda é escrita à mão.
