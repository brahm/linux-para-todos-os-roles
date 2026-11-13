#!/usr/bin/env bash
# Barra os clichês de texto gerado por IA que o guia de estilo proíbe.
#
# A lista e as alternativas estão em docs/estilo.md. Ficam de fora o próprio
# guia, o CLAUDE.md (que repete a lista) e as decisões antigas, que são
# histórico.
#
# Uso: ferramentas/estilo/conferir.sh   (na raiz do repositório)
set -euo pipefail

padrao='mergulh|desvend|crucia(l|is)|robust[oa]s?\b|elevand|em suma|vale ressaltar|no cenário atual|tapeçaria|sinfonia|desbloque[a-z]* o potencial|(^|[.!?>"(][[:space:]]*)imagine\b'

achados=$(grep -rniE "$padrao" \
    --include='*.md' --include='*.html' --include='*.py' --include='*.yaml' \
    --include='*.yml' --include='*.rs' --include='*.sh' --include='*.js' \
    README.md CONTRIBUTING.md docs objetivos receitas familias testes marca src ferramentas .github \
    | grep -vE '^(docs/estilo\.md|docs/decisoes\.md|CLAUDE\.md|ferramentas/estilo/)' || true)
if [ -n "$achados" ]; then
    echo "Clichês que o guia de estilo proíbe (veja docs/estilo.md):"
    echo "$achados"
    exit 1
fi
echo "Nenhum clichê proibido."
