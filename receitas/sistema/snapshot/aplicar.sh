#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita sistema/snapshot (Snapshot do sistema).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-snapshot.sh
source ./comum-snapshot.sh
exigir_apt

read -r fonte uuid tipo modo < <(descobrir_destino)
msg "Os snapshots vão para $fonte ($tipo, modo $modo)."

if [ "$modo" = rsync ]; then
    livre_kb=$(df --output=avail -k "$(findmnt -n -f -o TARGET --source "$fonte" || echo /)" | tail -n1 | tr -d ' ')
    if [ -n "$livre_kb" ] && [ "$livre_kb" -lt $((ESPACO_MINIMO_GB * 1024 * 1024)) ]; then
        falha "há menos de $ESPACO_MINIMO_GB GB livres em $fonte; libere espaço ou escolha outro dispositivo"
    fi
fi

# Sem os recomendados: num desktop eles já estão lá, e num servidor trariam
# centenas de pacotes gráficos que o Timeshift não precisa para funcionar.
instalar_pacotes --sem-recomendados timeshift

guardar_arquivo "$CONFIG"
mkdir -p /etc/timeshift
novo=$(mktemp)
python3 - "$CONFIG" /etc/timeshift/default.json "$uuid" "$modo" "${BORA_DIARIOS:-5}" "${BORA_SEMANAIS:-3}" >"$novo" <<'PY'
import json, os, sys
caminho, padrao, uuid, modo, diarios, semanais = sys.argv[1:]
c = {}
for origem in (caminho, padrao):
    if os.path.exists(origem):
        try:
            c = json.load(open(origem))
            break
        except ValueError:
            pass
c.update({
    "backup_device_uuid": uuid,
    "parent_device_uuid": "",
    "do_first_run": "false",
    "btrfs_mode": "true" if modo == "btrfs" else "false",
    "include_btrfs_home": c.get("include_btrfs_home", "false"),
    "stop_cron_emails": "true",
    "schedule_monthly": "false",
    "schedule_weekly": "true",
    "schedule_daily": "true",
    "schedule_hourly": "false",
    "schedule_boot": "false",
    "count_weekly": semanais,
    "count_daily": diarios,
})
# O Timeshift guarda o sistema; as pastas pessoais ficam para o backup.
excluir = c.get("exclude") or []
for item in ("/root/**", "/home/*/**"):
    if item not in excluir:
        excluir.append(item)
c["exclude"] = excluir
c.setdefault("exclude-apps", [])
print(json.dumps(c, indent=2, ensure_ascii=False))
PY
escrever_arquivo "$CONFIG" 0644 <"$novo"
rm -f "$novo"

# O Timeshift agenda pelo cron quando é configurado pelo aplicativo. Como a
# configuração aqui é feita direto no arquivo, o agendamento fica num timer
# do systemd, que roda "timeshift --check" e cria o snapshot quando ele vence.
escrever_arquivo "/etc/systemd/system/$UNIDADE.service" <<'UNIT'
[Unit]
Description=Snapshot agendado do sistema (Timeshift), configurado pelo bora
Documentation=https://github.com/brahm/linux-para-todos-os-roles/tree/main/receitas/sistema/snapshot
ConditionACPower=true

[Service]
Type=oneshot
ExecStart=/usr/bin/timeshift --check --scripted
Nice=19
IOSchedulingClass=idle
UNIT
escrever_arquivo "/etc/systemd/system/$UNIDADE.timer" <<'UNIT'
[Unit]
Description=Confere de hora em hora se um snapshot do sistema venceu (bora)

[Timer]
OnBootSec=15min
OnCalendar=hourly
RandomizedDelaySec=10min
Persistent=true

[Install]
WantedBy=timers.target
UNIT
if systemd_rodando; then
    systemctl daemon-reload
fi
habilitar_unidade "$UNIDADE.timer"

if [ "${BORA_CRIAR_AGORA:-sim}" = sim ] && [ -z "$(listar_snapshots)" ]; then
    msg "Criando o primeiro snapshot. Na primeira vez, o Timeshift copia o sistema inteiro e pode levar de 5 a 30 minutos."
    antes=$(listar_snapshots | sort)
    # Até a versão 26.11.0, o Timeshift às vezes cai com segfault logo no
    # começo, antes de copiar qualquer coisa (issue #16). A causa é uma corrida
    # entre duas threads dele, corrigida em linuxmint/timeshift#552. Enquanto as
    # distros trazem versões antigas, se nenhum snapshot apareceu, tenta mais uma vez.
    for tentativa in 1 2; do
        timeshift --create --scripted --comments "bora: primeiro snapshot" | tr '\r' '\n' | grep -v '% complete' || true
        [ -n "$(listar_snapshots)" ] && break
        if [ "$tentativa" = 1 ]; then aviso "o Timeshift não criou o snapshot na primeira tentativa; tentando de novo"; fi
    done
    comm -13 <(printf '%s\n' "$antes") <(listar_snapshots | sort) | sed '/^$/d' >>"$BORA_ESTADO/snapshots-criados"
    # O Timeshift sai com código 0 mesmo quando não acha o dispositivo.
    [ -s "$BORA_ESTADO/snapshots-criados" ] || falha "o Timeshift não conseguiu criar o snapshot"
fi
msg "Pronto. O Timeshift vai guardar ${BORA_DIARIOS:-5} snapshots diários e ${BORA_SEMANAIS:-3} semanais."
