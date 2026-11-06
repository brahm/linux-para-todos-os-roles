#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-compilacao.sh
source ./comum-compilacao.sh

# shellcheck disable=SC2086
instalar_pacotes $PACOTES
msg "Pronto: gcc, g++, make e pkg-config instalados."
