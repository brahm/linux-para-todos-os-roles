#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-sem-snap.sh
source ./comum-sem-snap.sh
exigir_apt

sem_snapd() { ! pacote_instalado snapd; }
sem_snaps() { [ -z "$(snaps_instalados)" ]; }
tinha() { grep -qx "$1" "$BORA_ESTADO/snaps-removidos" 2>/dev/null; }
perfis_no_lugar() {
    local p para
    [ -f "$BORA_ESTADO/perfis-copiados" ] || return 0
    while IFS=$'\t' read -r p _ para; do
        [ -n "$p" ] || continue
        [ -d "$(pasta_pessoal "$p")/$para" ] || return 1
    done <"$BORA_ESTADO/perfis-copiados"
}
thunderbird_flatpak() { flatpak info --system org.mozilla.Thunderbird; }

conferir "o snapd não está instalado (dpkg -l snapd)" sem_snapd
conferir "nenhum snap ficou em /var/lib/snapd/snaps" sem_snaps
conferir "o apt não instala o snapd de volta (apt-cache policy snapd)" snapd_bloqueado
if tinha firefox; then
    conferir "o Firefox é o pacote da Mozilla (apt-cache policy firefox)" firefox_da_mozilla
fi
if tinha thunderbird; then
    conferir "o Thunderbird é o do Flathub" thunderbird_flatpak
fi
conferir "os perfis copiados estão no lugar novo" perfis_no_lugar
resultado_dos_testes
