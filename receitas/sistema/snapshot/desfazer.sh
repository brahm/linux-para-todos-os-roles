#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita sistema/snapshot (Snapshot do sistema).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
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

# A configuração do Timeshift não existia antes do bora?
config_nova=nao
if grep -qxF "$CONFIG" "$BORA_ESTADO/arquivos-novos" 2>/dev/null; then config_nova=sim; fi

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
# O "timeshift --list" acima grava um timeshift.json quando ele não existe.
# Num Timeshift que já estava instalado (como no Linux Mint), esse arquivo
# ficaria para trás; ele sai de novo, como antes do bora.
if [ "$config_nova" = sim ]; then rm -f "$CONFIG"; fi
msg "O Timeshift voltou a ser como era antes."
