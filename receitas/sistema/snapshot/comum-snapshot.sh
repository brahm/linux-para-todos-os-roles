# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita sistema/snapshot.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

CONFIG=/etc/timeshift/timeshift.json
UNIDADE=bora-snapshot
ESPACO_MINIMO_GB=10

# Descobre o dispositivo dos snapshots e imprime "dispositivo uuid tipo modo".
# modo é rsync ou btrfs.
descobrir_destino() {
    local alvo=${BORA_DISPOSITIVO:-auto} fonte uuid tipo modo=rsync subvol
    if [ "$alvo" = auto ]; then
        fonte=$(findmnt -n -o SOURCE / | sed 's/\[.*\]$//')
        tipo=$(findmnt -n -o FSTYPE /)
        if [ "$tipo" = btrfs ]; then
            subvol=$(findmnt -n -o OPTIONS / | tr ',' '\n' | sed -n 's/^subvol=//p')
            if [ "$subvol" = "/@" ] || [ "$subvol" = "@" ]; then
                modo=btrfs
            else
                falha "a raiz é btrfs sem o subvolume @; o Timeshift não funciona nesse arranjo (o snapper vem numa próxima versão)"
            fi
        fi
    else
        fonte=$alvo
        [ -b "$fonte" ] || falha "$fonte não é um dispositivo de bloco"
        tipo=$(blkid -o value -s TYPE "$fonte" || true)
        [ "$tipo" = btrfs ] && falha "para guardar snapshots em outro disco, use um sistema de arquivos como ext4, não btrfs"
    fi
    [ -b "$fonte" ] || falha "não encontrei a partição do sistema ($fonte)"
    uuid=$(blkid -o value -s UUID "$fonte" || true)
    [ -n "$uuid" ] || falha "a partição $fonte não tem UUID"
    case "$tipo" in
        ext2 | ext3 | ext4 | xfs | btrfs | f2fs | jfs | reiserfs) ;;
        *) falha "o Timeshift precisa de uma partição Linux (ext4, xfs ou btrfs), e $fonte é $tipo" ;;
    esac
    printf '%s %s %s %s\n' "$fonte" "$uuid" "$tipo" "$modo"
}

# Lista os nomes dos snapshots que o Timeshift conhece.
# O Timeshift sai com erro quando ainda não há nenhum snapshot; aqui isso
# é só uma lista vazia.
listar_snapshots() {
    { LC_ALL=C timeshift --list --scripted 2>/dev/null || true; } | awk '$1 ~ /^[0-9]+$/ && $2 == ">" {print $3}'
}

# O timeshift.json já tem o disco, o modo e quantos snapshots guardar, como a receita pede?
config_certa() {
    local uuid=$1 modo=$2
    [ -f "$CONFIG" ] || return 1
    python3 - "$CONFIG" "$uuid" "$modo" "${BORA_DIARIOS:-5}" "${BORA_SEMANAIS:-3}" <<'PY'
import json, sys
caminho, uuid, modo, diarios, semanais = sys.argv[1:]
c = json.load(open(caminho))
ok = (
    c.get("backup_device_uuid") == uuid
    and c.get("btrfs_mode") == ("true" if modo == "btrfs" else "false")
    and c.get("schedule_daily") == "true" and c.get("count_daily") == diarios
    and c.get("schedule_weekly") == "true" and c.get("count_weekly") == semanais
    and c.get("do_first_run") == "false"
)
sys.exit(0 if ok else 1)
PY
}
