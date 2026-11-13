#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita sistema/snapshot (Snapshot do sistema).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-snapshot.sh
source ./comum-snapshot.sh
exigir_apt

read -r _ uuid _ modo < <(descobrir_destino)
# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
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
