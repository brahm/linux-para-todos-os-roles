# Para agentes de IA (e para gente com pressa)

Este repositório é o catálogo de rolês do Linux para todos os rolês e o `bora`, a ferramenta de terminal que aplica esses rolês. Leia o [README](README.md) para o quadro geral e o [`CONTRIBUTING.md`](CONTRIBUTING.md) para os comandos de teste.

## Texto: siga o guia de estilo

Todo texto (README, LEIAME, rolê, site, mensagem do `bora`, issue, pull request) segue o [`docs/estilo.md`](docs/estilo.md). O resumo:

1. **Direto e claro.** O que faz, na primeira frase. Frases curtas, listas sempre que der.
2. **Zero clichê de IA.** Proibido: mergulhar, desvendar, crucial, robusto, elevando, em suma, vale ressaltar, no cenário atual, tapeçaria, sinfonia, desbloquear o potencial. Nada de frase começando com "Imagine que..." nem de fecho motivacional genérico.
3. **Leve e bem-humorado.** Dev experiente explicando para um amigo no café. Humor sutil (bug, café, gambiarra), nunca em aviso de segurança nem às custas da precisão.

O leitor é o protagonista; o `bora` é o mentor. Resumo primeiro, detalhe depois, e toda página termina com o próximo passo concreto.

Antes de terminar, rode `ferramentas/estilo/conferir.sh`.

## Código: comente tudo

Todo código que você escrever ou mudar (Rust, bash, Python, JavaScript, CSS, HTML, YAML, workflows) sai comentado, para que quem baixe o projeto do GitHub entenda sem perguntar. As regras estão em [`docs/estilo.md`](docs/estilo.md#comentários-no-código) e são as mesmas do texto: direto, sem clichê, humor só de leve.

- Todo arquivo começa dizendo o que é e onde se encaixa.
- Toda função ou bloco que não é óbvio diz o que faz e, se precisar, por quê.
- Mudou o comportamento, mude o comentário junto.

## Arquitetura: mantenha o diagrama em dia

O diagrama é o SVG [`docs/arquitetura.svg`](docs/arquitetura.svg), mostrado e explicado em [`docs/arquitetura.md`](docs/arquitetura.md), e o README só tem o link. Toda evolução do projeto (comando, módulo, pasta, workflow ou fluxo novo ou mudado) atualiza o diagrama no mesmo pull request.

## Regras do projeto que não se negociam

- **Versão:** o projeto segue em 0.x. Nunca suba para fora da 0.x nem sugira isso; quem decide é o Brahm.
- **Interface:** o `bora` é de terminal, com menus. Não construa nem prometa uma versão gráfica; ela só entra quando o Brahm decidir que há um caso de uso que exija.
- **README e site:** o README tem só o projeto, o status, como instalar, compilar e contribuir. Comparações e recomendações vão para o site, que recomenda o Linux Toys para quem só quer configurar algo automaticamente.
- **Site:** as páginas em `docs/catalogo/` e `docs/distro/` são geradas. Mude o texto em `ferramentas/catalogo/*.py` e rode `python3 ferramentas/catalogo/gerar.py`. A `docs/index.html` é escrita à mão.
- **LEIAMEs:** mantenha as seis seções (`O que faz`, `Por que`, `O que muda no sistema`, `Como conferir`, `Como desfazer`, `Fontes`). O `cargo test` confere, e o `bora --passo-a-passo` mostra duas delas no terminal.
- **Receitas:** só repositórios da distro e Flathub, nada de AUR, nada de porta aberta para a internet, nada de segredo no repositório. As regras completas estão em [`receitas/README.md`](receitas/README.md).
- **Decisões:** o que foi decidido, e por quê, fica em [`docs/decisoes.md`](docs/decisoes.md). Decisão nova entra lá com data.

## Conferências

```sh
cargo test
cargo run -- conferir
ferramentas/pipes/conferir.sh
ferramentas/estilo/conferir.sh
python3 ferramentas/catalogo/gerar.py && git status --short docs/   # o site gerado precisa bater com a fonte
```
