#!/usr/bin/env bash
# Já está aplicada? 0 = sim, 1 = precisa aplicar.
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-atualizar.sh
source ./comum-atualizar.sh
exigir_apt

marca=/var/lib/apt/periodic/update-success-stamp
if [ ! -f "$marca" ] || [ -z "$(find "$marca" -mmin -360 2>/dev/null)" ]; then
    msg "A lista de pacotes não foi atualizada nas últimas 6 horas."
    exit 1
fi
if precisa_consertar_dpkg; then
    msg "Há pacotes instalados pela metade."
    exit 1
fi
n=$(pacotes_pendentes)
if [ "$n" -gt 0 ]; then
    msg "$n pacote(s) para atualizar."
    exit 1
fi
if [ "${BORA_AUTOMATICAS:-sim}" = sim ] && ! automaticas_ligadas; then
    msg "As atualizações automáticas de segurança estão desligadas."
    exit 1
fi
msg "O sistema está atualizado."
exit 0
