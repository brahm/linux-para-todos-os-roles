# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

ARQUIVO_AUTOMATICAS=/etc/apt/apt.conf.d/20auto-upgrades

precisa_consertar_dpkg() { [ -n "$(dpkg --audit 2>/dev/null)" ]; }

# Quantos pacotes o apt atualizaria agora (sem contar os retidos de propósito).
pacotes_pendentes() {
    LC_ALL=C apt-get -s -o Debug::NoLocking=1 upgrade --with-new-pkgs 2>/dev/null | grep -c '^Inst ' || true
}

automaticas_ligadas() {
    pacote_instalado unattended-upgrades || return 1
    local conf
    conf=$(apt-config dump 2>/dev/null)
    grep -qx 'APT::Periodic::Update-Package-Lists "1";' <<<"$conf" &&
        grep -qx 'APT::Periodic::Unattended-Upgrade "1";' <<<"$conf"
}
