#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita desktop/ambiente-leve (Ambiente gráfico leve).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-ambiente.sh
source ./comum-ambiente.sh
exigir_apt

for p in $(pacotes_do_ambiente); do
    if ! pacote_instalado "$p"; then
        msg "O $(nome_do_ambiente) não está instalado (falta $p)."
        exit 1
    fi
done
if [ "${BORA_ENTRAR_NO_LEVE:-nao}" = sim ]; then
    for u in $(pessoas); do
        if [ "$(sessao_de "$u")" != "$(sessao)" ]; then
            msg "$u ainda não entra no $(nome_do_ambiente) por padrão."
            exit 1
        fi
    done
fi
msg "O $(nome_do_ambiente) está instalado."
exit 0
