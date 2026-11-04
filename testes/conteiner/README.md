# Testes em contêiner

Aplicam as receitas de verdade numa distro limpa, sem tocar no seu computador.

```sh
cargo build --release --target x86_64-unknown-linux-musl
docker build -t bora-teste --build-arg IMAGEM=ubuntu:26.04 testes/conteiner
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/rodar.sh
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/cenarios.sh
```

Os scripts usam o binário estático em `target/x86_64-unknown-linux-musl/release/bora`, com as receitas embutidas; para usar outro, passe `-e BORA=/bora/caminho/do/bora` ao `docker run`. Troque `IMAGEM` por `ubuntu:24.04` ou `debian:13`. O CI roda as três a cada pull request.

- `rodar.sh` aplica `base/atualizar`, `sistema/snapshot` e `seguranca/firewall`, aplica de novo (a segunda vez não pode mudar nada) e desfaz, conferindo que os pacotes e os arquivos voltaram ao que eram.
- `cenarios.sh` testa o firewall com um ufw que já estava ligado e com regras próprias, e a proteção de quem está conectado por SSH.

O `--privileged` é necessário para o firewall mexer no netfilter do contêiner e para o teste criar um disco virtual para os snapshots. O contêiner tem a própria rede, então o firewall não afeta a máquina que roda o teste.

## O que um contêiner não testa

Um contêiner não é um computador: não há systemd rodando, nem udev, nem uma partição própria. Por isso:

- a variável `BORA_PERMITIR_SEM_SYSTEMD=1` deixa o `bora` rodar sem systemd, só para estes testes;
- os timers são habilitados, mas não disparam;
- o snapshot vai para um disco virtual, e o teste escreve à mão no banco do udev o UUID que o Timeshift procura.

Por isso o teste em contêiner é registrado com `onde: conteiner`, e o `bora` avisa, ao montar o plano, quando uma receita ainda não rodou numa máquina virtual com a distro instalada do jeito normal.
