# Ferramentas do terminal

## O que faz

Instala o `ripgrep` (o comando `rg`), o `fd`, o `jq` e o GitHub CLI (`gh`), todos dos repositórios da distro.

## Por que

São as ferramentas que os agentes de IA mais usam para entender um projeto: o `rg` procura um texto em todos os arquivos, muito mais rápido que o `grep -r`, e respeita o `.gitignore`; o `fd` acha arquivos pelo nome; o `jq` lê e filtra JSON, que é a língua das APIs; e o `gh` clona repositórios, abre pull requests e entra no GitHub sem senha. Quando elas faltam, o agente gasta tempo e tokens tentando outro caminho, ou pede para instalar.

No Debian e no Ubuntu, o `fd` se chama `fdfind`, porque já existia outro programa com o nome `fd`. A receita cria o comando `fd`, que é o nome que os tutoriais e os agentes usam.

## O que muda no sistema

- Instala os pacotes `ripgrep`, `fd-find`, `jq` e `gh`.
- Cria o link `/usr/local/bin/fd`, apontando para `/usr/bin/fdfind`. Se já existir um `fd` ali que não veio do `bora`, ele fica, e a receita só avisa.

## Como conferir

O `testar.sh` cria uma pasta de teste e:

- procura um texto com `rg` e um arquivo `.py` com `fd`;
- lê um campo de um JSON com `jq`;
- roda `gh --version`.

Para entrar no GitHub pelo terminal: `gh auth login`.

## Como desfazer

O `desfazer.sh` apaga o link `/usr/local/bin/fd` e remove os pacotes que a receita instalou, menos o que outro programa passou a usar. O login no GitHub, se você fez, fica em `~/.config/gh`.

## Fontes

- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [fd](https://github.com/sharkdp/fd), com a nota sobre o nome `fdfind` no Debian
- [jq](https://jqlang.org/manual/)
- [GitHub CLI](https://cli.github.com/manual/)
