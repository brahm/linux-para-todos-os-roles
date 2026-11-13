#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita sistema/zram (Memória comprimida (zram)).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-zram.sh
source ./comum-zram.sh
exigir_apt

if zram_do_bora && systemd_rodando && zram_ligado; then
    msg "Desligando o zram. O que estava nele volta para a memória."
    if ! systemctl stop dev-zram0.swap; then
        aviso "não deu para desligar o zram agora, provavelmente por falta de memória livre; ele sai no próximo reinício"
    fi
    systemctl stop systemd-zram-setup@zram0.service 2>/dev/null || true
fi
restaurar_arquivos
if systemd_rodando && [ -f "$BORA_ESTADO/sysctl-antes" ]; then
    while IFS= read -r linha; do
        if [ -n "${linha#*=}" ]; then sysctl -q -w "$linha" || true; fi
    done <"$BORA_ESTADO/sysctl-antes"
fi
rm -f "$BORA_ESTADO/sysctl-antes"
remover_pacotes_instalados
if systemd_rodando; then systemctl daemon-reload; fi
msg "O zram voltou a ser como era antes."
