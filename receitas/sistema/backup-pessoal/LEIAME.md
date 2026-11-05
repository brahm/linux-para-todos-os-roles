# Backup da pasta pessoal

## O que faz

Copia a pasta pessoal de cada pessoa do computador para um disco externo, uma vez por dia e logo que o disco é conectado. Guarda as últimas versões (7, por padrão), para dar para buscar um arquivo como ele estava há alguns dias.

## Por que

O snapshot do sistema volta o computador a como estava ontem, mas fica no mesmo disco e deixa as pastas pessoais de fora de propósito. Se o disco morrer, o notebook for roubado ou um arquivo for apagado sem querer, só uma cópia em outro disco salva o trabalho.

Cada cópia é uma pasta comum no disco externo, que abre em qualquer computador com Linux, sem programa especial. Os arquivos que não mudaram de um dia para o outro não ocupam espaço de novo: as versões compartilham esses arquivos por hardlinks. Por isso sete versões costumam ocupar pouco mais do que uma.

## O que muda no sistema

- Instala o `rsync`, se ainda não estiver instalado.
- Escreve `/etc/bora/backup-pessoal.conf` com o UUID do disco, o nome do computador, as pessoas copiadas e quantas versões manter.
- Instala o programa do backup em `/usr/local/lib/bora/backup-pessoal`.
- Cria três unidades do systemd em `/etc/systemd/system`:
  - `bora-backup-pessoal.timer`, que de hora em hora roda o `bora-backup-pessoal.service`. Ele só copia se o disco estiver conectado e a última cópia tiver mais de 20 horas;
  - `bora-backup-pessoal-conectar.service`, que roda quando o disco é conectado. Ele espera até um minuto pela sessão gráfica montar o disco, para não disputá-lo com o gerenciador de arquivos.
- Com `fazer_agora: sim` (o padrão) e o disco conectado, faz a primeira cópia. Ela copia tudo e pode demorar; as seguintes copiam só o que mudou.

### O disco

Com `destino: auto` (o padrão), a receita usa o único disco USB conectado que tenha um sistema de arquivos do Linux (ext4, xfs ou btrfs). O disco é reconhecido pelo UUID, então pode ser conectado em qualquer porta.

A receita para sem mudar nada se:

- não houver disco externo conectado, ou houver mais de um (aí informe qual no parâmetro `destino`, como `/dev/sdb1`);
- o disco usar exFAT, NTFS ou FAT, como a maioria dos discos e pendrives vendidos. A receita explica o motivo na hora: esses sistemas não guardam hardlinks (cada versão ocuparia uma cópia inteira), não guardam dono nem permissões (o que voltasse do backup viria errado) e se corrompem com mais facilidade se o disco for puxado no meio da cópia. O `bora` não formata discos, porque formatar apaga o que está neles: copie o que houver no disco para outro lugar, formate em ext4 pelo aplicativo Discos e rode de novo;
- a partição informada for a do próprio sistema.

### Onde ficam as cópias

```text
<disco>/bora-backup/<computador>/<pessoa>/
  2026-11-05_093012/      uma cópia completa da pasta pessoal
  2026-11-06_101544/
  ultimo -> 2026-11-06_101544
```

Cada pessoa só consegue abrir a própria pasta. Ficam de fora o `.cache`, a lixeira e os caches dos aplicativos Flatpak e Snap, que são refeitos sozinhos.

Para recuperar um arquivo, conecte o disco, abra `bora-backup` no gerenciador de arquivos e copie o arquivo de volta. Para fazer uma cópia na hora: `sudo /usr/local/lib/bora/backup-pessoal --agora`. Para ver o que aconteceu no último backup: `journalctl -u bora-backup-pessoal`.

## Como conferir

O `testar.sh` roda:

- `command -v rsync`: o rsync está instalado;
- uma comparação do programa instalado com o da receita e da configuração com o disco e as pessoas do plano;
- `systemctl is-enabled bora-backup-pessoal.timer` e `systemctl is-enabled bora-backup-pessoal-conectar.service`: os dois gatilhos estão ligados;
- com o disco conectado, `backup-pessoal --conferir`, que monta o disco só para leitura (se ele não estiver montado) e confere que cada pessoa tem uma cópia completa.

## Como desfazer

O `desfazer.sh` desliga e remove as unidades do systemd, apaga a configuração e o programa e remove o `rsync`, se foi a receita que o instalou.

As cópias que já estão no disco externo **não** são apagadas: são os seus arquivos. A receita avisa onde elas estão, para você decidir.

## Fontes

- [Manual do rsync](https://download.samba.org/pub/rsync/rsync.1), em especial as opções `--link-dest` e `--one-file-system`
- [Manual do systemd.device](https://www.freedesktop.org/software/systemd/man/latest/systemd.device.html), sobre unidades que rodam quando um disco aparece
- [Manual do systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html)
- [BackupAndRecovery, na wiki do Debian](https://wiki.debian.org/BackupAndRecovery)
