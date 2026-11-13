#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita dev/editor (Editor de código).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
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
