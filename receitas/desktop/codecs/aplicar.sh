#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-codecs.sh
source ./comum-codecs.sh
exigir_apt

disponivel() {
    local candidato
    candidato=$(LC_ALL=C apt-cache policy "$1" 2>/dev/null | awk '/Candidate:/ {print $2}')
    [ -n "$candidato" ] && [ "$candidato" != "(none)" ]
}

atualizar_indices
for p in "${PACOTES[@]}"; do
    if pacote_instalado "$p" || disponivel "$p"; then continue; fi
    if [ "$BORA_FAMILIA" = ubuntu ]; then
        falha "o pacote $p não está disponível; ele fica no repositório universe, que precisa estar ligado (em Programas e atualizações, ou com sudo add-apt-repository universe)"
    fi
    falha "o pacote $p não está disponível nos repositórios configurados"
done
instalar_pacotes "${PACOTES[@]}"
msg "Pronto. Feche e abra de novo o player de vídeo ou o navegador para eles verem os codecs novos."
