#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita seguranca/segredos (Verificação de segredos).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-segredos.sh
source ./comum-segredos.sh

for p in $PACOTES; do
    if ! pacote_instalado "$p"; then
        msg "Falta o pacote $p."
        exit 1
    fi
done
if ! tem_bloco "$(arquivo_ignore)"; then
    msg "O Git de $PESSOA ainda não ignora os arquivos .env e as chaves."
    exit 1
fi
if ! ganchos_prontos; then
    msg "O gitleaks ainda não confere os commits de $PESSOA."
    exit 1
fi
msg "O gitleaks já confere os commits de $PESSOA, e o Git já ignora os arquivos .env e as chaves."
exit 0
