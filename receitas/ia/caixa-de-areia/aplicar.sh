#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-caixa.sh
source ./comum-caixa.sh

if [ -e "$CAIXA" ] && ! grep -q 'receita ia/caixa-de-areia' "$CAIXA"; then
    falha "já existe $CAIXA, que não veio do bora; tire de lá e rode de novo"
fi
# shellcheck disable=SC2086
instalar_pacotes $PACOTES
echo "$PESSOA" >"$BORA_ESTADO/pessoa"
escrever_arquivo "$CAIXA" 0755 <./caixa

# O Ubuntu 26.04 já traz um perfil para o bubblewrap (bwrap-userns-restrict);
# o 24.04, não. O perfil do bora só entra quando o bubblewrap não abre sem ele,
# para não disputar o /usr/bin/bwrap com o perfil da distro.
if userns_restrito && ! bwrap_abre; then
    command -v apparmor_parser >/dev/null ||
        falha "o kernel só deixa abrir a caixa de areia com um perfil do AppArmor, e este sistema não tem o apparmor_parser (pacote apparmor) para carregar um"
    perfil_apparmor | escrever_arquivo "$PERFIL_APPARMOR" 0644
    apparmor_parser -r "$PERFIL_APPARMOR"
    msg "O AppArmor passa a deixar o bubblewrap abrir a caixa de areia."
fi
bwrap_abre || aviso "o bubblewrap não conseguiu abrir uma caixa de areia nesta máquina; o teste vai mostrar o motivo"

if claude_instalado && ! sandbox_claude_ligada; then
    if [ ! -e "$CONFIG_CLAUDE" ]; then
        criar_pasta_da_pessoa "$PESSOA" "$CASA/.claude"
        echo "$CONFIG_CLAUDE" >"$BORA_ESTADO/claude-criado"
    fi
    [ -e "$CONFIG_CLAUDE" ] && cp -a "$CONFIG_CLAUDE" "$BORA_ESTADO/claude-original"
    # Muda só a chave sandbox.enabled; o resto das configurações fica.
    como_pessoa "$PESSOA" python3 - "$CONFIG_CLAUDE" >"$BORA_ESTADO/claude-antes" <<'PY'
import json, os, sys
caminho = sys.argv[1]
c = {}
if os.path.exists(caminho):
    with open(caminho) as f:
        c = json.load(f)
antes = c.get("sandbox", {}).get("enabled", None)
c.setdefault("sandbox", {})["enabled"] = True
with open(caminho + ".bora", "w") as f:
    json.dump(c, f, indent=2, ensure_ascii=False)
    f.write("\n")
os.replace(caminho + ".bora", caminho)
print(json.dumps(antes))
PY
    cp "$CONFIG_CLAUDE" "$BORA_ESTADO/claude-escrito"
    echo sim >"$BORA_ESTADO/claude-sandbox"
    msg "A caixa de areia do Claude Code foi ligada ($CONFIG_CLAUDE)."
fi
msg "Pronto. Entre na pasta de um projeto e rode: caixa claude, caixa codex, caixa opencode, ou o agente que você usa."
