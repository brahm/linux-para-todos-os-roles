#!/usr/bin/env bash
# Roda dentro do contêiner de teste: o rolê "Pasta compartilhada da casa".
# Aplica o firewall de servidor da casa e o Samba, entra na pasta pelo
# smbclient com a senha de cada pessoa, aplica de novo (a segunda vez não pode
# mudar nada), acrescenta uma pessoa, desfaz as duas aplicações e confere que
# os pacotes, as contas e a configuração voltaram ao que eram, sem apagar os
# arquivos da pasta. Depois, repete com um Samba que já existia, com uma
# pasta própria, e uma pasta do root ainda vazia.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}
SENHAS=/var/lib/bora/pasta-compartilhada/senhas
pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }
senha_de() { awk -v n="$1" '$1 == n {print $2}' "$SENHAS"; }
# Sem systemd no contêiner, o smbd não liga sozinho: o teste liga à mão.
ligar_smbd() {
    pkill -x smbd 2>/dev/null || true
    sleep 1
    mkdir -p /run/samba
    smbd -D
    for _ in $(seq 1 20); do
        [ -n "$(ss -Hltn 'sport = :445')" ] && return 0
        sleep 0.5
    done
    falhou "o smbd não abriu a porta 445"
}
desligar_smbd() {
    pkill -x smbd 2>/dev/null || true
    sleep 1
}
entra() { smbclient "//127.0.0.1/$1" -U "$2%$3" -c "${4:-ls}" >/dev/null 2>&1; }
recusa() {
    local saida
    if saida=$(bora plano --receitas servicos/samba "$@" -o /tmp/recusa.yaml 2>&1) &&
        saida=$(bora aplicar /tmp/recusa.yaml --sem-perguntar --sem-snapshot 2>&1); then
        printf '%s\n' "$saida"
        falhou "o bora aceitou: $*"
    fi
    printf '%s\n' "$saida" | grep -E 'Erro|✗' || true
}

etapa "Preparar: uma pessoa com conta e senha no computador"
id aluno >/dev/null 2>&1 || useradd -m -s /bin/bash aluno
echo 'aluno:senha-do-computador' | chpasswd
export SUDO_USER=aluno
sombra_antes=$(getent shadow aluno | cut -d: -f2)

etapa "Diagnóstico"
bora diag

etapa "O rolê monta um plano válido"
bora plano pasta-compartilhada -r usuarios=aluno,beto -o /tmp/plano-role.yaml
bora validar /tmp/plano-role.yaml
cat /tmp/plano-role.yaml
grep -q 'perfil: servidor-lan' /tmp/plano-role.yaml || falhou "o rolê não pediu o firewall de servidor da casa"

etapa "Atualizar antes"
bora plano --receitas base/atualizar -p base/atualizar.automaticas=nao -o /tmp/so-atualizar.yaml
bora aplicar /tmp/so-atualizar.yaml --sem-perguntar --sem-snapshot
pacotes >/tmp/pacotes-antes

etapa "Recusar o que não pode"
recusa -p servicos/samba.usuarios=beto -p servicos/samba.pasta=/etc
recusa -p servicos/samba.usuarios=beto -p servicos/samba.pasta=/home/aluno
recusa -p servicos/samba.usuarios=beto -p servicos/samba.pasta=/srv
recusa -p servicos/samba.usuarios=root
recusa -p servicos/samba.usuarios=daemon
recusa -p servicos/samba.usuarios=beto -p 'servicos/samba.nome=Pasta da Casa'
pacotes | diff -u /tmp/pacotes-antes - || falhou "uma recusa instalou alguma coisa"
[ ! -e /srv/compartilhado ] || falhou "uma recusa criou a pasta"

etapa "Plano: firewall de servidor da casa e Samba para aluno e beto"
bora plano --receitas seguranca/firewall,servicos/samba \
    -p seguranca/firewall.perfil=servidor-lan \
    -p servicos/samba.usuarios=aluno,beto \
    -o /tmp/plano.yaml
cat /tmp/plano.yaml

etapa "Aplicar"
bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot

etapa "Conferir o que mudou"
[ "$(stat -c '%U %a' /srv/compartilhado)" = "aluno 755" ] || falhou "a pasta não é do aluno"
[ "$(stat -c '%U %a' "$SENHAS")" = "root 600" ] || falhou "o arquivo de senhas não é só do root"
[ -n "$(senha_de aluno)" ] || falhou "falta a senha do aluno"
[ -n "$(senha_de beto)" ] || falhou "falta a senha do beto"
[ "$(getent passwd beto | cut -d: -f7)" = /usr/sbin/nologin ] || falhou "a conta do beto entra no computador"
[ ! -e /home/beto ] || falhou "a conta do beto ganhou pasta pessoal"
[ "$(getent shadow aluno | cut -d: -f2)" = "$sombra_antes" ] || falhou "a senha do aluno no computador mudou"
grep -q 'bora-samba' <<<"$(ufw status)" || falhou "o firewall não libera o Samba"
ufw status
testparm -s 2>/dev/null | sed -n '/^\[Compartilhado\]/,$p'
grep -rq "$(senha_de beto)" /etc && falhou "uma senha foi parar no /etc"

etapa "Entrar na pasta pelo Samba"
ligar_smbd
echo "foto da festa" >/tmp/foto.txt
entra Compartilhado beto "$(senha_de beto)" 'put /tmp/foto.txt foto.txt' || falhou "o beto não criou um arquivo na pasta"
[ "$(stat -c %U /srv/compartilhado/foto.txt)" = aluno ] || falhou "o arquivo do beto não ficou com o dono da pasta"
entra Compartilhado aluno "$(senha_de aluno)" 'get foto.txt /tmp/foto-de-volta.txt' || falhou "o aluno não abriu a pasta com a senha da pasta"
cmp -s /tmp/foto.txt /tmp/foto-de-volta.txt || falhou "o arquivo não voltou igual"
if entra Compartilhado aluno senha-do-computador; then falhou "a senha do computador abriu a pasta"; fi
if entra Compartilhado beto errada; then falhou "uma senha errada abriu a pasta"; fi
if smbclient -N //127.0.0.1/Compartilhado -c ls >/dev/null 2>&1; then falhou "um visitante sem senha abriu a pasta"; fi
if smbclient -m NT1 --option='client min protocol = NT1' //127.0.0.1/Compartilhado -U "beto%$(senha_de beto)" -c ls >/dev/null 2>&1; then falhou "o SMB1 continua ligado"; fi
echo "ok: beto e aluno entram com a senha da pasta; a senha do computador, a errada, o visitante e o SMB1, não"

etapa "Aplicar de novo (nada pode mudar)"
senha_beto=$(senha_de beto)
saida=$(bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"
grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "a segunda aplicação mudou alguma coisa"

etapa "Acrescentar uma pessoa"
bora plano --receitas servicos/samba -p servicos/samba.usuarios=aluno,beto,carla -o /tmp/plano-carla.yaml
bora aplicar /tmp/plano-carla.yaml --sem-perguntar --sem-snapshot
[ "$(senha_de beto)" = "$senha_beto" ] || falhou "a senha do beto mudou"
ligar_smbd
entra Compartilhado carla "$(senha_de carla)" || falhou "a carla não entrou"
entra Compartilhado beto "$senha_beto" || falhou "o beto deixou de entrar"

etapa "Desfazer as duas aplicações"
desligar_smbd
bora desfazer --sem-perguntar
getent passwd carla >/dev/null && falhou "a conta da carla ficou"
getent passwd beto >/dev/null || falhou "desfazer a carla levou o beto"
grep -q '^carla ' "$SENHAS" && falhou "a senha da carla ficou"
grep -q 'valid users = aluno beto$' /etc/samba/bora-pasta-compartilhada.conf || falhou "a configuração não voltou à da primeira aplicação"
bora desfazer --sem-perguntar

etapa "Conferir que voltou"
hash -r
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
getent passwd beto >/dev/null && falhou "a conta do beto ficou"
getent passwd aluno >/dev/null || falhou "o desfazer apagou a conta do aluno"
[ "$(getent shadow aluno | cut -d: -f2)" = "$sombra_antes" ] || falhou "a senha do aluno no computador mudou"
[ -f /srv/compartilhado/foto.txt ] || falhou "o desfazer apagou os arquivos da pasta"
[ ! -e /var/lib/bora/pasta-compartilhada ] || falhou "as senhas ficaram"
[ ! -e /etc/samba/bora-pasta-compartilhada.conf ] || falhou "a configuração do bora ficou"
if command -v ufw >/dev/null && grep -q '^Status: active' <<<"$(ufw status)"; then falhou "o firewall continuou ligado"; fi
rm -rf /srv/compartilhado

etapa "Um Samba que já existia, com uma pasta própria, e uma pasta do root vazia"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends samba >/dev/null
printf '\n[fotos]\n   path = /srv/fotos\n   read only = yes\n' >>/etc/samba/smb.conf
mkdir -p /srv/fotos /mnt/hd
cp /etc/samba/smb.conf /tmp/smb-antes.conf
pacotes >/tmp/pacotes-antes
bora plano --receitas servicos/samba -p servicos/samba.usuarios=beto -p servicos/samba.pasta=/mnt/hd \
    -p servicos/samba.nome=HD -p servicos/samba.aparecer_na_rede=nao -p servicos/samba.rede_local=192.168.50.0/24 -o /tmp/plano-hd.yaml
bora aplicar /tmp/plano-hd.yaml --sem-perguntar --sem-snapshot
[ "$(stat -c %U /mnt/hd)" = aluno ] || falhou "a pasta vazia do root não passou para o aluno"
testparm -s 2>/dev/null | grep -qx '\[fotos\]' || falhou "a pasta que já existia no Samba sumiu"
[ "$(testparm -s --section-name=HD --parameter-name='hosts allow' 2>/dev/null)" = "127.0.0.1 ::1 192.168.50.0/24" ] || falhou "o Samba aceita outra rede"
pacote() { [ "$(dpkg-query -W -f='${db:Status-Abbrev}' "$1" 2>/dev/null)" = "ii " ]; }
if pacote wsdd2; then falhou "instalou o wsdd2 sem pedir para aparecer na rede"; fi
ligar_smbd
entra HD beto "$(senha_de beto)" || falhou "o beto não entrou na pasta HD"
desligar_smbd
bora desfazer --sem-perguntar
diff -u /tmp/smb-antes.conf /etc/samba/smb.conf || falhou "o smb.conf não voltou ao que era"
pacotes | diff -u /tmp/pacotes-antes - || falhou "os pacotes não voltaram ao que eram"
[ "$(stat -c '%U %a' /mnt/hd)" = "root 755" ] || falhou "a pasta não voltou a ser do root"
mkdir -p /mnt/cheia && echo x >/mnt/cheia/arquivo
recusa -p servicos/samba.usuarios=beto -p servicos/samba.pasta=/mnt/cheia

echo
echo "Tudo certo: compartilhou, só entra quem tem a senha da pasta, não mudou nada na segunda vez e desfez sem apagar os arquivos."
