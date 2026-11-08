# shellcheck shell=bash
# As regras que cada perfil pede, usadas por verificar, aplicar e testar.

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
# Só as faixas de rede local (RFC 1918). CGNAT (100.64/10), endereços de
# teste e IPs públicos ficam de fora.
locais = [ipaddress.ip_network(r) for r in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
if any(rede.subnet_of(r) for r in locais):
    print(rede)
PY
}

# Portas em que um servidor SSH escuta agora (o sshd ou o ssh.socket do systemd).
portas_ssh() {
    {
        ss -Hltnp 2>/dev/null | awk '/"sshd"|"sshd-session"/ {n = split($4, a, ":"); print a[n]}'
        if grep -q . <<<"$(ss -Hltn 'sport = :22' 2>/dev/null)"; then echo 22; fi
    } | sort -un
}

# Endereços de quem está conectado por SSH neste momento.
clientes_ssh() {
    local p
    for p in $(portas_ssh); do
        ss -Htn state established "( sport = :$p )" 2>/dev/null | awk '{print $4}'
    done | sed -E 's/^\[?(::ffff:)?//; s/\]?:[0-9]+$//' | sort -u
}

# Monta a lista de regras (uma por linha, no formato dos argumentos do ufw).
regras_do_perfil() {
    local rede=$1 p
    local portas
    portas=$(portas_ssh)
    if [ "$BORA_PERFIL" = servidor-lan ] && [ -z "$portas" ]; then
        portas=22
    fi
    if [ -n "$rede" ]; then
        for p in $portas; do
            printf 'allow from %s to any port %s proto tcp comment bora-ssh-rede-local\n' "$rede" "$p"
        done
    fi
    if [ "$BORA_PERFIL" = tailscale ]; then
        printf 'allow in on tailscale0 comment bora-tailscale\n'
    fi
}

ufw_ativo() { grep -q '^Status: active' <<<"$(LC_ALL=C ufw status 2>/dev/null)"; }

padroes_certos() {
    grep -q '^Default: deny (incoming), allow (outgoing)' <<<"$(LC_ALL=C ufw status verbose 2>/dev/null)"
}

# A regra já está no ufw? Compara com "ufw show added", que repete os comandos.
regra_existe() {
    local regra=$1
    grep -qxF "ufw $regra" <<<"$(LC_ALL=C ufw show added 2>/dev/null | sed "s/'//g")"
}
