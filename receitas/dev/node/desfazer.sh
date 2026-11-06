#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

restaurar_arquivos
if [ -f "$BORA_ESTADO/links-criados" ]; then
    while read -r alvo; do
        if [ -n "$alvo" ] && [ -L "$alvo" ]; then rm -f "$alvo"; fi
    done <"$BORA_ESTADO/links-criados"
    rm -f "$BORA_ESTADO/links-criados"
fi
if [ -f "$BORA_ESTADO/links-anteriores" ]; then
    while read -r c destino; do
        if [ -n "$c" ] && [ -e "$destino" ]; then ln -sfn "$destino" "/usr/local/bin/$c"; fi
    done <"$BORA_ESTADO/links-anteriores"
    rm -f "$BORA_ESTADO/links-anteriores"
fi
if [ -f "$BORA_ESTADO/node-instalado" ]; then
    dir=$(cat "$BORA_ESTADO/node-instalado")
    case "$dir" in
        /usr/local/lib/nodejs/node-v*)
            rm -rf "${dir:?}"
            msg "Node.js removido: $dir"
            ;;
    esac
    rm -f "$BORA_ESTADO/node-instalado"
fi
remover_pastas_novas
remover_pacotes_instalados
msg "O Node.js que a receita instalou foi removido. Os pacotes que você instalou com npm install -g ficam em ~/.local/lib/node_modules."
