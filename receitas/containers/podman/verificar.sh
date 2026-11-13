#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita containers/podman (Contêineres com Podman).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-podman.sh
source ./comum-podman.sh

for p in $PACOTES; do
    if ! pacote_instalado "$p"; then
        msg "Falta o pacote $p."
        exit 1
    fi
done
if ! cmp -s <(registros_esperado) "$REGISTROS"; then
    msg "O Podman ainda não procura as imagens no Docker Hub."
    exit 1
fi
for f in subuid subgid; do
    if ! tem_faixa "$f"; then
        msg "$PESSOA ainda não tem a faixa de IDs para os contêineres (/etc/$f)."
        exit 1
    fi
done
msg "O Podman já está pronto para $PESSOA."
exit 0
