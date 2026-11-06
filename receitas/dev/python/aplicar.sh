#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-python.sh
source ./comum-python.sh

# shellcheck disable=SC2086
instalar_pacotes $PACOTES
# O ~/.profile do Debian e do Ubuntu põe ~/.local/bin no PATH se a pasta
# existir na hora do login. Criando agora, os programas do pipx funcionam
# a partir do próximo login, sem mexer em arquivo nenhum.
if [ ! -d "$BIN_DA_PESSOA" ]; then
    criar_pasta_da_pessoa "$PESSOA" "$BIN_DA_PESSOA"
    msg "Pasta criada: $BIN_DA_PESSOA (entra no PATH no próximo login)"
fi
msg "Pronto: $(python3 --version). Para cada projeto, crie um ambiente com: python3 -m venv .venv && source .venv/bin/activate"
