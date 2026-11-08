#!/usr/bin/env bash
# Sobe uma máquina virtual com tela de login (o GDM, como num desktop) e
# confere as receitas que só se veem com tela, as de so-com-tela.txt: o
# ambiente leve aparece e abre sozinho, o Firefox abre com o uBlock Origin
# que a política instala e, no Ubuntu, o Firefox é o da Mozilla, e não o do
# Snap. Tira capturas da tela em cada passo, em $PASTA/telas.
#
#   testes/vm/qemu/tela.sh ubuntu-24.04 binario/bora
#   testes/vm/qemu/tela.sh ubuntu-26.04 binario/bora
#   testes/vm/qemu/tela.sh debian-13 binario/bora
#   testes/vm/qemu/tela.sh debian-13 binario/bora lightdm
#
# O terceiro argumento escolhe a tela de login: o GDM, do GNOME (o padrão),
# ou o LightDM, das máquinas com Xfce.
#
# Quando tudo passa, $PASTA/cobertas.txt lista as receitas que a máquina
# aplicou, desfez e conferiu; o workflow usa a lista para gravar o registro.
# As capturas ficam em $PASTA/telas e, com a metade do tamanho, em
# $PASTA/telas/site, que o workflow leva para o site.
# Os programas e a pasta são os mesmos do rodar.sh (padrão: /tmp/bora-tela).
set -euo pipefail

USO="uso: tela.sh ubuntu-24.04|ubuntu-26.04|debian-13 caminho/do/bora [gdm|lightdm]"
DISTRO=${1:?$USO}
BORA_BIN=$(realpath "${2:?$USO}")
TELA=${3:-gdm}
RAIZ=$(cd "$(dirname "$0")/../../.." && pwd)
PASTA=${PASTA:-/tmp/bora-tela}
PORTA=${PORTA:-2223}
mkdir -p "$PASTA"
cd "$PASTA"
# shellcheck source=maquina.sh
source "$RAIZ/testes/vm/qemu/maquina.sh"

# Grava a tela num PNG em $PASTA/telas e confere que ela não está vazia. A
# sessão pode já existir antes de a tela terminar de desenhar (a tela de
# login do Ubuntu 24.04 já apareceu toda preta), então tenta por até 1 minuto.
capturar() {
    local nome=$1
    for tentativa in $(seq 1 12); do
        rm -f "telas/$nome.ppm"
        monitor "screendump $PASTA/telas/$nome.ppm"
        for _ in $(seq 1 10); do
            [ -s "telas/$nome.ppm" ] && break
            sleep 1
        done
        if python3 "$RAIZ/testes/vm/qemu/captura.py" "telas/$nome.ppm" "telas/$nome.png" "telas/site/$nome.png"; then
            rm -f "telas/$nome.ppm"
            return 0
        fi
        echo "a tela ainda não mostra nada (tentativa $tentativa); esperando"
        sleep 5
    done
    falhou "a captura $nome não mostra nada"
}

etapa "Preparar a máquina ($DISTRO)"
preparar_maquina
rm -rf telas
mkdir -p telas/site

etapa "Ligar a máquina"
# shellcheck disable=SC2119 # sem disco a mais
ligar_maquina
# Se algo falhar, a última tela vai junto (ela costuma mostrar o porquê).
trap 'if [ $? -ne 0 ] && [ -S monitor.sock ]; then
        monitor "screendump $PASTA/telas/falhou.ppm" || true
        sleep 2
        python3 "$RAIZ/testes/vm/qemu/captura.py" telas/falhou.ppm telas/falhou.png || true
        rm -f telas/falhou.ppm
    fi
    kill "$(cat "$PASTA/qemu.pid" 2>/dev/null)" 2>/dev/null || true' EXIT
esperar_ssh
vm "uname -r; sed -n 1,2p /etc/os-release"

etapa "Copiar o bora e o catálogo"
copiar_bora

etapa "Instalar a tela de login e reiniciar"
fase tela-na-vm.sh "preparar $TELA"
reiniciar
fase tela-na-vm.sh tela-de-login
capturar 1-tela-de-login

etapa "Aplicar e reiniciar"
fase tela-na-vm.sh aplicar
reiniciar
fase tela-na-vm.sh sessao
capturar 2-ambiente-leve

etapa "Abrir o Firefox"
fase tela-na-vm.sh firefox
capturar 3-firefox

etapa "Sair, reiniciar e desfazer"
fase tela-na-vm.sh sair
reiniciar
fase tela-na-vm.sh desfazer
capturar 4-depois-de-desfazer
vm "sudo cat /root/cobertas.txt" >cobertas.txt.parcial
mv cobertas.txt.parcial cobertas.txt

etapa "Tudo certo em $DISTRO, com o $TELA"
