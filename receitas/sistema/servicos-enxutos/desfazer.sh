#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita sistema/servicos-enxutos (Serviços enxutos).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"

if [ -f "$BORA_ESTADO/unidades-desligadas" ]; then
    while read -r unidade; do
        [ -n "$unidade" ] || continue
        if systemd_rodando; then
            systemctl enable --now "$unidade" 2>&1 | sed '/^Created symlink/d' || true
        else
            systemctl enable "$unidade" 2>&1 | sed '/^Created symlink/d' || true
        fi
        msg "Ligado de novo: $unidade"
    done <"$BORA_ESTADO/unidades-desligadas"
    rm -f "$BORA_ESTADO/unidades-desligadas"
fi
msg "Os serviços voltaram a ser como eram antes."
