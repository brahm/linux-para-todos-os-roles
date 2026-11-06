#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

remover_pastas_novas
remover_pacotes_instalados
msg "O Python voltou a ser como era antes. Os ambientes virtuais dos seus projetos ficam nas pastas deles."
