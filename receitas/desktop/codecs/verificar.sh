#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita desktop/codecs (Codecs de áudio e vídeo).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-codecs.sh
source ./comum-codecs.sh
exigir_apt

for p in "${PACOTES[@]}"; do
    if ! pacote_instalado "$p"; then
        msg "Falta o pacote $p."
        exit 1
    fi
done
msg "Os codecs de áudio e vídeo já estão instalados."
exit 0
