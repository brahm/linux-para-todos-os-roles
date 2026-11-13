# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita sistema/servicos-enxutos.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.
#
# Cada serviço só é desligado quando o computador não tem o que ele serve.
# A receita usa "systemctl disable", e não "mask": o serviço continua
# instalado, e volta com um "systemctl enable --now" se um dia fizer falta.

# A máquina não tem nenhum adaptador Bluetooth?
sem_bluetooth() { [ -z "$(ls -A /sys/class/bluetooth 2>/dev/null)" ]; }

# Modem de celular (3G, 4G, 5G): aparece como interface ww* ou como /dev/cdc-wdm*.
sem_modem() {
    ! compgen -G '/sys/class/net/ww*' >/dev/null && ! compgen -G '/dev/cdc-wdm*' >/dev/null
}

# Pastas da rede no fstab (NFS, Samba) precisam que o boot espere a rede.
sem_pastas_de_rede() {
    ! grep -q . <<<"$(awk '$1 !~ /^#/ && ($3 ~ /^(nfs|nfs4|cifs|smb3|sshfs|fuse\.sshfs|glusterfs|ceph)$/ || $4 ~ /_netdev/)' /etc/fstab 2>/dev/null)"
}

# Lista "serviço|motivo" do que a receita desliga nesta máquina.
candidatos() {
    if sem_bluetooth; then echo "bluetooth.service|este computador não tem Bluetooth"; fi
    if sem_modem; then echo "ModemManager.service|este computador não tem modem de celular"; fi
    if [ "${BORA_ESPERAR_REDE:-nao}" = nao ] && sem_pastas_de_rede; then
        echo "NetworkManager-wait-online.service|o boot não precisa esperar a rede conectar"
    fi
}

# Estado de uma unidade: enabled, disabled, static, masked... ou vazio se não existe.
estado_de() {
    [ -n "$(systemctl list-unit-files --no-legend "$1" 2>/dev/null)" ] || return 0
    systemctl is-enabled "$1" 2>/dev/null || true
}

# Os candidatos que estão ligados agora, e por isso a receita desliga.
para_desligar() {
    local linha unidade
    while IFS= read -r linha; do
        unidade=${linha%%|*}
        if [ "$(estado_de "$unidade")" = enabled ]; then echo "$linha"; fi
    done < <(candidatos)
}
