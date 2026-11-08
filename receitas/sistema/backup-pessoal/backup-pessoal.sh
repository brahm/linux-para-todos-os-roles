#!/usr/bin/env bash
set -euo pipefail
# Backup da pasta pessoal num disco externo, instalado pelo bora em
# /usr/local/lib/bora/backup-pessoal (receita sistema/backup-pessoal).
#
# Uso:
#   backup-pessoal              copia, se a última cópia tiver mais de 20 horas
#   backup-pessoal --agora      copia agora, mesmo que a última seja recente
#   backup-pessoal --conectado  espera o disco ser montado pela sessão (ao conectar)
#   backup-pessoal --conferir   só confere se cada pessoa tem uma cópia completa
#
# Cada cópia fica em <disco>/bora-backup/<computador>/<pessoa>/<data>/ e
# parece uma cópia inteira da pasta pessoal. Os arquivos que não mudaram de
# uma cópia para a outra não ocupam espaço de novo (são hardlinks).

CONFIG=/etc/bora/backup-pessoal.conf
MONTAGEM_PROPRIA=/run/bora-backup-pessoal
INTERVALO_MIN=$((20 * 60))
ESPACO_MINIMO_MB=1024

modo=${1:-normal}
msg() { printf '%s\n' "$*"; }
falha() {
    printf 'Erro: %s\n' "$*" >&2
    exit 1
}

[ -r "$CONFIG" ] || falha "não encontrei $CONFIG"
UUID=$(sed -n 's/^UUID=//p' "$CONFIG" | tr -d '"')
COMPUTADOR=$(sed -n 's/^COMPUTADOR=//p' "$CONFIG" | tr -d '"')
USUARIOS=$(sed -n 's/^USUARIOS=//p' "$CONFIG" | tr -d '"')
MANTER=$(sed -n 's/^MANTER=//p' "$CONFIG" | tr -d '"')
if [ -z "$UUID" ] || [ -z "$COMPUTADOR" ] || [ -z "$USUARIOS" ]; then
    falha "$CONFIG está incompleto"
fi
if ! [[ "$MANTER" =~ ^[1-9][0-9]*$ ]]; then MANTER=7; fi

# Uma cópia de cada vez.
exec 9>/run/bora-backup-pessoal.lock
flock -n 9 || {
    msg "Já há um backup em andamento."
    exit 0
}

# O blkid pode responder com um disco que acabou de ser desconectado (pelo
# cache ou por um atalho em /dev/disk que ainda não sumiu). Por isso, a
# resposta só vale depois de ler o UUID direto do disco, com -p.
achar_disco() {
    local d
    d=$(blkid -c /dev/null -U "$1" 2>/dev/null || true)
    [ -n "$d" ] && [ "$(blkid -c /dev/null -p -o value -s UUID "$d" 2>/dev/null || true)" = "$1" ] && echo "$d"
}
dev=$(achar_disco "$UUID" || true)
if [ -z "$dev" ]; then
    msg "O disco do backup não está conectado. Nada a fazer agora."
    [ "$modo" = --conferir ] && exit 1
    exit 0
fi

ponto_de_montagem() { findmnt -n -f -o TARGET --source "$dev" 2>/dev/null || true; }

# Ao conectar o disco, a sessão gráfica costuma montá-lo em /media. Espera
# um pouco por isso, para não disputar o disco com o gerenciador de arquivos.
if [ "$modo" = --conectado ]; then
    for _ in $(seq 1 30); do
        [ -n "$(ponto_de_montagem)" ] && break
        sleep 2
    done
fi

ponto=$(ponto_de_montagem)
montei=nao
if [ -z "$ponto" ]; then
    mkdir -p "$MONTAGEM_PROPRIA"
    if [ "$modo" = --conferir ]; then
        mount -o ro "$dev" "$MONTAGEM_PROPRIA"
    else
        mount "$dev" "$MONTAGEM_PROPRIA"
    fi
    ponto=$MONTAGEM_PROPRIA
    montei=sim
fi
desmontar() {
    if [ "$montei" = sim ]; then
        sync
        umount "$MONTAGEM_PROPRIA" 2>/dev/null || true
        rmdir "$MONTAGEM_PROPRIA" 2>/dev/null || true
    fi
}
trap desmontar EXIT

base="$ponto/bora-backup/$COMPUTADOR"
padrao_versao='^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{6}$'
versoes() { find "$1" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | { grep -E "$padrao_versao" || true; } | sort; }

if [ "$modo" = --conferir ]; then
    erros=0
    for u in $USUARIOS; do
        if [ -d "$base/$u/ultimo/" ] && [ -n "$(versoes "$base/$u")" ]; then
            msg "ok: $u tem $(versoes "$base/$u" | wc -l) cópia(s), a última em $(readlink "$base/$u/ultimo")"
        else
            msg "FALHOU: $u ainda não tem nenhuma cópia completa"
            erros=$((erros + 1))
        fi
    done
    exit "$erros"
fi

[ -w "$ponto" ] || falha "o disco do backup está montado só para leitura em $ponto"
livre_mb=$(df --output=avail -m "$ponto" | tail -n1 | tr -d ' ')
if [ "$livre_mb" -lt "$ESPACO_MINIMO_MB" ]; then
    falha "o disco do backup tem menos de $ESPACO_MINIMO_MB MB livres; apague cópias antigas em $base ou diminua o número de versões guardadas"
fi

mkdir -p "$base"
chmod 755 "$ponto/bora-backup" "$base"

falhas=0
for u in $USUARIOS; do
    linha=$(getent passwd "$u" || true)
    [ -n "$linha" ] || {
        msg "A conta $u não existe mais; pulando."
        continue
    }
    casa=$(cut -d: -f6 <<<"$linha")
    uid=$(cut -d: -f3 <<<"$linha")
    gid=$(cut -d: -f4 <<<"$linha")
    [ -d "$casa" ] || continue
    destino="$base/$u"
    mkdir -p "$destino"
    # Cada pessoa vê só as próprias cópias.
    chown "$uid:$gid" "$destino"
    chmod 700 "$destino"

    if [ "$modo" != --agora ] && [ -n "$(find "$destino/.bora-ultimo" -mmin -"$INTERVALO_MIN" 2>/dev/null)" ]; then
        msg "$u: a última cópia tem menos de 20 horas."
        continue
    fi

    # Sobras de uma cópia interrompida (disco desconectado no meio, por exemplo).
    find "$destino" -mindepth 1 -maxdepth 1 -type d -name '*.parcial' -exec rm -rf {} +

    anterior=$(versoes "$destino" | tail -n1)
    nova=$(date +%Y-%m-%d_%H%M%S)
    opcoes=(-aHAX --numeric-ids --one-file-system --delete
        --exclude=/.cache/ --exclude=/.local/share/Trash/ --exclude='/.var/app/*/cache/'
        --exclude='/snap/*/*/.cache/' --exclude=/.thumbnails/)
    [ -n "$anterior" ] && opcoes+=(--link-dest="$destino/$anterior")
    msg "$u: copiando $casa para $destino/$nova"
    rc=0
    rsync "${opcoes[@]}" "$casa/" "$destino/$nova.parcial/" || rc=$?
    # 24: arquivos que sumiram durante a cópia, o que é normal com a sessão aberta.
    if [ "$rc" -ne 0 ] && [ "$rc" -ne 24 ]; then
        msg "$u: a cópia falhou (rsync saiu com $rc)."
        rm -rf "${destino:?}/$nova.parcial"
        falhas=$((falhas + 1))
        continue
    fi
    mv "$destino/$nova.parcial" "$destino/$nova"
    ln -sfn "$nova" "$destino/ultimo"
    touch "$destino/.bora-ultimo"

    # Guarda só as últimas $MANTER versões.
    total=$(versoes "$destino" | wc -l)
    if [ "$total" -gt "$MANTER" ]; then
        versoes "$destino" | awk -v n=$((total - MANTER)) 'NR <= n' | while read -r velha; do
            rm -rf "${destino:?}/${velha:?}"
            msg "$u: cópia antiga apagada: $velha"
        done
    fi
    msg "$u: pronto. $(versoes "$destino" | wc -l) cópia(s) guardada(s)."
done
[ "$falhas" -eq 0 ] || exit 1
