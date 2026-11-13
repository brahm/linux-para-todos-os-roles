#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita ia/caixa-de-areia (Caixa de areia para os agentes).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ -f "$BORA_ESTADO/pessoa" ]; then
    BORA_USUARIO=$(cat "$BORA_ESTADO/pessoa")
    # shellcheck source=comum-caixa.sh
    source ./comum-caixa.sh
    if [ -f "$BORA_ESTADO/claude-sandbox" ] && [ -f "$CONFIG_CLAUDE" ]; then
        if [ -f "$BORA_ESTADO/claude-criado" ] && cmp -s "$BORA_ESTADO/claude-escrito" "$CONFIG_CLAUDE"; then
            rm -f "$CONFIG_CLAUDE"
        elif [ -f "$BORA_ESTADO/claude-original" ] && cmp -s "$BORA_ESTADO/claude-escrito" "$CONFIG_CLAUDE"; then
            # Ninguém mexeu depois: volta o arquivo exatamente como era.
            cat "$BORA_ESTADO/claude-original" >"$CONFIG_CLAUDE"
        else
            # O Claude Code ou a pessoa mudou o arquivo depois: tira só a chave.
            # Roda como root, para ler a cópia em BORA_ESTADO; o dono volta a ser a pessoa.
            python3 - "$CONFIG_CLAUDE" "$(cat "$BORA_ESTADO/claude-antes" 2>/dev/null || echo null)" "$BORA_ESTADO/claude-original" <<'PY'
import json, os, sys
caminho, antes, original = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3]
with open(caminho) as f:
    c = json.load(f)
s = c.get("sandbox", {})
if antes is None:
    s.pop("enabled", None)
else:
    s["enabled"] = antes
if not s:
    c.pop("sandbox", None)
texto = json.dumps(c, indent=2, ensure_ascii=False) + "\n"
# Se o que sobrou é o mesmo que havia antes, volta o arquivo de antes, byte a byte.
if os.path.exists(original):
    with open(original) as f:
        bruto = f.read()
    try:
        if json.loads(bruto) == c:
            texto = bruto
    except ValueError:
        pass
with open(caminho, "w") as f:
    f.write(texto)
PY
        fi
        msg "A caixa de areia do Claude Code voltou a ser como era."
    fi
    rm -f "$BORA_ESTADO/claude-sandbox" "$BORA_ESTADO/claude-criado" "$BORA_ESTADO/claude-antes" "$BORA_ESTADO/claude-original" "$BORA_ESTADO/claude-escrito" "$BORA_ESTADO/pessoa"
fi
if [ -f /etc/apparmor.d/bora-bwrap ] && command -v apparmor_parser >/dev/null; then
    apparmor_parser -R /etc/apparmor.d/bora-bwrap 2>/dev/null || true
fi
restaurar_arquivos
remover_pastas_novas
remover_pacotes_instalados
msg "O comando caixa foi removido."
