# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita dev/ferramentas.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

# ripgrep: o comando rg, que procura texto em todos os arquivos de um projeto;
# fd-find: o fd, que acha arquivos pelo nome; jq: lê e filtra JSON;
# gh: o GitHub CLI, para clonar, abrir pull requests e entrar no GitHub.
PACOTES="ripgrep fd-find jq gh"

# No Debian e no Ubuntu, o fd se chama fdfind, porque já existia outro
# programa chamado fd. A receita cria o nome que os tutoriais e os agentes usam.
LINK_FD=/usr/local/bin/fd

# O link /usr/local/bin/fd é o do bora?
fd_ligado() { [ "$(readlink "$LINK_FD" 2>/dev/null)" = /usr/bin/fdfind ]; }

# Existe um fd que não veio do bora (outro programa, ou um link feito à mão)?
fd_de_outro() {
    { [ -e "$LINK_FD" ] || [ -L "$LINK_FD" ]; } && ! fd_ligado
}
