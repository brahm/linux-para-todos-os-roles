#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-snapshot.sh
source ./comum-snapshot.sh
exigir_apt

desabilitar_unidades_habilitadas

# Apaga só o snapshot que esta receita criou; os outros ficam.
if [ -s "$BORA_ESTADO/snapshots-criados" ] && command -v timeshift >/dev/null; then
    while read -r nome; do
        [ -n "$nome" ] || continue
        msg "Apagando o snapshot criado por esta receita: $nome"
        timeshift --delete --snapshot "$nome" --scripted --yes || aviso "não consegui apagar o snapshot $nome"
    done <"$BORA_ESTADO/snapshots-criados"
    rm -f "$BORA_ESTADO/snapshots-criados"
fi

restaurar_arquivos
if systemd_rodando; then
    systemctl daemon-reload
fi
remover_pacotes_instalados

if command -v timeshift >/dev/null && [ -n "$(listar_snapshots 2>/dev/null || true)" ]; then
    msg "Outros snapshots continuam guardados. Para ver: sudo timeshift --list"
elif [ -d /timeshift/snapshots ] && [ -n "$(ls -A /timeshift/snapshots 2>/dev/null)" ]; then
    msg "Ficaram snapshots antigos em /timeshift/snapshots. Eles ocupam espaço e podem ser apagados à mão."
fi
msg "O Timeshift voltou a ser como era antes."
