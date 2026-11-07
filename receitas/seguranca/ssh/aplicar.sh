#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-ssh.sh
source ./comum-ssh.sh
exigir_apt

# Só chave, sem uma chave cadastrada, trancaria a pessoa do lado de fora.
if [ "${BORA_SO_CHAVE:-nao}" = sim ]; then
    pessoa=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
    chave_da_pessoa "$pessoa" ||
        falha "so_chave pede uma chave pública em $(pasta_pessoal "$pessoa")/.ssh/authorized_keys, e ela não existe. Copie a sua chave com ssh-copy-id, de outro computador, e rode o bora de novo"
fi

instalar_pacotes openssh-server

conteudo_config | escrever_arquivo "$CONFIG" 0644
pasta_do_sshd
if ! sshd -t; then
    restaurar_arquivos
    falha "o sshd recusou a configuração; nada foi mudado"
fi

unidade=$(unidade_ssh)
habilitar_unidade "$unidade"
if systemd_rodando && systemctl is-active --quiet ssh.service; then
    systemctl reload ssh.service
fi

rede=$(descobrir_rede_local)
if ufw_ativo; then
    if [ -z "$rede" ]; then
        falha "o firewall está ligado e não encontrei a rede local; informe rede_local no plano, por exemplo 192.168.0.0/24"
    fi
    regra=$(regra_ufw "$rede")
    if ! regra_existe "$regra"; then
        # shellcheck disable=SC2086
        ufw $regra >/dev/null
        printf '%s\n' "$regra" >>"$BORA_ESTADO/regras-ufw"
        msg "Firewall: SSH liberado só para a rede local ($rede)."
    fi
else
    aviso "o firewall não está ligado, então o SSH responde em qualquer rede em que este computador estiver. Para aceitar só a rede de casa, aplique também a receita seguranca/firewall"
fi

endereco=$(ip -4 -o addr show scope global 2>/dev/null | awk '{sub(/\/.*/, "", $4); print $4; exit}')
quem=$( (descobrir_pessoa "${BORA_USUARIO:-auto}") 2>/dev/null) || quem=voce
msg "Pronto. De outro computador da casa: ssh $quem@${endereco:-este-computador}"
