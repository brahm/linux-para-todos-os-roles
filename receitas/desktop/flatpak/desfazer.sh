#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-flatpak.sh
source ./comum-flatpak.sh
exigir_apt

if [ -f "$BORA_ESTADO/remoto-criado" ] && command -v flatpak >/dev/null; then
    apps=$(flatpak list --system --app --columns=application,origin 2>/dev/null | awk '$2 == "flathub" {print $1}')
    if [ -n "$apps" ]; then
        # Remover o Flathub agora quebraria as atualizações desses aplicativos.
        aviso "estes aplicativos vieram do Flathub depois do bora, e por isso o Flathub e o Flatpak continuam instalados: $(tr '\n' ' ' <<<"$apps")"
        msg "Para tirar tudo depois: remova os aplicativos com 'flatpak uninstall', e então rode 'sudo flatpak remote-delete flathub' e 'sudo apt purge flatpak'."
        exit 0
    fi
    flatpak remote-delete --system flathub
    msg "O Flathub foi removido."
fi
rm -f "$BORA_ESTADO/remoto-criado"
remover_pacotes_instalados
msg "O Flatpak voltou a ser como era antes."
