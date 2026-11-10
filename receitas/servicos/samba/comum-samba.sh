# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

# A configuração da receita fica num arquivo só dela, que o smb.conf da
# distro inclui na última linha. Assim, um Samba que já existia continua com
# as próprias pastas, e o desfazer só tira a linha e o arquivo.
CONFIG=/etc/samba/bora-pasta-compartilhada.conf
SMB_CONF=/etc/samba/smb.conf
INCLUDE="include = $CONFIG"
# As senhas ficam fora do /etc, para não irem parar no histórico do etckeeper.
SENHAS=/var/lib/bora/pasta-compartilhada/senhas
# Marca nas contas que a receita cria, só para entrar na pasta.
MARCA="Pasta compartilhada da casa (bora)"

pacotes_da_receita() {
    printf '%s\n' samba smbclient
    if [ "${BORA_APARECER_NA_REDE:-sim}" = sim ]; then printf '%s\n' wsdd2; fi
}

# O nome da pasta na rede, conferido.
nome_do_compartilhamento() {
    local n=${BORA_NOME:-Compartilhado}
    [[ "$n" =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$ ]] ||
        falha "o nome do compartilhamento ($n) pode ter só letras sem acento, números, - e _, até 40"
    case "${n,,}" in
        global | homes | printers | print | ipc) falha "o nome $n é reservado pelo Samba; escolha outro" ;;
    esac
    printf '%s\n' "$n"
}

# Os nomes de quem vai entrar, um por linha, em minúsculas e sem repetir.
pessoas_da_pasta() {
    local n vistos=" "
    for n in ${BORA_USUARIOS//,/ }; do
        n=${n,,}
        [ -n "$n" ] || continue
        [[ "$n" =~ ^[a-z][a-z0-9_-]{0,31}$ ]] ||
            falha "o nome $n não serve para uma conta; use letras minúsculas sem acento, números, - e _, começando com letra"
        [ "$n" != root ] || falha "o root não entra na pasta compartilhada"
        [[ "$vistos" == *" $n "* ]] && continue
        vistos+="$n "
        printf '%s\n' "$n"
    done
}

exigir_pessoas() {
    local lista
    lista=$(pessoas_da_pasta) || exit 1
    [ -n "$lista" ] || falha "informe pelo menos um nome em usuarios, como ana,beto"
}

# A pasta, com o caminho resolvido, recusando as do sistema e as pastas pessoais inteiras.
pasta_da_receita() {
    local p
    p=$(realpath -m "${BORA_PASTA:-/srv/compartilhado}")
    case "$p" in
        / | /home | /srv | /mnt | /media | /tmp | /var | /var/tmp | /opt) falha "compartilhar $p inteira não é seguro; use uma pasta dentro dela, como /srv/compartilhado" ;;
        /bin | /bin/* | /boot | /boot/* | /dev | /dev/* | /etc | /etc/* | /lib | /lib/* | /lib64 | /lib64/* | /proc | /proc/* | \
            /root | /root/* | /run | /run/* | /sbin | /sbin/* | /sys | /sys/* | /usr | /usr/* | /var/lib | /var/lib/* | /var/log | /var/log/*)
            falha "$p é uma pasta do sistema e não pode ser compartilhada; use uma pasta como /srv/compartilhado" ;;
    esac
    if getent passwd | awk -F: -v p="$p" '$6 == p {achou = 1} END {exit !achou}'; then
        falha "$p é a pasta pessoal inteira de uma conta; compartilhe uma pasta dentro dela, como $p/Compartilhado"
    fi
    [ ! -e "$p" ] || [ -d "$p" ] || falha "$p existe e não é uma pasta"
    printf '%s\n' "$p"
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

exigir_rede() {
    local rede
    rede=$(descobrir_rede_local)
    [ -n "$rede" ] || falha "não encontrei a rede local; informe rede_local no plano, por exemplo 192.168.0.0/24"
    printf '%s\n' "$rede"
}

# O arquivo da receita, para a pasta $1, com os arquivos de $2 e só a rede $3.
conteudo_config() {
    local pasta=$1 dono=$2 rede=$3 nome validos
    nome=$(nome_do_compartilhamento)
    validos=$(pessoas_da_pasta | paste -sd' ' -)
    cat <<CONF
# Escrito pelo bora (receita servicos/samba). Para mudar, rode o bora de novo
# ou edite este arquivo e rode: sudo testparm -s && sudo systemctl restart smbd
#
# Este [global] vale para o Samba inteiro e vem depois do da distro, então
# ganha dele: nada de visitante sem senha, nada do protocolo SMB1, nada do
# NetBIOS, e a senha da pasta nunca troca a senha da conta no computador.
[global]
   map to guest = Never
   usershare allow guests = No
   restrict anonymous = 2
   server min protocol = SMB2_10
   disable netbios = Yes
   smb ports = 445
   unix password sync = No
   pam password change = No

[$nome]
   comment = Pasta compartilhada da casa
   path = $pasta
   valid users = $validos
   force user = $dono
   read only = No
   browseable = Yes
   create mask = 0664
   directory mask = 0775
   hosts allow = 127.0.0.1 ::1 $rede
   hosts deny = ALL
CONF
}

include_presente() { [ -f "$SMB_CONF" ] && grep -qxF "$INCLUDE" "$SMB_CONF"; }

# O dono que a pasta tem (ou vai ter): numa pasta que já existe, quem já é dono.
dono_atual() { stat -c %U "$1" 2>/dev/null; }

# Contas.
conta_existe() { getent passwd "$1" >/dev/null; }
conta_da_receita() { [ "$(getent passwd "$1" | cut -d: -f5)" = "$MARCA" ]; }
conta_de_pessoa() {
    local linha uid shell
    linha=$(getent passwd "$1") || return 1
    uid=$(cut -d: -f3 <<<"$linha")
    shell=$(cut -d: -f7 <<<"$linha")
    [ "$uid" -ge 1000 ] && [ "$uid" -lt 60000 ] && [[ "$shell" != *nologin ]] && [[ "$shell" != */false ]]
}
no_samba() { grep -qxF "$1" <<<"$(pdbedit -L 2>/dev/null | cut -d: -f1)"; }

# Firewall.
ufw_ativo() { command -v ufw >/dev/null && grep -q '^Status: active' <<<"$(LC_ALL=C ufw status 2>/dev/null)"; }

# As regras que a receita pede, no formato dos argumentos do ufw: o Samba
# (445/tcp) e, para aparecer na rede, o WS-Discovery (3702/udp e 5357/tcp) e
# o LLMNR (5355/udp), que deixa o Windows achar o computador pelo nome.
regras_ufw() {
    local rede=$1
    printf 'allow from %s to any port 445 proto tcp comment bora-samba\n' "$rede"
    if [ "${BORA_APARECER_NA_REDE:-sim}" = sim ]; then
        printf 'allow from %s to any port 3702 proto udp comment bora-samba-descoberta\n' "$rede"
        printf 'allow from %s to any port 5357 proto tcp comment bora-samba-descoberta\n' "$rede"
        printf 'allow from %s to any port 5355 proto udp comment bora-samba-descoberta\n' "$rede"
    fi
}

regra_existe() {
    local regras
    regras=$(LC_ALL=C ufw show added 2>/dev/null)
    grep -qxF "ufw $1" <<<"${regras//\'/}"
}

# Uma senha fácil de ditar: três blocos de quatro letras e números, sem os
# que se confundem (0 e o, 1 e l).
gerar_senha() {
    python3 -c '
import secrets
a = "abcdefghjkmnpqrstuvwxyz23456789"
print("-".join("".join(secrets.choice(a) for _ in range(4)) for _ in range(3)))'
}

senha_de() { awk -v n="$1" '$1 == n {print $2; exit}' "$SENHAS" 2>/dev/null; }

endereco_ip() { ip -4 -o addr show scope global 2>/dev/null | awk '{sub(/\/.*/, "", $4); print $4; exit}'; }
