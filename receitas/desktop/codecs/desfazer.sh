#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

remover_pacotes_instalados
msg "Os codecs voltaram a ser como eram antes: só saiu o que o bora instalou."
