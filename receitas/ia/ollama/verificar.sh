#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-ollama.sh
source ./comum-ollama.sh

if ! ollama_instalado; then
    msg "O Ollama $OLLAMA_VERSAO não está instalado."
    exit 1
fi
if ! getent passwd "$OLLAMA_CONTA" >/dev/null; then
    msg "Falta a conta $OLLAMA_CONTA, que roda o serviço."
    exit 1
fi
if ! cmp -s <(unidade_esperada) "$OLLAMA_UNIDADE" || ! systemctl is-enabled --quiet ollama.service 2>/dev/null; then
    msg "O serviço do Ollama ainda não está configurado."
    exit 1
fi
if [ "$MODELO" != nenhum ] && [ ! -f "$(manifesto_do_modelo "$MODELO")" ]; then
    msg "O modelo $MODELO ainda não foi baixado."
    exit 1
fi
msg "O Ollama $OLLAMA_VERSAO já está instalado."
exit 0
