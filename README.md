<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="marca/logotipo/logotipo-horizontal-escuro.svg">
  <img alt="Linux para todos os rolês" src="marca/logotipo/logotipo-horizontal.svg" width="560">
</picture>

**A IA te passa os comandos. O `bora` te leva até o rolê, com passos testados e um jeito de voltar atrás.**

[Site](https://brahm.github.io/linux-para-todos-os-roles/) · [Rolês](objetivos/README.md) · [Status](https://brahm.github.io/linux-para-todos-os-roles/#status) · [Como contribuir](CONTRIBUTING.md) · [Decisões](docs/decisoes.md)

</div>

Você acabou de instalar o Linux. E agora?

Você diz o que quer do computador. O `bora` faz o resto:

```sh
sudo bora      # escolha o rolê, responda as perguntas, revise o plano, aplique
```

Não gostou? `sudo bora desfazer`. Sem formatar, sem chorar no fórum.

> [!NOTE]
> **Versão 0, para testar.** Use numa máquina que possa ser formatada sem dor. Funciona no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13, em computadores de 64 bits com Intel ou AMD. A trilha completa está no [site](https://brahm.github.io/linux-para-todos-os-roles/#status).

## O que é

Duas coisas, feitas para andar juntas:

- **Um catálogo de rolês.** Um rolê é um objetivo concreto para o computador, dito em linguagem de gente: "pronto para estudar e trabalhar", "dar vida nova a uma máquina antiga", "pasta compartilhada da casa".
- **O `bora`.** Uma ferramenta de terminal que leva o computador até o rolê escolhido. Cada receita sabe verificar, aplicar, testar e desfazer o que muda.

O `bora` funciona sozinho: sem conta, sem cartão e sem IA. Se você tiver uma IA, ela ajuda a decidir e a montar o plano. Quem executa é sempre o `bora`, só com receitas do catálogo, e a senha de administrador é você que digita.

## Os rolês que já funcionam

| Rolê | O que o computador ganha | Status |
|---|---|---|
| **Pronto para estudar e trabalhar** | Sistema atualizado, firewall ligado, snapshot do sistema, codecs de áudio e vídeo, Flatpak, backup da pasta pessoal num disco externo e histórico do `/etc`. Se você pedir, tira o Snap | testado |
| **Dar vida nova a uma máquina antiga** | Memória comprimida (zram), Xfce ou LXQt ao lado do ambiente atual, Firefox mais leve e com bloqueio de anúncios, serviços que a máquina não usa desligados. Se você pedir, SSH só na rede de casa | testado |
| **Começar a programar** | Git com chave SSH, ferramentas de compilação, Podman e, conforme o perfil, Python com ambientes virtuais ou Node.js LTS | testado |
| **Vibecodar** | Os agentes de IA que você escolher (Claude Code, Codex, Copilot CLI, OpenCode, Mistral Vibe), na sua conta e sem `sudo`; chaves de API num arquivo só seu; gitleaks em cada commit; caixa de areia; editor; e, se quiser, um modelo local no Ollama ou no LM Studio, escolhido pelo que cabe na máquina | testado |
| **Pasta compartilhada da casa** | Uma pasta que os outros computadores e celulares da casa abrem pelo Samba, só na rede local, com uma senha só da pasta para cada pessoa | em teste |

"Testado" quer dizer que, toda semana, cada receita é aplicada, conferida e desfeita em máquinas virtuais de verdade nas três distros, inclusive com tela de login e navegador. O que só se confere olhando (e o Linux Mint) está nos [roteiros de teste em VM](testes/vm/README.md).

Vêm depois: **Filmes e séries da casa** (Jellyfin) e **Acessar de fora sem abrir portas** (Tailscale). Depois deles, rolês de jogos (console, emulação, realidade virtual e outros), começando por uma receita de driver de vídeo testada em máquina de verdade. Os detalhes estão em [`objetivos/`](objetivos/README.md).

## Instalar

Ainda não instalou o Linux? O [site](https://brahm.github.io/linux-para-todos-os-roles/distro/) ajuda a escolher a distro e mostra o caminho do pendrive até o primeiro boot.

O `bora` é um arquivo só. Baixe, confira e coloque em `/usr/local/bin`:

```sh
wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/bora-linux-x86_64
wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/SHA256SUMS
sha256sum --check --ignore-missing SHA256SUMS
sudo install -m 755 bora-linux-x86_64 /usr/local/bin/bora
bora diag      # não muda nada, só mostra o que encontrou
sudo bora      # abre o menu
```

- **Atualizar:** repita os mesmos comandos. `bora versao` mostra qual você tem.
- **Onde ele guarda as coisas:** o que fez, em `/var/lib/bora`; o registro, em `/var/log/bora/bora.log`.
- **Voltar atrás:** `sudo bora desfazer`.

## Os comandos

<img align="right" src="marca/icones/hicolor/scalable/apps/br.com.brahm.Bora.svg" width="112" alt="Ícone do bora: duas pegadas de pinguim brancas sobre um quadrado laranja">

```text
sudo bora                      abre o menu de rolês
bora diag                      descobre distro, memória, disco, rede e placa de vídeo
bora lista                     lista os rolês e as receitas, com o status de teste
bora modelos                   mostra os modelos de IA locais que cabem na máquina
bora ajuda                     monta uma pergunta pronta para colar em qualquer chat de IA
sudo bora aplicar plano.yaml   aplica o plano, receita por receita, com snapshot antes
sudo bora desfazer             volta atrás
bora historico                 mostra o que o bora já aplicou e desfez
```

## Três jeitos de usar

| Jeito | Como funciona | Precisa de |
|---|---|---|
| **Menus** | O `bora` pergunta o rolê, faz as perguntas necessárias, mostra o plano e aplica. Com `--passo-a-passo`, explica cada etapa antes de rodar. | Só o `bora` |
| **Pergunta pronta** | Travou? `bora ajuda` gera um texto com o diagnóstico (sem dados sensíveis), a etapa e o erro, para colar em qualquer chat de IA, gratuito ou pago. | Qualquer chat |
| **Agente** | Agentes de terminal (Claude Code, Codex, Copilot CLI, OpenCode e outros) leem a skill do `bora`, que o rolê "Vibecodar" instala, conversam com você e escrevem o plano. O `bora` valida, e quem aplica é você. Em breve, o agente também poderá pedir ao `bora` para aplicar, com a senha digitada por você e o plano à vista. | Um agente que leia skills |

## Para quem

- **Curiosos:** máquina antiga ou doada, sem plano pago de nada. Menus e pergunta pronta, custo zero.
- **Estudantes:** notebook comum e vontade de aprender. Modo passo a passo, e agentes gratuitos quando quiserem.
- **Entusiastas:** várias máquinas e planos pagos. O plano é um arquivo: vai para o git e é reaplicado em outra máquina com `ssh maquina sudo bora aplicar plano.yaml`. Em breve, o agente que você já tem (de terminal ou de desktop) poderá pedir ao `bora` para aplicar por você.

## Distros

As distros entram por família, em ondas:

| Onda | Família | Distros |
|:-:|---|---|
| 1 | Ubuntu e Debian | Ubuntu LTS, Linux Mint, Pop!_OS, Zorin OS, Debian |
| 2 | Fedora | Fedora, Nobara |
| 3 | Arch e Fedora imutável | CachyOS, EndeavourOS, Manjaro, Arch, Bazzite, Silverblue, Kinoite, Bluefin, Aurora |
| 4 | openSUSE (pela comunidade) | Tumbleweed, Leap |

Ficam de fora: máquinas de 32 bits, distros sem systemd por padrão (MX Linux, Slackware, Gentoo, Void, Alpine) e distros com outro modelo de sistema (NixOS, SteamOS). O porquê está em [`familias/`](familias/README.md).

## Princípios

- **Funciona sem IA.** A IA acelera, mas nunca é requisito.
- **Aprender é opcional, mas está sempre à mão.** Aplique tudo de uma vez e entenda depois, ou vá no passo a passo, com o porquê de cada etapa.
- **Terminal, com menus.** Sem versão gráfica até haver um caso de uso que exija uma.
- **A IA não roda comando solto como administrador.** Ela monta o plano e, se você deixar, pede ao `bora` para aplicar. Quem executa é o `bora`, e a senha é você que digita.
- **Só receitas do catálogo.** O `bora` não roda comando livre.
- **Toda mudança tem volta.** Snapshot antes de aplicar, e cada receita sabe se desfazer.
- **Nada exposto à internet.** Acesso de fora só por VPN.
- **Testado de verdade.** Cada receita diz em que distro e em que data foi testada.
- **Em português do Brasil,** para quem está começando e para quem já sabe sair do Vim.

O porquê de cada decisão está em [`docs/decisoes.md`](docs/decisoes.md).

## Parecido, mas diferente: o Linux Toys

O [Linux Toys](https://linux.toys) é um projeto vizinho, e dos bons. É uma caixa de ferramentas com janela gráfica: você escolhe um programa, um driver ou um ajuste num catálogo de uns 200 itens, e ele instala com um clique, em umas quinze famílias de distro. Tem muita coisa para jogos e hardware específico.

| | Linux Toys | `bora` |
|---|---|---|
| Pergunta que responde | "Como instalo isto sem dor?" | "Quero que este computador sirva para isto" |
| Unidade | Um programa ou ajuste | Um rolê, feito de receitas |
| Alcance | Muito: ~200 itens, ~15 famílias de distro | Pouco, mas conferido: 5 rolês, Ubuntu e Debian por enquanto |
| De onde vêm os pacotes | Da distro, de COPR, AUR, repositórios de terceiros e instaladores da internet | Da distro e do Flathub, com poucas exceções de fabricante, conferidas |
| Depois de aplicar | Desfaz o que registrou | Testa se funcionou, desfaz e explica o porquê de cada mudança |
| Interface | Janela gráfica e terminal | Terminal, com menus |
| Licença | GPL-3.0 | 0BSD |

Quer instalar um programa, um driver ou um ajuste de jogos agora? O Linux Toys provavelmente já tem. Quer levar o computador até um objetivo, entender o que mudou e poder voltar atrás? Bora.

## Marca

Pegadas de pinguim: o pinguim é o Linux, e as pegadas são o rolê e os passos testados que o `bora` segue, um de cada vez. Logotipo, ícone, paleta e regras de uso estão em [`marca/`](marca/README.md).

## Licença

[0BSD](LICENSE). Na prática, domínio público: copie, modifique e use como quiser, sem pedir e sem citar.

## Contribuir

Testar uma receita numa distro nova já ajuda muito. O caminho está no [`CONTRIBUTING.md`](CONTRIBUTING.md), e o jeito de escrever, no [guia de estilo](docs/estilo.md).
