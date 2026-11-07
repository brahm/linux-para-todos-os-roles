#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-etckeeper.sh
source ./comum-etckeeper.sh
exigir_apt

# Um /etc que já tinha histórico (de outro VCS ou feito à mão) não é tocado
# no desfazer.
if [ ! -f "$BORA_ESTADO/etc-git-antes" ]; then
    if [ -e /etc/.git ] || [ -e /etc/.hg ] || [ -e /etc/.bzr ] || [ -e /etc/_darcs ]; then
        echo sim >"$BORA_ESTADO/etc-git-antes"
    else
        echo nao >"$BORA_ESTADO/etc-git-antes"
    fi
fi
if [ -e /etc/.hg ] || [ -e /etc/.bzr ] || [ -e /etc/_darcs ]; then
    falha "o /etc já tem um histórico de outro programa (Mercurial, Bazaar ou Darcs); a receita não mistura os dois"
fi

# O pacote do Debian e do Ubuntu já cria o histórico e o primeiro registro
# na instalação, e liga o registro diário pelo timer do systemd.
instalar_pacotes etckeeper

if ! etc_versionado; then
    msg "Criando o histórico do /etc."
    etckeeper init
    etckeeper commit "Primeiro registro do /etc, feito pelo bora" >/dev/null
fi
# O que mudou entre a instalação e agora (inclusive o que as receitas
# anteriores do plano fizeram) entra num registro próprio.
if etckeeper unclean 2>/dev/null; then
    etckeeper commit "Mudanças de antes do etckeeper, registradas pelo bora" >/dev/null
fi
chmod 700 /etc/.git
msg "Pronto. Para ver o histórico: sudo git -C /etc log --oneline"
