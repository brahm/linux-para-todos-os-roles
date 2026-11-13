# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita dev/node.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

# A versão LTS que esta receita instala e testa. Ao trocar, troque também a
# soma, copiada de https://nodejs.org/dist/v<versão>/SHASUMS256.txt.
# O bora só roda em x86_64, então só entra o pacote linux-x64.
NODE_VERSAO=26.13.0
NODE_SHA256_X64=d28a96af6c38596f6d9d97c0ee531c13d238d757742387d1928de822d959e997

case "$(uname -m)" in
    x86_64) NODE_ARQ=x64 NODE_SHA256=$NODE_SHA256_X64 ;;
    *) falha "o Node.js oficial não tem versão para $(uname -m)" ;;
esac
NODE_NOME=node-v$NODE_VERSAO-linux-$NODE_ARQ
NODE_URL=https://nodejs.org/dist/v$NODE_VERSAO/$NODE_NOME.tar.xz
NODE_RAIZ=/usr/local/lib/nodejs
NODE_DIR=$NODE_RAIZ/$NODE_NOME
NODE_COMANDOS="node npm npx"
# O npm lê este arquivo em qualquer conta. Com o prefix na pasta pessoal,
# o "npm install -g" instala em ~/.local, sem sudo.
NPMRC=$NODE_DIR/etc/npmrc

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
BIN_DA_PESSOA=$(pasta_pessoal "$PESSOA")/.local/bin

# O conteúdo que o $NPMRC precisa ter.
npmrc_esperado() {
    cat <<'NPMRC'
# Configurado pelo bora (receita dev/node): "npm install -g" instala na pasta
# pessoal de quem roda, em ~/.local, sem precisar de sudo.
prefix=${HOME}/.local
NPMRC
}

# Cada comando em /usr/local/bin aponta para esta versão?
comandos_ligados() {
    local c
    for c in $NODE_COMANDOS; do
        [ "$(readlink "/usr/local/bin/$c" 2>/dev/null)" = "$NODE_DIR/bin/$c" ] || return 1
    done
}

# A versão certa do Node.js está na pasta e responde?
node_instalado() {
    [ -x "$NODE_DIR/bin/node" ] && [ "$("$NODE_DIR/bin/node" --version 2>/dev/null)" = "v$NODE_VERSAO" ]
}
