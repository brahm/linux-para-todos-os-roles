#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-git.sh
source ./comum-git.sh

tem() { [ -n "$(valor_do_git "$1")" ]; }
# Um commit de verdade, num repositório de teste que some no fim.
commit_de_teste() {
    local d
    d=$(como_pessoa "$PESSOA" mktemp -d)
    como_pessoa "$PESSOA" git -C "$d" init -q &&
        como_pessoa "$PESSOA" git -C "$d" commit -q --allow-empty -m "teste do bora"
    local r=$?
    rm -rf "${d:?}"
    return $r
}
chave_valida() { ssh-keygen -l -f "$(chave_existente).pub"; }

conferir "Git instalado (git --version)" git --version
conferir "nome nos commits de $PESSOA (git config user.name)" tem user.name
conferir "e-mail nos commits de $PESSOA (git config user.email)" tem user.email
conferir "repositórios novos começam no ramo main (init.defaultBranch)" tem init.defaultBranch
conferir "o git pull sabe juntar as mudanças (pull.rebase)" test -n "$(valor_do_git pull.rebase)$(valor_do_git pull.ff)"
conferir "um commit de teste funciona" commit_de_teste
if [ "${BORA_CHAVE_SSH:-sim}" = sim ]; then
    conferir "$PESSOA tem uma chave SSH válida (ssh-keygen -l)" chave_valida
fi
resultado_dos_testes
