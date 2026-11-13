#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita ia/lm-studio (LM Studio, para modelos de IA com janela).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-lm-studio.sh
source ./comum-lm-studio.sh

if ! lms_instalado; then
    msg "O LM Studio $LMS_VERSAO não está instalado."
    exit 1
fi
if ! cmp -s <(atalho_esperado) "$LMS_ATALHO"; then
    msg "Falta o atalho do LM Studio no menu de aplicativos."
    exit 1
fi
for p in $LMS_PACOTES; do
    if ! pacote_instalado "$p"; then
        msg "Falta o pacote $p, que o LM Studio usa para abrir a janela."
        exit 1
    fi
done
msg "O LM Studio $LMS_VERSAO já está instalado."
exit 0
