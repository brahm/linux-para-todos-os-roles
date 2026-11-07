#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-etckeeper.sh
source ./comum-etckeeper.sh
exigir_apt

if ! pacote_instalado etckeeper; then
    msg "O etckeeper não está instalado."
    exit 1
fi
if ! etc_versionado; then
    msg "O /etc ainda não tem histórico."
    exit 1
fi
msg "O /etc já tem histórico no etckeeper."
exit 0
