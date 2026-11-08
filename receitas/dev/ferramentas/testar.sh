#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-ferramentas.sh
source ./comum-ferramentas.sh

# Cada ferramenta faz o seu trabalho numa pasta de teste, que some no fim.
d=$(mktemp -d)
trap 'rm -rf "${d:?}"' EXIT
mkdir -p "$d/src"
echo 'print("olá, rolê")' >"$d/src/ola.py"
echo '{"nome": "bora", "rolês": [1, 2, 3, 4]}' >"$d/dados.json"
acha_texto() { [ "$(rg -l 'rolê' "$d/src")" = "$d/src/ola.py" ]; }
acha_arquivo() { [ "$(fd -e py . "$d")" = "$d/src/ola.py" ]; }
le_json() { [ "$(jq -r '.["rolês"] | length' "$d/dados.json")" = 4 ]; }

conferir "ripgrep acha um texto num projeto (rg)" acha_texto
conferir "fd acha um arquivo pelo nome (fd)" acha_arquivo
conferir "jq lê um JSON (jq)" le_json
conferir "GitHub CLI (gh --version)" gh --version
resultado_dos_testes
