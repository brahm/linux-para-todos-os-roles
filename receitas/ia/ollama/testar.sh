#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita ia/ollama (Ollama, para modelos de IA no computador).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-ollama.sh
source ./comum-ollama.sh

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
versao_certa() { "$OLLAMA_BIN" --version 2>&1 | grep -qF "$OLLAMA_VERSAO"; }
so_neste_computador() { grep -qx "Environment=OLLAMA_HOST=$OLLAMA_ENDERECO" "$OLLAMA_UNIDADE"; }
sem_porta_aberta() { ss -Hltn 2>/dev/null | awk '$4 ~ /^(0\.0\.0\.0|\[::\]|\*):11434$/ {aberta = 1} END {exit aberta}'; }
modelo_listado() { com_servidor "$OLLAMA_BIN" list | awk -v m="$1" 'NR > 1 && $1 == m {achou = 1} END {exit !achou}'; }
nome_completo() { [[ "$1" == *:* ]] && echo "$1" || echo "$1:latest"; }

conferir "Ollama $OLLAMA_VERSAO (ollama --version)" versao_certa
conferir "o serviço ollama.service está habilitado" systemctl is-enabled --quiet ollama.service
conferir "o Ollama atende só este computador ($OLLAMA_ENDERECO)" so_neste_computador
if systemd_rodando; then
    conferir "o serviço responde em http://$OLLAMA_ENDERECO" api_responde
    conferir "nenhuma porta do Ollama aberta para a rede" sem_porta_aberta
fi
conferir "a pasta dos modelos é da conta $OLLAMA_CONTA" test "$(stat -c %U "$OLLAMA_CASA")" = "$OLLAMA_CONTA"
if [ "$MODELO" != nenhum ]; then
    conferir "o modelo $MODELO está baixado (ollama list)" modelo_listado "$(nome_completo "$MODELO")"
fi
resultado_dos_testes
