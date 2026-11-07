#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-ssh.sh
source ./comum-ssh.sh
exigir_apt

senha_esperada=yes
[ "${BORA_SO_CHAVE:-nao}" = sim ] && senha_esperada=no
root_bloqueado() { [ "$(valor_efetivo permitrootlogin)" = no ]; }
senha_certa() { [ "$(valor_efetivo passwordauthentication)" = "$senha_esperada" ]; }
tentativas() { [ "$(valor_efetivo maxauthtries)" = 4 ]; }
ligado_no_boot() { systemctl is-enabled --quiet "$(unidade_ssh)"; }
escutando() { [ -n "$(ss -Hltn 'sport = :22')" ]; }
regra_no_firewall() { regra_existe "$(regra_ufw "$(descobrir_rede_local)")"; }

conferir "servidor SSH instalado (openssh-server)" pacote_instalado openssh-server
conferir "o sshd aceita a configuração (sshd -t)" config_valida
conferir "o root não entra por SSH (PermitRootLogin no)" root_bloqueado
if [ "$senha_esperada" = no ]; then
    conferir "só entra quem tem chave (PasswordAuthentication no)" senha_certa
else
    conferir "entra com a senha da conta ou com chave (PasswordAuthentication yes)" senha_certa
fi
conferir "no máximo 4 tentativas por conexão (MaxAuthTries 4)" tentativas
conferir "o SSH liga junto com o computador ($(unidade_ssh))" ligado_no_boot
if systemd_rodando; then
    conferir "o SSH está esperando conexões na porta 22" escutando
fi
if ufw_ativo; then
    conferir "o firewall libera o SSH só para a rede local" regra_no_firewall
fi
resultado_dos_testes
