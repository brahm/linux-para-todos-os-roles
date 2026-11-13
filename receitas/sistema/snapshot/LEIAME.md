# Snapshot do sistema

## O que faz

Configura o Timeshift para guardar uma foto diária e uma semanal dos arquivos do sistema. Se uma atualização ou uma mudança quebrar alguma coisa, dá para voltar o sistema a como estava num desses dias.

## Por que

Cada receita do `bora` sabe se desfazer, mas há coisas que nenhuma receita controla, como uma atualização com defeito ou um driver que não sobe. O snapshot é a rede de segurança para esses casos.

Depois que esta receita roda, o `bora` passa a criar um snapshot antes de aplicar qualquer plano.

O Timeshift guarda o sistema, não os seus arquivos pessoais. As pastas em `/home` e a do `root` ficam de fora de propósito: voltar o sistema não pode apagar o trabalho que você fez depois. O backup da pasta pessoal é outra receita.

## O que muda no sistema

- Instala o `timeshift` sem os pacotes recomendados. Num desktop eles já estão instalados, e num servidor seriam centenas de pacotes gráficos que o Timeshift não usa.
- Escreve `/etc/timeshift/timeshift.json` com:
  - o UUID da partição onde os snapshots ficam (por padrão, a do próprio sistema);
  - o modo `rsync`, ou o modo `btrfs` se a raiz for btrfs com o subvolume `@`;
  - 5 snapshots diários e 3 semanais (os parâmetros `diarios` e `semanais`);
  - `/root/**` e `/home/*/**` na lista do que fica de fora.
- Cria o `bora-snapshot.service` e o `bora-snapshot.timer` em `/etc/systemd/system`. De hora em hora, o timer roda `timeshift --check`, que só cria um snapshot quando um deles vence. O Timeshift costuma agendar pelo cron, mas só quando é configurado pelo aplicativo; como aqui a configuração vai direto no arquivo, o agendamento fica com o systemd.
- Com `criar_agora: sim` (o padrão), cria o primeiro snapshot. Na primeira vez, o Timeshift copia o sistema inteiro, o que leva de 5 a 30 minutos. Os seguintes copiam só o que mudou.
- Se o Timeshift cair nesse primeiro snapshot, a receita tenta mais uma vez. Até a versão 26.11.0, ele às vezes cai com falha de segmentação logo no começo da cópia. A versão do Ubuntu 24.04 é a 24.01.1.

A receita para antes de mudar qualquer coisa se:

- houver menos de 10 GB livres na partição de destino;
- a raiz for btrfs sem o subvolume `@`, porque o Timeshift não funciona nesse arranjo. O snapper vem numa próxima versão.

## Como conferir

O `testar.sh` roda:

- `command -v timeshift`: o programa está instalado;
- uma leitura do `timeshift.json`, que confere o UUID, o modo e os agendamentos;
- `timeshift --list`: o Timeshift consegue montar o dispositivo e listar os snapshots;
- `systemctl is-enabled bora-snapshot.timer`: o agendamento está ligado;
- com `criar_agora: sim`, confere se existe pelo menos um snapshot.

Para ver os snapshots: `sudo timeshift --list`. Para voltar o sistema: `sudo timeshift --restore`, ou abra o aplicativo Timeshift.

## Como desfazer

O `desfazer.sh` desliga e remove o timer, apaga o snapshot que esta receita criou, volta o `timeshift.json` ao que era e remove o Timeshift, se ele foi instalado pela receita.

Se o Timeshift já vinha instalado, como no Linux Mint, ele fica, e o `timeshift.json` volta a não existir. Assim, na primeira vez que você abrir o Timeshift, o assistente de configuração aparece, como antes do `bora`.

Snapshots criados depois, pelo `bora` ou pelo agendamento, continuam guardados. A receita avisa onde eles estão, para você decidir se apaga.

## Fontes

- [Timeshift, no repositório do Linux Mint](https://github.com/linuxmint/timeshift)
- [Correção da falha de segmentação no Timeshift 26.11.0](https://github.com/linuxmint/timeshift/pull/552)
- [Manual do systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html)
- O arquivo `/etc/timeshift/default.json`, instalado pelo pacote, como referência dos campos da configuração
