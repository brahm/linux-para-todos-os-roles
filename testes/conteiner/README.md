# Testes em contêiner

Aplicam as receitas de verdade numa distro limpa, sem tocar no seu computador.

```sh
cargo build --release --target x86_64-unknown-linux-musl
docker build -t bora-teste --build-arg IMAGEM=ubuntu:26.04 testes/conteiner
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/rodar.sh
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/cenarios.sh
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/backup.sh
docker run --rm --privileged -e AMBIENTE=xfce -v "$PWD":/bora bora-teste ./testes/conteiner/maquina-antiga.sh
docker run --rm --privileged -e PERFIL=python -v "$PWD":/bora bora-teste ./testes/conteiner/comecar-a-programar.sh
```

Os scripts usam o binário estático em `target/x86_64-unknown-linux-musl/release/bora`, com as receitas embutidas; para usar outro, passe `-e BORA=/bora/caminho/do/bora` ao `docker run`. Troque `IMAGEM` por `ubuntu:24.04` ou `debian:13`. O CI roda as três a cada pull request.

- `rodar.sh` confere que o rolê "Pronto para estudar e trabalhar" monta um plano válido e aplica as seis receitas dele (`base/atualizar`, `sistema/snapshot`, `seguranca/firewall`, `desktop/codecs`, `desktop/flatpak` e `sistema/backup-pessoal`), aplica de novo (a segunda vez não pode mudar nada) e desfaz, conferindo que os pacotes e os arquivos voltaram ao que eram e que as cópias do backup continuam no disco externo.
- `backup.sh` testa o backup da pasta pessoal: as versões que compartilham os arquivos que não mudaram, o intervalo de 20 horas, o limite de versões, o disco desconectado e a recusa de um disco em FAT.
- `maquina-antiga.sh` confere que o rolê "Dar vida nova a uma máquina antiga" monta um plano válido e aplica as quatro receitas dele que não estão no rolê 1 (`sistema/zram`, `desktop/ambiente-leve`, `desktop/navegador-leve` e `sistema/servicos-enxutos`), com o ambiente de `AMBIENTE` (`xfce` ou `lxqt`), aplica de novo e desfaz. Antes, liga o Bluetooth, o ModemManager e a espera da rede, como num desktop, e cria uma política do Firefox e uma conta no AccountsService, para conferir que o desfazer volta cada uma ao que era. No fim, confere que a receita do zram não mexe num `zram-tools` que já existia. O CI roda o Xfce no Ubuntu e o LXQt no Debian.
- `comecar-a-programar.sh` confere que o rolê "Começar a programar" monta o plano do perfil de `PERFIL` (`python` ou `web`) só com as receitas daquele perfil, aplica, aplica de novo e desfaz, como uma pessoa que chamou o `bora` com `sudo`. A conta de teste já tem um `.gitconfig` e não tem faixa de IDs para contêineres, para conferir que o desfazer volta os dois ao que eram. Depois de aplicar, cria um projeto de exemplo, instala um pacote num ambiente virtual do Python ou com `npm install -g`, sem sudo, e faz um commit. O teste do Node.js baixa o arquivo de nodejs.org, e o do Python, um pacote do PyPI, então precisam de rede. O CI roda os dois perfis nas três distros.
- `cenarios.sh` testa o firewall com um ufw que já estava ligado e com regras próprias, e a proteção de quem está conectado por SSH.

O `--privileged` é necessário para o firewall mexer no netfilter do contêiner e para o teste criar discos virtuais para os snapshots e para o backup. O contêiner tem a própria rede, então o firewall não afeta a máquina que roda o teste.

## O que um contêiner não testa

Um contêiner não é um computador: não há systemd rodando, nem udev, nem uma partição própria. Por isso:

- a variável `BORA_PERMITIR_SEM_SYSTEMD=1` deixa o `bora` rodar sem systemd, só para estes testes;
- os timers são habilitados, mas não disparam;
- o snapshot vai para um disco virtual, e o teste escreve à mão no banco do udev o UUID que o Timeshift procura;
- o backup vai para outro disco virtual, informado no plano: sem udev, o `destino: auto` não reconhece discos USB, e o gatilho de conectar o disco não dispara;
- o Flatpak baixa a configuração do Flathub da internet, então o teste precisa de rede;
- o zram não liga: sem systemd, o gerador não roda, e o teste confere só a configuração. Ligar o zram de verdade mexeria no kernel da máquina que roda o teste;
- não há tela de login nem placa de vídeo, então o teste confere que o ambiente leve aparece na lista de sessões, mas não abre ele;
- não há Firefox: o teste confere o arquivo de políticas, e não o uBlock Origin instalado;
- o Podman roda sem root, mas o teste não baixa imagem nenhuma: ele confere o `podman info`, e não um `podman run`.

Por isso o teste em contêiner é registrado com `onde: conteiner`, e o `bora` avisa, ao montar o plano, quando uma receita ainda não rodou numa máquina virtual com a distro instalada do jeito normal.
