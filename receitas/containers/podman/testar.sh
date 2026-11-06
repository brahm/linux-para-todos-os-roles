#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-podman.sh
source ./comum-podman.sh

sem_root() { [ "$(como_pessoa "$PESSOA" podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null)" = true ]; }
docker_hub() { podman info --format '{{.Registries}}' 2>/dev/null | grep -q docker.io; }

conferir "Podman instalado (podman --version)" podman --version
conferir "faixa de IDs de $PESSOA para os contêineres (/etc/subuid e /etc/subgid)" eval 'tem_faixa subuid && tem_faixa subgid'
conferir "o newuidmap pode mapear os IDs (uidmap)" test -u /usr/bin/newuidmap -o -n "$(getcap /usr/bin/newuidmap 2>/dev/null)"
conferir "$PESSOA roda o Podman sem ser root (podman info)" sem_root
conferir "imagens com nome curto vêm do Docker Hub" docker_hub
resultado_dos_testes
