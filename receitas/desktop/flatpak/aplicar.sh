#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita desktop/flatpak (Flatpak e Flathub).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-flatpak.sh
source ./comum-flatpak.sh
exigir_apt

# shellcheck disable=SC2046
instalar_pacotes flatpak $(plugins_da_loja)

if flathub_ligado; then
    msg "O Flathub já estava configurado."
elif flatpak remotes --system --show-disabled --columns=name 2>/dev/null | grep -qx flathub; then
    # Já existe um "flathub", mas desativado ou com outro endereço. A receita
    # não mexe nele, porque alguém configurou assim de propósito.
    falha "já existe um repositório flathub com outra configuração; confira com: flatpak remotes --show-details"
else
    msg "Ligando o Flathub."
    # O --if-not-exists evita erro se outro programa criar o remoto ao mesmo tempo.
    flatpak remote-add --system --if-not-exists flathub "$FLATHUB_ARQUIVO"
    echo flathub >"$BORA_ESTADO/remoto-criado"
fi
msg "Pronto. Os atalhos dos aplicativos do Flathub aparecem no menu depois que você sair e entrar de novo na sessão."
