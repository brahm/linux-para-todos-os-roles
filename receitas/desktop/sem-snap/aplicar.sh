#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-sem-snap.sh
source ./comum-sem-snap.sh
exigir_apt

# 1. O que sai. Um snap que a receita não sabe trocar faria um programa sumir
#    sem aviso, então ela para e diz qual é.
outros=$(snaps_sem_troca)
if [ -n "$outros" ]; then
    falha "estes snaps não têm um substituto que a receita conheça: $(tr '\n' ' ' <<<"$outros"). Instale a versão do Flathub ou do apt de cada um, remova o snap com 'sudo snap remove <nome>' e rode o bora de novo"
fi
[ -f "$BORA_ESTADO/snaps-removidos" ] || snaps_instalados >"$BORA_ESTADO/snaps-removidos"
tinha() { grep -qx "$1" "$BORA_ESTADO/snaps-removidos"; }

if tinha thunderbird; then
    if ! command -v flatpak >/dev/null || ! flatpak remotes --system --columns=name 2>/dev/null | grep -qx flathub; then
        falha "o Thunderbird do Snap vai para a versão do Flathub, que ainda não está ligado; aplique antes a receita desktop/flatpak"
    fi
fi

# 2. O repositório da Mozilla entra antes de qualquer coisa sair: se a
#    internet ou a chave falharem, nada mudou e o Firefox do Snap continua.
trocar_firefox=nao
if tinha firefox || { pacote_instalado firefox && deb_de_transicao firefox; }; then
    trocar_firefox=sim
fi
if [ "$trocar_firefox" = sim ] && ! firefox_da_mozilla; then
    command -v gpg >/dev/null || instalar_pacotes gpg
    tmp=$(mktemp)
    if ! python3 - "$URL_CHAVE_MOZILLA" "$tmp" <<'PY'; then
import sys, urllib.request
try:
    with urllib.request.urlopen(sys.argv[1], timeout=60) as r, open(sys.argv[2], "wb") as f:
        f.write(r.read())
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
PY
        rm -f "$tmp"
        falha "não consegui baixar a chave do repositório da Mozilla ($URL_CHAVE_MOZILLA). Confira a internet e rode o bora de novo; nada foi mudado"
    fi
    digital=$(gpg --show-keys --with-colons "$tmp" 2>/dev/null | awk -F: '/^fpr/ {print $10; exit}')
    if [ "$digital" != "$DIGITAL_MOZILLA" ]; then
        rm -f "$tmp"
        falha "a chave baixada de packages.mozilla.org não é a que a Mozilla publica (${digital:-nenhuma}); nada foi mudado"
    fi
    escrever_arquivo "$CHAVE_MOZILLA" 0644 <"$tmp"
    rm -f "$tmp"
    escrever_arquivo "$FONTE_MOZILLA" 0644 <<'FONTE'
# Escrito pelo bora (receita desktop/sem-snap): o Firefox oficial da Mozilla.
Types: deb
URIs: https://packages.mozilla.org/apt
Suites: mozilla
Components: main
Signed-By: /etc/apt/keyrings/packages.mozilla.org.asc
FONTE
    escrever_arquivo "$PIN_MOZILLA" 0644 <<'PIN'
# Escrito pelo bora (receita desktop/sem-snap): o Firefox vem da Mozilla, e
# não do pacote de transição do Ubuntu, que instalaria o Snap.
Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000
PIN
    msg "Atualizando a lista de pacotes, com o repositório da Mozilla."
    apt_get update -q
    if ! grep -q packages.mozilla.org <<<"$(LC_ALL=C apt-cache policy firefox 2>/dev/null)"; then
        restaurar_arquivos
        apt_get update -q || true
        falha "o repositório da Mozilla não respondeu; nada foi mudado"
    fi
fi

if pacote_instalado snapd; then
    sai=$(_removeria snapd)
    estranhos=$(grep -Ev "$DEBS_PERMITIDOS" <<<"$sai" || true)
    if [ -n "$estranhos" ]; then
        falha "tirar o snapd levaria junto pacotes que não são do Snap: $(tr '\n' ' ' <<<"$estranhos"). Nada foi mudado"
    fi
    [ -f "$BORA_ESTADO/debs-removidos" ] || printf '%s\n' "$sai" | sed '/^$/d' >"$BORA_ESTADO/debs-removidos"

    # 3. Os perfis. O snap remove apaga ~/snap/<programa>, então a cópia vem antes.
    for p in $(pessoas_do_sistema); do
        if tinha firefox; then copiar_perfil "$p" "$PERFIL_FIREFOX_SNAP" "$PERFIL_FIREFOX_DEB"; fi
        if tinha thunderbird; then copiar_perfil "$p" "$PERFIL_THUNDERBIRD_SNAP" "$PERFIL_THUNDERBIRD_FLATPAK"; fi
    done

    # 4. Os metapacotes do Ubuntu (ubuntu-desktop e companhia) saem junto com
    #    o snapd. O que eles puxavam fica, marcado como instalado de propósito,
    #    para o autoremove nunca levar o ambiente gráfico.
    for meta in $(grep -E '^ubuntu-(desktop|server)' "$BORA_ESTADO/debs-removidos" || true); do
        apt-cache depends --no-pre-depends --no-suggests --no-conflicts --no-breaks --no-replaces --no-enhances "$meta" 2>/dev/null |
            awk '/Depends:|Recommends:/ {print $2}' | grep -v '^<' | sort -u | while read -r dep; do
            if pacote_instalado "$dep" && apt-mark showauto "$dep" | grep -qx "$dep"; then
                apt-mark manual "$dep" >/dev/null
                echo "$dep" >>"$BORA_ESTADO/marcados-manual"
            fi
        done
    done

    # 5. Tira os snaps (com o serviço rodando, um a um, dos programas para as
    #    bases) e o snapd. O snapd fica num instantâneo automático por 31 dias.
    if systemd_rodando && systemctl is-active --quiet snapd.service 2>/dev/null; then
        for s in $(grep -Ev "$SNAPS_DO_SISTEMA" "$BORA_ESTADO/snaps-removidos") $(grep -E 'snap-store|firmware-updater|desktop-security-center|prompting-client|snapd-desktop-integration' "$BORA_ESTADO/snaps-removidos"); do
            msg "Removendo o snap $s"
            snap remove "$s" || aviso "o snap $s não saiu agora; ele sai junto com o snapd"
        done
    fi
    msg "Removendo o snapd: $(tr '\n' ' ' <"$BORA_ESTADO/debs-removidos")"
    # shellcheck disable=SC2046
    apt_get purge -y -q $(cat "$BORA_ESTADO/debs-removidos")
fi

# 6. O apt não traz o snapd de volta, nem por um pacote de transição.
escrever_arquivo "$PIN_SNAPD" 0644 <<'PIN'
# Escrito pelo bora (receita desktop/sem-snap): o apt não instala o snapd.
Package: snapd
Pin: release a=*
Pin-Priority: -10
PIN

# 7. O Firefox da Mozilla no lugar do Firefox do Snap.
if [ "$trocar_firefox" = sim ] && ! firefox_da_mozilla; then
    instalar_pacotes firefox firefox-l10n-pt-br
fi

# 8. O Thunderbird do Flathub e a loja de aplicativos em pacote.
if tinha thunderbird && ! flatpak info --system org.mozilla.Thunderbird >/dev/null 2>&1; then
    msg "Instalando o Thunderbird do Flathub."
    flatpak install --system -y --noninteractive flathub org.mozilla.Thunderbird
    echo org.mozilla.Thunderbird >>"$BORA_ESTADO/flatpaks-instalados"
fi
if tinha snap-store; then
    if command -v flatpak >/dev/null; then
        instalar_pacotes gnome-software gnome-software-plugin-flatpak
    else
        instalar_pacotes gnome-software
    fi
fi
msg "Pronto. O Snap saiu e não volta pelo apt."
