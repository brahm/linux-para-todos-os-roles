#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita sistema/servicos-enxutos (Serviços enxutos).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-servicos.sh
source ./comum-servicos.sh

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
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
