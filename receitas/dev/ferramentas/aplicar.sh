#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-ferramentas.sh
source ./comum-ferramentas.sh

# shellcheck disable=SC2086
instalar_pacotes $PACOTES
if fd_de_outro; then
    aviso "já existe $LINK_FD, que não veio do bora; ele fica, e o fd do Debian continua como fdfind"
elif ! fd_ligado; then
    ln -s /usr/bin/fdfind "$LINK_FD"
    echo "$LINK_FD" >>"$BORA_ESTADO/links-criados"
    msg "Comando criado: fd (o fdfind do Debian)"
fi
msg "Pronto: rg, fd, jq e gh instalados. Para entrar no GitHub pelo terminal: gh auth login"
