#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-node.sh
source ./comum-node.sh

# Um node, npm ou npx em /usr/local/bin que não veio do bora foi instalado à
# mão, e a receita não passa por cima.
for c in $NODE_COMANDOS; do
    alvo="/usr/local/bin/$c"
    if [ -e "$alvo" ] || [ -L "$alvo" ]; then
        case "$(readlink "$alvo" 2>/dev/null)" in
            "$NODE_RAIZ"/*) ;;
            *) falha "já existe $alvo, que não veio do bora; tire de lá ou desinstale esse Node.js e rode de novo" ;;
        esac
    fi
done

if ! node_instalado; then
    instalar_pacotes curl xz-utils ca-certificates
    tmp=$(mktemp -d)
    trap 'rm -rf "${tmp:?}"' EXIT
    msg "Baixando o Node.js $NODE_VERSAO de $NODE_URL"
    curl -fsSL --proto '=https' --tlsv1.2 --retry 3 -o "$tmp/node.tar.xz" "$NODE_URL" ||
        falha "não consegui baixar o Node.js; confira a conexão com a internet e rode de novo"
    # A soma está gravada na receita: o que chega precisa ser exatamente o arquivo testado.
    echo "$NODE_SHA256  $tmp/node.tar.xz" | sha256sum --check --quiet ||
        falha "o arquivo baixado não bate com a soma SHA256 que a receita conhece; nada foi instalado"
    msg "Soma SHA256 conferida."
    mkdir -p "$tmp/x"
    tar -xJf "$tmp/node.tar.xz" -C "$tmp/x" --no-same-owner
    if [ ! -d "$NODE_RAIZ" ]; then
        mkdir -p "$NODE_RAIZ"
        echo "$NODE_RAIZ" >>"$BORA_ESTADO/pastas-novas"
    fi
    rm -rf "${NODE_DIR:?}"
    mv "$tmp/x/$NODE_NOME" "$NODE_DIR"
    chown -R root:root "$NODE_DIR"
    echo "$NODE_DIR" >"$BORA_ESTADO/node-instalado"
    msg "Node.js instalado em $NODE_DIR"
fi

for c in $NODE_COMANDOS; do
    alvo="/usr/local/bin/$c"
    if [ "$(readlink "$alvo" 2>/dev/null)" != "$NODE_DIR/bin/$c" ]; then
        if [ -L "$alvo" ]; then
            # Um link de uma versão anterior do bora: guarda para o desfazer voltar.
            echo "$c $(readlink "$alvo")" >>"$BORA_ESTADO/links-anteriores"
        fi
        ln -sfn "$NODE_DIR/bin/$c" "$alvo"
        echo "$alvo" >>"$BORA_ESTADO/links-criados"
    fi
done

npmrc_esperado | escrever_arquivo "$NPMRC"
if [ ! -d "$BIN_DA_PESSOA" ]; then
    criar_pasta_da_pessoa "$PESSOA" "$BIN_DA_PESSOA"
    msg "Pasta criada: $BIN_DA_PESSOA (entra no PATH no próximo login)"
fi
if [ -x /usr/bin/node ]; then
    aviso "o Node.js da distro ($(/usr/bin/node --version 2>/dev/null)) continua instalado; o comando node passa a abrir o $NODE_VERSAO, que vem antes no PATH"
fi
msg "Pronto: Node.js $NODE_VERSAO e npm $("$NODE_DIR/bin/node" "$NODE_DIR/bin/npm" --version 2>/dev/null)."
