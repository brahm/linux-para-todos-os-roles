#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-ferramentas.sh
source ./comum-ferramentas.sh

for p in $PACOTES; do
    if ! pacote_instalado "$p"; then
        msg "Falta o pacote $p."
        exit 1
    fi
done
if ! fd_ligado && ! fd_de_outro; then
    msg "Falta o comando fd."
    exit 1
fi
msg "O ripgrep, o fd, o jq e o GitHub CLI já estão instalados."
exit 0
