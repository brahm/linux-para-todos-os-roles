# Caixa de areia para os agentes

## O que faz

Instala o comando `caixa`, que roda um agente de IA dentro de uma caixa de areia feita com o `bubblewrap`: ele escreve só na pasta do projeto, não vê as suas chaves SSH e não consegue usar `sudo`. Também liga a caixa de areia do próprio Claude Code, se ele estiver instalado.

## Por que

Um agente roda comandos no seu computador, com as suas permissões. Na maioria das vezes, são comandos que você aprovaria. Mas um modelo erra, entende mal ou lê, num arquivo do projeto, uma instrução escondida para apagar algo ou mandar as suas chaves para fora. Numa caixa de areia, o estrago fica limitado à pasta do projeto, que está no Git.

**Por que o bubblewrap, e não um contêiner.** O distrobox e o toolbox, que o plano citava, são ótimos para ter outra distro, mas não isolam: eles montam a sua pasta pessoal inteira e o sistema todo dentro do contêiner. O `bubblewrap` é a mesma peça que o Flatpak usa para isolar os aplicativos, e é o que a caixa de areia do Claude Code e a do Codex usam no Linux. Ele não precisa de serviço nem de imagem, e abre em milissegundos.

**Duas camadas.** O Claude Code e o Codex têm a própria caixa de areia, que isola cada comando que o agente roda e pede permissão para sair dela. A receita liga a do Claude Code (`sandbox.enabled` em `~/.claude/settings.json`); a do Codex já vem ligada. O comando `caixa` isola o agente inteiro, e serve para qualquer um, inclusive os que não têm caixa própria, como o OpenCode, o Copilot CLI e o Mistral Vibe.

**O AppArmor do Ubuntu.** Do Ubuntu 24.04 em diante, só os programas com um perfil do AppArmor podem criar o "espaço de usuário" que a caixa de areia usa. Sem um perfil para o `bubblewrap`, a caixa do `bora`, a do Claude Code e a do Codex não abrem. A receita escreve esse perfil, do mesmo jeito que o Ubuntu faz com o Flatpak, só quando o sistema tem essa restrição.

## O que muda no sistema

- Instala os pacotes `bubblewrap` e `socat` (que a caixa de areia do Claude Code usa para a rede).
- Escreve o comando `/usr/local/bin/caixa`.
- No Ubuntu 24.04 em diante, escreve o perfil `/etc/apparmor.d/bora-bwrap` e carrega com `apparmor_parser`.
- Se o Claude Code estiver instalado, liga `sandbox.enabled` em `~/.claude/settings.json`, sem mexer no resto do arquivo.

Dentro da `caixa`, o agente:

- escreve só na pasta em que você está, nas pastas dos agentes (`~/.claude`, `~/.codex`, `~/.copilot`, `~/.config/opencode` e as de cache) e num `/tmp` que some no fim;
- lê o resto do sistema, mas não muda nada;
- não vê `~/.ssh`, `~/.gnupg`, o login do GitHub CLI (`~/.config/gh`), o arquivo de chaves de API, o `.netrc` nem as credenciais do Git (as chaves que já estão no terminal continuam valendo, para o agente falar com o modelo);
- não vê os outros programas nem os sockets de `/run`, como o do D-Bus e o do Podman;
- não consegue usar `sudo`;
- acessa a internet.

A `caixa` se recusa a abrir na sua pasta pessoal inteira ou fora dela: entre na pasta de um projeto antes. Como o agente não vê a sua chave SSH, faça o `git push` fora da caixa.

## Como conferir

O `testar.sh` cria uma pasta de projeto e um arquivo de mentira em `~/.ssh` e confere, como você, que dentro da `caixa`:

- dá para escrever na pasta do projeto;
- não dá para escrever fora dela;
- não dá para ler o arquivo de `~/.ssh`;
- o `sudo` não funciona;
- e que a `caixa` se recusa a abrir na pasta pessoal.

Para usar: `cd ~/projetos/meu-site && caixa opencode` (ou `caixa claude`, `caixa codex`, `caixa bash`).

## Como desfazer

O `desfazer.sh` apaga o comando `caixa` e o perfil do AppArmor, volta `~/.claude/settings.json` ao que era (ou tira só a chave `sandbox.enabled`, se o arquivo mudou depois) e remove os pacotes que a receita instalou.

## Fontes

- [bubblewrap](https://github.com/containers/bubblewrap)
- [Claude Code: caixa de areia](https://docs.claude.com/en/docs/claude-code/sandboxing)
- [Codex: segurança e caixa de areia](https://developers.openai.com/codex/security)
- [Ubuntu 24.04: restrição de user namespaces sem privilégio](https://ubuntu.com/blog/ubuntu-23-10-restricted-unprivileged-user-namespaces)
- [distrobox: não é uma caixa de areia](https://distrobox.it/)
