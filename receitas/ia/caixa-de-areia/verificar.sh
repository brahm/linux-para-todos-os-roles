#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-caixa.sh
source ./comum-caixa.sh

for p in $PACOTES; do
    if ! pacote_instalado "$p"; then
        msg "Falta o pacote $p."
        exit 1
    fi
done
if ! cmp -s ./caixa "$CAIXA"; then
    msg "Falta o comando caixa."
    exit 1
fi
if userns_restrito && ! cmp -s <(perfil_apparmor) "$PERFIL_APPARMOR"; then
    msg "O AppArmor ainda não deixa o bubblewrap abrir a caixa de areia."
    exit 1
fi
if claude_instalado && ! sandbox_claude_ligada; then
    msg "A caixa de areia do Claude Code ainda não está ligada."
    exit 1
fi
msg "A caixa de areia está pronta: rode os agentes com caixa <agente>."
exit 0
