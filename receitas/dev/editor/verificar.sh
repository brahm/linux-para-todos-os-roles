#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-editor.sh
source ./comum-editor.sh

if [ "$EDITOR_PEDIDO" = terminal ]; then
    msg "Nenhum editor novo pedido: fica o terminal."
    exit 0
fi
if ! editor_pronto; then
    msg "O editor $EDITOR_PEDIDO ainda não está instalado."
    exit 1
fi
msg "O editor $EDITOR_PEDIDO já está instalado."
exit 0
