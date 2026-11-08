#!/usr/bin/env bash
# Escreve, em português, as notas da página de uma versão do bora.
#
# A lista de pull requests vem da própria API do GitHub (a mesma das notas
# automáticas), que só existe em inglês; este script traduz os títulos das
# seções e reescreve cada linha.
#
#   ferramentas/notas/escrever.sh v0.5.2 <commit> >notas.md
#
# Precisa do gh com GH_TOKEN e de GITHUB_REPOSITORY (o Actions já define os dois).
set -euo pipefail
TAG=${1:?uso: escrever.sh vX.Y.Z commit}
ALVO=${2:?uso: escrever.sh vX.Y.Z commit}
REPO=${GITHUB_REPOSITORY:?defina GITHUB_REPOSITORY, como em brahm/linux-para-todos-os-roles}

cru=$(gh api "repos/$REPO/releases/generate-notes" -f tag_name="$TAG" -f target_commitish="$ALVO" --jq .body)

cat <<TEXTO
O \`bora\` é um arquivo só, para computadores de 64 bits (x86_64). Baixe o \`bora-linux-x86_64\` e o \`SHA256SUMS\` aqui embaixo e confira antes de rodar:

\`\`\`sh
sha256sum --check --ignore-missing SHA256SUMS
chmod +x bora-linux-x86_64
sudo mv bora-linux-x86_64 /usr/local/bin/bora
bora diag
\`\`\`

TEXTO

# "* Título by @pessoa in https://github.com/.../pull/17" vira "- Título (#17, @pessoa)".
sed -E \
    -e 's/^## What.s Changed$/## O que mudou/' \
    -e 's/^## New Contributors$/## Quem contribuiu pela primeira vez/' \
    -e 's#^\* (.*) by (@[^ ]+) in https://github\.com/[^ ]+/pull/([0-9]+)$#- \1 (\#\3, \2)#' \
    -e 's#^\* (@[^ ]+) made their first contribution in https://github\.com/[^ ]+/pull/([0-9]+)$#- \1, no \#\2#' \
    -e 's/^\*\*Full Changelog\*\*: /**Todas as mudanças:** /' \
    <<<"$cru"
