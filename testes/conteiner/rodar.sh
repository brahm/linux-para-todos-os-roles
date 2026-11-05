#!/usr/bin/env bash
# Roda dentro do contêiner de teste: aplica as receitas, aplica de novo
# (a segunda vez não pode mudar nada), testa e desfaz, conferindo que os
# pacotes voltaram ao que eram.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }

etapa "Diagnóstico"
bora diag

# Disco virtual para os snapshots: o contêiner não tem partição própria.
truncate -s 12G /tmp/disco-snapshots.img
mkfs.ext4 -q /tmp/disco-snapshots.img
DISCO=$(losetup -f --show /tmp/disco-snapshots.img)
# Sem udev no contêiner, o lsblk (que o Timeshift usa) não vê o UUID do
# disco. Aqui o teste escreve à mão o que o udev escreveria.
mkdir -p /dev/mapper /run/udev/data
UUID_DISCO=$(blkid -o value -s UUID "$DISCO")
printf 'E:ID_FS_UUID=%s\nE:ID_FS_UUID_ENC=%s\nE:ID_FS_TYPE=ext4\nE:ID_FS_USAGE=filesystem\n' "$UUID_DISCO" "$UUID_DISCO" \
    >"/run/udev/data/b$(lsblk -n -d -o MAJ:MIN "$DISCO" | tr -d ' ')"
# Um segundo disco, no papel do disco externo do backup, e uma pessoa com
# arquivos na pasta pessoal.
truncate -s 3G /tmp/disco-backup.img
mkfs.ext4 -q /tmp/disco-backup.img
DISCO_BACKUP=$(losetup -f --show /tmp/disco-backup.img)
trap 'losetup -d "$DISCO" "$DISCO_BACKUP" 2>/dev/null || true' EXIT
id aluno >/dev/null 2>&1 || useradd -m -s /bin/bash aluno
mkdir -p /home/aluno/Documentos
echo "trabalho de história" >/home/aluno/Documentos/trabalho.txt
chown -R aluno:aluno /home/aluno

pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }

etapa "Plano"
bora plano --receitas base/atualizar,sistema/snapshot,seguranca/firewall,desktop/codecs,desktop/flatpak,sistema/backup-pessoal \
    -p "sistema/snapshot.dispositivo=$DISCO" \
    -p "sistema/backup-pessoal.destino=$DISCO_BACKUP" \
    -p "seguranca/firewall.perfil=${PERFIL:-servidor-lan}" \
    -p "seguranca/firewall.rede_local=${REDE_LOCAL:-auto}" \
    -o /tmp/plano.yaml
cat /tmp/plano.yaml

# A atualização entra primeiro, sozinha, para a comparação de pacotes
# no fim não contar o que foi só atualizado.
etapa "O rolê Pronto para estudar e trabalhar monta um plano válido"
bora plano pronto-para-estudar \
    -p "sistema/snapshot.dispositivo=$DISCO" \
    -p "sistema/backup-pessoal.destino=$DISCO_BACKUP" \
    -o /tmp/plano-role.yaml
bora validar /tmp/plano-role.yaml

etapa "Atualizar antes"
bora plano --receitas base/atualizar -p base/atualizar.automaticas=nao -o /tmp/so-atualizar.yaml
bora aplicar /tmp/so-atualizar.yaml --sem-perguntar --sem-snapshot
pacotes >/tmp/pacotes-antes

etapa "Aplicar"
bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot

etapa "Aplicar de novo (nada pode mudar)"
saida=$(bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"
grep -q "Tudo já estava aplicado" <<<"$saida" || { echo "FALHOU: a segunda aplicação mudou alguma coisa"; exit 1; }

etapa "Histórico"
bora historico

etapa "Desfazer"
bora desfazer --sem-perguntar

etapa "Conferir que voltou"
# Pacotes essenciais ou de prioridade required/important nunca são removidos
# (um desktop de verdade já os tem), nem as dependências deles; a comparação
# ignora os que sobraram assim.
do_sistema() {
    case "$(dpkg-query -W -f='${Essential} ${Protected} ${Priority}' "$1" 2>/dev/null)" in
        yes\ * | *\ yes\ * | *\ required | *\ important) return 0 ;;
    esac
    return 1
}
sistema_depende() {
    local r
    while read -r r; do
        if [ "$r" != "$1" ] && do_sistema "$r"; then return 0; fi
    done < <(LC_ALL=C apt-get -s purge "$1" 2>/dev/null | awk '/^Purg |^Remv / {print $2}')
    return 1
}
pacotes | while read -r p; do
    if ! grep -qxF "$p" /tmp/pacotes-antes; then
        if do_sistema "$p"; then echo "(mantido por ser do sistema: $p)" >&2; continue; fi
        if sistema_depende "$p"; then echo "(mantido porque um pacote do sistema depende dele: $p)" >&2; continue; fi
    fi
    echo "$p"
done >/tmp/pacotes-depois
if ! diff -u /tmp/pacotes-antes /tmp/pacotes-depois; then
    echo "FALHOU: os pacotes não voltaram ao que eram"
    exit 1
fi
[ ! -e /etc/systemd/system/bora-snapshot.timer ] || { echo "FALHOU: o timer ficou"; exit 1; }
[ ! -e /etc/timeshift/timeshift.json ] || { echo "FALHOU: a configuração do Timeshift ficou"; exit 1; }
[ ! -e /etc/systemd/system/bora-backup-pessoal.timer ] || { echo "FALHOU: o timer do backup ficou"; exit 1; }
[ ! -e /usr/local/lib/bora/backup-pessoal ] || { echo "FALHOU: o programa do backup ficou"; exit 1; }
if command -v flatpak >/dev/null; then echo "FALHOU: o Flatpak continuou instalado"; exit 1; fi
mount "$DISCO_BACKUP" /mnt
ls /mnt/bora-backup/*/aluno/ultimo/Documentos/trabalho.txt >/dev/null 2>&1 || { echo "FALHOU: o desfazer apagou as cópias do disco externo"; exit 1; }
umount /mnt
if command -v ufw >/dev/null && ufw status | grep -q '^Status: active'; then
    echo "FALHOU: o firewall continuou ligado"
    exit 1
fi
echo
echo "Tudo certo: aplicou, não mudou nada na segunda vez e desfez."
