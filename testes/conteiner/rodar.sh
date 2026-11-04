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
trap 'losetup -d "$DISCO" 2>/dev/null || true' EXIT

pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }

etapa "Plano"
bora plano --receitas base/atualizar,sistema/snapshot,seguranca/firewall \
    -p "sistema/snapshot.dispositivo=$DISCO" \
    -p "seguranca/firewall.perfil=${PERFIL:-servidor-lan}" \
    -p "seguranca/firewall.rede_local=${REDE_LOCAL:-auto}" \
    -o /tmp/plano.yaml
cat /tmp/plano.yaml

# A atualização entra primeiro, sozinha, para a comparação de pacotes
# no fim não contar o que foi só atualizado.
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
# (um desktop de verdade já os tem); a comparação ignora os que sobraram assim.
pacotes | while read -r p; do
    if ! grep -qxF "$p" /tmp/pacotes-antes; then
        case "$(dpkg-query -W -f='${Essential} ${Protected} ${Priority}' "$p")" in
            yes\ * | *\ yes\ * | *\ required | *\ important) echo "(mantido por ser do sistema: $p)" >&2; continue ;;
        esac
    fi
    echo "$p"
done >/tmp/pacotes-depois
if ! diff -u /tmp/pacotes-antes /tmp/pacotes-depois; then
    echo "FALHOU: os pacotes não voltaram ao que eram"
    exit 1
fi
[ ! -e /etc/systemd/system/bora-snapshot.timer ] || { echo "FALHOU: o timer ficou"; exit 1; }
[ ! -e /etc/timeshift/timeshift.json ] || { echo "FALHOU: a configuração do Timeshift ficou"; exit 1; }
if command -v ufw >/dev/null && ufw status | grep -q '^Status: active'; then
    echo "FALHOU: o firewall continuou ligado"
    exit 1
fi
echo
echo "Tudo certo: aplicou, não mudou nada na segunda vez e desfez."
