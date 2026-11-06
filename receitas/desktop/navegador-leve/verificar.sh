#!/usr/bin/env bash
set -euo pipefail
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
