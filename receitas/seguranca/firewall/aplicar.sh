#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita seguranca/firewall (Firewall).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=regras.sh
source ./regras.sh

rede=$(descobrir_rede_local)
if [ -n "$rede" ]; then
    msg "Rede local: $rede"
else
    aviso "não encontrei uma rede local privada; nada será liberado para a rede"
    if [ "$BORA_PERFIL" = servidor-lan ]; then
        falha "o perfil servidor-lan precisa da rede local; informe rede_local no plano, por exemplo 192.168.0.0/24"
    fi
fi

# Não derrubar quem está conectado por SSH agora.
while read -r cliente; do
    [ -n "$cliente" ] || continue
    if ! python3 - "$cliente" "${rede:-}" "$BORA_PERFIL" <<'PY'; then
import ipaddress, sys
cliente, rede, perfil = sys.argv[1:]
ip = ipaddress.ip_address(cliente)
ok = ip.is_loopback
if rede:
    ok = ok or ip in ipaddress.ip_network(rede)
if perfil == "tailscale":
    ok = ok or ip in ipaddress.ip_network("100.64.0.0/10") or ip in ipaddress.ip_network("fd7a:115c:a1e0::/48")
sys.exit(0 if ok else 1)
PY
        falha "há uma sessão SSH vinda de $cliente, fora da rede local; ligar o firewall cortaria o acesso. Conecte-se pela rede local ou use o perfil tailscale."
    fi
done < <(clientes_ssh)

instalar_pacotes ufw

# Guarda a configuração inteira do ufw, para o desfazer voltar exatamente como estava.
if [ ! -f "$BORA_ESTADO/ufw-antes.tar" ]; then
    tar -C / -cf "$BORA_ESTADO/ufw-antes.tar" etc/ufw etc/default/ufw 2>/dev/null || true
    if ufw_ativo; then echo sim >"$BORA_ESTADO/ufw-estava-ativo"; else echo nao >"$BORA_ESTADO/ufw-estava-ativo"; fi
fi

ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
while read -r regra; do
    [ -n "$regra" ] || continue
    if regra_existe "$regra"; then
        msg "Regra já existia: $regra"
    else
        # shellcheck disable=SC2086
        ufw $regra >/dev/null
        msg "Regra adicionada: $regra"
    fi
done < <(regras_do_perfil "$rede")

if ! ufw_ativo; then
    ufw --force enable >/dev/null
    msg "Firewall ligado."
else
    ufw reload >/dev/null
fi
if command -v systemctl >/dev/null && { [ -f /usr/lib/systemd/system/ufw.service ] || [ -f /lib/systemd/system/ufw.service ]; }; then
    habilitar_unidade ufw.service
fi
LC_ALL=C ufw status verbose
