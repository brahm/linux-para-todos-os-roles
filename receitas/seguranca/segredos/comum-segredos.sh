# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita seguranca/segredos.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

PACOTES="git gitleaks"
INICIO="# >>> bora (seguranca/segredos): arquivos que nunca vão para o Git"
FIM="# <<< bora (seguranca/segredos)"

# Os ganchos do Git que o gancho do bora repassa para o .git/hooks do projeto.
# Com o core.hooksPath, o Git deixa de olhar o .git/hooks; o repasse mantém
# funcionando os ganchos que cada projeto já tinha.
GANCHOS="applypatch-msg pre-applypatch post-applypatch pre-commit pre-merge-commit prepare-commit-msg commit-msg post-commit pre-rebase post-checkout post-merge pre-push post-rewrite pre-auto-gc push-to-checkout"

# Uma opção global do Git da pessoa, ou vazio.
valor_global() { como_pessoa "$PESSOA" git config --global --get "$1" 2>/dev/null || true; }

# O arquivo de exclusões globais: o que a pessoa já configurou, ou o padrão
# do Git, ~/.config/git/ignore, que vale sem nenhuma configuração.
arquivo_ignore() {
    local f
    f=$(valor_global core.excludesFile)
    case "$f" in
        "") echo "$CASA/.config/git/ignore" ;;
        \~/*) echo "$CASA/${f#\~/}" ;;
        /*) echo "$f" ;;
        *) echo "$CASA/$f" ;;
    esac
}

# Os padrões de arquivos de segredo que o Git passa a ignorar em todo projeto.
bloco_ignore() {
    cat <<BLOCO
$INICIO
.env
.env.*
*.env
!.env.example
!.env.exemplo
!*.env.example
*.pem
*.key
id_rsa
id_ed25519
id_ecdsa
.netrc
$FIM
BLOCO
}

# O arquivo já tem o bloco do bora?
tem_bloco() { [ -f "$1" ] && grep -qxF "$INICIO" "$1"; }

# Tira o bloco do bora de um arquivo, sem mexer no resto.
tirar_bloco() {
    local f=$1 tmp
    tem_bloco "$f" || return 0
    tmp=$(mktemp)
    awk -v i="$INICIO" -v f="$FIM" '$0 == i {fora = 1; next} fora && $0 == f {fora = 0; next} !fora' "$f" >"$tmp"
    cat "$tmp" >"$f"
    rm -f "$tmp"
}

# O gancho do Git que roda o gitleaks antes de cada commit.
gancho() {
    cat <<'GANCHO'
#!/bin/sh
# Escrito pelo bora (receita seguranca/segredos). Antes de cada commit, o
# gitleaks confere o que vai entrar; depois, este gancho chama o do próprio
# projeto, em .git/hooks, se existir. Para pular a conferência uma vez, quando
# o gitleaks errar: git commit --no-verify
nome=$(basename "$0")
if [ "$nome" = pre-commit ]; then
    if command -v gitleaks >/dev/null 2>&1; then
        if ! gitleaks protect --staged --redact --no-banner; then
            echo
            echo "O gitleaks achou o que parece uma chave ou uma senha no commit, e o commit não foi feito."
            echo "Tire o segredo do arquivo (guarde em .env, que o Git ignora) e rode git add de novo."
            echo "Se for um alarme falso, faça o commit com: git commit --no-verify"
            exit 1
        fi
    else
        echo "Aviso: o gitleaks não está instalado; o commit não foi conferido." >&2
    fi
fi
dir=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0
proprio="$dir/hooks/$nome"
if [ -x "$proprio" ]; then
    exec "$proprio" "$@"
fi
exit 0
GANCHO
}

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
CASA=$(pasta_pessoal "$PESSOA")
GANCHOS_DIR=$CASA/.config/git/ganchos-bora

# O Git usa a pasta de ganchos do bora, e cada gancho aponta para o script certo?
ganchos_prontos() {
    [ "$(valor_global core.hooksPath)" = "$GANCHOS_DIR" ] || return 1
    cmp -s <(gancho) "$GANCHOS_DIR/gancho" || return 1
    local g
    for g in $GANCHOS; do
        [ "$(readlink "$GANCHOS_DIR/$g" 2>/dev/null)" = gancho ] || return 1
    done
}
