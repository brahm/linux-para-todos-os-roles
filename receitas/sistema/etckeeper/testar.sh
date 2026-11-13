#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita sistema/etckeeper (Histórico do /etc).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-etckeeper.sh
source ./comum-etckeeper.sh
exigir_apt

# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
so_o_root() { [ "$(stat -c %a /etc/.git)" = 700 ]; }
permissoes_guardadas() { [ -f /etc/.etckeeper ]; }

conferir "etckeeper instalado" pacote_instalado etckeeper
conferir "o /etc tem um histórico com pelo menos um registro (git -C /etc log)" etc_versionado
conferir "o apt registra cada instalação no histórico (/etc/apt/apt.conf.d/05etckeeper)" gancho_do_apt
conferir "só o root lê o histórico (/etc/.git com permissão 700)" so_o_root
conferir "dono e permissões de cada arquivo guardados à parte (/etc/.etckeeper)" permissoes_guardadas
resultado_dos_testes
