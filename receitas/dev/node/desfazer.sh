#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita dev/node (Node.js).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
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
