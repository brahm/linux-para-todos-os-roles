# shellcheck shell=bash
# As unidades do systemd desta receita. Usado por aplicar e verificar.

servico() {
    cat <<UNIT
[Unit]
Description=Backup da pasta pessoal num disco externo (bora)
Documentation=https://github.com/brahm/linux-para-todos-os-roles/tree/main/receitas/sistema/backup-pessoal

[Service]
Type=oneshot
ExecStart=$PROGRAMA
Nice=19
IOSchedulingClass=idle
UNIT
}

# Roda quando o disco é conectado: o systemd cria uma unidade .device para
# cada disco que aparece, e esta unidade é "querida" pela do disco do backup.
servico_ao_conectar() {
    cat <<UNIT
[Unit]
Description=Backup da pasta pessoal ao conectar o disco externo (bora)
Documentation=https://github.com/brahm/linux-para-todos-os-roles/tree/main/receitas/sistema/backup-pessoal

[Service]
Type=oneshot
ExecStart=$PROGRAMA --conectado
Nice=19
IOSchedulingClass=idle

[Install]
WantedBy=$1
UNIT
}

temporizador() {
    cat <<'UNIT'
[Unit]
Description=Confere de hora em hora se o backup da pasta pessoal venceu (bora)

[Timer]
OnBootSec=20min
OnCalendar=hourly
RandomizedDelaySec=10min
Persistent=true

[Install]
WantedBy=timers.target
UNIT
}
