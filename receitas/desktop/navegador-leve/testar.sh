#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita desktop/navegador-leve (Navegador enxuto).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-navegador.sh
source ./comum-navegador.sh

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
json_valido() { python3 -c 'import json, sys; json.load(open(sys.argv[1]))' "$POLITICAS"; }
com_ublock() { grep -q "$UBLOCK" "$POLITICAS"; }
conferir "o arquivo de políticas é um JSON que o Firefox lê ($POLITICAS)" json_valido
conferir "telemetria, estudos e atalhos patrocinados desligados" politicas_aplicadas
conferir "abas paradas saem da memória quando ela acaba (browser.tabs.unloadOnLowMemory)" grep -q unloadOnLowMemory "$POLITICAS"
if [ "${BORA_BLOQUEAR_ANUNCIOS:-sim}" = sim ]; then
    conferir "o uBlock Origin é instalado na próxima vez que o Firefox abrir" com_ublock
fi
if firefox_instalado; then
    msg "Para ver no Firefox: abra about:policies e confira a lista de políticas ativas."
else
    msg "O Firefox não está instalado; as políticas ficam prontas para quando ele for."
fi
resultado_dos_testes
