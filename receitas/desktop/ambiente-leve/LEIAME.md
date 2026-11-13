# Ambiente gráfico leve

## O que faz

Instala um ambiente gráfico leve, o Xfce ou o LXQt, ao lado do que o computador já tem. Na tela de login, você escolhe qual usar. Com `entrar_no_leve: sim`, o leve passa a abrir por padrão.

## Por que

O GNOME, do Ubuntu e do Debian, e o KDE Plasma são bonitos e completos, mas pedem uma placa de vídeo com aceleração e uns 1,5 GB de memória só para a área de trabalho. Numa máquina de dez anos, com 2 ou 4 GB, sobra pouco para o navegador, que é justamente o que você queria abrir.

O Xfce e o LXQt gastam de 400 a 600 MB, desenham as janelas sem efeitos e funcionam bem com placas de vídeo antigas. O Xfce é o mais completo, com o jeito de sempre: menu, barra de tarefas e área de trabalho com ícones. O LXQt é ainda mais leve, para quem tem 2 GB ou menos.

O ambiente novo fica ao lado do antigo para você testar sem perder nada: os seus arquivos, programas e configurações continuam os mesmos, só a área de trabalho muda.

## O que muda no sistema

- Com `ambiente: xfce` (o padrão), instala `xfce4`, `xfce4-terminal`, `xfce4-notifyd`, `xfce4-power-manager`, `xfce4-screensaver`, `mate-polkit` e `tango-icon-theme`.
- Com `ambiente: lxqt`, instala `lxqt-core`, `qterminal`, `openbox`, `lxqt-powermanagement`, `pavucontrol-qt` e `xscreensaver`.
- Nos dois, instala o `xserver-xorg` se o computador ainda não tiver o Xorg (os desktops novos usam Wayland e podem vir sem ele) e, com o NetworkManager, o `network-manager-applet` (`network-manager-gnome` no Ubuntu 24.04), para escolher a rede Wi-Fi.
- Instala sem os pacotes recomendados (`--no-install-recommends`). Assim não vem junto outra tela de login, que mudaria o jeito de entrar no computador, nem jogos e programas que você não pediu.
- Com `entrar_no_leve: sim`, grava `Session` e `XSession` em `/var/lib/AccountsService/users/<pessoa>`, para cada pessoa do computador. É daí que o GDM e o LightDM tiram a sessão que abre por padrão. O SDDM, do KDE, guarda a última sessão escolhida por conta própria: nele, escolha o ambiente uma vez na tela de login.

## Como conferir

O `testar.sh` confere:

- que cada pacote do ambiente está instalado;
- que existe `/usr/share/xsessions/xfce.desktop` (ou `lxqt.desktop`), o arquivo que põe o ambiente na tela de login;
- que o programa que abre a sessão existe: `startxfce4` ou `startlxqt`;
- que o Xorg está instalado;
- com `entrar_no_leve: sim`, que a sessão de cada pessoa ficou gravada no AccountsService.

Para ver você mesmo: saia da sessão, e na tela de login procure a escolha de sessão (no GNOME, é a engrenagem no canto, depois de clicar no seu nome).

## Como desfazer

O `desfazer.sh` volta os arquivos do AccountsService ao que eram e remove os pacotes que a receita instalou, com as dependências que vieram junto. Se alguém estiver usando o ambiente leve na hora, ele para e pede para sair dessa sessão primeiro, para não derrubá-la. O ambiente antigo nunca saiu do computador.

## Fontes

- [Xfce, na wiki do Debian](https://wiki.debian.org/Xfce)
- [LXQt, na wiki do Debian](https://wiki.debian.org/LXQt)
- [Xfce: documentação](https://docs.xfce.org/)
- [AccountsService: a sessão de cada pessoa](https://www.freedesktop.org/wiki/Software/AccountsService/)
