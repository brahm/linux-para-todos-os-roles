#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ -f "$BORA_ESTADO/links-criados" ]; then
    while read -r alvo; do
        if [ -n "$alvo" ] && [ -L "$alvo" ]; then rm -f "$alvo"; fi
    done <"$BORA_ESTADO/links-criados"
    rm -f "$BORA_ESTADO/links-criados"
fi
remover_pacotes_instalados
msg "O ripgrep, o fd, o jq e o GitHub CLI que a receita instalou foram removidos. O login no GitHub, se você fez, fica em ~/.config/gh."
