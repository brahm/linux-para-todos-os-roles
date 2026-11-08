#!/usr/bin/env bash
# Barra pipes que podem quebrar com "set -o pipefail".
#
# Em "cmd | grep -q x", "cmd | grep -m1 x" ou "cmd | head", o lado da direita
# sai assim que acha o que queria. Se "cmd" ainda estiver escrevendo, leva um
# SIGPIPE e sai com 141, e com pipefail a linha inteira falha, às vezes sim,
# às vezes não. Troque por uma destas formas:
#
#   grep -q x <<<"$(cmd)"        captura tudo antes e só então procura
#   cmd | awk 'NR == 1'          lê até o fim, em vez de "| head -n1"
#   git log -n 5, findmnt -f     a própria ferramenta limita a saída
#
# Uso: ferramentas/pipes/conferir.sh   (na raiz do repositório)
set -euo pipefail

padrao='(^|[^|])\|[[:space:]]*(grep[[:space:]]+(-[[:alnum:]]*[qm]|--quiet|--max-count)|head)([[:space:]]|$)'

achados=$(grep -rnE --include='*.sh' "$padrao" receitas testes ferramentas | grep -v '^ferramentas/pipes/' || true)
if [ -n "$achados" ]; then
    echo "Pipes que podem falhar com SIGPIPE (veja ferramentas/pipes/conferir.sh):"
    echo "$achados"
    exit 1
fi
echo "Nenhum pipe arriscado."
