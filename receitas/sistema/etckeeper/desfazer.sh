#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

if [ "$(cat "$BORA_ESTADO/etc-git-antes" 2>/dev/null || echo sim)" = nao ] && [ -d /etc/.git ]; then
    # Uma cópia do histórico fica em /var/backups, caso você queira consultar depois.
    copia="/var/backups/bora-etc-historico-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -C /etc -czf "$copia" .git .etckeeper 2>/dev/null || tar -C /etc -czf "$copia" .git
    chmod 600 "$copia"
    msg "Uma cópia do histórico do /etc ficou em $copia"
    if command -v etckeeper >/dev/null; then
        etckeeper uninit -f
    else
        rm -rf "/etc/.git" "/etc/.etckeeper" "/etc/.gitignore"
    fi
    msg "O histórico do /etc foi removido."
fi
rm -f "$BORA_ESTADO/etc-git-antes"
remover_pacotes_instalados
msg "O etckeeper voltou a ser como era antes."
