#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ -f "$BORA_ESTADO/pessoa" ]; then
    BORA_USUARIO=$(cat "$BORA_ESTADO/pessoa")
    # shellcheck source=comum-segredos.sh
    source ./comum-segredos.sh
    if [ -f "$BORA_ESTADO/hookspath" ]; then
        if [ "$(valor_global core.hooksPath)" = "$GANCHOS_DIR" ]; then
            como_pessoa "$PESSOA" git config --global --unset core.hooksPath
            msg "O Git de $PESSOA volta a usar só os ganchos de cada projeto."
        fi
        rm -f "$BORA_ESTADO/hookspath"
    fi
    if [ -d "$GANCHOS_DIR" ]; then
        rm -f "${GANCHOS_DIR:?}/gancho"
        for g in $GANCHOS; do
            if [ -L "$GANCHOS_DIR/$g" ]; then rm -f "${GANCHOS_DIR:?}/$g"; fi
        done
    fi
    if [ -f "$BORA_ESTADO/ignore" ]; then
        ignore=$(cat "$BORA_ESTADO/ignore")
        tirar_bloco "$ignore"
        if [ -f "$BORA_ESTADO/ignore-criado" ] && [ ! -s "$ignore" ]; then rm -f "$ignore"; fi
        rm -f "$BORA_ESTADO/ignore" "$BORA_ESTADO/ignore-criado"
        msg "As regras do bora saíram de $ignore."
    fi
    rm -f "$BORA_ESTADO/pessoa"
fi
remover_pastas_novas
remover_pacotes_instalados
msg "O gitleaks não confere mais os commits."
