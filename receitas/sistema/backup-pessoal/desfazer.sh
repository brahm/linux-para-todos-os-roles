#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita sistema/backup-pessoal (Backup da pasta pessoal).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
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
