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
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/vibecodar.sh
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/vibecode-local.sh
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/novas-capacidades.sh
docker run --rm --privileged -v "$PWD":/bora bora-teste ./testes/conteiner/pasta-compartilhada.sh
```

Os scripts usam o binário estático em `target/x86_64-unknown-linux-musl/release/bora`, com as receitas embutidas; para usar outro, passe `-e BORA=/bora/caminho/do/bora` ao `docker run`. Troque `IMAGEM` por `ubuntu:24.04` ou `debian:13`. O CI roda as três a cada pull request.

- `rodar.sh` confere que o rolê "Pronto para estudar e trabalhar" monta um plano válido e aplica as seis receitas dele (`base/atualizar`, `sistema/snapshot`, `seguranca/firewall`, `desktop/codecs`, `desktop/flatpak` e `sistema/backup-pessoal`), aplica de novo (a segunda vez não pode mudar nada) e desfaz, conferindo que os pacotes e os arquivos voltaram ao que eram e que as cópias do backup continuam no disco externo.
- `backup.sh` testa o backup da pasta pessoal: as versões que compartilham os arquivos que não mudaram, o intervalo de 20 horas, o limite de versões, o disco desconectado e a recusa de um disco em FAT.
- `maquina-antiga.sh` confere que o rolê "Dar vida nova a uma máquina antiga" monta um plano válido e aplica as quatro receitas dele que não estão no rolê 1 (`sistema/zram`, `desktop/ambiente-leve`, `desktop/navegador-leve` e `sistema/servicos-enxutos`), com o ambiente de `AMBIENTE` (`xfce` ou `lxqt`), aplica de novo e desfaz. Antes, liga o Bluetooth, o ModemManager e a espera da rede, como num desktop, e cria uma política do Firefox e uma conta no AccountsService, para conferir que o desfazer volta cada uma ao que era. No fim, confere que a receita do zram não mexe num `zram-tools` que já existia. O CI roda o Xfce no Ubuntu e o LXQt no Debian.
- `comecar-a-programar.sh` confere que o rolê "Começar a programar" monta o plano do perfil de `PERFIL` (`python` ou `web`) só com as receitas daquele perfil, aplica, aplica de novo e desfaz, como uma pessoa que chamou o `bora` com `sudo`. A conta de teste já tem um `.gitconfig` e não tem faixa de IDs para contêineres, para conferir que o desfazer volta os dois ao que eram. Depois de aplicar, cria um projeto de exemplo, instala um pacote num ambiente virtual do Python ou com `npm install -g`, sem sudo, e faz um commit. O teste do Node.js baixa o arquivo de nodejs.org, e o do Python, um pacote do PyPI, então precisam de rede. O CI roda os dois perfis nas três distros.
- `vibecodar.sh` confere que o rolê "Vibecodar" monta o plano certo para cada resposta (com e sem a caixa de areia, com o Zed puxando o Flatpak, e recusando um agente que não existe), aplica com os cinco agentes, o VS Code e a caixa de areia, aplica de novo e desfaz, como uma pessoa que chamou o `bora` com `sudo`. A conta de teste já tem uma regra no ignore global do Git e uma configuração do Claude Code, para conferir que o desfazer volta as duas ao que eram. Depois de aplicar, confere que cada agente responde, cria um projeto de exemplo de dentro da `caixa`, confere que o `.env` fica fora do Git, que o gitleaks barra um commit com um token e que a caixa não deixa escrever fora do projeto. Precisa de rede, para nodejs.org, o npm, o PyPI e o repositório da Microsoft. Troque os agentes com `-e AGENTES=opencode,codex` e o editor com `-e EDITOR_=terminal`.
- `vibecode-local.sh` confere o cenário de vibecode local do rolê "Vibecodar": o `bora modelos`, o plano de cada resposta da pergunta sobre modelos locais (com `modelo: sugerido` trocado pelo nome do modelo no plano salvo) e a recusa de um nome que não é de modelo. Depois aplica o Ollama, com o `qwen3:0.6b`, e o LM Studio, aplica de novo, pergunta ao modelo e confere que ele responde, e desfaz, conferindo que os pacotes, o `/usr/local`, o `/opt`, os atalhos e a conta `ollama` voltaram ao que eram. Precisa de rede, para o GitHub, `registry.ollama.ai` e `installers.lmstudio.ai`, uns 3 GB. Troque o modelo com `-e MODELO=qwen3:1.7b`.
- `novas-capacidades.sh` testa as três receitas opcionais ou de apoio dos rolês 1 e 2. O `sistema/etckeeper` aplica, registra uma instalação do apt no histórico do `/etc` e desfaz, guardando uma cópia do histórico. O `seguranca/ssh` aplica com o firewall ligado, confere que só a rede local entra, recusa `so_chave` numa conta sem chave e aceita numa conta com chave. O `desktop/sem-snap` bloqueia o snapd numa máquina sem Snap, recusa tirar um snap que não sabe trocar e, com um snapd instalado e um snap do Firefox de mentira, troca o Firefox pelo da Mozilla, copiando o perfil, e desfaz. Essa última parte precisa de rede para `packages.mozilla.org`; sem ela, rode com `-e SEM_MOZILLA=1`, e o teste confere que nada muda quando a chave da Mozilla não chega.
- `pasta-compartilhada.sh` confere que o rolê "Pasta compartilhada da casa" monta um plano válido, com o firewall de servidor da casa, recusa as pastas do sistema, a pasta pessoal inteira, o root e uma conta do sistema, e aplica o firewall e o `servicos/samba` para `aluno` (que tem conta no computador) e `beto` (que ganha uma conta só para a pasta). Liga o `smbd` à mão, porque o contêiner não tem systemd, e entra na pasta com o `smbclient`: cada um cria ou lê um arquivo com a senha da pasta, e a senha do computador, uma senha errada, um visitante e o SMB1 não entram. Aplica de novo, acrescenta a `carla`, desfaz as duas aplicações e confere que os pacotes, as contas e a senha do `aluno` no computador voltaram ao que eram, e que os arquivos da pasta ficaram. No fim, repete com um Samba que já existia, com uma pasta própria, e uma pasta do root vazia, e confere que o `smb.conf` e o dono da pasta voltam ao que eram.
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
