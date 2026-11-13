#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita dev/ferramentas (Ferramentas do terminal).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ -f "$BORA_ESTADO/links-criados" ]; then
    while read -r alvo; do
        if [ -n "$alvo" ] && [ -L "$alvo" ]; then rm -f "$alvo"; fi
    done <"$BORA_ESTADO/links-criados"
    rm -f "$BORA_ESTADO/links-criados"
fi
remover_pacotes_instalados
msg "O ripgrep, o fd, o jq e o GitHub CLI que a receita instalou foram removidos. O login no GitHub, se você fez, fica em ~/.config/gh."
