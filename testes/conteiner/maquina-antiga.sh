#!/usr/bin/env bash
# Roda dentro do contêiner de teste: aplica as receitas do rolê "Dar vida
# nova a uma máquina antiga", aplica de novo (a segunda vez não pode mudar
# nada), testa e desfaz, conferindo que os pacotes, os arquivos e os serviços
# voltaram ao que eram. AMBIENTE escolhe o ambiente leve: xfce ou lxqt.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
AMBIENTE="${AMBIENTE:-xfce}"
# Atalhos: `bora` roda o binário em teste, `etapa` imprime um título para
# achar o passo no log do CI, e `falhou` para tudo com a mensagem.
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}

etapa "Preparar uma máquina parecida com um desktop"
# Os serviços que a receita servicos-enxutos desliga, como num desktop, e
# uma pessoa no computador, para a sessão padrão do ambiente leve.
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends bluez modemmanager network-manager >/dev/null
for u in bluetooth.service ModemManager.service NetworkManager-wait-online.service; do
    systemctl enable "$u" 2>&1 | sed '/^Created symlink/d'
done
id aluno >/dev/null 2>&1 || useradd -m -s /bin/bash aluno
mkdir -p /var/lib/AccountsService/users
printf '[User]\nLanguage=pt_BR.UTF-8\nSession=ubuntu\n' >/var/lib/AccountsService/users/aluno
cp /var/lib/AccountsService/users/aluno /tmp/conta-antes
# Uma política do Firefox que já existia, para conferir que a receita junta.
mkdir -p /etc/firefox/policies
echo '{"policies": {"DisableAppUpdate": true}}' >/etc/firefox/policies/policies.json
cp /etc/firefox/policies/policies.json /tmp/politicas-antes

# O estado (enabled, disabled...) dos serviços que a receita servicos-enxutos mexe.
servicos() {
    for u in bluetooth.service ModemManager.service NetworkManager-wait-online.service; do
        printf '%s %s\n' "$u" "$(systemctl is-enabled "$u" 2>/dev/null || true)"
    done
}
# Os pacotes instalados, um por linha. O teste compara o antes e o depois.
pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }

etapa "Diagnóstico"
bora diag

etapa "O rolê monta um plano válido"
bora plano maquina-antiga -o /tmp/plano-role.yaml
bora validar /tmp/plano-role.yaml
cat /tmp/plano-role.yaml

etapa "Atualizar antes"
bora plano --receitas base/atualizar -p base/atualizar.automaticas=nao -o /tmp/so-atualizar.yaml
bora aplicar /tmp/so-atualizar.yaml --sem-perguntar --sem-snapshot
pacotes >/tmp/pacotes-antes
servicos >/tmp/servicos-antes

etapa "Plano"
bora plano --receitas sistema/zram,desktop/ambiente-leve,desktop/navegador-leve,sistema/servicos-enxutos \
    -p "desktop/ambiente-leve.ambiente=$AMBIENTE" \
    -p desktop/ambiente-leve.entrar_no_leve=sim \
    -o /tmp/plano.yaml
cat /tmp/plano.yaml

# O contêiner vê o /proc/swaps da máquina do CI. Alguns runners do GitHub
# (os de kernel -aws) já vêm com zram ligado, e aí a receita, de propósito,
# não mexe nele. Anota isso antes, para cobrar o comportamento certo depois.
zram_do_runner=nao
if grep -q '^/dev/zram' /proc/swaps 2>/dev/null; then zram_do_runner=sim; fi

etapa "Aplicar"
saida=$(bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"

etapa "Conferir o que mudou"
if [ "$zram_do_runner" = sim ]; then
    # A máquina do CI já tem zram: a receita só confere e não escreve nada.
    grep -q "Memória comprimida (zram): já estava aplicada" <<<"$saida" || falhou "a receita mexeu no zram que a máquina do CI já tinha"
    [ ! -e /etc/systemd/zram-generator.conf ] || falhou "a receita escreveu a configuração por cima do zram da máquina do CI"
    echo "ok: a máquina do CI já tem zram, e a receita não mexeu nele"
else
    grep -q "zram-size = min(ram \* 50 / 100, 8192)" /etc/systemd/zram-generator.conf || falhou "o zram não foi configurado"
    grep -q "vm.swappiness = 180" /etc/sysctl.d/99-bora-zram.conf || falhou "faltam os ajustes do kernel"
fi
grep -qx "Session=$AMBIENTE" /var/lib/AccountsService/users/aluno || falhou "aluno não entra no $AMBIENTE por padrão"
grep -qx "Language=pt_BR.UTF-8" /var/lib/AccountsService/users/aluno || falhou "o resto da conta do aluno sumiu"
python3 - <<'PY' || falhou "as políticas do Firefox não ficaram certas"
import json
p = json.load(open("/etc/firefox/policies/policies.json"))["policies"]
assert p["DisableAppUpdate"] is True, "a política que já existia sumiu"
assert "uBlock0@raymondhill.net" in p["ExtensionSettings"]
assert p["Preferences"]["browser.tabs.unloadOnLowMemory"]["Value"] is True
PY
servicos
for u in bluetooth.service ModemManager.service NetworkManager-wait-online.service; do
    [ "$(systemctl is-enabled "$u" 2>/dev/null || true)" != enabled ] || falhou "$u continuou ligado"
done
echo "ok: zram, ambiente, Firefox e serviços como o plano pediu"

etapa "Aplicar de novo (nada pode mudar)"
saida=$(bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"
grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "a segunda aplicação mudou alguma coisa"

etapa "Desfazer"
bora desfazer --sem-perguntar

etapa "Conferir que voltou"
# Pacote essencial ou protegido? O desfazer nunca tira esses (igual ao comum.sh),
# então o teste também não cobra que eles saiam.
do_sistema() {
    case "$(dpkg-query -W -f='${Essential} ${Protected} ${Priority}' "$1" 2>/dev/null)" in
        yes\ * | *\ yes\ * | *\ required | *\ important) return 0 ;;
    esac
    return 1
}
pacotes | while read -r p; do
    if ! grep -qxF "$p" /tmp/pacotes-antes && do_sistema "$p"; then
        echo "(mantido por ser do sistema: $p)" >&2
        continue
    fi
    echo "$p"
done >/tmp/pacotes-depois
diff -u /tmp/pacotes-antes /tmp/pacotes-depois || falhou "os pacotes não voltaram ao que eram"
servicos >/tmp/servicos-depois
diff -u /tmp/servicos-antes /tmp/servicos-depois || falhou "os serviços não voltaram ao que eram"
diff -u /tmp/conta-antes /var/lib/AccountsService/users/aluno || falhou "a conta do aluno não voltou ao que era"
diff -u /tmp/politicas-antes /etc/firefox/policies/policies.json || falhou "as políticas do Firefox não voltaram ao que eram"
[ ! -e /etc/systemd/zram-generator.conf ] || falhou "a configuração do zram ficou"
[ ! -e /etc/sysctl.d/99-bora-zram.conf ] || falhou "os ajustes do kernel ficaram"

etapa "Um zram que já existia não é mexido"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq zram-tools >/dev/null
bora plano --receitas sistema/zram -o /tmp/zram.yaml
saida=$(bora aplicar /tmp/zram.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"
grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "a receita mexeu num zram que já existia"
[ ! -e /etc/systemd/zram-generator.conf ] || falhou "a receita escreveu a configuração por cima do zram-tools"

echo
echo "Tudo certo: aplicou, não mudou nada na segunda vez e desfez."
