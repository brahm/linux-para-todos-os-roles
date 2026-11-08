# Roteiro em VM: Vibecodar

Comece do snapshot `limpa` da VM. Rode nas quatro distros do [README](README.md). Para os agentes que pedem conta, use contas de teste: o Codex com uma conta gratuita do ChatGPT, o Copilot CLI com o plano gratuito do Copilot e o OpenCode com um modelo gratuito. O Claude Code e o Mistral Vibe precisam de plano pago ou de crédito na API; confira esses só se tiver.

## 1. Aplicar o rolê

Rode com `sudo`, da sua conta, para as receitas configurarem a sua pasta pessoal:

```sh
sudo bora
```

Escolha "Vibecodar". Nos agentes, escreva `codex,copilot,opencode` (e `claude` ou `vibe`, se tiver conta). Escolha o OpenRouter na chave de API, o VS Code no editor e "sim" na caixa de areia, e informe o seu nome e e-mail.

- [ ] O plano termina com "cada receita passou no teste".
- [ ] `sudo bora aplicar` de novo, com o mesmo plano, diz "Tudo já estava aplicado".

Repita depois, a partir do `limpa`, com o Zed e, outra vez, com o VSCodium no editor.

## 2. Conferir o que o contêiner não confere

Feche e abra o terminal antes, para o `PATH` e as chaves valerem.

**Agentes (`ia/agentes`)**

- [ ] Numa pasta de projeto, `opencode`, `codex` e `copilot` abrem, pedem para entrar na conta (ou escolher um modelo) e respondem a um "olá".
- [ ] Peça a um deles: "use a skill do bora para montar um plano que liga o firewall". Ele roda `bora plano` e `bora validar`, mostra o plano e pede para você aplicar, sem rodar `sudo`.

**Chaves de API (`ia/chaves-de-api`)**

- [ ] Abra `~/.config/chaves-de-api/chaves.env`, tire o `#` da linha do OpenRouter e cole uma chave de teste. Num terminal novo, `printenv OPENROUTER_API_KEY` mostra a chave.
- [ ] No OpenCode, `/models` mostra os modelos do OpenRouter.

**Segredos (`seguranca/segredos`)**

- [ ] Num projeto, peça ao agente para escrever a chave num `config.py` e fazer commit. O gitleaks barra o commit.
- [ ] `git status` não mostra o `.env` do projeto.

**Caixa de areia (`ia/caixa-de-areia`)**

- [ ] `caixa opencode`, numa pasta de projeto, abre o OpenCode e ele consegue criar e editar arquivos no projeto.
- [ ] Peça ao agente, dentro da caixa, para listar `~/.ssh` e para criar um arquivo na pasta pessoal: as duas coisas falham.
- [ ] No Claude Code (se tiver conta), `/sandbox` mostra a caixa de areia ligada.
- [ ] No Codex, um comando que ele roda sozinho (como `ls`) funciona, sem erro de "bwrap" ou de namespace.

**Editor (`dev/editor`)**

- [ ] O VS Code abre pelo menu, e `code .` abre a pasta do projeto. No terminal integrado, `opencode --version` responde.
- [ ] `sudo apt update` não reclama de repositório duplicado da Microsoft.
- [ ] Com o Zed ou o VSCodium: abre pelo menu de aplicativos. Anote se o terminal integrado acha o `opencode`.

## 3. Desfazer

```sh
sudo bora desfazer
```

- [ ] `opencode`, `codex` e `caixa` não existem mais; `ls ~/.config/opencode` ainda mostra o login.
- [ ] O arquivo de chaves, com a chave colada, continua em `~/.config/chaves-de-api`.
- [ ] `git config --global core.hooksPath` não mostra nada.
- [ ] O VS Code sumiu do menu, e `/etc/apt/sources.list.d/vscode.sources` não existe.

Anote a distro, a data e o resultado num [relato de teste](https://github.com/brahm/linux-para-todos-os-roles/issues/new?template=5-relato-de-teste.yml).
