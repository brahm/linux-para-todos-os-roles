#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita seguranca/firewall (Firewall).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=regras.sh
source ./regras.sh

conferir "ufw instalado" command -v ufw
conferir "firewall ligado (ufw status)" ufw_ativo
conferir "bloqueia o que chega e libera o que sai (ufw status verbose)" padroes_certos
rede=$(descobrir_rede_local)
while read -r regra; do
    [ -n "$regra" ] || continue
    conferir "regra presente: $regra" regra_existe "$regra"
done < <(regras_do_perfil "$rede")
if command -v systemctl >/dev/null; then
    conferir "o firewall liga sozinho no boot (ufw.service)" systemctl is-enabled --quiet ufw.service
fi
resultado_dos_testes
