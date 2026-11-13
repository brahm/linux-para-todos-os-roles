#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita dev/compilacao (Ferramentas de compilação).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-compilacao.sh
source ./comum-compilacao.sh

# shellcheck disable=SC2086
instalar_pacotes $PACOTES
msg "Pronto: gcc, g++, make e pkg-config instalados."
