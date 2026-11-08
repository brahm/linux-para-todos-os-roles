# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
CASA=$(pasta_pessoal "$PESSOA")
PASTA=$CASA/.config/chaves-de-api
ARQUIVO=$PASTA/chaves.env
BASHRC=$CASA/.bashrc
INICIO="# >>> bora (ia/chaves-de-api): carrega as chaves de API dos agentes"
FIM="# <<< bora (ia/chaves-de-api)"

# As variáveis que cada agente procura, com o provedor escolhido primeiro.
linhas_dos_provedores() {
    local todas=(
        "openrouter|OPENROUTER_API_KEY|OpenRouter: https://openrouter.ai/settings/keys"
        "deepseek|DEEPSEEK_API_KEY|DeepSeek: https://platform.deepseek.com/api_keys"
        "outro|ANTHROPIC_API_KEY|Anthropic (Claude Code sem assinatura): https://console.anthropic.com/settings/keys"
        "outro|OPENAI_API_KEY|OpenAI (Codex sem assinatura): https://platform.openai.com/api-keys"
        "outro|GEMINI_API_KEY|Google Gemini: https://aistudio.google.com/apikey"
        "outro|MISTRAL_API_KEY|Mistral (Mistral Vibe): https://console.mistral.ai/api-keys"
    )
    local l escolhido=${BORA_PROVEDOR:-nenhum}
    for l in "${todas[@]}"; do [ "${l%%|*}" = "$escolhido" ] && echo "$l"; done
    for l in "${todas[@]}"; do [ "${l%%|*}" != "$escolhido" ] && echo "$l"; done
    return 0
}

modelo_de_chaves() {
    cat <<'TOPO'
# Chaves de API dos agentes de IA. Criado pelo bora (receita ia/chaves-de-api).
#
# Este arquivo só abre na sua conta (permissão 600) e fica fora de qualquer
# projeto, então nunca vai para o Git. Cada terminal novo carrega as chaves
# que estiverem aqui, e os agentes as encontram sozinhos.
#
# Para usar uma chave: tire o # do começo da linha, cole a chave depois do =
# e abra um terminal novo. Nunca cole uma chave dentro de um projeto, nem num
# chat de IA.
TOPO
    local l nome url
    while IFS='|' read -r _ nome url; do
        printf '\n# %s\n# %s=\n' "$url" "$nome"
    done < <(linhas_dos_provedores)
}

bloco_bashrc() {
    cat <<BLOCO
$INICIO
if [ -r "\$HOME/.config/chaves-de-api/chaves.env" ]; then
    set -a
    . "\$HOME/.config/chaves-de-api/chaves.env"
    set +a
fi
$FIM
BLOCO
}

tem_bloco() { [ -f "$BASHRC" ] && grep -qxF "$INICIO" "$BASHRC"; }

tirar_bloco() {
    local tmp
    tem_bloco || return 0
    tmp=$(mktemp)
    awk -v i="$INICIO" -v f="$FIM" '$0 == i {fora = 1; next} fora && $0 == f {fora = 0; next} !fora' "$BASHRC" >"$tmp"
    cat "$tmp" >"$BASHRC"
    rm -f "$tmp"
}

permissoes_certas() {
    [ -d "$PASTA" ] && [ -f "$ARQUIVO" ] || return 1
    [ "$(stat -c '%a %U' "$PASTA")" = "700 $PESSOA" ] || return 1
    [ "$(stat -c '%a %U' "$ARQUIVO")" = "600 $PESSOA" ] || return 1
}
