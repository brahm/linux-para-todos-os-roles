# docs

Esta pasta guarda a documentação do projeto e o site publicado no GitHub Pages, em <https://brahm.github.io/linux-para-todos-os-roles/>.

| Arquivo | O que é |
|---|---|
| [`decisoes.md`](decisoes.md) | As decisões que definem o projeto, com o porquê de cada uma |
| `index.html`, `estilo.css` e `site.js` | A página inicial do site |
| `404.html` | A página de "não encontrado" |
| `imagens/` | Ícone e imagem social, copiados de [`marca/`](../marca/README.md) |
| `fontes/` | A Inter em WOFF2, só com os caracteres do português, sob a [SIL OFL 1.1](fontes/OFL.txt) |

## Como é publicado

O workflow [`site.yml`](../.github/workflows/site.yml) publica a pasta no GitHub Pages a cada mudança em `docs/` na `main`. Ele envia só os arquivos do site: os `.md` desta pasta ficam no repositório. Também dá para publicar à mão em Actions, Site, Run workflow.

## Como ver localmente

O site é HTML, CSS e um pouco de JavaScript, sem etapa de build:

```sh
python3 -m http.server -d docs 8000
```

e abra <http://localhost:8000>. A lista de últimas mudanças vem da API pública do GitHub; se ela falhar, a página mostra o link para o histórico.

## Como manter

- **Status de um rolê:** quando um rolê mudar de `planejado` para `rascunho` ou `testado` em [`objetivos/`](../objetivos/README.md), troque a ficha dele no `index.html` (classe `ficha`).
- **Trilha do status:** cada etapa é um `<li class="passo">`. Use `feito` nas concluídas e `agora` na que está em andamento.
- **Marca:** o ícone e a imagem social vêm de `marca/`. Se a marca mudar, copie de novo `marca/icones/hicolor/scalable/apps/br.com.brahm.Bora.svg` para `imagens/icone.svg`, `marca/png/icone-256.png` para `imagens/icone-256.png` e `marca/png/imagem-social.png` para `imagens/imagem-social.png`.
- **Domínio próprio:** a `404.html` usa caminhos absolutos começando em `/linux-para-todos-os-roles/`. Se o site ganhar um domínio próprio, troque esse prefixo por `/`, e ajuste também os endereços completos no `<head>` do `index.html`.

Mais adiante, a proposta é gerar parte do site a partir dos rolês e das receitas. Até lá, a página é escrita à mão.
