# Histórico do /etc

## O que faz

Instala o etckeeper, que guarda a pasta `/etc`, onde fica a configuração do sistema, num repositório do Git. Cada instalação pelo apt e cada dia ganham um registro, e qualquer arquivo de configuração pode ser comparado com o de ontem ou voltado a uma versão antiga.

## Por que

O snapshot volta o sistema inteiro a como estava; o histórico do `/etc` responde a uma pergunta menor e mais comum: "o que mudou na configuração desde que o Wi-Fi parou?". Com ele, dá para ver a diferença de um arquivo, saber que pacote mexeu nele e voltar só aquele arquivo, sem desfazer o resto.

É também um jeito de aprender: `git -C /etc log -p` mostra, linha por linha, o que cada programa e cada receita do `bora` mudou na configuração.

## O que muda no sistema

- Instala o pacote `etckeeper`, que traz o `git` se ele não estiver instalado.
- O pacote cria o repositório em `/etc/.git` e faz o primeiro registro. Se alguma coisa mudou antes disso, a receita faz um registro próprio.
- O apt passa a avisar o etckeeper antes e depois de cada instalação (`/etc/apt/apt.conf.d/05etckeeper`), e o timer `etckeeper.timer` registra o que mudou por fora do apt uma vez por dia.
- O dono e as permissões de cada arquivo ficam guardados em `/etc/.etckeeper`, porque o Git não guarda isso sozinho.
- A pasta `/etc/.git` fica com permissão 700: só o root lê, porque o `/etc` tem arquivos como o `shadow`, com as senhas cifradas.
- Se o `/etc` já tinha um histórico do Git, a receita usa o que existe. Se o histórico for de outro programa, como Mercurial, ela para sem mudar nada.

## Como conferir

O `testar.sh` confere:

- que o pacote `etckeeper` está instalado;
- `git -C /etc rev-parse HEAD`: o histórico tem pelo menos um registro;
- que existe `/etc/apt/apt.conf.d/05etckeeper`, o gancho do apt;
- que `/etc/.git` tem permissão 700;
- que existe `/etc/.etckeeper`, com o dono e as permissões dos arquivos.

Para ver você mesmo:

- `sudo git -C /etc log --oneline`: a lista de registros;
- `sudo git -C /etc log -p -- ssh/sshd_config`: o histórico de um arquivo;
- `sudo git -C /etc diff`: o que mudou desde o último registro;
- `sudo git -C /etc checkout <registro> -- arquivo` e `sudo etckeeper init`: volta um arquivo e reaplica as permissões.

## Como desfazer

O `desfazer.sh` guarda uma cópia do histórico em `/var/backups/bora-etc-historico-<data>.tar.gz`, com permissão só do root, remove o repositório com `etckeeper uninit` e tira o pacote `etckeeper` e o que veio junto. Os arquivos do `/etc` ficam como estão.

Se o `/etc` já tinha um histórico antes do `bora`, o desfazer não mexe nele.

## Fontes

- [etckeeper](https://etckeeper.branchable.com/)
- [etckeeper, no Debian](https://packages.debian.org/stable/etckeeper)
- [etckeeper, na ArchWiki](https://wiki.archlinux.org/title/Etckeeper)
