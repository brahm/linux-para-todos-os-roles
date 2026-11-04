#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"

if [ -s "$BORA_ESTADO/pacotes-pedidos" ] && grep -qx ufw "$BORA_ESTADO/pacotes-pedidos"; then
    # O ufw não existia antes: desliga e remove.
    if command -v ufw >/dev/null; then ufw --force disable >/dev/null || true; fi
    desabilitar_unidades_habilitadas
    remover_pacotes_instalados
    msg "O ufw foi removido, como antes do bora."
    exit 0
fi

if [ -f "$BORA_ESTADO/ufw-antes.tar" ]; then
    ufw --force disable >/dev/null || true
    rm -rf /etc/ufw
    tar -C / -xpf "$BORA_ESTADO/ufw-antes.tar"
    desabilitar_unidades_habilitadas
    if [ "$(cat "$BORA_ESTADO/ufw-estava-ativo" 2>/dev/null)" = sim ]; then
        ufw --force enable >/dev/null
        msg "A configuração anterior do ufw foi restaurada, e o firewall continua ligado."
    else
        msg "A configuração anterior do ufw foi restaurada, e o firewall voltou a ficar desligado."
    fi
    rm -f "$BORA_ESTADO/ufw-antes.tar" "$BORA_ESTADO/ufw-estava-ativo"
else
    msg "Nada para desfazer: a receita não chegou a mudar o firewall."
fi
