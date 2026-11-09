# Agentes de IA no terminal

## O que faz

Instala, na sua conta e sem `sudo`, os agentes de programação que você escolher: Claude Code, Codex, Copilot CLI, OpenCode e Mistral Vibe. Também instala a skill do `bora` para eles, que ensina como montar um plano sem rodar nada como root.

## Por que

Um agente de programação conversa com você no terminal, lê o projeto, escreve código e roda comandos. Cada fabricante tem o seu, e cada um funciona com um tipo de conta:

| Agente | Comando | Funciona com |
|---|---|---|
| Claude Code (Anthropic) | `claude` | plano pago do Claude ou chave de API da Anthropic |
| Codex (OpenAI) | `codex` | conta do ChatGPT, inclusive a gratuita, com limites, ou chave de API da OpenAI |
| Copilot CLI (GitHub) | `copilot` | plano do GitHub Copilot, inclusive o gratuito |
| OpenCode | `opencode` | modelos gratuitos do próprio OpenCode, ou a chave de qualquer provedor, como OpenRouter e DeepSeek |
| Mistral Vibe | `vibe` | chave de API da Mistral |

Os planos e os limites mudam o tempo todo; confira na página de cada fabricante antes de assinar.

**De onde eles vêm.** Os quatro primeiros vêm dos pacotes oficiais de cada fabricante no npm, e o Mistral Vibe, do PyPI, com o `pipx`. O npm e o pip conferem a soma de cada arquivo com a que o registro publica. Os instaladores que se baixam e rodam com um script ficam de fora, porque o `bora` não tem como conferir um script que muda a cada versão. Por isso o Antigravity CLI, do Google, que só tem esse instalador, ainda não entra.

**Por que na sua conta.** Com o `npm` da receita `dev/node`, o `npm install -g` instala em `~/.local`, e os agentes aparecem em `~/.local/bin`. Assim, eles nunca rodam como root, e conseguem se atualizar sozinhos, sem `sudo`, como vários deles fazem.

**Versão.** A receita instala a versão mais nova de cada agente no dia. Os agentes mudam toda semana, e uma versão antiga costuma parar de funcionar com o serviço. A máquina virtual do CI confere todos toda semana.

**A skill do bora.** Uma skill é um arquivo `SKILL.md` que o agente lê quando o assunto aparece. A do `bora` explica como ver a máquina (`bora diag --json`), montar e validar um plano (`bora plano`, `bora validar`) e pedir para você aplicar, sem nunca rodar `sudo`. É a porta "agente" do `bora`.

## O que muda no sistema

- Para cada agente escolhido que ainda não existe na sua conta, roda como você `npm install -g <pacote>` (`@anthropic-ai/claude-code`, `@openai/codex`, `@github/copilot` ou `opencode-ai`) ou `pipx install mistral-vibe`. Se o comando do agente já existir (instalado à mão ou pelo instalador do fabricante), a receita não mexe nele.
- Escreve a skill do `bora` em `~/.claude/skills/bora/SKILL.md`, que o Claude Code, o Copilot CLI e o OpenCode leem, e em `~/.agents/skills/bora/SKILL.md`, que o Codex e o OpenCode leem. Se já existir outro arquivo ali, ele fica.

A receita precisa do `npm` (receita `dev/node`) e, para o Mistral Vibe, do `pipx` (receita `dev/python`). O rolê Vibecodar já traz as duas.

## Como conferir

O `testar.sh` confere, para cada agente, que o comando responde a `--version` como você e que o programa está na sua conta, e não na do root. Ele não conversa com o agente, porque isso precisa da sua conta.

Para conferir de verdade: abra um terminal novo, entre na pasta de um projeto e rode o agente pelo nome, como `opencode`. Na primeira vez, ele pede para entrar na sua conta ou para escolher um modelo. Depois, diga "olá".

## Como desfazer

O `desfazer.sh` roda `npm uninstall -g` ou `pipx uninstall` nos agentes que a receita instalou e apaga a skill do `bora`, se ela não mudou. As configurações e os logins dos agentes (como `~/.claude`, `~/.codex`, `~/.copilot` e `~/.config/opencode`) ficam na sua pasta.

## Fontes

- [Claude Code: instalação](https://docs.claude.com/en/docs/claude-code/setup)
- [Codex CLI](https://github.com/openai/codex)
- [GitHub Copilot CLI: instalação](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)
- [OpenCode: instalação](https://opencode.ai/docs/)
- [Mistral Vibe](https://github.com/mistralai/mistral-vibe)
- [Agent Skills: o formato SKILL.md](https://agentskills.io/)
