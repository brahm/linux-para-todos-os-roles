# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita ia/caixa-de-areia.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

PACOTES="bubblewrap socat"
CAIXA=/usr/local/bin/caixa
# O Ubuntu 24.04 em diante só deixa criar um user namespace sem root aos
# programas que têm um perfil do AppArmor para isso. Sem ele, o bubblewrap
# (e a caixa de areia do Claude Code e do Codex) não abre.
PERFIL_APPARMOR=/etc/apparmor.d/bora-bwrap

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
CASA=$(pasta_pessoal "$PESSOA")
CONFIG_CLAUDE=$CASA/.claude/settings.json

# O conteúdo do perfil do AppArmor para o bubblewrap.
perfil_apparmor() {
    cat <<'PERFIL'
# Escrito pelo bora (receita ia/caixa-de-areia). Deixa o bubblewrap criar o
# user namespace da caixa de areia, como o Ubuntu faz com o Flatpak.
abi <abi/4.0>,
include <tunables/global>

profile bora-bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bora-bwrap>
}
PERFIL
}

# O kernel restringe os user namespaces pelo AppArmor? (Ubuntu 24.04 em diante)
userns_restrito() {
    [ "$(cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns 2>/dev/null || echo 0)" = 1 ]
}

# O bubblewrap abre uma caixa, como a pessoa?
bwrap_abre() {
    como_pessoa "$PESSOA" bwrap --ro-bind / / --dev /dev --proc /proc --unshare-all --die-with-parent true >/dev/null 2>&1
}

# O Claude Code está instalado na conta da pessoa? Se estiver, a receita
# liga a caixa de areia dele também.
claude_instalado() {
    como_pessoa "$PESSOA" env PATH="$CASA/.local/bin:/usr/local/bin:/usr/bin:/bin" sh -c 'command -v claude' >/dev/null 2>&1
}

# A caixa de areia do Claude Code está ligada nas configurações da pessoa?
sandbox_claude_ligada() {
    python3 - "$CONFIG_CLAUDE" <<'PY'
import json, sys
try:
    with open(sys.argv[1]) as f:
        c = json.load(f)
    sys.exit(0 if c.get("sandbox", {}).get("enabled") is True else 1)
except Exception:
    sys.exit(1)
PY
}
