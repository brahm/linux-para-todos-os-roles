#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita sistema/zram (Memória comprimida (zram)).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
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

if systemd_rodando && ! modulo_do_zram; then
    mapfile -t extras < <(pacotes_do_modulo)
    [ "${#extras[@]}" -gt 0 ] || falha "o kernel deste computador ($(uname -r)) não traz o módulo do zram, e não achei um pacote que traga"
    msg "O kernel deste computador não traz o módulo do zram. Ele vem nos módulos extras do kernel."
    instalar_pacotes "${extras[@]}"
fi
instalar_pacotes systemd-zram-generator
conf_esperada | escrever_arquivo "$CONF_ZRAM"

# Guarda os valores de agora, para o desfazer voltar sem reiniciar.
if [ ! -f "$BORA_ESTADO/sysctl-antes" ]; then
    for a in "${AJUSTES[@]}"; do
        chave=${a%%=*}
        printf '%s=%s\n' "$chave" "$(sysctl -n "$chave" 2>/dev/null || echo)" >>"$BORA_ESTADO/sysctl-antes"
    done
fi
sysctl_esperado | escrever_arquivo "$CONF_SYSCTL"

if systemd_rodando; then
    msg "Ligando o zram."
    # O pacote só carrega o módulo no boot (por /usr/lib/modules-load.d). Sem
    # carregar agora, o /dev/zram0 não aparece e o systemd desiste depois de
    # 90 segundos, como a VM do CI mostrou no Ubuntu 24.04.
    modprobe zram
    systemctl daemon-reload
    # Se já havia um zram desta receita com outro tamanho, ele é refeito.
    systemctl stop dev-zram0.swap 2>/dev/null || true
    systemctl restart systemd-zram-setup@zram0.service
    systemctl start dev-zram0.swap
    sysctl -q -p "$CONF_SYSCTL"
    zramctl /dev/zram0 || true
else
    msg "Sem systemd rodando, o zram liga no próximo boot."
fi
if awk 'NR > 1 && $1 !~ /^\/dev\/zram/ { achou = 1 } END { exit !achou }' /proc/swaps 2>/dev/null; then
    msg "A swap no disco continua lá, como reserva: o kernel só usa ela quando o zram enche."
fi
