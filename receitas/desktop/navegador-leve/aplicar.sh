#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita desktop/navegador-leve (Navegador enxuto).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-navegador.sh
source ./comum-navegador.sh

if [ -f "$POLITICAS" ] && ! python3 -c 'import json, sys; json.load(open(sys.argv[1]))' "$POLITICAS" 2>/dev/null; then
    falha "$POLITICAS existe, mas não é um JSON válido; o Firefox também não consegue ler. Conserte ou apague o arquivo e rode de novo"
fi
atual=/dev/null
if [ -f "$POLITICAS" ]; then atual=$POLITICAS; fi
novo=$(juntar_politicas <"$atual")
# As pastas que a receita criar saem no desfazer.
for d in /etc/firefox /etc/firefox/policies; do
    if [ ! -d "$d" ]; then echo "$d" >>"$BORA_ESTADO/pastas-novas"; fi
done
printf '%s\n' "$novo" | escrever_arquivo "$POLITICAS"

if ! firefox_instalado; then
    aviso "o Firefox não está instalado; as configurações passam a valer quando ele for instalado"
elif flatpak info org.mozilla.firefox >/dev/null 2>&1; then
    aviso "o Firefox do Flatpak não lê $POLITICAS; as configurações valem para o Firefox da distro"
fi
msg "Pronto. Feche e abra o Firefox para valer.$([ "${BORA_BLOQUEAR_ANUNCIOS:-sim}" = sim ] && echo ' O uBlock Origin é baixado da loja de extensões da Mozilla na primeira vez que ele abrir.')"
