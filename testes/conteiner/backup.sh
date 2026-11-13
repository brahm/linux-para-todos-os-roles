#!/usr/bin/env bash
# Cenários do backup da pasta pessoal que o teste principal não cobre:
# versões que compartilham arquivos, o intervalo de 20 horas, o limite de
# versões, o disco desconectado e os discos que a receita recusa.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
# Atalhos: `bora` roda o binário em teste, `etapa` imprime um título para
# achar o passo no log do CI, e `falhou` para tudo com a mensagem.
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}
PROGRAMA=/usr/local/lib/bora/backup-pessoal

id aluno >/dev/null 2>&1 || useradd -m -s /bin/bash aluno
id professora >/dev/null 2>&1 || useradd -m -s /bin/bash professora
mkdir -p /home/aluno/Documentos /home/aluno/.cache
head -c 20M /dev/urandom >/home/aluno/Documentos/video.bin
echo "versão 1" >/home/aluno/Documentos/texto.txt
echo "lixo" >/home/aluno/.cache/temporario
echo "da professora" >/home/professora/aula.txt
chown -R aluno:aluno /home/aluno
chown -R professora:professora /home/professora

truncate -s 3G /tmp/externo.img
mkfs.ext4 -q /tmp/externo.img
DISCO=$(losetup -f --show /tmp/externo.img)
trap 'umount /mnt 2>/dev/null || true; losetup -D 2>/dev/null || true' EXIT

etapa "Cenário 1: só o aluno, guardando 2 versões"
bora plano --receitas sistema/backup-pessoal \
    -p "sistema/backup-pessoal.destino=$DISCO" \
    -p sistema/backup-pessoal.usuarios=aluno \
    -p sistema/backup-pessoal.manter=2 -o /tmp/backup.yaml
bora aplicar /tmp/backup.yaml --sem-perguntar --sem-snapshot

mount -o ro "$DISCO" /mnt
base=$(echo /mnt/bora-backup/*)
[ -f "$base/aluno/ultimo/Documentos/texto.txt" ] || falhou "a primeira cópia não tem o arquivo"
[ ! -e "$base/aluno/ultimo/.cache/temporario" ] || falhou "o .cache entrou na cópia"
[ ! -e "$base/professora" ] || falhou "copiou a pasta de quem não estava na lista"
[ "$(stat -c %U:%a "$base/aluno")" = aluno:700 ] || falhou "a pasta das cópias não é só do aluno: $(stat -c %U:%a "$base/aluno")"
[ "$(stat -c %U "$base/aluno/ultimo/Documentos/texto.txt")" = aluno ] || falhou "a cópia perdeu o dono dos arquivos"
umount /mnt
echo "ok: a primeira cópia tem os arquivos, com o dono certo, sem o cache"

etapa "Menos de 20 horas depois, não copia de novo"
saida=$("$PROGRAMA")
printf '%s\n' "$saida"
grep -q "menos de 20 horas" <<<"$saida" || falhou "copiou de novo antes do intervalo"

etapa "Uma segunda e uma terceira cópia, com um arquivo mudado"
for n in 2 3; do
    sleep 1
    echo "versão $n" >/home/aluno/Documentos/texto.txt
    "$PROGRAMA" --agora
done
mount -o ro "$DISCO" /mnt
mapfile -t versoes < <(find "$base/aluno" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
[ "${#versoes[@]}" -eq 2 ] || falhou "esperava 2 versões guardadas, há ${#versoes[@]}: ${versoes[*]}"
[ "$(cat "$base/aluno/ultimo/Documentos/texto.txt")" = "versão 3" ] || falhou "a última cópia não tem a versão nova"
[ "$(cat "$base/aluno/${versoes[0]}/Documentos/texto.txt")" = "versão 2" ] || falhou "a versão anterior não foi guardada"
inodes=$(stat -c %i "$base/aluno/${versoes[0]}/Documentos/video.bin" "$base/aluno/${versoes[1]}/Documentos/video.bin" | sort -u | wc -l)
[ "$inodes" -eq 1 ] || falhou "o arquivo que não mudou foi copiado de novo, em vez de compartilhado"
umount /mnt
echo "ok: guarda só 2 versões, e o arquivo de 20 MB que não mudou ocupa espaço uma vez só"

etapa "Disco desconectado"
losetup -d "$DISCO"
saida=$("$PROGRAMA" --agora)
printf '%s\n' "$saida"
grep -q "não está conectado" <<<"$saida" || falhou "não explicou que o disco não está conectado"
DISCO=$(losetup -f --show /tmp/externo.img)

etapa "Desfazer mantém as cópias"
bora desfazer --sem-perguntar
[ ! -e /etc/bora/backup-pessoal.conf ] || falhou "a configuração ficou"
mount -o ro "$DISCO" /mnt
[ -f "$base/aluno/ultimo/Documentos/texto.txt" ] || falhou "o desfazer apagou as cópias"
umount /mnt
echo "ok: o backup foi desligado e as cópias continuam no disco"

etapa "Cenário 2: disco em FAT é recusado sem mudar nada"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq dosfstools >/dev/null
truncate -s 2G /tmp/fat.img
mkfs.vfat -n PENDRIVE /tmp/fat.img >/dev/null
FAT=$(losetup -f --show /tmp/fat.img)
bora plano --receitas sistema/backup-pessoal -p "sistema/backup-pessoal.destino=$FAT" -o /tmp/fat.yaml
if bora aplicar /tmp/fat.yaml --sem-perguntar --sem-snapshot >/tmp/saida-fat 2>&1; then
    cat /tmp/saida-fat
    falhou "aceitou um disco em FAT"
fi
cat /tmp/saida-fat
grep -q "não guarda hardlinks" /tmp/saida-fat || falhou "a mensagem não explica o motivo"
grep -q "não formata discos" /tmp/saida-fat || falhou "a mensagem não explica o que fazer"
[ ! -e /etc/bora/backup-pessoal.conf ] || falhou "configurou mesmo recusando o disco"
echo "ok: o bora recusou o disco em FAT e explicou por quê"

echo
echo "Todos os cenários do backup passaram."
