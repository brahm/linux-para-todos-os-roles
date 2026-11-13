# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

PIN_SNAPD=/etc/apt/preferences.d/bora-sem-snap.pref
CHAVE_MOZILLA=/etc/apt/keyrings/packages.mozilla.org.asc
FONTE_MOZILLA=/etc/apt/sources.list.d/mozilla.sources
PIN_MOZILLA=/etc/apt/preferences.d/mozilla.pref
URL_CHAVE_MOZILLA=https://packages.mozilla.org/apt/repo-signing-key.gpg
# A impressão digital publicada pela Mozilla em
# https://support.mozilla.org/kb/install-firefox-linux
DIGITAL_MOZILLA=35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3

# Snaps que vêm com o Ubuntu e saem sem perguntar: bases, temas, a loja e o
# atualizador de firmware, que têm equivalentes em pacote. As plataformas do
# GNOME mudam de nome com a base (gnome-46-2404, gnome-core26), e as duas
# formas entram aqui.
SNAPS_DO_SISTEMA='^(bare|core[0-9]*|snapd|gtk-common-themes|gtk2-common-themes|gnome-[0-9].*|gnome-core[0-9]*|mesa-.*|kf[56]-.*|snap-store|snapd-desktop-integration|firmware-updater|desktop-security-center|prompting-client)$'
# Snaps que a receita troca por outra versão do mesmo programa.
SNAPS_TROCADOS='^(firefox|thunderbird)$'
# Pacotes que o apt pode remover junto com o snapd: os pacotes de transição
# (que só instalam o Snap) e os metapacotes do Ubuntu.
DEBS_PERMITIDOS='^(snapd|firefox|thunderbird|chromium-browser|ubuntu-desktop|ubuntu-desktop-minimal|ubuntu-server|ubuntu-server-minimal|gnome-software-plugin-snap|snapd-.*|lxd-installer|ubuntu-snappy.*)$'

# Os snaps instalados, um por linha. Lê a pasta do snapd, que funciona mesmo
# sem o serviço rodando.
snaps_instalados() {
    local f
    for f in /var/lib/snapd/snaps/*.snap; do
        [ -e "$f" ] || continue
        f=${f##*/}
        printf '%s\n' "${f%%_*}"
    done | sort -u
}

snaps_sem_troca() { snaps_instalados | grep -Ev "$SNAPS_DO_SISTEMA|$SNAPS_TROCADOS" || true; }

# O apt não instala o snapd de jeito nenhum?
# A saída vai para uma variável antes do grep: com pipefail, um grep -q que
# para no meio faria o apt-cache sair com erro.
snapd_bloqueado() { grep -q 'Candidate: (none)' <<<"$(LC_ALL=C apt-cache policy snapd 2>/dev/null)"; }

# É o pacote do Ubuntu que só instala o Snap? (versão "1:1snap1-...")
deb_de_transicao() { grep -q 'snap' <<<"$(dpkg-query -W -f='${Version}' "$1" 2>/dev/null)"; }

# O Firefox instalado é o da Mozilla?
firefox_da_mozilla() {
    pacote_instalado firefox && ! deb_de_transicao firefox &&
        grep -q packages.mozilla.org <<<"$(grep -A1 '^ \*\*\*' <<<"$(LC_ALL=C apt-cache policy firefox 2>/dev/null)")"
}

# Copia uma pasta de perfil de um caminho para outro, como a própria pessoa,
# se o destino ainda não existir.
copiar_perfil() {
    local p=$1 de=$2 para=$3 casa
    casa=$(pasta_pessoal "$p")
    [ -d "$casa/$de" ] || return 0
    [ ! -e "$casa/$para" ] || return 0
    como_pessoa "$p" mkdir -p "$casa/$(dirname "$para")"
    como_pessoa "$p" cp -a "$casa/$de" "$casa/$para"
    msg "Perfil copiado para $casa/$para"
    printf '%s\t%s\t%s\n' "$p" "$de" "$para" >>"$BORA_ESTADO/perfis-copiados"
}

# Onde cada programa guarda o perfil: no Snap e na versão que entra no lugar.
PERFIL_FIREFOX_SNAP=snap/firefox/common/.mozilla/firefox
PERFIL_FIREFOX_DEB=.mozilla/firefox
PERFIL_THUNDERBIRD_SNAP=snap/thunderbird/common/.thunderbird
PERFIL_THUNDERBIRD_FLATPAK=.var/app/org.mozilla.Thunderbird/.thunderbird
