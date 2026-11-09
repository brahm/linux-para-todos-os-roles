# Rolês (objetivos)

Um rolê é o que a pessoa quer fazer com o computador, dito em linguagem de gente. O `bora` mostra no menu só os rolês que cabem na máquina e na família da distro.

Cada rolê é um arquivo `objetivos/<id>.yaml`.

## Formato

```yaml
id: pasta-compartilhada
nome: Pasta compartilhada da casa
descricao: Uma pasta neste computador que os outros computadores da casa conseguem abrir.
para_quem: [curiosos, estudantes, entusiastas]
status: planejado            # planejado | rascunho | testado
hardware_minimo:
  ram_gb: 2
  disco_livre_gb: 10
familias: [ubuntu, debian, fedora, arch]
perguntas:
  - id: pasta
    texto: Qual pasta você quer compartilhar?
    padrao: /srv/compartilhado
  - id: usuarios
    texto: Quem vai acessar? Escreva os nomes separados por vírgula.
receitas:
  - id: base/atualizar
  - id: sistema/snapshot
  - id: seguranca/firewall
    perfil: servidor-lan
  - id: servicos/samba
    pasta: "{pasta}"
    usuarios: "{usuarios}"
pronto_quando: Outro computador da rede abre a pasta e consegue criar um arquivo nela.
como_desfazer: O bora desfaz o compartilhamento e as regras de firewall, sem apagar os arquivos da pasta.
```

Campos:

| Campo | Para que serve |
|---|---|
| `id` | Nome curto, sem acento, usado no plano e na linha de comando |
| `nome` e `descricao` | O que aparece no menu |
| `para_quem` | Públicos que o rolê atende: `curiosos`, `estudantes`, `entusiastas` |
| `status` | `planejado` (só a ideia), `rascunho` (receitas escritas e testadas em contêiner) ou `testado` (cada receita passou nas [máquinas virtuais do CI](../testes/vm/README.md) no Ubuntu 24.04 e no Debian 13) |
| `hardware_minimo` | O `bora diag` esconde o rolê se a máquina não atender |
| `familias` | Famílias de distro em que o rolê funciona (ver [`familias/`](../familias/README.md)) |
| `perguntas` | O que o `bora` pergunta antes de montar o plano; as respostas entram nos parâmetros como `{id}`. Com `opcoes` (e, se quiser, `rotulos`), a pergunta vira um menu, e a resposta precisa ser uma das opções |
| `receitas` | As receitas aplicadas, em ordem, com seus parâmetros. Com `quando: {pergunta: resposta}`, a receita só entra no plano quando a resposta for aquela |
| `pronto_quando` | Um teste que qualquer pessoa consegue fazer para saber que deu certo |
| `como_desfazer` | O que o `bora desfazer` faz, em uma frase |

Um rolê com perfis, como o "Começar a programar", faz uma pergunta com opções e usa `quando` nas receitas que dependem dela:

```yaml
perguntas:
  - id: perfil
    texto: Por onde você quer começar?
    opcoes: [python, web]
    rotulos:
      python: Python, para dados, automação e ciência.
      web: Web, com JavaScript e Node.js.
    padrao: python
receitas:
  - id: dev/git
  - id: dev/python
    quando: {perfil: python}
  - id: dev/node
    quando: {perfil: web}
```

Na linha de comando, a resposta vai com `-r`: `bora plano comecar-a-programar -r perfil=web`.

## Quando um rolê vira `testado`

Um rolê passa de `rascunho` para `testado` quando cada receita dele tem o teste registrado com `onde: vm` (ou `maquina`) e `resultado: ok` no **Ubuntu 24.04** e no **Debian 13**. Quem grava esse registro são as duas [máquinas virtuais do CI](../testes/vm/README.md#a-parte-automática-no-ci), a sem tela e a [com tela](../testes/vm/README.md#a-máquina-com-tela), que aplicam, conferem e desfazem cada receita toda semana; um teste numa máquina de verdade também conta. O Ubuntu 26.04 roda nas mesmas máquinas, mas não segura a mudança de status: um problema nele vira uma issue, e o rolê segue `testado`. Os [roteiros manuais](../testes/vm/README.md) continuam como complemento, para o que só o olho confere (se o vídeo toca, se a loja abre, se os favoritos vieram) e para o Linux Mint, que não tem imagem para as máquinas do CI. Um problema achado neles vira uma issue, e o rolê volta para `rascunho` só se o problema impedir o uso. Escolhido por Brahm em 8/11/2026.

## Rolês da primeira versão

| # | Rolê | O que inclui | Status |
|:-:|---|---|---|
| 1 | Pronto para estudar e trabalhar | Atualização, firewall, codecs, Flatpak, snapshot do sistema e backup da pasta pessoal | testado |
| 2 | Dar vida nova a uma máquina antiga | Ambiente leve, zram, navegador enxuto e serviços desnecessários desligados | testado |
| 3 | Começar a programar | Git, ferramentas de compilação, Python com ambientes virtuais, Node.js e contêineres, em dois perfis (web e Python) | testado |
| 4 | Vibecodar | Tudo do "Começar a programar", mais agentes de IA, chaves de API guardadas com segurança, verificação de segredos, caixa de areia opcional, editor e, se a pessoa quiser, modelos locais com o Ollama ou o LM Studio | testado |
| 5 | Pasta compartilhada da casa | Samba, apenas na rede local | planejado |
| 6 | Filmes e séries da casa | Jellyfin, apenas na rede local | planejado |
| 7 | Acessar de fora sem abrir portas | Tailscale, com teste de CGNAT | planejado |

### O rolê "Vibecodar"

Perguntas:

- Quais agentes você quer? Claude Code (`claude`), Codex (`codex`), Copilot CLI (`copilot`), OpenCode (`opencode`) ou Mistral Vibe (`vibe`), separados por vírgula. O padrão é o OpenCode, que funciona com modelos gratuitos.
- Vai usar chave de API (OpenRouter, DeepSeek ou outra)? Se sim, o arquivo de chaves já sai com a linha do provedor no topo, e o OpenCode encontra a chave sozinho.
- Qual editor? VS Code, VSCodium, Zed ou só o terminal.
- Quer isolar os agentes numa caixa de areia? É o recomendado, e o padrão.
- Quer rodar modelos no próprio computador? Não (o padrão), o Ollama com o modelo que o `bora` sugere, o Ollama com um modelo que a pessoa baixa por conta própria, o LM Studio, ou os dois. A pergunta já mostra a sugestão para a máquina.

O que é instalado e configurado:

- a base do "Começar a programar", com o Python e o Node.js juntos (`base/atualizar`, `dev/git`, `dev/compilacao`, `dev/python`, `dev/node` e `containers/podman`);
- `ripgrep`, `fd`, `jq` e o GitHub CLI (`dev/ferramentas`);
- um `.gitignore` global que já ignora `.env` e chaves, e o `gitleaks` conferindo cada commit (`seguranca/segredos`);
- um lugar para as chaves de API em `~/.config/chaves-de-api`, com permissão só do dono, carregado em cada terminal (`ia/chaves-de-api`);
- os agentes escolhidos, na conta da pessoa e sem `sudo`, pelos pacotes oficiais no npm e no PyPI, e a skill do `bora` para eles (`ia/agentes`);
- quando escolhida, a caixa de areia: o comando `caixa`, com o `bubblewrap`, onde o agente só escreve na pasta do projeto e não vê as chaves SSH, e a caixa de areia do próprio Claude Code ligada (`ia/caixa-de-areia`); nenhum agente recebe `sudo`;
- o editor escolhido (`dev/editor`), com o Flatpak quando ele vem do Flathub;
- quando escolhido, o vibecode local: o Ollama (`ia/ollama`), baixado do GitHub e conferido por SHA256, como um serviço que só este computador acessa, e o LM Studio (`ia/lm-studio`), com janela.

No vibecode local, o `bora` mede a máquina antes (a RAM, a memória da placa de vídeo e o disco) e confere cada modelo da lista [`receitas/ia/ollama/modelos.yaml`](../receitas/ia/ollama/modelos.yaml). O `bora modelos` mostra a conta. A sugestão é o modelo mais capaz que roda bem e serve para agente; numa máquina sem memória para isso, um modelo só de conversa, ou nenhum. No plano, `modelo: sugerido` vira o nome do modelo, com o tamanho do download, antes de a pessoa aceitar. No Ollama, o `bora` baixa o modelo; no LM Studio, a pessoa baixa na aba Discover, com o nome que o `bora` mostrou. Escolhido por Brahm em 9/11/2026.

Ficou para depois o Antigravity CLI, que só tem instalador do tipo `curl | sh`.

Pronto quando: cada agente responde no terminal, e um projeto de exemplo é criado, versionado e tem o commit barrado pelo gitleaks quando leva uma chave.

É o rolê que mais vai quebrar, porque os agentes mudam de versão, de instalador e de plano o tempo todo. A máquina virtual do CI aplica os cinco agentes toda semana.

## Ideias para depois

Bloqueador de anúncios da casa, fotos da família (Immich), backup da família, servidor de IA da casa (o Ollama servindo os modelos para a rede, com o firewall), dual boot e ajustes brasileiros (cedilha no teclado internacional, programa do IRPF).
