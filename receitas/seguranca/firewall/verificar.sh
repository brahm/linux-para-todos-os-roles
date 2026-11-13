#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita seguranca/firewall (Firewall).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=regras.sh
source ./regras.sh

if ! command -v ufw >/dev/null; then
    msg "O ufw não está instalado."
    exit 1
fi
if ! ufw_ativo; then
    msg "O firewall está desligado."
    exit 1
fi
if ! padroes_certos; then
    msg "O firewall não bloqueia por padrão o que chega de fora."
    exit 1
fi
rede=$(descobrir_rede_local)
while read -r regra; do
    [ -n "$regra" ] || continue
    if ! regra_existe "$regra"; then
        msg "Falta a regra: $regra"
        exit 1
    fi
done < <(regras_do_perfil "$rede")
msg "O firewall está ligado com o perfil $BORA_PERFIL."
exit 0
