# shellcheck shell=bash
# O que o rodar.sh e o tela.sh dividem: baixar a imagem de nuvem da distro,
# criar o disco, ligar a máquina no QEMU e falar com ela pelo SSH e pelo
# monitor do QEMU. Quem carrega este arquivo define antes DISTRO, PASTA e
# PORTA, e já está dentro de $PASTA.

case "$DISTRO" in
    ubuntu-24.04)
        IMAGEM_URL=https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
        USUARIO=ubuntu ;;
    ubuntu-26.04)
        IMAGEM_URL=https://cloud-images.ubuntu.com/resolute/current/resolute-server-cloudimg-amd64.img
        USUARIO=ubuntu ;;
    debian-13)
        # A "generic", e não a "genericcloud": o kernel de nuvem não traz o
        # zram, boa parte dos módulos de disco nem os de vídeo.
        IMAGEM_URL=https://cloud.debian.org/images/cloud/trixie/latest/debian-13-generic-amd64.qcow2
        USUARIO=debian ;;
    *) echo "distro desconhecida: $DISTRO" >&2; exit 2 ;;
esac

etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() { echo "FALHOU: $*" >&2; exit 1; }

# Baixa a imagem (uma vez só), cria o disco de 30 GB por cima dela e o
# cloud-init com a chave do SSH. O arquivo do disco só cresce com o uso.
preparar_maquina() {
    [ -f "base-$DISTRO.img" ] || curl -fsSL --retry 3 -o "base-$DISTRO.img" "$IMAGEM_URL"
    rm -f disco.qcow2 seed.img chave chave.pub monitor.sock serial.log cobertas.txt
    qemu-img create -q -f qcow2 -F qcow2 -b "base-$DISTRO.img" disco.qcow2 30G
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
}

# Liga a máquina, com 4 GB de memória e 2 processadores. Os argumentos vão
# direto para o QEMU (um disco a mais, por exemplo). A placa de vídeo é a
# padrão do QEMU; sem janela, a tela só se vê pelo screendump do monitor.
ligar_maquina() {
    local acel=(-machine "q35,accel=kvm" -cpu host)
    if [ ! -w /dev/kvm ]; then
        echo "AVISO: sem /dev/kvm, a máquina roda emulada e bem mais devagar." >&2
        acel=(-machine "q35,accel=tcg")
    fi
    # O bootindex é obrigatório: sem ele, a BIOS tenta só o primeiro disco que
    # acha, que pode ser outro, e para em "No bootable device".
    qemu-system-x86_64 "${acel[@]}" -m 4096 -smp 2 \
        -drive file=disco.qcow2,if=none,id=raiz,format=qcow2 \
        -device virtio-blk-pci,drive=raiz,bootindex=0 \
        -drive file=seed.img,if=virtio,format=raw,readonly=on \
        "$@" \
        -netdev user,id=rede,hostfwd=tcp:127.0.0.1:"$PORTA"-:22 \
        -device virtio-net-pci,netdev=rede \
        -monitor unix:"$PASTA/monitor.sock",server,nowait \
        -serial file:"$PASTA/serial.log" -display none \
        -daemonize -pidfile "$PASTA/qemu.pid"
    trap 'kill "$(cat "$PASTA/qemu.pid" 2>/dev/null)" 2>/dev/null || true' EXIT
}

SSH_OPCOES=(-i chave -p "$PORTA" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=5 -o ServerAliveInterval=15)
# Os comandos vão como texto e rodam do lado da máquina.
# shellcheck disable=SC2029
vm() { ssh "${SSH_OPCOES[@]}" "$USUARIO@127.0.0.1" "$@"; }
# Um comando no monitor do QEMU. O -t dá tempo de o QEMU terminar antes de a
# conexão fechar (o screendump grava o arquivo depois de responder).
monitor() { printf '%s\n' "$*" | socat -t 5 - "UNIX-CONNECT:$PASTA/monitor.sock" >/dev/null; }

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

reiniciar() {
    local boot
    boot=$(vm cat /proc/sys/kernel/random/boot_id)
    vm "sudo systemctl reboot" || true
    sleep 5
    esperar_ssh "$boot"
}

# Copia o bora e o catálogo para /bora, na máquina.
copiar_bora() {
    tar -C "$RAIZ" --exclude=./target --exclude=./.git --exclude=./docs --exclude=./binario -czf repo.tar.gz .
    scp -q -P "$PORTA" -i chave -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
        repo.tar.gz "$BORA_BIN" "$USUARIO@127.0.0.1:/tmp/"
    vm "sudo mkdir -p /bora && sudo tar -C /bora -xzf /tmp/repo.tar.gz && sudo install -m 0755 /tmp/bora /usr/local/bin/bora"
}

# Roda uma fase de um script de testes/vm/qemu na máquina, como root. Se ela
# falha, mostra os avisos do boot atual, que costumam dizer o porquê (uma
# unidade do systemd que não subiu, por exemplo).
fase() {
    vm "sudo /bora/testes/vm/qemu/$1 $2" && return 0
    echo "--- avisos do journal na máquina ---" >&2
    vm "sudo journalctl -b -p warning --no-pager | tail -n 60" >&2 || true
    falhou "a fase $2 ($1) falhou"
}
