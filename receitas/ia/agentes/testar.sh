#!/usr/bin/env bash
set -euo pipefail
# testar.sh da receita ia/agentes (Agentes de IA no terminal).
# Roda logo depois do aplicar e confere que a mudança funciona de verdade.
# Cada `conferir` é um teste; `resultado_dos_testes` sai com erro se algum falhou.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-agentes.sh
source ./comum-agentes.sh

# Sem conta nem chave, o teste não conversa com o agente: confere que o
# comando abre e responde a versão, como a pessoa, sem sudo.
responde() { [ -n "$(na_sessao "$1" --version 2>/dev/null)" ]; }
# Ajudantes das conferências abaixo. Cada `conferir "descrição" função` diz,
# em português, o que a função testa. Elas só leem o sistema ou usam pastas temporárias.
da_pessoa() { [ "$(stat -c %U "$(na_sessao sh -c "command -v '$1'")")" = "$PESSOA" ] || [ "$(stat -c %U "$(readlink -f "$(na_sessao sh -c "command -v '$1'")")")" = "$PESSOA" ]; }

for a in $(escolhidos); do
    c=$(comando_do_agente "$a")
    conferir "$a responde ($c --version)" responde "$c"
    conferir "$a está na conta de $PESSOA, sem sudo" da_pessoa "$c"
done
for s in $SKILLS; do
    conferir "a skill do bora está em $s" test -f "$s/SKILL.md"
done
resultado_dos_testes
