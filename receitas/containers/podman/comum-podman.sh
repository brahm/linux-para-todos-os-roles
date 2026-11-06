# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

# uidmap traz o newuidmap e o newgidmap, que os contêineres sem root usam.
PACOTES="podman uidmap"
# Com um registro só na lista, "podman run python" acha docker.io/library/python
# sem perguntar em qual registro procurar, como no Docker.
REGISTROS=/etc/containers/registries.conf.d/50-bora-docker-hub.conf
FAIXA=65536

PESSOA=$(descobrir_pessoa "${BORA_USUARIO:-auto}")

registros_esperado() {
    cat <<'CONF'
# Configurado pelo bora (receita containers/podman): imagens com nome curto,
# como "python" ou "nginx", vêm do Docker Hub, como no Docker.
unqualified-search-registries = ["docker.io"]
CONF
}

# A pessoa tem uma faixa de IDs para os usuários de dentro dos contêineres?
tem_faixa() { grep -q "^$PESSOA:" "/etc/$1" 2>/dev/null; }

# O começo da primeira faixa livre, depois de todas as que já existem.
proxima_faixa() {
    cat /etc/subuid /etc/subgid 2>/dev/null |
        awk -F: -v min=100000 '{fim = $2 + $3; if (fim > min) min = fim} END {print min}'
}
