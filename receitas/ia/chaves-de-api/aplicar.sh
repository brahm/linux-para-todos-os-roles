#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-chaves.sh
source ./comum-chaves.sh

echo "$PESSOA" >"$BORA_ESTADO/pessoa"
if [ ! -d "$PASTA" ]; then
    criar_pasta_da_pessoa "$PESSOA" "$PASTA"
fi
chmod 700 "$PASTA"
if [ ! -e "$ARQUIVO" ]; then
    # umask 077: o arquivo já nasce só da pessoa, sem um instante aberto.
    modelo_de_chaves | como_pessoa "$PESSOA" sh -c "umask 077; cat >'$ARQUIVO'"
    modelo_de_chaves >"$BORA_ESTADO/modelo"
    echo "$ARQUIVO" >"$BORA_ESTADO/arquivo-criado"
    msg "Arquivo de chaves criado: $ARQUIVO"
else
    msg "O arquivo de chaves já existia ($ARQUIVO) e fica como está."
fi
chown "$PESSOA:" "$ARQUIVO"
chmod 600 "$ARQUIVO"

if ! tem_bloco; then
    [ -e "$BASHRC" ] || echo "$BASHRC" >"$BORA_ESTADO/bashrc-criado"
    {
        if [ -s "$BASHRC" ] && [ -n "$(tail -c1 "$BASHRC")" ]; then echo; fi
        bloco_bashrc
    } | como_pessoa "$PESSOA" tee -a "$BASHRC" >/dev/null
    echo sim >"$BORA_ESTADO/bloco"
    msg "Cada terminal novo de $PESSOA passa a carregar as chaves ($BASHRC)."
fi

case "${BORA_PROVEDOR:-nenhum}" in
    nenhum) msg "Quando tiver uma chave, abra $ARQUIVO num editor e siga as instruções do começo." ;;
    *) msg "Para usar a sua chave, abra $ARQUIVO num editor, tire o # da linha $(linhas_dos_provedores | awk -F'|' 'NR == 1 {print $2}')= e cole a chave depois do =. O OpenCode encontra a chave sozinho." ;;
esac
