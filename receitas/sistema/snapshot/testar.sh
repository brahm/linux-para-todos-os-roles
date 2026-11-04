#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-snapshot.sh
source ./comum-snapshot.sh
exigir_apt

read -r _ uuid _ modo < <(descobrir_destino)
tem_snapshot() { [ -n "$(listar_snapshots)" ]; }
lista_funciona() { timeshift --list --scripted; }

conferir "Timeshift instalado" command -v timeshift
conferir "configuração aponta para o dispositivo certo (UUID $uuid, modo $modo)" config_certa "$uuid" "$modo"
conferir "o Timeshift consegue ler o dispositivo (timeshift --list)" lista_funciona
conferir "agendamento ligado ($UNIDADE.timer)" systemctl is-enabled --quiet "$UNIDADE.timer"
if [ "${BORA_CRIAR_AGORA:-sim}" = sim ]; then
    conferir "existe pelo menos um snapshot" tem_snapshot
fi
resultado_dos_testes
