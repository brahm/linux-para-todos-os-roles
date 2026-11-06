# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

# A versão LTS que esta receita instala e testa. Ao trocar, troque também as
# somas, copiadas de https://nodejs.org/dist/v<versão>/SHASUMS256.txt.
NODE_VERSAO=26.13.0
NODE_SHA256_X64=d28a96af6c38596f6d9d97c0ee531c13d238d757742387d1928de822d959e997
NODE_SHA256_ARM64=406fe3fbde1c054adff8b297c16fdb5af6659db327c1ac8acd46b56ef1af9a92

case "$(uname -m)" in
    x86_64) NODE_ARQ=x64 NODE_SHA256=$NODE_SHA256_X64 ;;
    aarch64) NODE_ARQ=arm64 NODE_SHA256=$NODE_SHA256_ARM64 ;;
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

node_instalado() {
    [ -x "$NODE_DIR/bin/node" ] && [ "$("$NODE_DIR/bin/node" --version 2>/dev/null)" = "v$NODE_VERSAO" ]
}
