#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita sistema/etckeeper (Histórico do /etc).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
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
