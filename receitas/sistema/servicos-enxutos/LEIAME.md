# Serviços enxutos

## O que faz

Desliga os serviços que este computador não usa: o Bluetooth, se a máquina não tem Bluetooth, e o ModemManager, se ela não tem modem de celular. E faz o boot parar de esperar a rede conectar.

## Por que

Cada serviço ligado ocupa memória e acorda de tempos em tempos para conferir se o aparelho dele apareceu. Numa máquina nova, isso não se nota. Numa de 2 GB com disco rígido, cada coisa que sai do boot e da memória faz diferença.

A receita só desliga o que confere que a máquina não usa:

- `bluetooth.service`, se não houver nenhuma placa em `/sys/class/bluetooth`;
- `ModemManager.service`, se não houver modem de celular (3G, 4G ou 5G), nem como interface `ww*`, nem como `/dev/cdc-wdm*`;
- `NetworkManager-wait-online.service`, que segura o boot até a rede conectar. Num computador de mesa ou notebook, nada precisa da rede tão cedo, e o boot fica alguns segundos mais rápido, às vezes bem mais com Wi-Fi. Ele continua ligado se o `/etc/fstab` montar pastas da rede (NFS, Samba, `_netdev`), ou com `esperar_rede: sim`.

Ela não mexe na impressão, no som, nas atualizações automáticas nem na busca de arquivos, porque é difícil saber de fora se você usa.

## O que muda no sistema

Roda `systemctl disable --now` em cada serviço da lista que estiver ligado. É `disable`, e não `mask`: o serviço continua instalado, só não liga mais no boot.

Se um dia você conectar um adaptador Bluetooth, ligue de novo com `sudo systemctl enable --now bluetooth`, ou desfaça a receita.

## Como conferir

O `testar.sh` roda `systemctl is-enabled` e `systemctl is-active` em cada serviço da lista: nenhum pode estar ligado no boot nem rodando.

Para ver você mesmo:

- `systemctl list-unit-files --state=enabled` lista o que liga no boot;
- `systemd-analyze blame` mostra quanto tempo cada serviço levou no último boot.

## Como desfazer

O `desfazer.sh` liga de novo, com `systemctl enable --now`, exatamente os serviços que a receita desligou.

## Fontes

- [systemctl(1)](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [Serviços que esperam a rede, no systemd](https://systemd.io/NETWORK_ONLINE/)
- [Melhorar o desempenho do boot, na ArchWiki](https://wiki.archlinux.org/title/Improving_performance/Boot_process)
