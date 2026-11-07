#!/usr/bin/env bash
# Roda dentro do contêiner de teste: as receitas sistema/etckeeper,
# desktop/sem-snap e seguranca/ssh. Cada uma é aplicada, aplicada de novo
# (a segunda vez não pode mudar nada) e desfeita, conferindo que os pacotes
# e os arquivos voltaram ao que eram. O sem-snap usa um snapd instalado sem
# o serviço rodando e um snap do Firefox de mentira, para conferir a troca
# pelo Firefox da Mozilla, a cópia do perfil e a recusa de um snap que a
# receita não conhece. Precisa de rede, para o repositório da Mozilla; sem
# ela, rode com SEM_MOZILLA=1, e o teste confere que nada muda quando a
# chave da Mozilla não chega.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}
pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }
do_sistema() {
    case "$(dpkg-query -W -f='${Essential} ${Protected} ${Priority}' "$1" 2>/dev/null)" in
        yes\ * | *\ yes\ * | *\ required | *\ important) return 0 ;;
    esac
    return 1
}
mesmos_pacotes() {
    pacotes | while read -r p; do
        if ! grep -qxF "$p" "$1" && do_sistema "$p"; then continue; fi
        echo "$p"
    done >/tmp/pacotes-depois
    diff -u "$1" /tmp/pacotes-depois || falhou "os pacotes não voltaram ao que eram ($2)"
}
# O valor que vale de verdade para uma conexão do aluno vinda da rede local.
efetivo() { sshd -T -C user=aluno,host=x,addr=192.168.50.2 | awk -v op="$1" '$1 == op {print $2}'; }
aplicar_duas_vezes() {
    bora aplicar "$1" --sem-perguntar --sem-snapshot
    local saida
    saida=$(bora aplicar "$1" --sem-perguntar --sem-snapshot)
    printf '%s\n' "$saida"
    grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "a segunda aplicação mudou alguma coisa ($1)"
}

id aluno >/dev/null 2>&1 || useradd -m -s /bin/bash aluno

etapa "Os rolês montam planos válidos, com e sem as receitas opcionais"
bora plano pronto-para-estudar -p "sistema/snapshot.dispositivo=/dev/null" -p "sistema/backup-pessoal.destino=/dev/null" -o /tmp/r1.yaml
grep -q 'sistema/etckeeper' /tmp/r1.yaml || falhou "o rolê 1 não tem o etckeeper"
! grep -q 'desktop/sem-snap' /tmp/r1.yaml || falhou "o sem-snap entrou sem a pessoa pedir"
bora plano pronto-para-estudar -r sem_snap=sim -p "sistema/snapshot.dispositivo=/dev/null" -p "sistema/backup-pessoal.destino=/dev/null" -o /tmp/r1s.yaml
grep -q 'desktop/sem-snap' /tmp/r1s.yaml || falhou "o sem-snap não entrou com sem_snap=sim"
bora plano maquina-antiga -o /tmp/r2.yaml
! grep -q 'seguranca/ssh' /tmp/r2.yaml || falhou "o SSH entrou sem a pessoa pedir"
bora plano maquina-antiga -r acesso_ssh=sim -o /tmp/r2s.yaml
bora validar /tmp/r2s.yaml
grep -q 'seguranca/ssh' /tmp/r2s.yaml || falhou "o SSH não entrou com acesso_ssh=sim"

etapa "Atualizar antes"
bora plano --receitas base/atualizar -p base/atualizar.automaticas=nao -o /tmp/so-atualizar.yaml
bora aplicar /tmp/so-atualizar.yaml --sem-perguntar --sem-snapshot

# --- etckeeper -------------------------------------------------------------
etapa "etckeeper"
pacotes >/tmp/antes-etc
bora plano --receitas sistema/etckeeper -o /tmp/etc.yaml
aplicar_duas_vezes /tmp/etc.yaml
git -C /etc log --oneline | head -5
echo "teste do bora" >/etc/bora-teste.conf
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends tree >/dev/null
[ -n "$(git -C /etc log --oneline)" ] || falhou "o histórico do /etc está vazio"
grep -q bora-teste.conf <<<"$(git -C /etc log --stat -3)" || falhou "o apt não registrou a mudança no /etc"
DEBIAN_FRONTEND=noninteractive apt-get purge -y -qq tree >/dev/null
rm -f /etc/bora-teste.conf
bora desfazer --sem-perguntar
[ ! -e /etc/.git ] || falhou "o histórico do /etc ficou"
ls /var/backups/bora-etc-historico-*.tar.gz >/dev/null || falhou "o desfazer não guardou a cópia do histórico"
mesmos_pacotes /tmp/antes-etc etckeeper
echo "ok: etckeeper aplicou, registrou o apt e desfez"

# --- SSH -------------------------------------------------------------------
etapa "SSH com o firewall ligado"
pacotes >/tmp/antes-ssh
bora plano --receitas seguranca/firewall -p seguranca/firewall.rede_local=192.168.50.0/24 -o /tmp/fw.yaml
bora aplicar /tmp/fw.yaml --sem-perguntar --sem-snapshot
bora plano --receitas seguranca/ssh -p seguranca/ssh.rede_local=192.168.50.0/24 -o /tmp/ssh.yaml
aplicar_duas_vezes /tmp/ssh.yaml
[ "$(efetivo permitrootlogin)" = no ] || falhou "o root continua entrando"
[ "$(efetivo passwordauthentication)" = yes ] || falhou "a senha deveria valer com so_chave=nao"
ufw show added | grep 'bora-ssh' >/dev/null || falhou "o firewall não liberou o SSH para a rede local"

etapa "SSH só com chave, sem chave cadastrada, é recusado"
bora plano --receitas seguranca/ssh -p seguranca/ssh.rede_local=192.168.50.0/24 -p seguranca/ssh.so_chave=sim -p seguranca/ssh.usuario=aluno -o /tmp/ssh-chave.yaml
if bora aplicar /tmp/ssh-chave.yaml --sem-perguntar --sem-snapshot >/tmp/saida-chave 2>&1; then
    cat /tmp/saida-chave
    falhou "a receita desligou a senha de uma conta sem chave"
fi
grep -q 'authorized_keys' /tmp/saida-chave || { cat /tmp/saida-chave; falhou "a recusa não explicou o motivo"; }
bora desfazer --sem-perguntar >/dev/null 2>&1 || true

etapa "SSH só com chave, com chave cadastrada"
mkdir -p /home/aluno/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBoraTesteBoraTesteBoraTesteBoraTesteBora aluno@teste" >/home/aluno/.ssh/authorized_keys
chown -R aluno:aluno /home/aluno/.ssh
aplicar_duas_vezes /tmp/ssh-chave.yaml
[ "$(efetivo passwordauthentication)" = no ] || falhou "a senha continua valendo com so_chave=sim"

etapa "Desfazer o SSH e o firewall"
# O SSH só com chave e o primeiro SSH, depois o firewall.
bora desfazer --sem-perguntar
bora desfazer --sem-perguntar
bora desfazer --sem-perguntar
[ ! -e /etc/ssh/sshd_config.d/10-bora.conf ] || falhou "a configuração do SSH ficou"
mesmos_pacotes /tmp/antes-ssh ssh
echo "ok: SSH aplicou, recusou só chave sem chave e desfez"

# --- Sem Snap --------------------------------------------------------------
etapa "Sem Snap numa máquina sem Snap só bloqueia o apt"
pacotes >/tmp/antes-snap
bora plano --receitas desktop/sem-snap -o /tmp/snap.yaml
aplicar_duas_vezes /tmp/snap.yaml
grep -q 'Candidate: (none)' <<<"$(apt-cache policy snapd)" || falhou "o apt ainda instalaria o snapd"
bora desfazer --sem-perguntar
[ ! -e /etc/apt/preferences.d/bora-sem-snap.pref ] || falhou "o bloqueio do snapd ficou"

etapa "Sem Snap recusa um snap que não sabe trocar"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends snapd >/dev/null
pacotes >/tmp/antes-snap
mkdir -p /var/lib/snapd/snaps
touch /var/lib/snapd/snaps/core24_100.snap /var/lib/snapd/snaps/firefox_200.snap /var/lib/snapd/snaps/spotify_80.snap
if bora aplicar /tmp/snap.yaml --sem-perguntar --sem-snapshot >/tmp/saida-snap 2>&1; then
    cat /tmp/saida-snap
    falhou "a receita tirou um snap que não sabia trocar"
fi
grep -q spotify /tmp/saida-snap || { cat /tmp/saida-snap; falhou "a recusa não disse qual snap"; }
grep -qx snapd <<<"$(pacotes)" || falhou "a recusa removeu o snapd"
bora desfazer --sem-perguntar >/dev/null 2>&1 || true

etapa "Sem Snap troca o Firefox do Snap pelo da Mozilla, com o perfil"
rm -f /var/lib/snapd/snaps/spotify_80.snap
mkdir -p /home/aluno/snap/firefox/common/.mozilla/firefox/abc.default
echo 'user_pref("bora.teste", true);' >/home/aluno/snap/firefox/common/.mozilla/firefox/abc.default/prefs.js
chown -R aluno:aluno /home/aluno/snap
if [ "${SEM_MOZILLA:-0}" = 1 ]; then
    if bora aplicar /tmp/snap.yaml --sem-perguntar --sem-snapshot >/tmp/saida-snap 2>&1; then
        falhou "a receita seguiu sem o repositório da Mozilla"
    fi
    grep -q 'nada foi mudado' /tmp/saida-snap || { cat /tmp/saida-snap; falhou "a recusa não explicou o motivo"; }
    grep -qx snapd <<<"$(pacotes)" || falhou "o snapd saiu sem o Firefox da Mozilla garantido"
    [ -d /home/aluno/snap/firefox ] || falhou "o perfil do Snap sumiu"
    bora desfazer --sem-perguntar >/dev/null 2>&1 || true
    mesmos_pacotes /tmp/antes-snap sem-snap
    echo "ok: sem a chave da Mozilla, nada mudou (o resto do teste precisa de rede)"
    exit 0
fi
aplicar_duas_vezes /tmp/snap.yaml
grep -qx snapd <<<"$(pacotes)" && falhou "o snapd continuou instalado"
grep -q 'bora.teste' /home/aluno/.mozilla/firefox/abc.default/prefs.js || falhou "o perfil do Firefox não foi copiado"
[ "$(stat -c %U /home/aluno/.mozilla/firefox/abc.default/prefs.js)" = aluno ] || falhou "o perfil copiado não é do aluno"
grep -A1 '^ \*\*\*' <<<"$(apt-cache policy firefox)" | grep -q packages.mozilla.org || falhou "o Firefox não é o da Mozilla"
firefox --version || true

etapa "Desfazer o Sem Snap"
bora desfazer --sem-perguntar
grep -qx snapd <<<"$(pacotes)" || falhou "o snapd não voltou"
for f in /etc/apt/preferences.d/bora-sem-snap.pref /etc/apt/preferences.d/mozilla.pref /etc/apt/sources.list.d/mozilla.sources /etc/apt/keyrings/packages.mozilla.org.asc; do
    [ ! -e "$f" ] || falhou "o arquivo $f ficou"
done
grep -q packages.mozilla.org <<<"$(apt-cache policy firefox)" && falhou "o repositório da Mozilla ficou"
mesmos_pacotes /tmp/antes-snap sem-snap
echo "ok: Sem Snap bloqueou, recusou, trocou o Firefox e desfez"

echo
echo "Tudo certo: as três receitas aplicaram, não mudaram nada na segunda vez e desfizeram."
