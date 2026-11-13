#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita dev/ferramentas (Ferramentas do terminal).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
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
