#!/usr/bin/env bash
set -euo pipefail
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
