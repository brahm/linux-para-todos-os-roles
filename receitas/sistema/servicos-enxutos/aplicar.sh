#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-servicos.sh
source ./comum-servicos.sh

lista=$(para_desligar)
if [ -z "$lista" ]; then
    msg "Nenhum serviço desnecessário ligado."
    exit 0
fi
while IFS='|' read -r unidade motivo; do
    if systemd_rodando; then
        systemctl disable --now "$unidade" 2>&1 | sed '/^Removed /d'
    else
        systemctl disable "$unidade" 2>&1 | sed '/^Removed /d'
    fi
    # Anota para o desfazer ligar de novo.
    echo "$unidade" >>"$BORA_ESTADO/unidades-desligadas"
    msg "Desligado: $unidade ($motivo)."
done <<<"$lista"
