#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita base/atualizar (Sistema atualizado).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

desabilitar_unidades_habilitadas
restaurar_arquivos
remover_pacotes_instalados
msg "As atualizações automáticas voltaram a ser como eram antes."
msg "Os pacotes atualizados continuam na versão nova: o apt não volta versões."
msg "Se uma atualização trouxe problema, use o snapshot do sistema criado antes do plano."
