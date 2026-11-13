#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita desktop/navegador-leve (Navegador enxuto).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-navegador.sh
source ./comum-navegador.sh

if politicas_aplicadas; then
    msg "O Firefox já está com as configurações enxutas."
    exit 0
fi
msg "O Firefox ainda não está com as configurações enxutas."
exit 1
