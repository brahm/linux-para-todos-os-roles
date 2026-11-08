#!/usr/bin/env bash
# Sobe uma máquina virtual de verdade com o QEMU (com KVM, quando houver) e
# roda nela a parte dos rolês que não depende de tela: o que o contêiner não
# consegue provar, como o boot com o zram e o firewall, o Timeshift tirando
# um snapshot da própria raiz, os temporizadores do systemd e o backup
# disparado quando o disco externo é conectado.
#
#   testes/vm/qemu/rodar.sh ubuntu-24.04 binario/bora
#   testes/vm/qemu/rodar.sh debian-13 binario/bora
#
# Precisa de qemu-system-x86, qemu-utils, cloud-image-utils, openssh-client e
# socat. Os arquivos da máquina ficam em $PASTA (padrão: /tmp/bora-vm).
set -euo pipefail

DISTRO=${1:?uso: rodar.sh ubuntu-24.04|debian-13 caminho/do/bora}
BORA_BIN=$(realpath "${2:?uso: rodar.sh ubuntu-24.04|debian-13 caminho/do/bora}")
RAIZ=$(cd "$(dirname "$0")/../../.." && pwd)
PASTA=${PASTA:-/tmp/bora-vm}
PORTA=${PORTA:-2222}
mkdir -p "$PASTA"
cd "$PASTA"

case "$DISTRO" in
    ubuntu-24.04)
        IMAGEM_URL=https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
        USUARIO=ubuntu ;;
    debian-13)
        # A "generic", e não a "genericcloud": o kernel de nuvem não traz o
        # zram nem boa parte dos módulos de disco.
        IMAGEM_URL=https://cloud.debian.org/images/cloud/trixie/latest/debian-13-generic-amd64.qcow2
        USUARIO=debian ;;
    *) echo "distro desconhecida: $DISTRO" >&2; exit 2 ;;
esac

etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() { echo "FALHOU: $*" >&2; exit 1; }

etapa "Preparar a máquina ($DISTRO)"
[ -f base.img ] || curl -fsSL --retry 3 -o base.img "$IMAGEM_URL"
rm -f disco.qcow2 externo.img seed.img chave chave.pub monitor.sock serial.log
# 30 GB: o rolê pede 20 GB livres para os snapshots. O arquivo só cresce com o uso.
qemu-img create -q -f qcow2 -F qcow2 -b base.img disco.qcow2 30G
# O disco externo do backup: 2 GB em ext4, sem partição, como um pen drive formatado.
truncate -s 2G externo.img
mkfs.ext4 -q -L BACKUP externo.img
ssh-keygen -q -t ed25519 -N '' -f chave
cat >user-data <<CLOUD
#cloud-config
ssh_authorized_keys:
  - $(cat chave.pub)
package_update: false
package_upgrade: false
CLOUD
printf 'instance-id: bora-%s\nlocal-hostname: bora-%s\n' "$DISTRO" "${DISTRO%%-*}" >meta-data
cloud-localds seed.img user-data meta-data

ACEL=(-machine "q35,accel=kvm" -cpu host)
if [ ! -w /dev/kvm ]; then
    echo "AVISO: sem /dev/kvm, a máquina roda emulada e bem mais devagar." >&2
    ACEL=(-machine "q35,accel=tcg")
fi

etapa "Ligar a máquina"
# O bootindex é obrigatório: sem ele, a BIOS tenta só o primeiro disco que
# acha, que pode ser o externo, e para em "No bootable device".
qemu-system-x86_64 "${ACEL[@]}" -m 4096 -smp 2 \
    -drive file=disco.qcow2,if=none,id=raiz,format=qcow2 \
    -device virtio-blk-pci,drive=raiz,bootindex=0 \
    -drive file=seed.img,if=virtio,format=raw,readonly=on \
    -device virtio-scsi-pci,id=scsi \
    -blockdev driver=file,filename="$PASTA/externo.img",node-name=externo-arq \
    -blockdev driver=raw,file=externo-arq,node-name=externo \
    -device scsi-hd,bus=scsi.0,drive=externo,id=disco-externo,removable=on \
    -netdev user,id=rede,hostfwd=tcp:127.0.0.1:"$PORTA"-:22 \
    -device virtio-net-pci,netdev=rede \
    -monitor unix:"$PASTA/monitor.sock",server,nowait \
    -serial file:"$PASTA/serial.log" -display none \
    -daemonize -pidfile "$PASTA/qemu.pid"
trap 'kill "$(cat "$PASTA/qemu.pid" 2>/dev/null)" 2>/dev/null || true' EXIT

SSH_OPCOES=(-i chave -p "$PORTA" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=5 -o ServerAliveInterval=15)
# Os comandos vão como texto e rodam do lado da máquina.
# shellcheck disable=SC2029
vm() { ssh "${SSH_OPCOES[@]}" "$USUARIO@127.0.0.1" "$@"; }
monitor() { printf '%s\n' "$*" | socat - "UNIX-CONNECT:$PASTA/monitor.sock" >/dev/null; }
esperar_ssh() {
    local antes=${1:-} boot
    for _ in $(seq 1 90); do
        if boot=$(vm cat /proc/sys/kernel/random/boot_id 2>/dev/null) && [ "$boot" != "$antes" ]; then
            vm cloud-init status --wait >/dev/null 2>&1 || true
            return 0
        fi
        sleep 5
    done
    tail -n 50 serial.log >&2 || true
    falhou "a máquina não respondeu pelo SSH"
}
# Roda uma fase do na-vm.sh. Se ela falha, mostra os avisos do boot atual,
# que costumam dizer o porquê (uma unidade do systemd que não subiu, por exemplo).
fase() {
    vm "sudo /bora/testes/vm/qemu/na-vm.sh $1" && return 0
    echo "--- avisos do journal na máquina ---" >&2
    vm "sudo journalctl -b -p warning --no-pager | tail -n 60" >&2 || true
    falhou "a fase $1 falhou"
}
esperar_ssh
vm "uname -r; cat /etc/os-release | head -n 2"

etapa "Copiar o bora e o catálogo"
tar -C "$RAIZ" --exclude=./target --exclude=./.git --exclude=./docs --exclude=./binario -czf repo.tar.gz .
scp -q -P "$PORTA" -i chave -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    repo.tar.gz "$BORA_BIN" "$USUARIO@127.0.0.1:/tmp/"
vm "sudo mkdir -p /bora && sudo tar -C /bora -xzf /tmp/repo.tar.gz && sudo install -m 0755 /tmp/bora /usr/local/bin/bora"

etapa "Aplicar, na máquina"
fase aplicar

etapa "Reiniciar"
boot=$(vm cat /proc/sys/kernel/random/boot_id)
vm "sudo systemctl reboot" || true
sleep 5
esperar_ssh "$boot"
fase depois-do-reinicio

etapa "Desconectar e conectar de novo o disco externo"
fase antes-de-conectar
monitor "device_del disco-externo"
sleep 5
monitor "device_add scsi-hd,bus=scsi.0,drive=externo,id=disco-externo,removable=on"
fase depois-de-conectar

etapa "Desfazer"
fase desfazer

etapa "Tudo certo em $DISTRO"
