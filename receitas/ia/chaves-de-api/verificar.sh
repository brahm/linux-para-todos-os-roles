#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-chaves.sh
source ./comum-chaves.sh

if ! permissoes_certas; then
    msg "Ainda não há um arquivo de chaves de API só de $PESSOA em $ARQUIVO."
    exit 1
fi
if ! tem_bloco; then
    msg "O terminal de $PESSOA ainda não carrega as chaves de API."
    exit 1
fi
msg "As chaves de API de $PESSOA ficam em $ARQUIVO, só com permissão dela."
exit 0
