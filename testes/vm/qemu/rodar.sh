#!/usr/bin/env bash
# Sobe uma máquina virtual de verdade com o QEMU (com KVM, quando houver) e
# roda nela a parte dos rolês que não depende de tela: o que o contêiner não
# consegue provar, como o boot com o zram e o firewall, o Timeshift tirando
# um snapshot da própria raiz, os temporizadores do systemd e o backup
# disparado quando o disco externo é conectado. Além do rolê 1, aplica os
# outros rolês sem as receitas que só se conferem com tela (veja o na-vm.sh).
#
#   testes/vm/qemu/rodar.sh ubuntu-24.04 binario/bora
#   testes/vm/qemu/rodar.sh ubuntu-26.04 binario/bora
#   testes/vm/qemu/rodar.sh debian-13 binario/bora
#
# Quando tudo passa, $PASTA/cobertas.txt lista as receitas que a máquina
# aplicou, desfez e conferiu; o workflow usa a lista para gravar o registro.
#
# Precisa de qemu-system-x86, qemu-utils, cloud-image-utils, openssh-client e
# socat. A parte que liga a máquina está no maquina.sh, que o tela.sh também
# usa. Os arquivos da máquina ficam em $PASTA (padrão: /tmp/bora-vm).
set -euo pipefail

USO="uso: rodar.sh ubuntu-24.04|ubuntu-26.04|debian-13 caminho/do/bora"
DISTRO=${1:?$USO}
BORA_BIN=$(realpath "${2:?$USO}")
RAIZ=$(cd "$(dirname "$0")/../../.." && pwd)
PASTA=${PASTA:-/tmp/bora-vm}
PORTA=${PORTA:-2222}
mkdir -p "$PASTA"
cd "$PASTA"
# shellcheck source=maquina.sh
source "$RAIZ/testes/vm/qemu/maquina.sh"

etapa "Preparar a máquina ($DISTRO)"
preparar_maquina
# O disco externo do backup: 2 GB em ext4, sem partição, como um pen drive formatado.
rm -f externo.img
truncate -s 2G externo.img
mkfs.ext4 -q -L BACKUP externo.img

etapa "Ligar a máquina"
ligar_maquina \
    -device virtio-scsi-pci,id=scsi \
    -blockdev driver=file,filename="$PASTA/externo.img",node-name=externo-arq \
    -blockdev driver=raw,file=externo-arq,node-name=externo \
    -device scsi-hd,bus=scsi.0,drive=externo,id=disco-externo,removable=on
esperar_ssh
vm "uname -r; sed -n 1,2p /etc/os-release"

etapa "Copiar o bora e o catálogo"
copiar_bora

etapa "Aplicar, na máquina"
fase na-vm.sh aplicar

etapa "Reiniciar"
reiniciar
fase na-vm.sh depois-do-reinicio

etapa "Desconectar e conectar de novo o disco externo"
fase na-vm.sh antes-de-conectar
monitor "device_del disco-externo"
sleep 5
monitor "device_add scsi-hd,bus=scsi.0,drive=externo,id=disco-externo,removable=on"
fase na-vm.sh depois-de-conectar

etapa "Desfazer"
fase na-vm.sh desfazer
vm "sudo cat /root/cobertas.txt" >cobertas.txt.parcial
mv cobertas.txt.parcial cobertas.txt

etapa "Tudo certo em $DISTRO"
