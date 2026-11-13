#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita ia/agentes (Agentes de IA no terminal).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ -f "$BORA_ESTADO/pessoa" ]; then
    BORA_USUARIO=$(cat "$BORA_ESTADO/pessoa")
    # shellcheck source=comum-agentes.sh
    source ./comum-agentes.sh
    if [ -f "$BORA_ESTADO/agentes-instalados" ]; then
        while IFS='|' read -r a origem pacote; do
            [ -n "$a" ] || continue
            case $origem in
                npm) na_sessao npm uninstall -g --loglevel=error "$pacote" || aviso "não consegui remover $pacote" ;;
                pipx) na_sessao pipx uninstall "$pacote" >/dev/null || aviso "não consegui remover $pacote" ;;
            esac
            msg "Agente removido: $a"
        done <"$BORA_ESTADO/agentes-instalados"
        rm -f "$BORA_ESTADO/agentes-instalados"
    fi
    if [ -f "$BORA_ESTADO/skills" ]; then
        while read -r f; do
            if [ -n "$f" ] && cmp -s ./SKILL.md "$f"; then rm -f "$f"; fi
        done <"$BORA_ESTADO/skills"
        rm -f "$BORA_ESTADO/skills"
    fi
    rm -f "$BORA_ESTADO/pessoa"
fi
remover_pastas_novas
msg "Os agentes que a receita instalou foram removidos. As configurações e os logins deles (como ~/.claude, ~/.codex e ~/.config/opencode) ficam na sua pasta."
