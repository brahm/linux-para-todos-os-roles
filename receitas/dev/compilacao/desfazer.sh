#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

remover_pacotes_instalados
msg "As ferramentas de compilação que a receita instalou foram removidas."
