#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita dev/python (Python com ambientes virtuais).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

remover_pastas_novas
remover_pacotes_instalados
msg "O Python voltou a ser como era antes. Os ambientes virtuais dos seus projetos ficam nas pastas deles."
