# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

# O arquivo da receita. Os arquivos de sshd_config.d são lidos em ordem
# alfabética, e o sshd fica com o primeiro valor de cada opção: o 10 vem
# antes do 50-cloud-init.conf e dos que as distros trazem.
CONFIG=/etc/ssh/sshd_config.d/10-bora.conf

conteudo_config() {
    local senha=yes
    [ "${BORA_SO_CHAVE:-nao}" = sim ] && senha=no
    cat <<CONF
# Escrito pelo bora (receita seguranca/ssh). Para mudar, rode o bora de novo
# ou edite este arquivo e rode: sudo sshd -t && sudo systemctl reload ssh
PermitRootLogin no
PasswordAuthentication $senha
KbdInteractiveAuthentication no
PermitEmptyPasswords no
MaxAuthTries 4
LoginGraceTime 30
X11Forwarding no
CONF
}

# Imprime a rede local em CIDR (por exemplo 192.168.0.0/24), ou nada.
descobrir_rede_local() {
    if [ "${BORA_REDE_LOCAL:-auto}" != auto ]; then
        printf '%s\n' "$BORA_REDE_LOCAL"
        return 0
    fi
    local dev endereco
    dev=$(ip -4 route show default 2>/dev/null | awk '{for (i = 1; i < NF; i++) if ($i == "dev") {print $(i + 1); exit}}')
    [ -n "$dev" ] || return 0
    endereco=$(ip -4 -o addr show dev "$dev" 2>/dev/null | awk '{print $4; exit}')
    [ -n "$endereco" ] || return 0
    python3 - "$endereco" <<'PY'
import ipaddress, sys
rede = ipaddress.ip_interface(sys.argv[1]).network
locais = [ipaddress.ip_network(r) for r in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
if any(rede.subnet_of(r) for r in locais):
    print(rede)
PY
}

ufw_ativo() { command -v ufw >/dev/null && grep -q '^Status: active' <<<"$(LC_ALL=C ufw status 2>/dev/null)"; }

# O ufw guarda uma regra só por endereço, porta e protocolo: adicionar a mesma
# regra com outro comentário só troca o comentário. A receita seguranca/firewall
# libera o SSH com o comentário dela, e as duas receitas ficavam trocando o
# comentário uma da outra a cada aplicação (a VM do CI pegou). Por isso esta
# receita aceita a regra com qualquer comentário e só adiciona a sua quando não
# há nenhuma.
regra_base() { printf 'allow from %s to any port 22 proto tcp' "$1"; }
regra_ufw() { printf '%s comment bora-ssh\n' "$(regra_base "$1")"; }

# O firewall já libera o SSH para a rede $1, com qualquer comentário?
ssh_liberado() {
    local regras base
    regras=$(LC_ALL=C ufw show added 2>/dev/null)
    regras=${regras//\'/}
    base="ufw $(regra_base "$1")"
    grep -qxF "$base" <<<"$regras" || grep -qF "$base comment " <<<"$regras"
}

regra_existe() {
    local regras
    regras=$(LC_ALL=C ufw show added 2>/dev/null)
    grep -qxF "ufw $1" <<<"${regras//\'/}"
}

# O sshd aceita a configuração e aplica os valores da receita?
# O sshd confere se a pasta /run/sshd existe, que o systemd cria ao ligar o serviço.
pasta_do_sshd() { mkdir -p /run/sshd && chmod 755 /run/sshd; }
config_valida() { pasta_do_sshd && sshd -t 2>/dev/null; }

valor_efetivo() {
    pasta_do_sshd
    # -C simula uma conexão comum, para o Match não mudar o resultado.
    sshd -T -C user=bora-teste,host=localhost,addr=127.0.0.1 2>/dev/null | awk -v op="$1" '$1 == op {print $2; exit}'
}

# A unidade que deixa o SSH ligado: o ssh.socket (Ubuntu 24.04 em diante) ou o ssh.service.
unidade_ssh() {
    if systemctl is-enabled --quiet ssh.socket 2>/dev/null; then echo ssh.socket; else echo ssh.service; fi
}

chave_da_pessoa() {
    local casa
    casa=$(pasta_pessoal "$1")
    [ -s "$casa/.ssh/authorized_keys" ] && grep -qE '^(ssh-|ecdsa-|sk-)' "$casa/.ssh/authorized_keys"
}
