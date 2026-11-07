#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-sem-snap.sh
source ./comum-sem-snap.sh
exigir_apt

if pacote_instalado snapd || [ -n "$(snaps_instalados)" ]; then
    msg "O Snap está instalado."
    exit 1
fi
if ! snapd_bloqueado; then
    msg "O Snap não está instalado, mas o apt ainda poderia trazê-lo de volta."
    exit 1
fi
msg "O Snap não está instalado e não volta pelo apt."
exit 0
