#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita desktop/codecs (Codecs de áudio e vídeo).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

remover_pacotes_instalados
msg "Os codecs voltaram a ser como eram antes: só saiu o que o bora instalou."
