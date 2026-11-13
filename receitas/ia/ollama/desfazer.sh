#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita ia/ollama (Ollama, para modelos de IA no computador).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

desabilitar_unidades_habilitadas
restaurar_arquivos
if systemd_rodando; then systemctl daemon-reload; fi
if [ -f "$BORA_ESTADO/link-criado" ]; then
    alvo=$(cat "$BORA_ESTADO/link-criado")
    if [ "$alvo" = /usr/local/bin/ollama ] && [ -L "$alvo" ]; then rm -f "$alvo"; fi
    rm -f "$BORA_ESTADO/link-criado"
fi
if [ -f "$BORA_ESTADO/link-anterior" ]; then
    destino=$(cat "$BORA_ESTADO/link-anterior")
    if [ -e "$destino" ]; then ln -sfn "$destino" /usr/local/bin/ollama; fi
    rm -f "$BORA_ESTADO/link-anterior"
fi
if [ -f "$BORA_ESTADO/ollama-instalado" ]; then
    dir=$(cat "$BORA_ESTADO/ollama-instalado")
    case "$dir" in
        /opt/ollama/[0-9]*)
            rm -rf "${dir:?}"
            msg "Ollama removido: $dir"
            ;;
    esac
    rm -f "$BORA_ESTADO/ollama-instalado"
fi
# A conta do serviço leva junto a pasta dela, com os modelos baixados.
if [ -f "$BORA_ESTADO/conta-criada" ]; then
    pkill -u ollama 2>/dev/null || true
    if getent passwd ollama >/dev/null; then
        casa=$(getent passwd ollama | cut -d: -f6)
        userdel ollama
        if [ "$casa" = /usr/share/ollama ]; then rm -rf "${casa:?}"; fi
        getent group ollama >/dev/null && groupdel ollama
        msg "Conta ollama removida, com os modelos que estavam em $casa"
    fi
    rm -f "$BORA_ESTADO/conta-criada" "$BORA_ESTADO/modelos-baixados"
fi
rm -f "$BORA_ESTADO/servidor-temporario.log"
remover_pastas_novas
remover_pacotes_instalados
msg "O Ollama que a receita instalou foi removido."
