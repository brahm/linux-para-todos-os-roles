#!/usr/bin/env bash
# Grava na main o registro de testes que o registrar.py escreveu, gera o site
# de novo e manda publicar. Usado pelos workflows de testes e da VM.
#
#   ferramentas/registros/gravar-na-main.sh "Registra o teste em contêiner de 2026-11-08"
#
# Precisa de GH_TOKEN com contents: write e actions: write.
set -euo pipefail
MENSAGEM=${1:?uso: gravar-na-main.sh "mensagem do commit"}

python3 -c 'import yaml' 2>/dev/null || pip install --quiet pyyaml
python3 ferramentas/catalogo/gerar.py >/dev/null

git add receitas docs
# As capturas da máquina virtual com tela, que o site mostra.
if [ -d testes/vm/telas ]; then git add testes/vm/telas; fi
if git diff --cached --quiet; then
    echo "Nada novo para registrar."
    exit 0
fi
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git commit -q -m "$MENSAGEM"

gravou=nao
for tentativa in 1 2 3; do
    if git pull -q --rebase origin main && git push -q origin HEAD:main; then
        gravou=sim
        break
    fi
    sleep $((tentativa * 5))
done
[ "$gravou" = sim ] || {
    echo "Não consegui gravar na main." >&2
    exit 1
}
# Um push feito pelo próprio workflow não dispara outros workflows, então o
# site é publicado por aqui.
gh workflow run site.yml --ref main
