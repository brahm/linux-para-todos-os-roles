#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita ia/ollama (Ollama, para modelos de IA no computador).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-ollama.sh
source ./comum-ollama.sh

# Um Ollama instalado de outro jeito (pelo instalador oficial, pela distro ou
# à mão) tem o próprio serviço e os próprios arquivos, e a receita não passa
# por cima deles.
for alvo in "$OLLAMA_BIN" /usr/bin/ollama; do
    if [ -e "$alvo" ] || [ -L "$alvo" ]; then
        case "$(readlink "$alvo" 2>/dev/null)" in
            "$OLLAMA_RAIZ"/*) ;;
            *) falha "já existe $alvo, que não veio do bora; desinstale esse Ollama (os modelos ficam em $OLLAMA_MODELOS) e rode de novo" ;;
        esac
    fi
done
if [ -e "$OLLAMA_UNIDADE" ] && ! grep -q 'receita ia/ollama' "$OLLAMA_UNIDADE"; then
    falha "já existe $OLLAMA_UNIDADE, que não veio do bora; desinstale esse Ollama e rode de novo"
fi

instalar_pacotes curl zstd ca-certificates

if ! ollama_instalado; then
    # Os arquivos têm mais de 1 GB: a pasta temporária fica no disco, e não na memória.
    tmp=$(mktemp -d -p /var/tmp bora-ollama.XXXXXX)
    trap 'rm -rf "${tmp:?}"' EXIT
    arquivos=("ollama-linux-amd64.tar.zst $OLLAMA_SHA256")
    if tem_placa_amd; then
        msg "Placa de vídeo AMD encontrada: baixando também as bibliotecas do ROCm."
        arquivos+=("ollama-linux-amd64-rocm.tar.zst $OLLAMA_ROCM_SHA256")
    fi
    mkdir -p "$tmp/x"
    for item in "${arquivos[@]}"; do
        read -r nome soma <<<"$item"
        msg "Baixando $nome ($OLLAMA_URL/$nome)"
        curl -fsSL --proto '=https' --tlsv1.2 --retry 3 -o "$tmp/$nome" "$OLLAMA_URL/$nome" ||
            falha "não consegui baixar o Ollama; confira a conexão com a internet e rode de novo"
        # A soma está gravada na receita: o que chega precisa ser exatamente o arquivo testado.
        echo "$soma  $tmp/$nome" | sha256sum --check --quiet ||
            falha "o arquivo $nome não bate com a soma SHA256 que a receita conhece; nada foi instalado"
        msg "Soma SHA256 conferida."
        tar --zstd -xf "$tmp/$nome" -C "$tmp/x" --no-same-owner
        rm -f "${tmp:?}/$nome"
    done
    [ -x "$tmp/x/bin/ollama" ] || falha "o arquivo do Ollama não trouxe bin/ollama; a receita precisa ser atualizada"
    if [ ! -d "$OLLAMA_RAIZ" ]; then
        mkdir -p "$OLLAMA_RAIZ"
        echo "$OLLAMA_RAIZ" >>"$BORA_ESTADO/pastas-novas"
    fi
    rm -rf "${OLLAMA_DIR:?}"
    mv "$tmp/x" "$OLLAMA_DIR"
    chown -R root:root "$OLLAMA_DIR"
    chmod 755 "$OLLAMA_DIR"
    echo "$OLLAMA_DIR" >"$BORA_ESTADO/ollama-instalado"
    msg "Ollama $OLLAMA_VERSAO instalado em $OLLAMA_DIR"
fi

if [ "$(readlink "$OLLAMA_BIN" 2>/dev/null)" != "$OLLAMA_DIR/bin/ollama" ]; then
    if [ -L "$OLLAMA_BIN" ]; then
        # Um link de uma versão anterior do bora: guarda para o desfazer voltar.
        readlink "$OLLAMA_BIN" >"$BORA_ESTADO/link-anterior"
    fi
    ln -sfn "$OLLAMA_DIR/bin/ollama" "$OLLAMA_BIN"
    echo "$OLLAMA_BIN" >"$BORA_ESTADO/link-criado"
fi

if ! getent passwd "$OLLAMA_CONTA" >/dev/null; then
    useradd --system --user-group --create-home --home-dir "$OLLAMA_CASA" \
        --shell /usr/sbin/nologin --comment "Ollama, instalado pelo bora" "$OLLAMA_CONTA"
    echo "$OLLAMA_CONTA" >"$BORA_ESTADO/conta-criada"
    # Os grupos que abrem a placa de vídeo, quando existem.
    for g in render video; do
        if getent group "$g" >/dev/null; then usermod -a -G "$g" "$OLLAMA_CONTA"; fi
    done
    msg "Conta do serviço criada: $OLLAMA_CONTA, com os modelos em $OLLAMA_MODELOS"
fi
if [ ! -d "$OLLAMA_CASA" ]; then
    install -d -o "$OLLAMA_CONTA" -g "$OLLAMA_CONTA" -m 0755 "$OLLAMA_CASA"
fi

unidade_esperada | escrever_arquivo "$OLLAMA_UNIDADE"
if systemd_rodando; then systemctl daemon-reload; fi
habilitar_unidade ollama.service

if [ "$MODELO" != nenhum ] && [ ! -f "$(manifesto_do_modelo "$MODELO")" ]; then
    msg "Baixando o modelo $MODELO. São alguns gigabytes; pode demorar."
    com_servidor "$OLLAMA_BIN" pull "$MODELO" ||
        falha "não consegui baixar o modelo $MODELO; confira o nome em https://ollama.com/library e a conexão, e rode de novo"
    echo "$MODELO" >>"$BORA_ESTADO/modelos-baixados"
fi

if [ -e /dev/nvidiactl ] || command -v nvidia-smi >/dev/null 2>&1; then
    msg "O Ollama vai usar a placa NVIDIA."
elif grep -qs 0x10de /sys/class/drm/card*/device/vendor; then
    aviso "há uma placa NVIDIA sem driver; instale o driver dela (no Ubuntu, em Programas e atualizações, Drivers adicionais) para o Ollama usá-la"
fi
msg "Pronto: Ollama $OLLAMA_VERSAO, atendendo só este computador em http://$OLLAMA_ENDERECO."
if [ "$MODELO" != nenhum ]; then
    msg "Para conversar com o modelo: ollama run $MODELO"
    msg "Para programar com um agente usando o modelo: ollama launch opencode (ou claude, ou codex)"
else
    msg "Para baixar um modelo: ollama pull NOME. O bora modelos mostra os que cabem nesta máquina."
fi
