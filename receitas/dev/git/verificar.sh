#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-git.sh
source ./comum-git.sh

if ! pacote_instalado git; then
    msg "O Git não está instalado."
    exit 1
fi
if ! git_configurado; then
    msg "O Git de $PESSOA ainda não está configurado como a receita pede."
    exit 1
fi
msg "O Git de $PESSOA já está configurado, como $(valor_do_git user.name) <$(valor_do_git user.email)>."
exit 0
