#!/usr/bin/env bash
# Cenários do firewall que o teste principal não cobre: um ufw que já estava
# ligado com regras próprias, e a proteção de quem está conectado por SSH.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}

etapa "Cenário 1: o ufw já existia, ligado e com uma regra própria"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ufw >/dev/null
ufw default deny incoming >/dev/null
ufw allow 8080/tcp comment minha-regra >/dev/null
ufw --force enable >/dev/null
ufw status verbose >/tmp/ufw-antes

bora plano --receitas seguranca/firewall -p seguranca/firewall.perfil=servidor-lan -o /tmp/fw.yaml
bora aplicar /tmp/fw.yaml --sem-perguntar --sem-snapshot
ufw status | grep -q 'bora-ssh-rede-local' || falhou "a regra do SSH da rede local não entrou"
ufw status | grep -q 'minha-regra' || falhou "a regra que já existia sumiu ao aplicar"

bora desfazer --sem-perguntar
command -v ufw >/dev/null || falhou "o desfazer removeu um ufw que já existia"
ufw status verbose >/tmp/ufw-depois
diff -u /tmp/ufw-antes /tmp/ufw-depois || falhou "o ufw não voltou a ser como era"
echo "ok: o ufw voltou exatamente como estava, ligado e com a regra própria"

etapa "Cenário 2: sessão SSH vinda de fora da rede local"
DEBIAN_FRONTEND=noninteractive apt-get purge -y -qq ufw >/dev/null
# Algo escutando na porta 22 e uma conexão chegando de um IP de fora.
ip addr add 203.0.113.5/32 dev lo
python3 - <<'PY' &
import socket, time
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 22)); s.listen(1)
c, _ = s.accept()
time.sleep(600)
PY
servidor=$!
sleep 1
python3 - <<'PY' &
import socket, time
c = socket.socket(); c.bind(("203.0.113.5", 0))
c.connect((socket.gethostbyname(socket.gethostname()), 22))
time.sleep(600)
PY
cliente=$!
sleep 1
ss -Htn state established '( sport = :22 )'

bora plano --receitas seguranca/firewall -o /tmp/fw2.yaml
if bora aplicar /tmp/fw2.yaml --sem-perguntar --sem-snapshot >/tmp/saida-ssh 2>&1; then
    cat /tmp/saida-ssh
    falhou "o bora ligou o firewall com uma sessão SSH vinda de fora"
fi
cat /tmp/saida-ssh
grep -q 'sessão SSH vinda de 203.0.113.5' /tmp/saida-ssh || falhou "a mensagem não explica o motivo"
if command -v ufw >/dev/null && ufw status | grep -q '^Status: active'; then
    falhou "o firewall ficou ligado"
fi
echo "ok: o bora parou antes de ligar o firewall"
bora desfazer --sem-perguntar
kill "$cliente" "$servidor" 2>/dev/null || true
ip addr del 203.0.113.5/32 dev lo
wait 2>/dev/null || true

etapa "Cenário 3: sessão SSH da rede local"
python3 - <<'PY' &
import socket, time
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 22)); s.listen(1)
c, _ = s.accept()
time.sleep(600)
PY
servidor=$!
sleep 1
python3 -c 'import socket, time; c = socket.create_connection((socket.gethostbyname(socket.gethostname()), 22)); time.sleep(600)' &
cliente=$!
sleep 1
bora aplicar /tmp/fw2.yaml --sem-perguntar --sem-snapshot
ufw status | grep -q '22/tcp.*bora-ssh-rede-local' || falhou "o SSH da rede local não foi liberado"
echo "ok: com SSH ligado, o perfil desktop libera a porta 22 só para a rede local"
bora desfazer --sem-perguntar
kill "$cliente" "$servidor" 2>/dev/null || true

echo
echo "Todos os cenários passaram."
