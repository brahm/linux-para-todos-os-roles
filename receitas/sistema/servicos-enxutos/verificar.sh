#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita sistema/servicos-enxutos (Serviços enxutos).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
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
