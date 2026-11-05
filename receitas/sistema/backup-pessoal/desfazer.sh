#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-backup.sh
source ./comum-backup.sh
exigir_apt

computador=$(valor_da_config COMPUTADOR)
desabilitar_unidades_habilitadas
restaurar_arquivos
if systemd_rodando; then
    systemctl daemon-reload
fi
rmdir /etc/bora /usr/local/lib/bora 2>/dev/null || true
remover_pacotes_instalados
msg "O backup automático foi desligado."
if [ -n "$computador" ]; then
    msg "As cópias que já estavam no disco externo continuam lá, em bora-backup/$computador. Apague à mão se não quiser mais."
fi
