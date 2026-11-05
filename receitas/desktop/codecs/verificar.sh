#!/usr/bin/env bash
set -euo pipefail
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
