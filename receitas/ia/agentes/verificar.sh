#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-agentes.sh
source ./comum-agentes.sh

for a in $(escolhidos); do
    if ! agente_instalado "$a"; then
        msg "Falta o agente $a."
        exit 1
    fi
done
for s in $SKILLS; do
    if ! skill_instalada "$s"; then
        msg "Falta a skill do bora em $s."
        exit 1
    fi
done
msg "Os agentes $(escolhidos) já estão instalados para $PESSOA."
exit 0
