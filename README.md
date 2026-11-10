<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="marca/logotipo/logotipo-horizontal-escuro.svg">
  <img alt="Linux para todos os rolês" src="marca/logotipo/logotipo-horizontal.svg" width="560">
</picture>

**A IA te passa os comandos. O `bora` te leva até o rolê, com passos testados e um jeito de voltar atrás.**

[Site](https://brahm.github.io/linux-para-todos-os-roles/) · [Rolês](objetivos/README.md) · [Status](https://brahm.github.io/linux-para-todos-os-roles/#status) · [Como contribuir](CONTRIBUTING.md) · [Decisões](docs/decisoes.md)

</div>

> [!NOTE]
> **Versão 0, para testar.** O `bora` já leva o computador até os cinco primeiros rolês no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13. "Pronto para estudar e trabalhar" atualiza o sistema e liga o firewall, o snapshot do sistema, os codecs de áudio e vídeo, o Flatpak e o backup da pasta pessoal num disco externo, guarda o histórico da configuração em `/etc` e, se você pedir, tira o Snap. "Dar vida nova a uma máquina antiga" liga a memória comprimida (zram), instala o Xfce ou o LXQt ao lado do ambiente atual, deixa o Firefox mais leve, com bloqueio de anúncios, desliga os serviços que a máquina não usa e, se você pedir, liga o SSH só para a rede de casa. "Começar a programar" configura o Git com uma chave SSH, instala as ferramentas de compilação e o Podman, e, conforme o perfil, o Python com ambientes virtuais ou o Node.js LTS. "Vibecodar" instala os agentes de IA que você escolher (Claude Code, Codex, Copilot CLI, OpenCode e Mistral Vibe) na sua conta, sem sudo, guarda as chaves de API num arquivo só seu, confere cada commit com o gitleaks, roda os agentes numa caixa de areia, instala o editor e, se você quiser, um modelo local com o Ollama ou o LM Studio, escolhido pelo que cabe na máquina. "Pasta compartilhada da casa", o quinto, ainda em teste, compartilha uma pasta com os outros computadores e celulares da casa pelo Samba, só na rede local, com uma senha só da pasta para cada pessoa. Os quatro primeiros estão testados: toda semana, cada receita é aplicada, conferida e desfeita em máquinas virtuais de verdade nessas três distros, inclusive com a tela de login e o navegador. Ainda é a versão 0, então use numa máquina que possa ser formatada sem dor. Os [roteiros de teste em VM](testes/vm/README.md) dizem como ajudar a conferir o que só se vê olhando e o Linux Mint. A trilha completa está no [site](https://brahm.github.io/linux-para-todos-os-roles/#status).

## O que é

Você acabou de instalar o Linux. E agora?

**Linux para todos os rolês** é duas coisas:

- um catálogo de **rolês**, que são objetivos concretos para um computador com Linux: "pronto para estudar e trabalhar", "dar vida nova a uma máquina antiga", "pasta compartilhada da casa";
- o **`bora`**, uma ferramenta de terminal que leva você até o rolê escolhido, com receitas testadas que sabem verificar, aplicar, testar e desfazer cada mudança.

O `bora` funciona sozinho, sem conta, sem cartão e sem IA. Se você tiver acesso a uma IA, ela ajuda a decidir e a montar o plano, mas nunca executa nada com privilégio de administrador.

## Como funciona

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

## Experimentar

Ainda não instalou o Linux? O [site](https://brahm.github.io/linux-para-todos-os-roles/distro/) ajuda a escolher a distro e mostra o caminho do pendrive até o primeiro boot.

O `bora` é um arquivo só, para computadores de 64 bits x86_64 (Intel ou AMD). Baixe o `bora-linux-x86_64` da [página de versões](https://github.com/brahm/linux-para-todos-os-roles/releases), junto com o `SHA256SUMS`, confira e instale em `/usr/local/bin`, para ele ficar à mão como `bora`:

```sh
wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/bora-linux-x86_64
wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/SHA256SUMS
sha256sum --check --ignore-missing SHA256SUMS
sudo install -m 755 bora-linux-x86_64 /usr/local/bin/bora
bora diag      # não muda nada, só mostra o que encontrou
sudo bora      # abre o menu
```

Para atualizar, repita os mesmos comandos; `bora versao` mostra qual você tem. O `bora` guarda o que fez em `/var/lib/bora` e o registro em `/var/log/bora/bora.log`. Para voltar atrás, use `sudo bora desfazer`.

## Três jeitos de usar

| Porta | Como funciona | Precisa de |
|---|---|---|
| **Menus** | O `bora` pergunta o rolê, faz as perguntas necessárias, mostra o plano e aplica. No modo `--passo-a-passo`, explica cada etapa antes de rodar. | Só o `bora` |
| **Pergunta pronta** | Travou? `bora ajuda` gera um texto com o diagnóstico (sem dados sensíveis), a etapa e o erro, para colar em qualquer chat de IA, gratuito ou pago. | Qualquer chat |
| **Agente** | Agentes de terminal (Claude Code, Codex, Copilot CLI, OpenCode e outros) leem a skill do `bora`, que o rolê "Vibecodar" instala, conversam com você e escrevem o plano. O `bora` valida o plano, e quem aplica é você. | Um agente que leia skills |

## Para quem

- **Curiosos:** máquina antiga ou doada, sem plano pago de nada. Menus e pergunta pronta, custo zero.
- **Estudantes:** notebook comum, vontade de aprender. Modo passo a passo, e agentes gratuitos quando quiserem.
- **Entusiastas:** várias máquinas, planos pagos. O plano é um arquivo: vai para o git e é reaplicado em outra máquina com `ssh maquina sudo bora aplicar plano.yaml`.

## Rolês da primeira versão

1. Pronto para estudar e trabalhar
2. Dar vida nova a uma máquina antiga
3. Começar a programar
4. Vibecodar
5. Pasta compartilhada da casa
6. Filmes e séries da casa
7. Acessar de fora sem abrir portas

Os detalhes estão em [`objetivos/`](objetivos/README.md).

## Distros

As distros são agrupadas por família e entram em ondas:

| Onda | Família | Distros |
|:-:|---|---|
| 1 | Ubuntu e Debian | Ubuntu LTS, Linux Mint, Pop!_OS, Zorin OS, Debian |
| 2 | Fedora | Fedora, Nobara |
| 3 | Arch e Fedora imutável | CachyOS, EndeavourOS, Manjaro, Arch, Bazzite, Silverblue, Kinoite, Bluefin, Aurora |
| 4 | openSUSE (pela comunidade) | Tumbleweed, Leap |

Ficam de fora: máquinas de 32 bits, distros sem systemd por padrão (MX Linux, Slackware, Gentoo, Void, Alpine) e distros com outro modelo de sistema (NixOS, SteamOS). Os detalhes estão em [`familias/`](familias/README.md).

## Princípios

- **Funciona sem IA.** A IA acelera, mas nunca é requisito.
- **A IA nunca executa com privilégio.** No máximo, escreve e valida um plano.
- **Só receitas do catálogo.** O `bora` não roda comando livre.
- **Toda mudança tem volta.** Snapshot antes de aplicar, e cada receita sabe se desfazer.
- **Nada exposto à internet.** Acesso de fora só por VPN.
- **Testado de verdade.** Cada receita diz em que distro e em que data foi testada.
- **Em português do Brasil,** para quem está começando e para quem já sabe sair do Vim.

As decisões tomadas até aqui, com o porquê de cada uma, estão em [`docs/decisoes.md`](docs/decisoes.md).

## Marca

A marca são pegadas de pinguim: o pinguim é o Linux, e a pegada é o rolê e também os passos testados que o `bora` segue, um de cada vez. O logotipo, o ícone do aplicativo, a paleta e as regras de uso estão em [`marca/`](marca/README.md).

## Licença

[0BSD](LICENSE). Na prática, é domínio público: copie, modifique e use como quiser, sem pedir e sem citar.

## Contribuir

Veja o [`CONTRIBUTING.md`](CONTRIBUTING.md).
