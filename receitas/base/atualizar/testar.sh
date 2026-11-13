#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita base/atualizar (Sistema atualizado).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-atualizar.sh
source ./comum-atualizar.sh
exigir_apt

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
nenhum_pela_metade() { ! precisa_consertar_dpkg; }
nada_pendente() { [ "$(pacotes_pendentes)" -eq 0 ]; }

conferir "nenhum pacote instalado pela metade (dpkg --audit)" nenhum_pela_metade
conferir "nenhum pacote para atualizar (apt-get -s upgrade)" nada_pendente
if [ "${BORA_AUTOMATICAS:-sim}" = sim ]; then
    conferir "unattended-upgrades instalado" pacote_instalado unattended-upgrades
    conferir "atualizações automáticas ligadas (apt-config dump)" automaticas_ligadas
fi
resultado_dos_testes
