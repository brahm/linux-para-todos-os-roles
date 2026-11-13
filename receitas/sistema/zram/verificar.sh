#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita sistema/zram (Memória comprimida (zram)).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-zram.sh
source ./comum-zram.sh
exigir_apt
porcentagem >/dev/null

if quem=$(outro_zram); then
    msg "Este computador já tem zram, configurado por $quem. A receita não mexe nele."
    exit 0
fi
if ! pacote_instalado systemd-zram-generator; then
    msg "O zram não está configurado."
    exit 1
fi
if [ "$(cat "$CONF_ZRAM" 2>/dev/null)" != "$(conf_esperada)" ]; then
    msg "A configuração do zram é diferente da pedida."
    exit 1
fi
if [ "$(cat "$CONF_SYSCTL" 2>/dev/null)" != "$(sysctl_esperado)" ]; then
    msg "Faltam os ajustes do kernel para o zram."
    exit 1
fi
if systemd_rodando && ! zram_ligado; then
    msg "O zram está configurado, mas não está ligado."
    exit 1
fi
msg "O zram está ligado."
exit 0
