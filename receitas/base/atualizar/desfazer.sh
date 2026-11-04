#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

desabilitar_unidades_habilitadas
restaurar_arquivos
remover_pacotes_instalados
msg "As atualizações automáticas voltaram a ser como eram antes."
msg "Os pacotes atualizados continuam na versão nova: o apt não volta versões."
msg "Se uma atualização trouxe problema, use o snapshot do sistema criado antes do plano."
