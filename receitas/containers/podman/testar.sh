#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita containers/podman (Contêineres com Podman).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-podman.sh
source ./comum-podman.sh

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
sem_root() { [ "$(como_pessoa "$PESSOA" podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null)" = true ]; }
docker_hub() { grep -q docker.io <<<"$(podman info --format '{{.Registries}}' 2>/dev/null)"; }

conferir "Podman instalado (podman --version)" podman --version
conferir "faixa de IDs de $PESSOA para os contêineres (/etc/subuid e /etc/subgid)" eval 'tem_faixa subuid && tem_faixa subgid'
conferir "o newuidmap pode mapear os IDs (uidmap)" test -u /usr/bin/newuidmap -o -n "$(getcap /usr/bin/newuidmap 2>/dev/null)"
conferir "$PESSOA roda o Podman sem ser root (podman info)" sem_root
conferir "imagens com nome curto vêm do Docker Hub" docker_hub
resultado_dos_testes
