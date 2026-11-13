#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita containers/podman (Contêineres com Podman).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-podman.sh
source ./comum-podman.sh

# shellcheck disable=SC2086
instalar_pacotes $PACOTES
registros_esperado | escrever_arquivo "$REGISTROS"

# Os contêineres sem root mapeiam os usuários de dentro para uma faixa de IDs
# da pessoa. O adduser do Ubuntu e do Debian já cria a faixa para contas
# novas; contas antigas, ou criadas de outro jeito, podem não ter.
if ! tem_faixa subuid || ! tem_faixa subgid; then
    inicio=$(proxima_faixa)
    fim=$((inicio + FAIXA - 1))
    opcoes=()
    if ! tem_faixa subuid; then opcoes+=(--add-subuids "$inicio-$fim"); fi
    if ! tem_faixa subgid; then opcoes+=(--add-subgids "$inicio-$fim"); fi
    guardar_arquivo /etc/subuid
    guardar_arquivo /etc/subgid
    usermod "${opcoes[@]}" "$PESSOA"
    msg "Faixa de IDs para os contêineres de $PESSOA: $inicio a $fim"
fi
msg "Pronto: $(podman --version). Para testar: podman run --rm hello-world"
