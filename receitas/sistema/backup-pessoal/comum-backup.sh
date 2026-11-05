# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

CONFIG=/etc/bora/backup-pessoal.conf
PROGRAMA=/usr/local/lib/bora/backup-pessoal
UNIDADE=bora-backup-pessoal
# Sistemas de arquivos em que as versões compartilham os arquivos que não
# mudaram (hardlinks) e guardam dono e permissões.
FS_LINUX="ext4 ext3 xfs btrfs f2fs"

# A partição com este UUID, se ela estiver conectada agora. A resposta do
# blkid só vale depois de ler o UUID direto do disco (-p), porque um disco
# recém-desconectado ainda pode aparecer pelo cache ou por /dev/disk.
achar_disco() {
    local d
    d=$(blkid -c /dev/null -U "$1" 2>/dev/null || true)
    [ -n "$d" ] && [ "$(blkid -c /dev/null -p -o value -s UUID "$d" 2>/dev/null || true)" = "$1" ] && echo "$d"
}

valor_da_config() {
    [ -f "$CONFIG" ] || return 0
    sed -n "s/^$1=//p" "$CONFIG" | tr -d '"' | head -n1
}

fs_linux() { [[ " $FS_LINUX " == *" $1 "* ]]; }

# Partições de discos USB ou removíveis, uma por linha: "caminho tipo".
particoes_externas() {
    lsblk -J -p -o PATH,TYPE,FSTYPE,TRAN,HOTPLUG,RM,MOUNTPOINT 2>/dev/null | python3 -c '
import json, sys
try:
    dados = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
def andar(dev, externo):
    externo = externo or dev.get("tran") == "usb" or dev.get("hotplug") in (True, "1") or dev.get("rm") in (True, "1")
    if externo and dev.get("fstype") and dev.get("type") in ("part", "disk") and dev.get("mountpoint") not in ("/", "/home", "/boot", "/boot/efi"):
        print(dev["path"], dev["fstype"])
    for filho in dev.get("children") or []:
        andar(filho, externo)
for d in dados.get("blockdevices", []):
    andar(d, False)
'
}

# Descobre o disco de destino e imprime "dispositivo uuid tipo".
# Com destino "auto", vale o disco que já está na configuração; se não houver,
# o único disco externo conectado com um sistema de arquivos do Linux.
descobrir_destino() {
    local alvo=${BORA_DESTINO:-auto} dev uuid tipo
    if [ "$alvo" = auto ] && [ -n "$(valor_da_config UUID)" ]; then
        uuid=$(valor_da_config UUID)
        dev=$(achar_disco "$uuid" || true)
        tipo=
        if [ -n "$dev" ]; then tipo=$(blkid -c /dev/null -o value -s TYPE "$dev" || true); fi
        printf '%s %s %s\n' "${dev:--}" "$uuid" "${tipo:--}"
        return 0
    fi
    if [ "$alvo" = auto ]; then
        local linux=() outros=() caminho fs
        while read -r caminho fs; do
            [ -n "$caminho" ] || continue
            if fs_linux "$fs"; then linux+=("$caminho"); else outros+=("$caminho ($fs)"); fi
        done < <(particoes_externas)
        if [ "${#linux[@]}" -eq 1 ]; then
            dev=${linux[0]}
        elif [ "${#linux[@]}" -gt 1 ]; then
            falha "há mais de um disco externo conectado (${linux[*]}); informe qual usar no parâmetro destino"
        elif [ "${#outros[@]}" -gt 0 ]; then
            falha "o disco externo conectado (${outros[*]}) não usa um sistema de arquivos do Linux. O bora não formata discos: para usar este disco, copie o que houver nele para outro lugar, formate em ext4 (pelo aplicativo Discos) e rode de novo"
        else
            falha "não encontrei nenhum disco externo conectado; conecte o disco e rode de novo, ou informe a partição no parâmetro destino"
        fi
    elif [[ "$alvo" == UUID=* ]]; then
        dev=$(achar_disco "${alvo#UUID=}" || true)
        [ -n "$dev" ] || falha "não encontrei a partição com $alvo; confira se o disco está conectado"
    else
        dev=$alvo
    fi
    [ -b "$dev" ] || falha "$dev não é uma partição de disco"
    uuid=$(blkid -c /dev/null -o value -s UUID "$dev" || true)
    tipo=$(blkid -c /dev/null -o value -s TYPE "$dev" || true)
    [ -n "$uuid" ] || falha "a partição $dev não tem sistema de arquivos (ou não tem UUID)"
    fs_linux "$tipo" || falha "$dev usa $tipo; o backup precisa de um sistema de arquivos do Linux, como ext4, para guardar as versões sem ocupar espaço repetido. O bora não formata discos"
    local d
    for d in / /home /boot; do
        if [ "$(findmnt -n -o SOURCE --target "$d" 2>/dev/null | sed 's/\[.*\]$//')" = "$dev" ]; then
            falha "$dev é a partição do próprio sistema ($d); o backup precisa ir para outro disco, para sobreviver se este morrer"
        fi
    done
    printf '%s %s %s\n' "$dev" "$uuid" "$tipo"
}

# Pessoas com conta neste computador e pasta pessoal em /home.
usuarios_do_sistema() {
    getent passwd | awk -F: '$3 >= 1000 && $3 < 60000 && $6 ~ "^/home/" && $7 !~ /(nologin|false)$/ {print $1}' |
        while read -r u; do
            [ -d "$(getent passwd "$u" | cut -d: -f6)" ] && echo "$u"
        done
}

# Imprime a lista de usuários, separada por espaços, ou falha.
descobrir_usuarios() {
    local lista=() u
    if [ "${BORA_USUARIOS:-auto}" = auto ]; then
        mapfile -t lista < <(usuarios_do_sistema)
    else
        IFS=', ' read -r -a lista <<<"$BORA_USUARIOS"
        for u in "${lista[@]}"; do
            getent passwd "$u" >/dev/null || falha "não existe a conta $u neste computador"
        done
    fi
    [ "${#lista[@]}" -gt 0 ] || falha "não encontrei nenhuma pessoa com pasta pessoal em /home"
    printf '%s\n' "${lista[*]}"
}

# O conteúdo que o arquivo de configuração precisa ter.
config_esperada() {
    local uuid=$1 usuarios=$2 computador
    computador=$(valor_da_config COMPUTADOR)
    [ -n "$computador" ] || computador=$(hostname -s 2>/dev/null || cat /proc/sys/kernel/hostname)
    cat <<CONF
# Backup da pasta pessoal, configurado pelo bora (receita sistema/backup-pessoal).
# O disco é achado pelo UUID; as cópias ficam em <disco>/bora-backup/COMPUTADOR/<pessoa>/.
UUID=$uuid
COMPUTADOR=$computador
USUARIOS="$usuarios"
MANTER=${BORA_MANTER:-7}
CONF
}

# Nome da unidade .device do systemd para um UUID (para rodar ao conectar).
unidade_do_disco() { systemd-escape --path --suffix=device "/dev/disk/by-uuid/$1"; }
