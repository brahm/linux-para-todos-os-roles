#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-git.sh
source ./comum-git.sh

email=$(email_desejado)
if [ -z "$email" ]; then
    falha "falta o e-mail que vai nos commits; informe no parâmetro email, de preferência o mesmo da sua conta no GitHub ou no GitLab"
fi
case "$email" in
    *@*.*) ;;
    *) falha "$email não parece um e-mail" ;;
esac

instalar_pacotes git openssh-client
echo "$PESSOA" >"$BORA_ESTADO/pessoa"

arquivo=$(arquivo_do_git "$CASA")
mudar() {
    if [ "$(valor_do_git "$1")" != "$2" ]; then
        guardar_arquivo "$arquivo"
        como_pessoa "$PESSOA" git config --file "$arquivo" "$1" "$2"
        msg "Git: $1 = $2"
    fi
}
mudar user.name "$(nome_desejado)"
mudar user.email "$email"
# Os padrões que evitam as duas mensagens que mais confundem quem começa.
if [ -z "$(valor_do_git init.defaultBranch)" ]; then mudar init.defaultBranch main; fi
if [ -z "$(valor_do_git pull.rebase)$(valor_do_git pull.ff)" ]; then mudar pull.rebase false; fi

if [ "${BORA_CHAVE_SSH:-sim}" = sim ]; then
    if chave=$(chave_existente); then
        msg "$PESSOA já tem uma chave SSH ($chave); a receita não cria outra."
    else
        if [ ! -d "$CASA/.ssh" ]; then
            criar_pasta_da_pessoa "$PESSOA" "$CASA/.ssh"
            chmod 700 "$CASA/.ssh"
        fi
        chave=$CASA/.ssh/id_ed25519
        como_pessoa "$PESSOA" ssh-keygen -q -t ed25519 -N "" -C "$email" -f "$chave"
        echo "$chave" >"$BORA_ESTADO/chave-criada"
        msg "Chave SSH criada: $chave"
    fi
    msg ""
    msg "Para usar a chave no GitHub, abra https://github.com/settings/ssh/new (no GitLab, https://gitlab.com/-/user_settings/ssh_keys) e cole esta linha:"
    msg "  $(cat "$chave.pub")"
fi
