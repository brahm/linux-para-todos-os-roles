#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

restaurar_arquivos
if [ -f "$BORA_ESTADO/chave-criada" ]; then
    # A chave pode já estar cadastrada no GitHub; apagar quebraria o acesso.
    msg "A chave SSH fica onde está: $(cat "$BORA_ESTADO/chave-criada"). Para apagar, remova o arquivo e a versão .pub, e tire a chave do GitHub ou do GitLab."
fi
remover_pastas_novas
remover_pacotes_instalados
msg "A configuração do Git voltou a ser como era antes."
