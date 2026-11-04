<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="marca/logotipo/logotipo-horizontal-escuro.svg">
  <img alt="Linux para todos os rolês" src="marca/logotipo/logotipo-horizontal.svg" width="560">
</picture>

**A IA te passa os comandos. O `bora` te leva até o rolê, com passos testados e um jeito de voltar atrás.**

[Site](https://brahm.github.io/linux-para-todos-os-roles/) · [Rolês](objetivos/README.md) · [Status](https://brahm.github.io/linux-para-todos-os-roles/#status) · [Como contribuir](CONTRIBUTING.md) · [Decisões](docs/decisoes.md)

</div>

> [!NOTE]
> **Versão 0, para testar.** O `bora` já aplica, testa e desfaz três receitas no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13: sistema atualizado, snapshot do sistema e firewall. Elas passaram nos testes automáticos em contêiner, mas ainda não foram testadas numa máquina virtual nem num computador de verdade. Use numa máquina que possa ser formatada sem dor. A trilha completa está no [site](https://brahm.github.io/linux-para-todos-os-roles/#status).

## O que é

Você acabou de instalar o Linux. E agora?

**Linux para todos os rolês** é duas coisas:

- um catálogo de **rolês**, que são objetivos concretos para um computador com Linux: "pronto para estudar e trabalhar", "dar vida nova a uma máquina antiga", "pasta compartilhada da casa";
- o **`bora`**, uma ferramenta de terminal que leva você até o rolê escolhido, com receitas testadas que sabem verificar, aplicar, testar e desfazer cada mudança.

O `bora` funciona sozinho, sem conta, sem cartão e sem IA. Se você tiver acesso a uma IA, ela ajuda a decidir e a montar o plano, mas nunca executa nada com privilégio de administrador.

## Como funciona

<img align="right" src="marca/icones/hicolor/scalable/apps/br.com.brahm.Bora.svg" width="112" alt="Ícone do bora: duas pegadas de pinguim brancas sobre um quadrado laranja">

```text
bora                           abre o menu de rolês
bora diag                      descobre distro, memória, disco, rede e placa de vídeo
bora ajuda                     monta uma pergunta pronta para colar em qualquer chat de IA
sudo bora aplicar plano.yaml   aplica o plano, receita por receita, com snapshot antes
bora desfazer                  volta atrás
```

## Experimentar

O `bora` é um arquivo só, para computadores de 64 bits (x86_64 ou aarch64). Baixe o da sua máquina na [página de versões](https://github.com/brahm/linux-para-todos-os-roles/releases), junto com o `SHA256SUMS`, e confira antes de rodar:

```sh
sha256sum --check --ignore-missing SHA256SUMS
chmod +x bora-linux-x86_64
./bora-linux-x86_64 diag      # não muda nada, só mostra o que encontrou
sudo ./bora-linux-x86_64      # abre o menu
```

O `bora` guarda o que fez em `/var/lib/bora` e o registro em `/var/log/bora/bora.log`. Para voltar atrás, use `sudo ./bora-linux-x86_64 desfazer`.

## Três jeitos de usar

| Porta | Como funciona | Precisa de |
|---|---|---|
| **Menus** | O `bora` pergunta o rolê, faz as perguntas necessárias, mostra o plano e aplica. No modo `--passo-a-passo`, explica cada etapa antes de rodar. | Só o `bora` |
| **Pergunta pronta** | Travou? `bora ajuda` gera um texto com o diagnóstico (sem dados sensíveis), a etapa e o erro, para colar em qualquer chat de IA, gratuito ou pago. | Qualquer chat |
| **Agente** | Agentes de terminal (Claude Code, Codex, Copilot CLI, OpenCode e outros) leem a skill do `bora`, conversam com você e escrevem o plano. O `bora` valida o plano, e quem aplica é você. | Um agente que leia skills |

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
