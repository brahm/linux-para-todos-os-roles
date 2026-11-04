# shellcheck shell=bash
# Funções comuns às receitas do bora.
#
# Uso, no começo de cada script:
#   # shellcheck source=../../comum.sh
#   source "$BORA_LIB"
#
# Tudo o que muda o sistema e precisa ser desfeito fica registrado em
# $BORA_ESTADO, a pasta que o bora reserva para cada receita em cada execução.

msg() { printf '%s\n' "$*"; }
aviso() { printf 'Aviso: %s\n' "$*"; }
falha() {
    printf 'Erro: %s\n' "$*" >&2
    exit 1
}

: "${BORA_ESTADO:?o bora não informou BORA_ESTADO}"
: "${BORA_FAMILIA:?o bora não informou BORA_FAMILIA}"
mkdir -p "$BORA_ESTADO"

systemd_rodando() { [ -d /run/systemd/system ]; }

# --- Pacotes -------------------------------------------------------------

_APT_OPCOES=(-o DPkg::Lock::Timeout=300 -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold)

exigir_apt() {
    case "$BORA_FAMILIA" in
        ubuntu | debian) ;;
        *) falha "esta parte da receita ainda só existe para Ubuntu e Debian (família $BORA_FAMILIA)" ;;
    esac
}

apt_get() { DEBIAN_FRONTEND=noninteractive apt-get "${_APT_OPCOES[@]}" "$@"; }

pacote_instalado() {
    exigir_apt
    [ "$(dpkg-query -W -f='${db:Status-Abbrev}' "$1" 2>/dev/null)" = "ii " ]
}

_pacotes_no_sistema() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' 2>/dev/null | awk '$1 == "ii" {print $2}' | sort -u; }

# Atualiza a lista de pacotes, se ela tiver mais de uma hora.
atualizar_indices() {
    exigir_apt
    local marca=/var/lib/apt/periodic/update-success-stamp
    if [ -f "$marca" ] && [ -n "$(find "$marca" -mmin -60 2>/dev/null)" ]; then
        return 0
    fi
    msg "Atualizando a lista de pacotes."
    apt_get update -q
    mkdir -p /var/lib/apt/periodic && touch "$marca"
}

# Instala pacotes e anota em $BORA_ESTADO/pacotes-novos tudo o que entrou,
# inclusive dependências, para o desfazer remover só o que esta receita trouxe.
# Com --sem-recomendados, instala só as dependências obrigatórias.
instalar_pacotes() {
    exigir_apt
    local faltando=() p opcoes=()
    if [ "${1:-}" = --sem-recomendados ]; then
        opcoes+=(--no-install-recommends)
        shift
    fi
    for p in "$@"; do
        pacote_instalado "$p" || faltando+=("$p")
    done
    [ "${#faltando[@]}" -eq 0 ] && return 0
    atualizar_indices
    local antes depois
    antes=$(mktemp)
    depois=$(mktemp)
    _pacotes_no_sistema >"$antes"
    msg "Instalando: ${faltando[*]}"
    apt_get install -y -q "${opcoes[@]}" "${faltando[@]}"
    _pacotes_no_sistema >"$depois"
    comm -13 "$antes" "$depois" >>"$BORA_ESTADO/pacotes-novos"
    printf '%s\n' "${faltando[@]}" >>"$BORA_ESTADO/pacotes-pedidos"
    rm -f "$antes" "$depois"
}

# Pacotes que o apt removeria junto com os dados (simulação, sem mudar nada).
_removeria() { LC_ALL=C apt-get -s purge "$@" 2>/dev/null | awk '/^Purg |^Remv / {print $2}' | sort -u; }

# Remove o que instalar_pacotes trouxe, inclusive as dependências, sem levar
# junto nada que já existia antes ou que outro programa passou a usar depois.
remover_pacotes_instalados() {
    exigir_apt
    [ -s "$BORA_ESTADO/pacotes-novos" ] || return 0
    local novos restantes=() p extras
    novos=$(sort -u "$BORA_ESTADO/pacotes-novos")
    while read -r p; do
        if [ -z "$p" ] || ! pacote_instalado "$p"; then continue; fi
        # Pacotes essenciais ou protegidos do sistema nunca saem, mesmo que
        # tenham entrado junto com a receita.
        case "$(dpkg-query -W -f='${Essential} ${Protected} ${Priority}' "$p" 2>/dev/null)" in
            yes\ * | *\ yes\ * | *\ required | *\ important) continue ;;
        esac
        restantes+=("$p")
    done <<<"$novos"
    if [ "${#restantes[@]}" -gt 0 ]; then
        extras=$(comm -23 <(_removeria "${restantes[@]}") <(printf '%s\n' "$novos") | sed '/^$/d')
        if [ -z "$extras" ]; then
            msg "Removendo o que a receita instalou: ${restantes[*]}"
            apt_get purge -y -q "${restantes[@]}"
        else
            # Algum programa instalado depois depende do que a receita trouxe.
            # Remove só os pacotes pedidos que não levam nada de fora junto.
            aviso "outros programas passaram a depender de parte do que a receita instalou; essa parte fica: $(tr '\n' ' ' <<<"$extras")"
            local pedidos=()
            while read -r p; do
                if [ -z "$p" ] || ! pacote_instalado "$p"; then continue; fi
                if [ -z "$(comm -23 <(_removeria "$p") <(printf '%s\n' "$novos") | sed '/^$/d')" ]; then
                    pedidos+=("$p")
                fi
            done <"$BORA_ESTADO/pacotes-pedidos"
            if [ "${#pedidos[@]}" -gt 0 ]; then
                msg "Removendo: ${pedidos[*]}"
                apt_get purge -y -q "${pedidos[@]}"
            fi
        fi
    fi
    rm -f "$BORA_ESTADO/pacotes-pedidos" "$BORA_ESTADO/pacotes-novos"
}

# --- Arquivos ------------------------------------------------------------

# Guarda uma cópia de um arquivo antes de mudá-lo (só a primeira vez).
guardar_arquivo() {
    local arquivo=$1 copia="$BORA_ESTADO/arquivos$1"
    [ -e "$copia" ] && return 0
    grep -qxF "$arquivo" "$BORA_ESTADO/arquivos-novos" 2>/dev/null && return 0
    if [ -e "$arquivo" ]; then
        mkdir -p "$(dirname "$copia")"
        cp -a "$arquivo" "$copia"
    else
        printf '%s\n' "$arquivo" >>"$BORA_ESTADO/arquivos-novos"
    fi
}

# Escreve um arquivo só se o conteúdo mudar. O conteúdo vem da entrada padrão.
escrever_arquivo() {
    local arquivo=$1 modo=${2:-0644} tmp
    tmp=$(mktemp)
    cat >"$tmp"
    if [ -f "$arquivo" ] && cmp -s "$tmp" "$arquivo"; then
        rm -f "$tmp"
        return 0
    fi
    guardar_arquivo "$arquivo"
    mkdir -p "$(dirname "$arquivo")"
    install -m "$modo" "$tmp" "$arquivo"
    rm -f "$tmp"
    msg "Arquivo atualizado: $arquivo"
}

# Volta todos os arquivos guardados e apaga os que a receita criou.
restaurar_arquivos() {
    if [ -d "$BORA_ESTADO/arquivos" ]; then
        (cd "$BORA_ESTADO/arquivos" && find . \( -type f -o -type l \) -print0) |
            while IFS= read -r -d '' rel; do
                local destino=${rel#.}
                mkdir -p "$(dirname "$destino")"
                cp -a "$BORA_ESTADO/arquivos/$rel" "$destino"
                msg "Arquivo restaurado: $destino"
            done
        rm -rf "$BORA_ESTADO/arquivos"
    fi
    if [ -f "$BORA_ESTADO/arquivos-novos" ]; then
        local arquivo
        while read -r arquivo; do
            if [ -n "$arquivo" ] && [ -e "$arquivo" ]; then
                rm -f "$arquivo"
                msg "Arquivo removido: $arquivo"
            fi
        done <"$BORA_ESTADO/arquivos-novos"
        rm -f "$BORA_ESTADO/arquivos-novos"
    fi
}

# --- Serviços ------------------------------------------------------------

# Habilita uma unidade do systemd e anota, para o desfazer desabilitar.
habilitar_unidade() {
    local unidade=$1
    if ! systemctl is-enabled --quiet "$unidade" 2>/dev/null; then
        systemctl enable "$unidade" 2>&1 | sed '/^Created symlink/d'
        printf '%s\n' "$unidade" >>"$BORA_ESTADO/unidades-habilitadas"
    fi
    if systemd_rodando; then
        systemctl start "$unidade"
    fi
}

desabilitar_unidades_habilitadas() {
    [ -f "$BORA_ESTADO/unidades-habilitadas" ] || return 0
    local unidade
    while read -r unidade; do
        [ -n "$unidade" ] || continue
        if systemd_rodando; then
            systemctl disable --now "$unidade" 2>/dev/null || true
        else
            systemctl disable "$unidade" 2>/dev/null || true
        fi
        msg "Serviço desabilitado: $unidade"
    done <"$BORA_ESTADO/unidades-habilitadas"
    rm -f "$BORA_ESTADO/unidades-habilitadas"
}

# --- Testes --------------------------------------------------------------

# conferir "descrição" comando...: roda o comando e imprime o resultado.
_FALHAS=0
conferir() {
    local descricao=$1
    shift
    if "$@" >/dev/null 2>&1; then
        msg "ok: $descricao"
    else
        msg "FALHOU: $descricao"
        _FALHAS=$((_FALHAS + 1))
    fi
}

resultado_dos_testes() {
    if [ "$_FALHAS" -gt 0 ]; then
        msg "$_FALHAS conferência(s) falharam."
        exit 1
    fi
    msg "Tudo conferido."
}
