#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-node.sh
source ./comum-node.sh

if ! node_instalado; then
    msg "O Node.js $NODE_VERSAO não está instalado."
    exit 1
fi
if ! comandos_ligados; then
    msg "Os comandos node, npm e npx ainda não apontam para o Node.js $NODE_VERSAO."
    exit 1
fi
if ! cmp -s <(npmrc_esperado) "$NPMRC"; then
    msg "O npm ainda não instala pacotes globais na pasta pessoal."
    exit 1
fi
if [ ! -d "$BIN_DA_PESSOA" ]; then
    msg "Falta a pasta $BIN_DA_PESSOA, onde o npm põe os programas."
    exit 1
fi
msg "O Node.js $NODE_VERSAO já está instalado."
exit 0
