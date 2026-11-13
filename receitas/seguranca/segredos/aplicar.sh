#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita seguranca/segredos (Verificação de segredos).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-segredos.sh
source ./comum-segredos.sh

atual=$(valor_global core.hooksPath)
if [ -n "$atual" ] && [ "$atual" != "$GANCHOS_DIR" ]; then
    falha "o Git de $PESSOA já usa ganchos de outra pasta ($atual, no core.hooksPath); a receita não passa por cima. Tire essa configuração ou chame o gitleaks a partir dos seus ganchos"
fi

# shellcheck disable=SC2086
instalar_pacotes $PACOTES
echo "$PESSOA" >"$BORA_ESTADO/pessoa"

# 1. Os arquivos que nunca vão para o Git, em todos os projetos.
ignore=$(arquivo_ignore)
if ! tem_bloco "$ignore"; then
    if [ ! -e "$ignore" ]; then
        criar_pasta_da_pessoa "$PESSOA" "$(dirname "$ignore")"
        echo "$ignore" >"$BORA_ESTADO/ignore-criado"
    fi
    {
        if [ -s "$ignore" ] && [ -n "$(tail -c1 "$ignore")" ]; then echo; fi
        bloco_ignore
    } | como_pessoa "$PESSOA" tee -a "$ignore" >/dev/null
    echo "$ignore" >"$BORA_ESTADO/ignore"
    msg "O Git de $PESSOA passa a ignorar .env e chaves em todos os projetos ($ignore)."
fi

# 2. O gancho que chama o gitleaks antes de cada commit.
if ! ganchos_prontos; then
    criar_pasta_da_pessoa "$PESSOA" "$GANCHOS_DIR"
    gancho | como_pessoa "$PESSOA" tee "$GANCHOS_DIR/gancho" >/dev/null
    chmod 0755 "$GANCHOS_DIR/gancho"
    for g in $GANCHOS; do
        como_pessoa "$PESSOA" ln -sfn gancho "$GANCHOS_DIR/$g"
    done
    if [ -z "$atual" ]; then
        como_pessoa "$PESSOA" git config --global core.hooksPath "$GANCHOS_DIR"
        echo sim >"$BORA_ESTADO/hookspath"
    fi
    msg "O gitleaks passa a conferir cada commit de $PESSOA (ganchos em $GANCHOS_DIR)."
fi
msg "Pronto. Para conferir um projeto inteiro, com o histórico: gitleaks detect"
