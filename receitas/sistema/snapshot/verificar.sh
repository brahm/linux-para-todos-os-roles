#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita sistema/snapshot (Snapshot do sistema).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-snapshot.sh
source ./comum-snapshot.sh
exigir_apt

if ! command -v timeshift >/dev/null; then
    msg "O Timeshift não está instalado."
    exit 1
fi
read -r _ uuid _ modo < <(descobrir_destino)
if ! config_certa "$uuid" "$modo"; then
    msg "O Timeshift não está configurado como esta receita pede."
    exit 1
fi
if ! systemctl is-enabled --quiet "$UNIDADE.timer" 2>/dev/null; then
    msg "O agendamento dos snapshots não está ligado."
    exit 1
fi
if [ "${BORA_CRIAR_AGORA:-sim}" = sim ] && [ -z "$(listar_snapshots)" ]; then
    msg "Ainda não há nenhum snapshot."
    exit 1
fi
msg "O Timeshift está configurado e agendado."
exit 0
