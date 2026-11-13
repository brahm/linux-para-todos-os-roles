#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita desktop/ambiente-leve (Ambiente gráfico leve).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-ambiente.sh
source ./comum-ambiente.sh
exigir_apt

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
na_tela_de_login() { [ -f "/usr/share/xsessions/$(sessao).desktop" ]; }
tem_servidor_grafico() { command -v Xorg; }
for p in $(pacotes_do_ambiente); do
    conferir "pacote $p instalado" pacote_instalado "$p"
done
conferir "o $(nome_do_ambiente) aparece na tela de login (/usr/share/xsessions/$(sessao).desktop)" na_tela_de_login
conferir "o programa que abre a sessão existe ($(programa_da_sessao))" command -v "$(programa_da_sessao)"
conferir "servidor gráfico instalado (Xorg)" tem_servidor_grafico
if [ "${BORA_ENTRAR_NO_LEVE:-nao}" = sim ]; then
    for u in $(pessoas); do
        e_padrao() { [ "$(sessao_de "$1")" = "$(sessao)" ]; }
        conferir "$u entra no $(nome_do_ambiente) por padrão ($PASTA_CONTAS/$u)" e_padrao "$u"
    done
fi
resultado_dos_testes
