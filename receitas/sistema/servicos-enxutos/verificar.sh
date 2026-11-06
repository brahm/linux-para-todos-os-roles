#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-servicos.sh
source ./comum-servicos.sh

lista=$(para_desligar)
if [ -n "$lista" ]; then
    msg "Serviços para desligar: $(cut -d'|' -f1 <<<"$lista" | tr '\n' ' ')"
    exit 1
fi
msg "Nenhum serviço desnecessário ligado."
exit 0
