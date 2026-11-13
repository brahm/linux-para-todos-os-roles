#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita sistema/backup-pessoal (Backup da pasta pessoal).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-backup.sh
source ./comum-backup.sh
exigir_apt

read -r dev uuid _ < <(descobrir_destino)
# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
programa_certo() { cmp -s ./backup-pessoal.sh "$PROGRAMA"; }
config_certa() { cmp -s <(config_esperada "$uuid" "$(descobrir_usuarios)") "$CONFIG"; }

conferir "rsync instalado" command -v rsync
conferir "programa do backup instalado ($PROGRAMA)" programa_certo
conferir "configuração aponta para o disco certo (UUID $uuid)" config_certa
conferir "agendamento diário ligado ($UNIDADE.timer)" systemctl is-enabled --quiet "$UNIDADE.timer"
conferir "backup ao conectar o disco ligado ($UNIDADE-conectar.service)" systemctl is-enabled --quiet "$UNIDADE-conectar.service"
if [ "$dev" = - ]; then
    msg "O disco não está conectado, então a cópia em si não foi conferida."
elif [ "${BORA_FAZER_AGORA:-sim}" = sim ]; then
    "$PROGRAMA" --conferir || _FALHAS=$((_FALHAS + 1))
fi
resultado_dos_testes
