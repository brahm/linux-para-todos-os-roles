#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita containers/podman (Contêineres com Podman).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

restaurar_arquivos
remover_pacotes_instalados
msg "O Podman voltou a ser como era antes."
msg "As imagens e os contêineres que você baixou ficam em ~/.local/share/containers. Para apagar, rode 'podman system reset' antes de desfazer, ou apague essa pasta."
