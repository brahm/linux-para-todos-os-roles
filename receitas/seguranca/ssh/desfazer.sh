#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ -f "$BORA_ESTADO/regras-ufw" ]; then
    while read -r regra; do
        [ -n "$regra" ] || continue
        # shellcheck disable=SC2086
        ufw delete $regra >/dev/null 2>&1 || true
        msg "Regra do firewall removida: $regra"
    done <"$BORA_ESTADO/regras-ufw"
    rm -f "$BORA_ESTADO/regras-ufw"
fi
restaurar_arquivos
desabilitar_unidades_habilitadas
if systemd_rodando && systemctl is-active --quiet ssh.service 2>/dev/null; then
    systemctl reload ssh.service 2>/dev/null || true
fi
if [ -s "$BORA_ESTADO/pacotes-novos" ] && pacote_instalado openssh-server; then
    aviso "o servidor SSH vai ser removido: quem está conectado por SSH agora continua, mas uma conexão nova não entra mais"
fi
remover_pacotes_instalados
msg "O SSH voltou a ser como era antes."
