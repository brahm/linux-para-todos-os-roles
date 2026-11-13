# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita dev/python.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

# python3-venv: ambientes virtuais; python3-pip: o pip dentro deles;
# python3-dev: os cabeçalhos para compilar pacotes com partes em C;
# pipx: programas em Python, cada um no seu ambiente;
# python-is-python3: o comando python, que os tutoriais usam.
PACOTES="python3-venv python3-pip python3-dev pipx python-is-python3"

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
BIN_DA_PESSOA=$(pasta_pessoal "$PESSOA")/.local/bin
