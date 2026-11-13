#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita sistema/zram (Memória comprimida (zram)).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-zram.sh
source ./comum-zram.sh
exigir_apt

if quem=$(outro_zram); then
    msg "O zram é configurado por $quem; a receita não confere a configuração dele."
    if systemd_rodando; then
        conferir "zram ligado como swap (/proc/swaps)" grep -q '^/dev/zram' /proc/swaps
    fi
    resultado_dos_testes
fi

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
conf_certa() { [ "$(cat "$CONF_ZRAM")" = "$(conf_esperada)" ]; }
sysctl_certo() { [ "$(cat "$CONF_SYSCTL")" = "$(sysctl_esperado)" ]; }
gerador() { [ -x /usr/lib/systemd/system-generators/zram-generator ]; }
com_zstd() { grep -q '\[zstd\]' /sys/block/zram0/comp_algorithm; }
prioridade() { awk '$1 == "/dev/zram0" && $5 >= 100 {achou = 1} END {exit !achou}' /proc/swaps; }

conferir "gerador do zram instalado (systemd-zram-generator)" gerador
conferir "configuração do zram ($CONF_ZRAM)" conf_certa
conferir "ajustes do kernel para o zram ($CONF_SYSCTL)" sysctl_certo
if systemd_rodando; then
    conferir "o kernel tem o módulo do zram (modinfo zram)" modulo_do_zram
    conferir "zram ligado como swap (swapon --show)" zram_ligado
    conferir "o zram comprime com zstd (zramctl)" com_zstd
    conferir "o kernel usa o zram antes da swap no disco (prioridade 100)" prioridade
else
    msg "Sem systemd rodando, o zram só liga no boot; os testes de agora conferem a configuração."
fi
resultado_dos_testes
