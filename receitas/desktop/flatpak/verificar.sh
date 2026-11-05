#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-flatpak.sh
source ./comum-flatpak.sh
exigir_apt

if ! pacote_instalado flatpak; then
    msg "O Flatpak não está instalado."
    exit 1
fi
if ! flathub_ligado; then
    msg "O Flathub não está configurado."
    exit 1
fi
for p in $(plugins_da_loja); do
    if ! pacote_instalado "$p"; then
        msg "A loja de aplicativos ainda não mostra o Flathub (falta $p)."
        exit 1
    fi
done
msg "O Flatpak está instalado e o Flathub, ligado."
exit 0
