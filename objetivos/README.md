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
| `status` | `planejado` (só a ideia), `rascunho` (receitas escritas, sem teste) ou `testado` |
| `hardware_minimo` | O `bora diag` esconde o rolê se a máquina não atender |
| `familias` | Famílias de distro em que o rolê funciona (ver [`familias/`](../familias/README.md)) |
| `perguntas` | O que o `bora` pergunta antes de montar o plano; as respostas entram nos parâmetros como `{id}` |
| `receitas` | As receitas aplicadas, em ordem, com seus parâmetros |
| `pronto_quando` | Um teste que qualquer pessoa consegue fazer para saber que deu certo |
| `como_desfazer` | O que o `bora desfazer` faz, em uma frase |

## Rolês da primeira versão

| # | Rolê | O que inclui | Status |
|:-:|---|---|---|
| 1 | Pronto para estudar e trabalhar | Atualização, firewall, codecs, Flatpak, snapshot do sistema e backup da pasta pessoal | rascunho |
| 2 | Dar vida nova a uma máquina antiga | Ambiente leve, zram, navegador enxuto e serviços desnecessários desligados | rascunho |
| 3 | Começar a programar | Git, ferramentas de compilação, Python com ambientes virtuais, Node.js e contêineres, em dois perfis (web e Python) | planejado |
| 4 | Vibecodar | Tudo do "Começar a programar", mais agentes de IA, chaves de API guardadas com segurança, verificação de segredos e caixa de areia opcional | planejado |
| 5 | Pasta compartilhada da casa | Samba, apenas na rede local | planejado |
| 6 | Filmes e séries da casa | Jellyfin, apenas na rede local | planejado |
| 7 | Acessar de fora sem abrir portas | Tailscale, com teste de CGNAT | planejado |

### O rolê "Vibecodar"

Perguntas:

- Quais agentes você quer? Claude Code, Codex, Copilot CLI, Antigravity CLI, Mistral Vibe ou OpenCode. O menu mostra o que funciona com as contas que você tem.
- Vai usar chave de API (OpenRouter, DeepSeek ou outra)? Se sim, o OpenCode já sai configurado com ela.
- Qual editor? VS Code, VSCodium, Zed ou só o terminal.
- Quer isolar os agentes numa caixa de areia? É o recomendado.

O que é instalado e configurado:

- a base do "Começar a programar";
- os agentes escolhidos, pelos instaladores oficiais, que o `bora` baixa, confere e mostra antes de rodar, mais o `bubblewrap`, que o Codex usa como sandbox no Linux;
- `ripgrep`, `fd`, `jq` e o GitHub CLI (`gh`);
- git com chave SSH e um `.gitignore` global que já ignora `.env` e chaves;
- um lugar para as chaves de API em `~/.config`, com permissão só do dono, e o `gitleaks` verificando segredos antes de cada commit;
- quando escolhida, uma caixa de areia (distrobox ou toolbox) onde os agentes rodam sem acesso ao sistema todo; nenhum agente recebe `sudo`;
- o Ollama, se o `bora diag` disser que a máquina aguenta modelo local;
- a skill do `bora` nos agentes instalados.

Pronto quando: cada agente responde a um "olá" no terminal, e um projeto de exemplo é criado, versionado e passa pela verificação de segredos.

É o rolê que mais vai quebrar, porque os agentes mudam de versão, de instalador e de plano o tempo todo. As receitas dele são conferidas a cada versão do `bora`.

## Ideias para depois

Bloqueador de anúncios da casa, fotos da família (Immich), backup da família, IA local, dual boot e ajustes brasileiros (cedilha no teclado internacional, programa do IRPF).
