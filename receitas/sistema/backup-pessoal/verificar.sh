#!/usr/bin/env bash
set -euo pipefail
# verificar.sh da receita sistema/backup-pessoal (Backup da pasta pessoal).
# Confere se a receita já está aplicada, sem mudar nada no sistema.
# Sai com 0 se já está, e com 1 se precisa aplicar (a mensagem diz o que falta).
# O bora roda este script antes de aplicar e no `bora aplicar --simular`.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-backup.sh
source ./comum-backup.sh
# shellcheck source=unidades.sh
source ./unidades.sh
exigir_apt

if ! pacote_instalado rsync; then
    msg "O rsync não está instalado."
    exit 1
fi
if [ ! -f "$CONFIG" ]; then
    msg "O backup da pasta pessoal não está configurado."
    exit 1
fi
read -r dev uuid _ < <(descobrir_destino)
usuarios=$(descobrir_usuarios)
if ! cmp -s <(config_esperada "$uuid" "$usuarios") "$CONFIG"; then
    msg "A configuração do backup é diferente da que o plano pede."
    exit 1
fi
if ! cmp -s ./backup-pessoal.sh "$PROGRAMA"; then
    msg "O programa do backup não está instalado ou é de outra versão."
    exit 1
fi
for u in "$UNIDADE.service" "$UNIDADE.timer" "$UNIDADE-conectar.service"; do
    if [ ! -f "/etc/systemd/system/$u" ]; then
        msg "Falta a unidade $u."
        exit 1
    fi
done
if ! cmp -s <(servico_ao_conectar "$(unidade_do_disco "$uuid")") "/etc/systemd/system/$UNIDADE-conectar.service"; then
    msg "A unidade que roda o backup ao conectar o disco aponta para outro disco."
    exit 1
fi
if ! systemctl is-enabled --quiet "$UNIDADE.timer" 2>/dev/null ||
    ! systemctl is-enabled --quiet "$UNIDADE-conectar.service" 2>/dev/null; then
    msg "O agendamento do backup não está ligado."
    exit 1
fi
if [ "${BORA_FAZER_AGORA:-sim}" = sim ] && [ "$dev" != - ] && ! "$PROGRAMA" --conferir >/dev/null 2>&1; then
    msg "O disco está conectado, mas ainda não há uma cópia completa."
    exit 1
fi
msg "O backup da pasta pessoal está configurado e agendado."
exit 0
