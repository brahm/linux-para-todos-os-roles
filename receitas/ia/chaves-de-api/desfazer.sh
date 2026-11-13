#!/usr/bin/env bash
set -euo pipefail
# desfazer.sh da receita ia/chaves-de-api (Chaves de API guardadas).
# Volta o que o aplicar mudou, lendo o que ficou anotado em $BORA_ESTADO.
# Roda a cópia da receita guardada na execução, então desfaz com os mesmos
# scripts que aplicaram. Chamado pelo `sudo bora desfazer`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"

[ -f "$BORA_ESTADO/pessoa" ] || exit 0
BORA_USUARIO=$(cat "$BORA_ESTADO/pessoa")
# shellcheck source=comum-chaves.sh
source ./comum-chaves.sh

if [ -f "$BORA_ESTADO/bloco" ]; then
    tirar_bloco
    if [ -f "$BORA_ESTADO/bashrc-criado" ] && [ ! -s "$BASHRC" ]; then rm -f "$BASHRC"; fi
    rm -f "$BORA_ESTADO/bloco" "$BORA_ESTADO/bashrc-criado"
    msg "O terminal de $PESSOA não carrega mais as chaves de API."
fi
if [ -f "$BORA_ESTADO/arquivo-criado" ]; then
    # Sem nenhuma chave colada, o arquivo é só o modelo e pode sair. Com
    # chaves, ele fica: são da pessoa, e apagar pode cortar o acesso dela.
    if cmp -s "$BORA_ESTADO/modelo" "$ARQUIVO"; then
        rm -f "$ARQUIVO"
        msg "Arquivo de chaves removido (estava sem nenhuma chave): $ARQUIVO"
    elif [ -e "$ARQUIVO" ]; then
        msg "O arquivo de chaves fica onde está, porque você mudou ele: $ARQUIVO. Para apagar, remova o arquivo e revogue as chaves no site de cada provedor."
    fi
    rm -f "$BORA_ESTADO/arquivo-criado" "$BORA_ESTADO/modelo"
fi
remover_pastas_novas
rm -f "$BORA_ESTADO/pessoa"
