# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita ia/agentes.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

# agente|comando|de onde vem|pacote
# Os agentes vêm dos pacotes oficiais de cada fabricante no npm e no PyPI, na
# versão mais nova. O npm e o pip conferem a soma de cada arquivo baixado com
# a que o registro publica. Nenhum script baixado da internet roda aqui.
AGENTES_CONHECIDOS="
claude|claude|npm|@anthropic-ai/claude-code
codex|codex|npm|@openai/codex
copilot|copilot|npm|@github/copilot
opencode|opencode|npm|opencode-ai
vibe|vibe|pipx|mistral-vibe
"

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
CASA=$(pasta_pessoal "$PESSOA")
# O PATH de uma sessão comum da pessoa: os programas dela, depois o Node.js do bora.
CAMINHO="$CASA/.local/bin:/usr/local/bin:/usr/bin:/bin"
# Roda um comando como a pessoa, com o PATH acima.
na_sessao() { como_pessoa "$PESSOA" env PATH="$CAMINHO" "$@"; }

# Onde a skill do bora vai: a pasta do Claude Code (que o Copilot CLI e o
# OpenCode também leem) e a pasta comum dos agentes (Codex e OpenCode).
SKILLS="$CASA/.claude/skills/bora $CASA/.agents/skills/bora"

# Os agentes pedidos no parâmetro agentes, separados por espaço.
escolhidos() { tr ',' ' ' <<<"${BORA_AGENTES:-opencode}"; }

# A linha de AGENTES_CONHECIDOS de um agente, ou para com erro se ele não existir.
dados_do_agente() {
    awk -F'|' -v a="$1" '$1 == a {print; achou = 1} END {exit !achou}' <<<"$AGENTES_CONHECIDOS" ||
        falha "agente desconhecido: $1"
}
# O nome do comando que o agente instala (o segundo campo da linha).
comando_do_agente() { dados_do_agente "$1" | cut -d'|' -f2; }

# O comando do agente existe na sessão da pessoa?
agente_instalado() { na_sessao sh -c "command -v '$(comando_do_agente "$1")'" >/dev/null 2>&1; }

# Os agentes do npm e do PyPI precisam do npm e do pipx; sem eles, a receita
# para e diz qual receita aplicar antes.
exigir_npm() {
    na_sessao sh -c 'command -v npm' >/dev/null 2>&1 ||
        falha "falta o npm; aplique antes a receita dev/node (o rolê Vibecodar já traz)"
}
exigir_pipx() {
    na_sessao sh -c 'command -v pipx' >/dev/null 2>&1 ||
        falha "falta o pipx; aplique antes a receita dev/python (o rolê Vibecodar já traz)"
}

# A skill do bora está na pasta e igual à desta receita?
skill_instalada() { [ -f "$1/SKILL.md" ] && cmp -s ./SKILL.md "$1/SKILL.md"; }
