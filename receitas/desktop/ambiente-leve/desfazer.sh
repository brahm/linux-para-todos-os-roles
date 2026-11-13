#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita desktop/ambiente-leve (Ambiente gráfico leve).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-ambiente.sh
source ./comum-ambiente.sh
exigir_apt

# Remover o ambiente com alguém dentro dele derrubaria a sessão dessa pessoa.
for proc in xfce4-session lxqt-session; do
    if pgrep -x "$proc" >/dev/null 2>&1; then
        falha "alguém está usando o ambiente leve agora ($proc); saia dessa sessão, entre no ambiente antigo e desfaça de novo"
    fi
done
restaurar_arquivos
remover_pacotes_instalados
msg "O ambiente leve foi removido. O ambiente antigo continua como estava."
