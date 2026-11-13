# Sistema atualizado

## O que faz

Atualiza a lista de pacotes e os programas instalados, e liga as atualizações automáticas de segurança, que passam a ser instaladas sozinhas todo dia.

## Por que

A maioria dos problemas de segurança é corrigida por atualizações que já existem, mas que ainda não foram instaladas. Um computador recém-instalado também costuma estar semanas atrás, porque a imagem de instalação foi gerada antes. Atualizar primeiro evita caçar um bug que alguém já consertou.

As atualizações automáticas instalam só o que vem dos repositórios de segurança da distro. Elas não trocam a versão da distro e não instalam programas novos.

## O que muda no sistema

- Roda `apt-get update` e `apt-get upgrade --with-new-pkgs`. Esse modo instala dependências novas, como um kernel novo, mas nunca remove pacotes. Remoções ficam para você decidir.
- Se um pacote ficou pela metade numa instalação anterior, roda `dpkg --configure -a` antes.
- Com `automaticas: sim` (o padrão):
  - instala o `unattended-upgrades`, se ainda não estiver instalado;
  - escreve `/etc/apt/apt.conf.d/20auto-upgrades` com `APT::Periodic::Update-Package-Lists "1"` e `APT::Periodic::Unattended-Upgrade "1"`, se essas opções ainda não estiverem ligadas;
  - habilita os timers `apt-daily.timer` e `apt-daily-upgrade.timer` do systemd, se estiverem desabilitados. Se algum estiver mascarado, a receita só avisa.
- O Ubuntu já vem com quase tudo isso ligado. Nesse caso, a receita só atualiza os pacotes.

## Como conferir

O `testar.sh` roda:

- `dpkg --audit`: não pode mostrar nenhum pacote instalado pela metade;
- `apt-get -s upgrade --with-new-pkgs`: simula a atualização e não pode sobrar nenhum pacote. Pacotes retidos de propósito pela distro, como as atualizações em fases do Ubuntu, não contam;
- `dpkg-query -W unattended-upgrades`: o pacote precisa estar instalado;
- `apt-config dump`: as duas opções `APT::Periodic` precisam valer `"1"`.

Se aparecer o arquivo `/var/run/reboot-required`, reinicie quando puder para começar a usar o kernel novo.

## Como desfazer

O `desfazer.sh` volta o `20auto-upgrades` ao que era, desabilita os timers que a receita habilitou e remove o `unattended-upgrades` e as dependências dele, se tiverem sido instalados pela receita.

As atualizações de pacotes não são desfeitas, porque o apt não volta versões. Se uma atualização trouxe algum problema, use o snapshot do sistema criado antes do plano.

## Fontes

- [Atualizações automáticas, na documentação do Ubuntu Server](https://documentation.ubuntu.com/server/how-to/software/automatic-updates/)
- [UnattendedUpgrades, na wiki do Debian](https://wiki.debian.org/UnattendedUpgrades)
- [Manual do apt-get](https://manpages.debian.org/trixie/apt/apt-get.8.en.html), opção `--with-new-pkgs`
