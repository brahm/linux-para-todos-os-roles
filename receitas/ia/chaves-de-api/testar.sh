#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-chaves.sh
source ./comum-chaves.sh

so_da_pessoa() { [ "$(stat -c '%a %U' "$1")" = "$2 $PESSOA" ]; }
# Um terminal novo, com uma chave de teste num arquivo de chaves temporário,
# lido pelo mesmo trecho que foi para o .bashrc.
carrega() {
    local d r
    d=$(como_pessoa "$PESSOA" mktemp -d)
    mkdir -p "$d/.config/chaves-de-api"
    echo 'OPENROUTER_API_KEY=sk-or-teste-do-bora' >"$d/.config/chaves-de-api/chaves.env"
    bloco_bashrc >"$d/bloco"
    chown -R "$PESSOA:" "$d"
    r=$(como_pessoa "$PESSOA" env HOME="$d" bash -c ". '$d/bloco'; printenv OPENROUTER_API_KEY" 2>/dev/null) || true
    rm -rf "${d:?}"
    [ "$r" = sk-or-teste-do-bora ]
}
le_sem_erro() { como_pessoa "$PESSOA" bash -c "set -a; . '$ARQUIVO'"; }
outros_nao_leem() { ! runuser -u nobody -- cat "$ARQUIVO" >/dev/null 2>&1; }

conferir "a pasta das chaves só abre para $PESSOA (700, $PASTA)" so_da_pessoa "$PASTA" 700
conferir "o arquivo das chaves só abre para $PESSOA (600, $ARQUIVO)" so_da_pessoa "$ARQUIVO" 600
conferir "outra conta não consegue ler as chaves" outros_nao_leem
conferir "o arquivo das chaves não tem erro" le_sem_erro
conferir "o .bashrc carrega as chaves em cada terminal novo" tem_bloco
conferir "uma chave do arquivo chega ao terminal (printenv)" carrega
resultado_dos_testes
