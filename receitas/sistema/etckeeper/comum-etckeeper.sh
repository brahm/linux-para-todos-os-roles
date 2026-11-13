# shellcheck shell=bash
# Variáveis e funções comuns aos scripts da receita sistema/etckeeper.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

# O /etc já tem um histórico do etckeeper, com pelo menos um registro?
etc_versionado() {
    [ -d /etc/.git ] && git -C /etc rev-parse --verify --quiet HEAD >/dev/null 2>&1
}

# O apt avisa o etckeeper antes e depois de cada instalação?
gancho_do_apt() { [ -f /etc/apt/apt.conf.d/05etckeeper ]; }
