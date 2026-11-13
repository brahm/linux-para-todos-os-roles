# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita dev/git.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

CHAVES="id_ed25519 id_ecdsa id_rsa"

# O arquivo de configuração do Git que o "git config --global" usa: o
# ~/.gitconfig, a não ser que só exista o ~/.config/git/config.
arquivo_do_git() {
    local casa=$1
    if [ ! -e "$casa/.gitconfig" ] && [ -f "$casa/.config/git/config" ]; then
        echo "$casa/.config/git/config"
    else
        echo "$casa/.gitconfig"
    fi
}

# Uma opção global do Git da pessoa, ou vazio se não estiver configurada.
valor_do_git() { como_pessoa "$PESSOA" git config --global --get "$1" 2>/dev/null || true; }

# O nome que vai nos commits: o pedido, o que já está configurado ou o da conta.
nome_desejado() {
    local nome=${BORA_NOME:-auto} atual completo
    if [ "$nome" != auto ] && [ -n "$nome" ]; then
        echo "$nome"
        return 0
    fi
    atual=$(valor_do_git user.name)
    if [ -n "$atual" ]; then
        echo "$atual"
        return 0
    fi
    completo=$(getent passwd "$PESSOA" | cut -d: -f5 | cut -d, -f1)
    echo "${completo:-$PESSOA}"
}

# O e-mail dos commits: o pedido ou o que já está configurado. Nunca inventa um.
email_desejado() {
    if [ -n "${BORA_EMAIL:-}" ]; then echo "$BORA_EMAIL"; else valor_do_git user.email; fi
}

# A primeira chave SSH que a pessoa já tem, se tiver.
chave_existente() {
    local c
    for c in $CHAVES; do
        if [ -f "$CASA/.ssh/$c.pub" ]; then
            echo "$CASA/.ssh/$c"
            return 0
        fi
    done
    return 1
}

# Tudo o que a receita configura já está assim?
git_configurado() {
    command -v git >/dev/null || return 1
    [ "$(valor_do_git user.name)" = "$(nome_desejado)" ] || return 1
    [ -n "$(email_desejado)" ] || return 1
    [ "$(valor_do_git user.email)" = "$(email_desejado)" ] || return 1
    [ -n "$(valor_do_git init.defaultBranch)" ] || return 1
    [ -n "$(valor_do_git pull.rebase)$(valor_do_git pull.ff)" ] || return 1
    if [ "${BORA_CHAVE_SSH:-sim}" = sim ]; then chave_existente >/dev/null || return 1; fi
    return 0
}

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
CASA=$(pasta_pessoal "$PESSOA")
