#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

restaurar_arquivos
remover_pacotes_instalados
msg "O Podman voltou a ser como era antes."
msg "As imagens e os contêineres que você baixou ficam em ~/.local/share/containers. Para apagar, rode 'podman system reset' antes de desfazer, ou apague essa pasta."
