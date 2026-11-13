# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita desktop/flatpak.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

FLATHUB_URL=https://dl.flathub.org/repo/
FLATHUB_ARQUIVO=https://dl.flathub.org/repo/flathub.flatpakrepo

# O Flathub está configurado para o sistema todo, apontando para o endereço oficial?
flathub_ligado() {
    command -v flatpak >/dev/null || return 1
    flatpak remotes --system --columns=name,url 2>/dev/null |
        awk -v url="$FLATHUB_URL" '$1 == "flathub" && $2 == url {achou = 1} END {exit !achou}'
}

# O Flathub está desativado (existe, mas com a opção disabled)?
flathub_desativado() {
    flatpak remotes --system --show-disabled --columns=name,options 2>/dev/null |
        awk '$1 == "flathub" && /disabled/ {achou = 1} END {exit !achou}'
}

# Os plugins que fazem a loja instalada mostrar os aplicativos do Flatpak.
plugins_da_loja() {
    [ "${BORA_INTEGRAR_LOJA:-sim}" = sim ] || return 0
    if pacote_instalado gnome-software; then echo gnome-software-plugin-flatpak; fi
    if pacote_instalado plasma-discover; then echo plasma-discover-backend-flatpak; fi
}
