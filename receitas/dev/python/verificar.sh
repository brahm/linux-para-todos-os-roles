#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita dev/python (Python com ambientes virtuais).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-python.sh
source ./comum-python.sh

for p in $PACOTES; do
    if ! pacote_instalado "$p"; then
        msg "Falta o pacote $p."
        exit 1
    fi
done
if [ ! -d "$BIN_DA_PESSOA" ]; then
    msg "Falta a pasta $BIN_DA_PESSOA, onde o pipx põe os programas."
    exit 1
fi
msg "O Python já está pronto para projetos."
exit 0
