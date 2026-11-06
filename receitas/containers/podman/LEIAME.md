# Contêineres com Podman

## O que faz

Instala o Podman, que roda contêineres na conta da pessoa, sem permissão de administrador, e faz as imagens com nome curto, como `python` ou `nginx`, virem do Docker Hub, como no Docker.

## Por que

Um contêiner é um programa rodando com o seu próprio sistema de arquivos, separado do resto do computador. É como os tutoriais sobem um banco de dados, testam um projeto numa versão específica do Python ou rodam um serviço sem instalar nada no sistema: `podman run --rm -it python:3.13` e pronto.

O Podman aceita os mesmos comandos do Docker na maioria dos casos (`run`, `ps`, `images`, `build`), com uma diferença importante: ele não tem um serviço rodando como root por trás. Cada pessoa roda os próprios contêineres, e um contêiner com problema não ganha acesso de administrador à máquina. No Docker, quem está no grupo `docker` tem, na prática, o mesmo poder do root.

Para os contêineres sem root funcionarem, a conta precisa de uma faixa de IDs de usuário, em `/etc/subuid` e `/etc/subgid`: o root de dentro do contêiner vira um desses IDs do lado de fora, sem poder nenhum no sistema. O `adduser` do Ubuntu e do Debian já cria essa faixa para contas novas; a receita cria para contas que não têm.

Por padrão, o Podman do Ubuntu não sabe onde procurar uma imagem chamada só `python`, e o comando falha. A receita diz para ele procurar no Docker Hub, que é onde os tutoriais esperam.

## O que muda no sistema

- Instala os pacotes `podman` e `uidmap`, com os recomendados.
- Cria `/etc/containers/registries.conf.d/50-bora-docker-hub.conf`, com `unqualified-search-registries = ["docker.io"]`.
- Se a conta de quem rodou o `bora` não tiver uma faixa de IDs, acrescenta uma de 65536 IDs, depois das que já existem, em `/etc/subuid` e `/etc/subgid`, com `usermod --add-subuids` e `--add-subgids`.

Nenhum serviço fica rodando. As imagens e os contêineres ficam em `~/.local/share/containers`, na pasta pessoal.

## Como conferir

O `testar.sh` roda:

- `podman --version`;
- a faixa de IDs da pessoa em `/etc/subuid` e `/etc/subgid`, e que o `newuidmap` tem a permissão para usá-la;
- `podman info`, como a pessoa, que precisa dizer `rootless: true`;
- que o Docker Hub está na lista de registros.

O teste não baixa imagem nenhuma. Para ver um contêiner de verdade: `podman run --rm hello-world`.

## Como desfazer

O `desfazer.sh` apaga a configuração dos registros, volta `/etc/subuid` e `/etc/subgid` ao que eram e remove os pacotes que a receita instalou.

As imagens e os contêineres ficam em `~/.local/share/containers`, porque são seus. Para apagar tudo, rode `podman system reset` antes de desfazer, ou apague essa pasta depois.

## Fontes

- [Podman sem root (tutorial oficial)](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)
- [registries.conf(5): unqualified-search-registries](https://github.com/containers/image/blob/main/docs/containers-registries.conf.5.md)
- [subuid(5)](https://man7.org/linux/man-pages/man5/subuid.5.html)
- [Podman, na wiki do Debian](https://wiki.debian.org/Podman)
