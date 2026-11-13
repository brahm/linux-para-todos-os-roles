#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita dev/node (Node.js).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-node.sh
source ./comum-node.sh

# O PATH de uma sessão comum, com /usr/local/bin antes de /usr/bin.
caminho="$BIN_DA_PESSOA:/usr/local/bin:/usr/bin:/bin"
# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
na_sessao() { como_pessoa "$PESSOA" env PATH="$caminho" "$@"; }
versao_certa() { [ "$(na_sessao node --version)" = "v$NODE_VERSAO" ]; }
roda_js() { [ "$(na_sessao node -e 'console.log(1 + 1)')" = 2 ]; }
global_sem_sudo() { [ "$(na_sessao npm prefix -g)" = "$(pasta_pessoal "$PESSOA")/.local" ]; }

conferir "Node.js $NODE_VERSAO (node --version)" versao_certa
conferir "npm (npm --version)" na_sessao npm --version
conferir "npx (npx --version)" na_sessao npx --version
conferir "o Node.js roda um programa" roda_js
conferir "npm install -g instala em ~/.local, sem sudo (npm prefix -g)" global_sem_sudo
conferir "a pasta dos programas do npm existe ($BIN_DA_PESSOA)" test -d "$BIN_DA_PESSOA"
resultado_dos_testes
