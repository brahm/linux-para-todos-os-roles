# Memória comprimida (zram)

## O que faz

Liga o zram: uma área de troca (swap) que fica na própria memória, comprimida. Quando a memória enche, o kernel comprime o que está parado em vez de mandar para o disco, e a máquina aguenta mais abas e programas abertos antes de engasgar.

## Por que

Num computador com 2 ou 4 GB de memória, abrir um navegador moderno já enche a memória. O Linux então começa a usar a swap no disco, e num disco rígido antigo isso é muito lento: o mouse trava, o som picota e às vezes a única saída é desligar no botão.

Com o zram, o que sairia da memória fica nela mesma, comprimido. A compressão com zstd costuma reduzir as páginas a um terço do tamanho, e comprimir e descomprimir gasta muito menos tempo do que ler e gravar no disco. O Fedora, o Pop!_OS e o ChromeOS já vêm com zram ligado por padrão; o Ubuntu e o Debian, não.

Os ajustes do kernel que vão junto dizem que trocar ficou barato: o kernel passa a comprimir mais cedo, antes de a memória ficar apertada, e lê uma página por vez, que é o certo para uma swap que não é disco.

## O que muda no sistema

- Se o kernel não traz o módulo do zram, como no Ubuntu Server e nas imagens de nuvem, instala os módulos extras do kernel: o `linux-modules-extra` do kernel de agora e, quando o sistema segue o kernel `linux-image-virtual`, o `linux-image-extra-virtual`, para o módulo continuar lá depois das atualizações do kernel. Num Ubuntu de desktop eles já vêm instalados.
- Instala o pacote `systemd-zram-generator`, que cria o zram a cada boot.
- Escreve `/etc/systemd/zram-generator.conf`: um zram de até 50% da memória (o parâmetro `porcentagem`), nunca mais de 8 GB, com compressão zstd e prioridade 100.
- Escreve `/etc/sysctl.d/99-bora-zram.conf` com `vm.swappiness = 180`, `vm.watermark_boost_factor = 0`, `vm.watermark_scale_factor = 125` e `vm.page-cluster = 0`.
- Liga o zram na hora, sem precisar reiniciar.

A swap que já existia no disco continua lá, como reserva. Por causa da prioridade, o kernel só usa ela quando o zram enche.

Se o computador já tiver zram (pelo `zram-tools`, pelo `zram-config`, pelo próprio `systemd-zram-generator` ou por outra configuração), a receita não mexe em nada e só confere.

Os 50% são o tamanho máximo, e não o que o zram ocupa de saída: ele começa vazio e só cresce quando a memória aperta. Como o conteúdo fica comprimido, 2 GB de zram costumam guardar uns 6 GB de páginas.

## Como conferir

O `testar.sh` roda:

- a existência do gerador em `/usr/lib/systemd/system-generators/zram-generator`;
- a comparação dos dois arquivos de configuração com o que a receita escreve;
- `swapon --show` (pela lista em `/proc/swaps`): o `/dev/zram0` aparece como swap, com prioridade 100;
- a leitura de `/sys/block/zram0/comp_algorithm`, que mostra `[zstd]` como algoritmo escolhido.

Para ver você mesmo: `zramctl` mostra o tamanho do zram, quanto ele guarda e quanto isso ocupa comprimido. O `bora diag` também mostra o zram ligado.

## Como desfazer

O `desfazer.sh` desliga o zram (o que estava nele volta para a memória), apaga os dois arquivos, volta os ajustes do kernel aos valores de antes e remove o `systemd-zram-generator`, se foi a receita que o instalou. Se a memória estiver cheia demais para desligar o zram na hora, ele avisa, e o zram sai no próximo reinício.

## Fontes

- [zram-generator.conf(5)](https://github.com/systemd/zram-generator/blob/main/man/zram-generator.conf.md)
- [zram, na ArchWiki](https://wiki.archlinux.org/title/Zram)
- [Documentação do kernel: zram](https://docs.kernel.org/admin-guide/blockdev/zram.html)
- [Fedora: swap no zram por padrão](https://fedoraproject.org/wiki/Changes/SwapOnZRAM)
