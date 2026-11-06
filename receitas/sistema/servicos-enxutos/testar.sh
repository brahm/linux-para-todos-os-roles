#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-servicos.sh
source ./comum-servicos.sh

desligado() { [ "$(estado_de "$1")" != enabled ]; }
parado() { ! systemctl is-active --quiet "$1"; }
n=0
while IFS='|' read -r unidade motivo; do
    [ -n "$unidade" ] || continue
    [ -n "$(estado_de "$unidade")" ] || continue
    n=$((n + 1))
    conferir "$unidade não liga no boot ($motivo)" desligado "$unidade"
    if systemd_rodando; then
        conferir "$unidade parado agora (systemctl is-active)" parado "$unidade"
    fi
done < <(candidatos)
if [ "$n" -eq 0 ]; then
    msg "Nenhum dos serviços que a receita conhece está instalado aqui; nada a desligar."
fi
resultado_dos_testes
