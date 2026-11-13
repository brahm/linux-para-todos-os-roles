#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita servicos/samba (Pasta compartilhada com Samba).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-samba.sh
source ./comum-samba.sh
exigir_apt

pasta=$(pasta_da_receita)
exigir_pessoas
nome_do_compartilhamento >/dev/null

while read -r p; do
    if ! pacote_instalado "$p"; then
        msg "Falta instalar o pacote $p."
        exit 1
    fi
done < <(pacotes_da_receita)
if [ ! -d "$pasta" ]; then
    msg "A pasta $pasta ainda não existe."
    exit 1
fi
rede=$(descobrir_rede_local)
if [ -z "$rede" ] || ! include_presente || [ ! -f "$CONFIG" ] || ! cmp -s <(conteudo_config "$pasta" "$(dono_atual "$pasta")" "$rede") "$CONFIG"; then
    msg "A configuração do bora para o Samba ainda não está em $CONFIG."
    exit 1
fi
while read -r n; do
    if ! conta_existe "$n" || ! no_samba "$n"; then
        msg "$n ainda não tem acesso à pasta."
        exit 1
    fi
done < <(pessoas_da_pasta)
if ufw_ativo; then
    while read -r regra; do
        if ! regra_existe "$regra"; then
            msg "O firewall ainda não libera o Samba para a rede local."
            exit 1
        fi
    done < <(regras_ufw "$rede")
fi
msg "A pasta $pasta já está compartilhada, com a configuração do bora."
exit 0
