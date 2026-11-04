#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-atualizar.sh
source ./comum-atualizar.sh
exigir_apt

nenhum_pela_metade() { ! precisa_consertar_dpkg; }
nada_pendente() { [ "$(pacotes_pendentes)" -eq 0 ]; }

conferir "nenhum pacote instalado pela metade (dpkg --audit)" nenhum_pela_metade
conferir "nenhum pacote para atualizar (apt-get -s upgrade)" nada_pendente
if [ "${BORA_AUTOMATICAS:-sim}" = sim ]; then
    conferir "unattended-upgrades instalado" pacote_instalado unattended-upgrades
    conferir "atualizações automáticas ligadas (apt-config dump)" automaticas_ligadas
fi
resultado_dos_testes
