#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita ia/chaves-de-api (Chaves de API guardadas).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-chaves.sh
source ./comum-chaves.sh

if ! permissoes_certas; then
    msg "Ainda não há um arquivo de chaves de API só de $PESSOA em $ARQUIVO."
    exit 1
fi
if ! tem_bloco; then
    msg "O terminal de $PESSOA ainda não carrega as chaves de API."
    exit 1
fi
msg "As chaves de API de $PESSOA ficam em $ARQUIVO, só com permissão dela."
exit 0
