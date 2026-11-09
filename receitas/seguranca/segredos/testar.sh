#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-segredos.sh
source ./comum-segredos.sh

d=$(como_pessoa "$PESSOA" mktemp -d)
trap 'rm -rf "${d:?}"' EXIT
git_() { como_pessoa "$PESSOA" git -C "$d" "$@"; }
git_ init -q
git_ config user.name "Teste do bora"
git_ config user.email teste@exemplo.com.br

env_ignorado() {
    echo "OPENROUTER_API_KEY=sk-or-v1-teste" | como_pessoa "$PESSOA" tee "$d/.env" >/dev/null
    git_ check-ignore -q .env
}
# Um token com o formato de um token do GitHub, inventado para o teste.
barra_segredo() {
    printf 'TOKEN = "ghp_%s"\n' "R7mQ2xK9vB4nL8pT3wY6zC1dF5gH0jS2aE7u" | como_pessoa "$PESSOA" tee "$d/config.py" >/dev/null
    git_ add config.py
    ! git_ commit -q -m "com segredo" >/dev/null 2>&1
}
passa_limpo() {
    git_ rm -q --cached config.py
    echo 'print("olá")' | como_pessoa "$PESSOA" tee "$d/ola.py" >/dev/null
    git_ add ola.py
    git_ commit -q -m "sem segredo"
}
repassa_gancho() {
    printf '#!/bin/sh\necho repassou >"%s/repassou"\n' "$d" | como_pessoa "$PESSOA" tee "$d/.git/hooks/post-commit" >/dev/null
    chmod +x "$d/.git/hooks/post-commit"
    git_ commit -q --allow-empty -m "gancho do projeto"
    [ -f "$d/repassou" ]
}

conferir "gitleaks instalado (gitleaks version)" gitleaks version
conferir "um arquivo .env fica fora do Git (git check-ignore .env)" env_ignorado
conferir "um commit com um token do GitHub é barrado" barra_segredo
conferir "um commit sem segredo passa" passa_limpo
conferir "os ganchos do próprio projeto continuam rodando" repassa_gancho
resultado_dos_testes
