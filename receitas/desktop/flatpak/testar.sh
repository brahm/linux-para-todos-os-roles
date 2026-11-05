#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-flatpak.sh
source ./comum-flatpak.sh
exigir_apt

com_assinatura() {
    # gpg-verify ligado: os aplicativos baixados são conferidos pela assinatura do Flathub.
    flatpak remotes --system --columns=name,options 2>/dev/null | awk '$1 == "flathub"' | grep -qv 'no-gpg-verify'
}
# O pacote põe /var/lib/flatpak/exports/share no XDG_DATA_DIRS de cada login.
caminho_no_login() { grep -q 'flatpak' /etc/profile.d/flatpak.sh; }

conferir "Flatpak instalado (flatpak --version)" flatpak --version
conferir "Flathub configurado para o sistema todo (flatpak remotes)" flathub_ligado
conferir "o Flathub confere a assinatura dos aplicativos" com_assinatura
conferir "os aplicativos aparecem no menu depois do login" caminho_no_login
for p in $(plugins_da_loja); do
    conferir "a loja de aplicativos mostra o Flathub ($p)" pacote_instalado "$p"
done
resultado_dos_testes
