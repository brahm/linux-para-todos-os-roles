#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-codecs.sh
source ./comum-codecs.sh
exigir_apt

for p in "${PACOTES[@]}"; do
    conferir "pacote instalado: $p" pacote_instalado "$p"
done
for nome in libav isomp4 matroska mpg123 videoparsersbad asf a52dec; do
    conferir "${PLUGINS[$nome]} (plugin $nome do GStreamer)" plugin_presente "$nome"
done
resultado_dos_testes
