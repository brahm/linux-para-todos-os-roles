# Guia de estilo

Como escrever qualquer texto do projeto: README, LEIAMEs das receitas, rolês, páginas do site, mensagens do `bora`, issues e pull requests. Vale para gente e para agentes de IA.

Resumo em quatro linhas:

1. **Primeiro o que faz, depois o porquê.** A primeira frase resolve a dúvida de quem chegou.
2. **Frases curtas, listas, comandos copiáveis.** Se cabe numa lista, vira lista.
3. **Zero clichê de IA.** A lista proibida está abaixo, e o `ferramentas/estilo/conferir.sh` barra.
4. **Leve, mas certo.** Um dev experiente explicando para um amigo no café. A piada tempera; o comando tem que funcionar.

## As regras de tom

Definidas por Brahm em 13/11/2026. Valem para todo texto novo e para toda revisão.

### 1. Direto e claro

- Vá direto ao ponto. Diga o que a coisa faz, na prática, logo na primeira frase.
- Nada de introdução longa, contexto histórico ou "neste documento, vamos ver".
- Frases curtas. Passou de duas vírgulas, provavelmente são duas frases.
- Listas sempre que houver três itens ou mais, ou passos em ordem.
- Um parágrafo, uma ideia. Mais de quatro linhas no site é sinal de que dá para quebrar.

### 2. Zero clichê de IA

Proibido, em qualquer forma (singular, plural, conjugado):

| Não use | Use, se precisar |
|---|---|
| mergulhar, mergulho | ver, entrar em, olhar de perto |
| desvendar | explicar, mostrar |
| crucial | importante, ou diga por quê |
| robusto | testado, que aguenta X (diga o quê) |
| elevar, elevando | melhorar, subir |
| em suma | (corte a frase) |
| vale ressaltar | (corte e diga a coisa) |
| no cenário atual | hoje |
| tapeçaria | (não existe tapeçaria em Linux) |
| sinfonia | (nem sinfonia) |
| desbloquear o potencial | (diga o que passa a funcionar) |

Também fora:

- começar frase com "Imagine que..." ou "Imagine...";
- fechar seção com conclusão genérica ou motivacional ("e assim você está pronto para conquistar o mundo do Linux"). Feche com o próximo passo concreto: um comando, um link, uma ação;
- adjetivo vazio no lugar de fato: "poderoso", "incrível", "perfeito", "essencial", "fundamental", "jornada", "experiência fluida". Troque pelo número, pelo comando ou pelo resultado.

### 3. Leve e bem-humorado

- O tom é de um dev experiente explicando o projeto para um amigo, tomando café.
- Humor sutil: uma piada rápida sobre bug, café, gambiarra, Vim, GRUB, impressora. No máximo uma por seção, e nunca no meio de um passo a passo.
- A piada não pode esconder informação. Se alguém tirar a piada, o texto tem que continuar completo.
- Sem humor em: avisos de segurança, comandos que apagam ou formatam, mensagens de erro do `bora`, perda de dados. Aí é sério e curto.
- Sem ironia com quem está começando. O alvo da piada é o computador, a gambiarra ou a gente mesmo, nunca o leitor.

Exemplos:

| Em vez de | Escreva |
|---|---|
| "O zram é uma solução robusta que eleva o desempenho de máquinas antigas." | "O zram comprime o que está parado na memória. A máquina aguenta mais abas antes de engasgar." |
| "Vale ressaltar que o desfazer é crucial." | "Deu ruim? `sudo bora desfazer` volta atrás." |
| "Imagine que você acabou de instalar o Linux..." | "Você acabou de instalar o Linux. E agora?" |
| "Em suma, o bora desbloqueia o potencial do seu computador." | "O `bora` leva o computador até o rolê e sabe voltar atrás." |

## Como montar o texto

Técnicas do *HBR Guide to Persuasive Presentations*, da Nancy Duarte, adaptadas para documentação.

### O leitor é o protagonista

- Quem lê é o herói da história. O `bora` é o mentor: entrega uma ferramenta, ensina a usar e tira a pessoa de onde ela travou.
- Escreva sobre o que a pessoa ganha, não sobre o que o projeto tem. "Seu notebook de 4 GB aguenta mais abas", e não "o projeto implementa zram".
- Fale com "você". O projeto é "a gente" quando precisa aparecer.

### Escolha um leitor principal

O projeto tem três públicos: **curiosos**, **estudantes** e **entusiastas**. Cada texto escreve para um deles, sem deixar os outros perdidos:

| Texto | Leitor principal | O que ele quer saber primeiro |
|---|---|---|
| Página inicial, README, página da distro | Curioso | O que é, se serve para mim, como começo |
| Página e YAML de rolê | Curioso ou estudante | O que o computador vai fazer depois, e o que pergunta |
| LEIAME e página de receita | Estudante | O que muda no sistema, por que, e como conferir |
| `receitas/README.md`, `CONTRIBUTING.md`, testes | Entusiasta | O contrato, os comandos e o que o CI confere |

### De onde para onde

Antes de escrever, responda: onde o leitor está quando chega, e onde ele precisa estar quando sai?

| Chega | Sai |
|---|---|
| "Instalei o Linux. E agora?" | Com um rolê escolhido e o primeiro comando na mão |
| "Meu notebook velho trava com duas abas" | Sabendo que o rolê 2 resolve, e o que ele muda |
| "Será que essa receita estraga meu sistema?" | Sabendo o que ela muda, como conferir e como desfazer |

Se o texto não leva de um para o outro, falta algo ou sobra algo.

### O resumo primeiro, o detalhe depois

- Quem tem pressa lê só o começo. O começo precisa bastar: o que é, o resultado, o próximo passo.
- Regra dos 10%: o resumo ocupa uns 10% do texto. O resto é apêndice, para quem quer ir fundo: os porquês, as exceções, as fontes.
- Pergunta direta, resposta direta. A seção "Como desfazer" começa dizendo o que o desfazer faz, não contando a história do desfazer.

### Fale a língua de quem lê

Ache o terreno comum: o notebook que trava, o pendrive que não dá boot, a impressora que some, o "funciona na minha máquina". Use exemplos que a pessoa já viveu.

### Toda página termina com uma ação

- O fim de uma página é o próximo passo: o comando para rodar, o link para seguir, o formulário para abrir.
- Antecipe a resistência: "e se der errado?" tem resposta (o desfazer); "preciso de IA?" tem resposta (não).

## Precisão técnica

O humor é tempero; a precisão é o prato.

- Comandos copiáveis, em bloco de código, do jeito que se digita. Nunca mude um comando para caber numa piada.
- Nomes exatos de pacote, arquivo, serviço e opção, sempre em `código`.
- Números e versões exatos: "Ubuntu 24.04", "até 50% da memória, no máximo 8 GB".
- Quando algo é planejado, diga que é planejado. Quando é testado, diga onde e quando.
- Versão do projeto: sempre 0.x. Quem decide quando o projeto sai da 0.x é o Brahm; nenhum texto anuncia, sugere ou promete outra coisa.

## Formato

- Português do Brasil, com acento. Nomes de arquivo e de comando sem acento, como já são.
- Termos do projeto: **rolê** (o objetivo), **receita** (a menor mudança), **plano**, **`bora`** (sempre em código, sempre minúsculo).
- Títulos curtos, em frase, sem ponto final.
- Negrito para o termo que a pessoa vai procurar com os olhos, não para ênfase emocional.
- Datas como "13/11/2026" em tabelas e "13 de novembro de 2026" em títulos.
- Os LEIAMEs das receitas mantêm as seis seções (`O que faz`, `Por que`, `O que muda no sistema`, `Como conferir`, `Como desfazer`, `Fontes`). O `bora` lê "O que faz" e "O que muda no sistema" no modo `--passo-a-passo`, então essas duas precisam ler bem no terminal: curtas e sem tabela.

## O que vai em cada lugar

- **README:** só o projeto em si e o status dele, mais como instalar, compilar e contribuir. Comparações com outros projetos, recomendações e conteúdo de divulgação vão para o site.
- **Site:** é onde o projeto conversa com quem ainda está escolhendo. Quando alguém só quer configurar algo automaticamente, sem objetivo nem explicação, o site recomenda o [Linux Toys](https://linux.toys) como a ferramenta mais indicada. Recomendar o vizinho certo vale mais do que prender a pessoa no `bora`.

## Onde fica cada texto

| Texto | Arquivo |
|---|---|
| README e guias | `*.md` na raiz e nas pastas |
| Página inicial do site | `docs/index.html`, escrita à mão |
| Catálogo e página da distro | `ferramentas/catalogo/*.py`; depois de mudar, rode `python3 ferramentas/catalogo/gerar.py` |
| Rolês | `objetivos/*.yaml` (o que o menu mostra) |
| Receitas | `receitas/<area>/<id>/LEIAME.md` e `receita.yaml` |

As decisões antigas em [`decisoes.md`](decisoes.md) e os registros de teste ficam como foram escritos: são histórico.

## Comentários no código

Definido por Brahm em 13/11/2026. Quem baixa o projeto do GitHub precisa conseguir ler qualquer arquivo e entender o que ele faz sem perguntar para ninguém. Vale para Rust, bash, Python, JavaScript, CSS, HTML, YAML e workflows do CI.

- **Todo arquivo começa dizendo o que é.** Para que serve, quem chama e onde ele se encaixa no projeto.
- **Toda função, tipo ou bloco que não é óbvio ganha comentário.** Diga o que faz e, quando não for evidente, por quê. O "como" o código já mostra.
- **Explique as gambiarras.** Contorno de bug de distro, ordem que importa, `|| true` proposital: escreva o motivo, senão alguém "conserta" e quebra.
- **Mesmas regras de texto deste guia.** Português do Brasil, direto, frases curtas, sem clichê de IA. Humor só se couber numa linha, e nunca em aviso de segurança.
- **Comentário acompanha o código.** Mudou o comportamento, mude o comentário no mesmo commit. Comentário errado é pior do que nenhum.
- **Código gerado por IA segue a mesma regra.** Não entra sem comentário.

## O diagrama da arquitetura

O mapa de como as peças se encaixam fica em [`arquitetura.md`](arquitetura.md), num desenho SVG feito à mão ([`arquitetura.svg`](arquitetura.svg)), com uma explicação curta de cada parte. O README só tem o link. O SVG é texto: mude as caixas e as setas num editor qualquer e confira no navegador, no tema claro e no escuro.

Definido por Brahm em 13/11/2026: **toda evolução do projeto atualiza o diagrama no mesmo pull request.** Peça nova, comando novo, pasta nova, workflow novo ou fluxo que mudou: se o desenho ficou desatualizado, o pull request não está pronto.

## Antes de abrir o pull request

```sh
ferramentas/estilo/conferir.sh     # barra as palavras proibidas
```

Confira também se o código novo tem comentários e se o [`arquitetura.md`](arquitetura.md) ainda descreve o projeto.

E leia o texto em voz alta uma vez. Se você tomou fôlego no meio de uma frase, ela está longa. Se riu, ótimo; se riu e não entendeu o comando, reescreva.
