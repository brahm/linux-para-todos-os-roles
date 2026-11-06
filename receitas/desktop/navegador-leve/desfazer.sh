#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"

restaurar_arquivos
if [ -f "$BORA_ESTADO/pastas-novas" ]; then
    # Da mais funda para a mais rasa, e só se ficaram vazias.
    sort -r "$BORA_ESTADO/pastas-novas" | while read -r d; do rmdir "$d" 2>/dev/null || true; done
    rm -f "$BORA_ESTADO/pastas-novas"
fi
msg "As políticas do Firefox voltaram a ser como eram antes."
msg "Se o uBlock Origin já tinha sido instalado, ele fica no Firefox até você remover, em about:addons."
