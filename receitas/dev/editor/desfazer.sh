#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ -f "$BORA_ESTADO/flatpaks-instalados" ]; then
    while read -r app; do
        [ -n "$app" ] || continue
        flatpak uninstall --system -y --noninteractive "$app" || aviso "não consegui remover $app"
        msg "Editor removido: $app"
    done <"$BORA_ESTADO/flatpaks-instalados"
    rm -f "$BORA_ESTADO/flatpaks-instalados"
fi
remover_pacotes_instalados
if [ -d "$BORA_ESTADO/arquivos" ] || [ -f "$BORA_ESTADO/arquivos-novos" ]; then
    restaurar_arquivos
    apt_get update -q || true
fi
msg "O editor que a receita instalou foi removido. As suas configurações e extensões ficam na sua pasta pessoal."
