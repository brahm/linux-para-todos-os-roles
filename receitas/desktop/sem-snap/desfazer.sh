#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita desktop/sem-snap (Sem Snap).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-sem-snap.sh
source ./comum-sem-snap.sh
exigir_apt

# 1. Sai o que a receita trouxe: o Firefox da Mozilla, a loja em pacote e o
#    Thunderbird do Flathub. Os perfis copiados ficam: são os seus dados.
if [ -f "$BORA_ESTADO/flatpaks-instalados" ]; then
    while read -r app; do
        [ -n "$app" ] || continue
        flatpak uninstall --system -y --noninteractive "$app" || aviso "não consegui remover o $app do Flathub"
    done <"$BORA_ESTADO/flatpaks-instalados"
    rm -f "$BORA_ESTADO/flatpaks-instalados"
fi
remover_pacotes_instalados
restaurar_arquivos

# 2. Volta o que o apt tirou junto com o snapd: o próprio snapd, os pacotes de
#    transição e os metapacotes do Ubuntu.
if [ -s "$BORA_ESTADO/debs-removidos" ]; then
    msg "Atualizando a lista de pacotes."
    apt_get update -q
    msg "Instalando de volta: $(tr '\n' ' ' <"$BORA_ESTADO/debs-removidos")"
    # Sem os recomendados: o que eles traziam nunca saiu, e assim não entra
    # nada que não estava antes (o snapd recomenda o gnupg, por exemplo).
    # shellcheck disable=SC2046
    apt_get install -y -q --no-install-recommends $(cat "$BORA_ESTADO/debs-removidos")
fi
rm -f "$BORA_ESTADO/debs-removidos"
if [ -f "$BORA_ESTADO/marcados-manual" ]; then
    # shellcheck disable=SC2046
    apt-mark auto $(sort -u "$BORA_ESTADO/marcados-manual") >/dev/null 2>&1 || true
    rm -f "$BORA_ESTADO/marcados-manual"
fi

# 3. Os snaps. As bases vêm sozinhas com os programas.
if [ -s "$BORA_ESTADO/snaps-removidos" ]; then
    if systemd_rodando && command -v snap >/dev/null; then
        systemctl start snapd.service 2>/dev/null || true
        snap wait system seed.loaded 2>/dev/null || true
        for s in $(grep -Ev "$SNAPS_DO_SISTEMA" "$BORA_ESTADO/snaps-removidos") $(grep -E '^(snap-store|firmware-updater|desktop-security-center|prompting-client|snapd-desktop-integration)$' "$BORA_ESTADO/snaps-removidos"); do
            if snap list "$s" >/dev/null 2>&1; then continue; fi
            msg "Instalando de volta o snap $s"
            snap install "$s" || aviso "não consegui instalar de volta o snap $s; tente depois com: sudo snap install $s"
        done
    else
        aviso "sem o systemd rodando, os snaps não voltam agora; instale depois com: sudo snap install $(grep -Ev "$SNAPS_DO_SISTEMA" "$BORA_ESTADO/snaps-removidos" | tr '\n' ' ')"
    fi
fi
rm -f "$BORA_ESTADO/snaps-removidos"

# 4. Os perfis voltam para onde o Snap procura, se ele ainda não tiver um.
if [ -f "$BORA_ESTADO/perfis-copiados" ]; then
    while IFS=$'\t' read -r p de para; do
        [ -n "$p" ] || continue
        casa=$(pasta_pessoal "$p")
        if [ -d "$casa/$para" ] && [ ! -e "$casa/$de" ]; then
            como_pessoa "$p" mkdir -p "$casa/$(dirname "$de")"
            como_pessoa "$p" cp -a "$casa/$para" "$casa/$de"
            msg "Perfil copiado de volta para $casa/$de"
        fi
    done <"$BORA_ESTADO/perfis-copiados"
    rm -f "$BORA_ESTADO/perfis-copiados"
fi
msg "O Snap voltou a ser como era antes."
