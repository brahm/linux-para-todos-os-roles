# Imagem para testar as receitas num contêiner. Não é uma máquina de verdade:
# não há systemd rodando nem partição própria, então o teste cria um disco
# virtual para os snapshots. Os pacotes abaixo existem em qualquer desktop
# Ubuntu ou Debian; sem eles, as receitas trariam dependências que um
# computador de verdade já tem. Uso: veja testes/conteiner/README.md.
ARG IMAGEM=ubuntu:26.04
FROM ${IMAGEM}
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -q \
 && apt-get install -y -q --no-install-recommends python3 systemd systemd-sysv dbus iproute2 e2fsprogs util-linux ca-certificates \
 && rm -rf /var/lib/apt/lists/*
ENV BORA_PERMITIR_SEM_SYSTEMD=1
WORKDIR /bora
