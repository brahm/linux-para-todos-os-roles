#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-ambiente.sh
source ./comum-ambiente.sh
exigir_apt

# Sem recomendados: o apt traria junto outra tela de login, que mudaria o
# jeito de entrar no computador, além de jogos e programas que pesam.
# shellcheck disable=SC2046
instalar_pacotes --sem-recomendados $(pacotes_do_ambiente)

if [ "${BORA_ENTRAR_NO_LEVE:-nao}" = sim ]; then
    mkdir -p "$PASTA_CONTAS"
    for u in $(pessoas); do
        if [ "$(sessao_de "$u")" != "$(sessao)" ]; then
            definir_sessao "$u" "$(sessao)"
            msg "$u passa a entrar no $(nome_do_ambiente) por padrão."
        fi
    done
fi

if [ ! -e /etc/systemd/system/display-manager.service ]; then
    aviso "este computador não tem tela de login gráfica; para abrir o $(nome_do_ambiente), entre no terminal e rode $(programa_da_sessao)"
elif [ "${BORA_ENTRAR_NO_LEVE:-nao}" = sim ]; then
    msg "Pronto. Na próxima vez que você entrar, o $(nome_do_ambiente) abre direto. O ambiente antigo continua na tela de login."
else
    msg "Pronto. Na tela de login, escolha $(nome_do_ambiente) antes de digitar a senha (no GNOME, pelo ícone de engrenagem)."
fi
