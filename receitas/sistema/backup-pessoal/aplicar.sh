#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita sistema/backup-pessoal (Backup da pasta pessoal).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-backup.sh
source ./comum-backup.sh
# shellcheck source=unidades.sh
source ./unidades.sh
exigir_apt

read -r dev uuid tipo < <(descobrir_destino)
usuarios=$(descobrir_usuarios)
if [ "$dev" = - ]; then
    msg "O disco do backup (UUID $uuid) não está conectado agora; a configuração continua valendo para ele."
else
    msg "As cópias vão para $dev ($tipo, UUID $uuid)."
fi
msg "Pastas pessoais copiadas: $usuarios"

instalar_pacotes rsync

config_esperada "$uuid" "$usuarios" | escrever_arquivo "$CONFIG" 0644
escrever_arquivo "$PROGRAMA" 0755 <./backup-pessoal.sh
servico | escrever_arquivo "/etc/systemd/system/$UNIDADE.service"
temporizador | escrever_arquivo "/etc/systemd/system/$UNIDADE.timer"
disco=$(unidade_do_disco "$uuid")
servico_ao_conectar "$disco" | escrever_arquivo "/etc/systemd/system/$UNIDADE-conectar.service"
if systemd_rodando; then
    systemctl daemon-reload
fi
habilitar_unidade "$UNIDADE.timer"
# Só habilita: quem dispara é o disco, ao ser conectado.
if ! systemctl is-enabled --quiet "$UNIDADE-conectar.service" 2>/dev/null; then
    systemctl enable "$UNIDADE-conectar.service" 2>&1 | sed '/^Created symlink/d; /non-existent unit/d'
    printf '%s\n' "$UNIDADE-conectar.service" >>"$BORA_ESTADO/unidades-habilitadas"
fi

if [ "${BORA_FAZER_AGORA:-sim}" = sim ]; then
    if [ "$dev" = - ]; then
        aviso "a primeira cópia acontece quando você conectar o disco"
    elif "$PROGRAMA" --conferir >/dev/null 2>&1; then
        msg "Cada pessoa já tem uma cópia no disco."
    else
        msg "Fazendo a primeira cópia. Ela copia tudo e pode demorar; as próximas copiam só o que mudou."
        "$PROGRAMA" --agora
    fi
fi
msg "Pronto. O backup roda uma vez por dia, quando o disco estiver conectado, e também logo que você conectar o disco."
