#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita ia/lm-studio (LM Studio, para modelos de IA com janela).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

restaurar_arquivos
if [ -f "$BORA_ESTADO/link-criado" ]; then
    alvo=$(cat "$BORA_ESTADO/link-criado")
    if [ "$alvo" = /usr/local/bin/lm-studio ] && [ -L "$alvo" ]; then rm -f "$alvo"; fi
    rm -f "$BORA_ESTADO/link-criado"
fi
if [ -f "$BORA_ESTADO/link-anterior" ]; then
    destino=$(cat "$BORA_ESTADO/link-anterior")
    if [ -e "$destino" ]; then ln -sfn "$destino" /usr/local/bin/lm-studio; fi
    rm -f "$BORA_ESTADO/link-anterior"
fi
if [ -f "$BORA_ESTADO/lm-studio-instalado" ]; then
    dir=$(cat "$BORA_ESTADO/lm-studio-instalado")
    case "$dir" in
        /opt/lm-studio/[0-9]*)
            rm -rf "${dir:?}"
            msg "LM Studio removido: $dir"
            ;;
    esac
    rm -f "$BORA_ESTADO/lm-studio-instalado"
fi
remover_pastas_novas
remover_pacotes_instalados
msg "O LM Studio que a receita instalou foi removido. Os modelos que você baixou nele ficam em ~/.lmstudio."
