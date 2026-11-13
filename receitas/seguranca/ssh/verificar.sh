#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita seguranca/ssh (Acesso por SSH na rede de casa).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-ssh.sh
source ./comum-ssh.sh
exigir_apt

if ! pacote_instalado openssh-server; then
    msg "O servidor SSH não está instalado."
    exit 1
fi
if [ ! -f "$CONFIG" ] || ! cmp -s <(conteudo_config) "$CONFIG"; then
    msg "A configuração do bora para o SSH ainda não está em $CONFIG."
    exit 1
fi
if ufw_ativo; then
    rede=$(descobrir_rede_local)
    if [ -n "$rede" ] && ! ssh_liberado "$rede"; then
        msg "O firewall ainda não libera o SSH para a rede local."
        exit 1
    fi
fi
msg "O SSH já está ligado, com a configuração do bora."
exit 0
