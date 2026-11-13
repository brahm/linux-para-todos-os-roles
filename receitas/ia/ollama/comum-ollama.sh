# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita ia/ollama.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

# A versão que esta receita instala e testa. Ao trocar, troque também as
# somas, copiadas do sha256sum.txt da página da versão em
# https://github.com/ollama/ollama/releases. O bora só roda em x86_64.
OLLAMA_VERSAO=0.40.9
OLLAMA_SHA256=01f0d0ae50cad3295a79a165033a65cf324f8ae5f7be64679464d29ecf28d67c
# Só para placas AMD: as bibliotecas do ROCm, num arquivo à parte.
OLLAMA_ROCM_SHA256=a0e670cfbb1deb4187fd04ee500dc56357cb77f4d39f283b06a84c55730dd0e8

[ "$(uname -m)" = x86_64 ] || falha "a receita do Ollama só existe para x86_64, e esta máquina é $(uname -m)"
OLLAMA_URL=https://github.com/ollama/ollama/releases/download/v$OLLAMA_VERSAO
OLLAMA_RAIZ=/opt/ollama
OLLAMA_DIR=$OLLAMA_RAIZ/$OLLAMA_VERSAO
OLLAMA_BIN=/usr/local/bin/ollama
OLLAMA_UNIDADE=/etc/systemd/system/ollama.service
# A conta do serviço e a pasta dos modelos, as mesmas do instalador oficial.
OLLAMA_CONTA=ollama
OLLAMA_CASA=/usr/share/ollama
OLLAMA_MODELOS=$OLLAMA_CASA/.ollama/models
# Só este computador fala com o Ollama: nada de porta aberta na rede.
OLLAMA_ENDERECO=127.0.0.1:11434

MODELO=${BORA_MODELO:-nenhum}
case "$MODELO" in
    sugerido) falha "o plano ainda diz modelo: sugerido; monte o plano de novo com o bora, que troca pelo modelo desta máquina" ;;
    nenhum) ;;
    *)
        [[ "$MODELO" =~ ^[a-z0-9][a-z0-9._-]*(/[a-z0-9][a-z0-9._-]*)?(:[A-Za-z0-9._-]+)?$ ]] ||
            falha "$MODELO não é um nome de modelo do Ollama"
        ;;
esac

# O serviço do systemd que mantém o Ollama rodando, só neste computador.
unidade_esperada() {
    cat <<UNIDADE
# Instalado pelo bora (receita ia/ollama).
[Unit]
Description=Ollama, modelos de IA neste computador
After=network-online.target

[Service]
ExecStart=$OLLAMA_BIN serve
User=$OLLAMA_CONTA
Group=$OLLAMA_CONTA
Environment=HOME=$OLLAMA_CASA
Environment=OLLAMA_HOST=$OLLAMA_ENDERECO
Restart=always
RestartSec=3
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=$OLLAMA_CASA
ProtectHome=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
UNIDADE
}

# A versão certa está na pasta e o comando aponta para ela?
ollama_instalado() {
    [ -x "$OLLAMA_DIR/bin/ollama" ] && [ "$(readlink "$OLLAMA_BIN" 2>/dev/null)" = "$OLLAMA_DIR/bin/ollama" ]
}

# Uma placa AMD com memória própria, que precisa das bibliotecas do ROCm.
tem_placa_amd() {
    local d
    for d in /sys/class/drm/card*/device; do
        [ "$(cat "$d/vendor" 2>/dev/null)" = 0x1002 ] || continue
        [ "$(cat "$d/mem_info_vram_total" 2>/dev/null || echo 0)" -ge $((2 * 1024 * 1024 * 1024)) ] && return 0
    done
    return 1
}

# O arquivo que diz que um modelo está baixado, sem precisar do servidor.
manifesto_do_modelo() {
    local nome=${1%%:*} etiqueta=latest
    [[ "$1" == *:* ]] && etiqueta=${1#*:}
    [[ "$nome" == */* ]] || nome=library/$nome
    echo "$OLLAMA_MODELOS/manifests/registry.ollama.ai/$nome/$etiqueta"
}

# O servidor do Ollama responde no endereço local?
api_responde() { curl -fsS --max-time 3 "http://$OLLAMA_ENDERECO/api/version" >/dev/null 2>&1; }

# Roda o comando com o servidor do Ollama no ar. Sem o serviço (num contêiner,
# ou antes do primeiro boot), sobe um servidor só para isso, na conta do serviço.
_OLLAMA_TEMPORARIO=
com_servidor() {
    if ! api_responde; then
        runuser -u "$OLLAMA_CONTA" -- env HOME="$OLLAMA_CASA" OLLAMA_HOST="$OLLAMA_ENDERECO" \
            "$OLLAMA_BIN" serve >"${BORA_ESTADO:?}/servidor-temporario.log" 2>&1 &
        _OLLAMA_TEMPORARIO=$!
        local i
        for i in $(seq 1 60); do
            api_responde && break
            sleep 0.5
            [ "$i" -lt 60 ] || falha "o servidor do Ollama não respondeu; veja $BORA_ESTADO/servidor-temporario.log"
        done
    fi
    local codigo=0
    OLLAMA_HOST=$OLLAMA_ENDERECO "$@" || codigo=$?
    if [ -n "$_OLLAMA_TEMPORARIO" ]; then
        kill "$_OLLAMA_TEMPORARIO" 2>/dev/null || true
        wait "$_OLLAMA_TEMPORARIO" 2>/dev/null || true
        _OLLAMA_TEMPORARIO=
    fi
    return "$codigo"
}
