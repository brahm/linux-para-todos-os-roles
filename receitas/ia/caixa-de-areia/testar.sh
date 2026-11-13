#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita ia/caixa-de-areia (Caixa de areia para os agentes).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-caixa.sh
source ./comum-caixa.sh

# Um projeto de teste e um segredo de mentira, na pasta da pessoa.
projeto=$(como_pessoa "$PESSOA" mktemp -d "$CASA/.teste-da-caixa-XXXXXX")
fora=$CASA/.teste-da-caixa-fora
segredo_criado=""
if [ ! -d "$CASA/.ssh" ]; then
    como_pessoa "$PESSOA" mkdir -m 700 "$CASA/.ssh"
    segredo_criado=pasta
fi
como_pessoa "$PESSOA" sh -c "echo segredo >'$CASA/.ssh/teste-da-caixa'"
# Apaga o projeto e o segredo de teste quando o script termina, dê certo ou não.
limpar() {
    rm -rf "${projeto:?}" "${fora:?}" "$CASA/.ssh/teste-da-caixa"
    if [ "$segredo_criado" = pasta ]; then rmdir "$CASA/.ssh" 2>/dev/null || true; fi
}
trap limpar EXIT
# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. `na_caixa` roda um comando dentro da
# caixa de areia, como a pessoa, a partir do projeto de teste.
na_caixa() { como_pessoa "$PESSOA" sh -c "cd '$projeto' && caixa $*"; }

escreve_no_projeto() { na_caixa "sh -c 'echo ok >arquivo'" && [ -f "$projeto/arquivo" ]; }
nao_escreve_fora() { ! na_caixa "sh -c 'echo x >$fora'" 2>/dev/null && [ ! -e "$fora" ]; }
nao_le_ssh() { ! na_caixa "cat $CASA/.ssh/teste-da-caixa" >/dev/null 2>&1; }
sem_sudo() { ! na_caixa "sudo -n true" >/dev/null 2>&1; }
recusa_a_casa() { ! como_pessoa "$PESSOA" sh -c "cd '$CASA' && caixa true" >/dev/null 2>&1; }

conferir "bubblewrap instalado (bwrap --version)" bwrap --version
conferir "o bubblewrap abre uma caixa de areia sem root" bwrap_abre
conferir "dentro da caixa, o agente escreve na pasta do projeto" escreve_no_projeto
conferir "dentro da caixa, ele não escreve fora do projeto" nao_escreve_fora
conferir "dentro da caixa, ele não lê as chaves SSH" nao_le_ssh
conferir "dentro da caixa, o sudo não funciona" sem_sudo
conferir "a caixa não abre com a pasta pessoal inteira" recusa_a_casa
if claude_instalado; then
    conferir "a caixa de areia do Claude Code está ligada (sandbox.enabled)" sandbox_claude_ligada
fi
resultado_dos_testes
