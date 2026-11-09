#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-agentes.sh
source ./comum-agentes.sh

echo "$PESSOA" >"$BORA_ESTADO/pessoa"

for a in $(escolhidos); do
    if agente_instalado "$a"; then
        msg "O agente $a já está instalado ($(na_sessao sh -c "command -v '$(comando_do_agente "$a")'")); a receita não mexe nele."
        continue
    fi
    IFS='|' read -r _ comando origem pacote <<<"$(dados_do_agente "$a")"
    case $origem in
        npm)
            exigir_npm
            msg "Instalando $pacote, do npm, em $CASA/.local"
            na_sessao npm install -g --no-audit --no-fund --loglevel=error "$pacote" ||
                falha "o npm não conseguiu instalar $pacote; confira a internet e rode o bora de novo"
            ;;
        pipx)
            exigir_pipx
            msg "Instalando $pacote, do PyPI, com o pipx"
            na_sessao pipx install --quiet "$pacote" ||
                falha "o pipx não conseguiu instalar $pacote; confira a internet e rode o bora de novo"
            ;;
    esac
    printf '%s|%s|%s\n' "$a" "$origem" "$pacote" >>"$BORA_ESTADO/agentes-instalados"
    agente_instalado "$a" || falha "o $pacote foi instalado, mas o comando $comando não apareceu em $CASA/.local/bin"
    msg "Instalado: $a ($(na_sessao "$comando" --version 2>/dev/null | awk 'NR == 1')) "
done

# A skill do bora, para os agentes saberem montar um plano sem pedir sudo.
for s in $SKILLS; do
    skill_instalada "$s" && continue
    if [ -e "$s/SKILL.md" ]; then
        aviso "já existe $s/SKILL.md, que não é a do bora; ele fica"
        continue
    fi
    criar_pasta_da_pessoa "$PESSOA" "$s"
    como_pessoa "$PESSOA" tee "$s/SKILL.md" >/dev/null <./SKILL.md
    echo "$s/SKILL.md" >>"$BORA_ESTADO/skills"
    msg "Skill do bora instalada: $s/SKILL.md"
done

msg ""
msg "Para começar, abra um terminal novo, entre na pasta de um projeto e rode o agente pelo nome. Na primeira vez, ele pede para entrar na sua conta."
