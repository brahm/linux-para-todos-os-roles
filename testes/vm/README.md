# Roteiros de teste em máquina virtual

Contêiner é ótimo para testar rápido, mas não tem kernel, disco, rede nem tela de login de verdade. Por isso cada receita também roda toda semana em duas máquinas virtuais (VM) do CI:

- uma **sem tela**, para tudo o que não precisa de monitor;
- uma **com a tela de login**, para o ambiente leve, o navegador e o Sem Snap.

São elas que gravam o registro `onde: vm` e fazem um rolê virar `testado` quando cada receita dele passa no Ubuntu 24.04 e no Debian 13 ([regra completa](../../objetivos/README.md#quando-um-rolê-vira-testado)).

Os roteiros manuais desta pasta, um por rolê, conferem o que robô nenhum garante: se o vídeo toca, se a loja abre, se os favoritos vieram no Firefox. Também cobrem o Linux Mint, que não tem imagem para as máquinas do CI. Achou um problema? Vira uma issue.

| Rolê | Roteiro | Tempo |
|---|---|---|
| Pronto para estudar e trabalhar | [`pronto-para-estudar.md`](pronto-para-estudar.md) | cerca de 1 hora |
| Dar vida nova a uma máquina antiga | [`maquina-antiga.md`](maquina-antiga.md) | cerca de 1 hora |
| Começar a programar | [`comecar-a-programar.md`](comecar-a-programar.md) | cerca de 40 minutos |
| Vibecodar | [`vibecodar.md`](vibecodar.md) | cerca de 1 hora |
| Pasta compartilhada da casa | [`pasta-compartilhada.md`](pasta-compartilhada.md) | cerca de 30 minutos, com outro aparelho na mesma rede |

## A parte automática, no CI

O workflow [Máquina virtual](../../.github/workflows/vm.yml), com os scripts em [`qemu/`](qemu/), liga uma VM de verdade com QEMU e KVM no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13. Em cada uma:

1. Liga a imagem de nuvem oficial da distro, com um disco externo de mentira.
2. Aplica o rolê 1 duas vezes. A segunda não pode mudar nada.
3. Aplica cada um dos outros rolês, com todas as receitas de uma vez e o snapshot de antes pelo Timeshift. Ficam de fora as que só se conferem com tela, listadas em [`qemu/so-com-tela.txt`](qemu/so-com-tela.txt).
4. Reinicia e confere que o zram, o firewall, o SSH, o histórico do `/etc`, o temporizador do backup e os snapshots voltaram sozinhos.
5. Aplica tudo de novo, sem mudar nada.
6. Desconecta e conecta o disco de novo, para ver o backup disparar.
7. Desfaz tudo.

Hoje isso cobre os rolês 3 e 4 inteiros (Git, compilação, Python, Node.js, Podman, as ferramentas do terminal, o gitleaks, as chaves de API, os cinco agentes, a caixa de areia e o VS Code) e, do rolê 2, a atualização, o snapshot, o zram, os serviços enxutos e o SSH.

- **Rolê novo** em `objetivos/` entra sozinho.
- **Receita nova que só se confere com tela** precisa entrar em `so-com-tela.txt`.
- **Parâmetro sem valor padrão**, como o e-mail do Git, recebe o valor de [`qemu/parametros.txt`](qemu/parametros.txt).

Na `main`, quando uma distro passa:

- o workflow grava o registro com `onde: vm` e `por: testes-automaticos` no `receita.yaml` de cada receita aplicada, com [`ferramentas/registros/registrar.py`](../../ferramentas/registros/registrar.py), e gera o site de novo;
- cada receita guarda um registro desses por distro, que só muda quando o resultado muda ou quando passa de 30 dias;
- as capturas da máquina com tela vão para `testes/vm/telas/<distro>/`, e as páginas do ambiente leve, do navegador enxuto e do Sem Snap mostram as mais recentes.

O workflow de testes faz o mesmo com o registro `onde: conteiner`. Quando o teste de domingo falha, o workflow abre uma issue com a etiqueta `vm`.

Para rodar no seu computador, com o `qemu-system-x86`, o `qemu-utils`, o `cloud-image-utils` e o `socat`:

```sh
cargo build --release --target x86_64-unknown-linux-musl
testes/vm/qemu/rodar.sh debian-13 target/x86_64-unknown-linux-musl/release/bora
```

### A máquina com tela

As receitas de `so-com-tela.txt` rodam no workflow [Máquina virtual com tela](../../.github/workflows/vm-tela.yml), com o [`qemu/tela.sh`](qemu/tela.sh). Roda nas mesmas três distros e numa quarta: o Debian 13 com o LightDM e o Xfce, o jeito mais comum de uma máquina antiga com Debian.

1. Instala na imagem de nuvem a tela de login do GNOME (o GDM) e o Firefox, como num desktop (no Ubuntu, o Firefox do Snap), e confere a tela de login.
2. Aplica as três receitas duas vezes, a segunda sem mudar nada: o Xfce no Ubuntu e o LXQt no Debian, com o ambiente leve como padrão da pessoa.
3. Liga a entrada automática e reinicia.
4. Confere que a pessoa entrou sozinha no ambiente leve, abre o Firefox na sessão dela e espera o uBlock Origin chegar pela política da receita.
5. Desliga a entrada automática, reinicia e desfaz tudo.
6. Confere que a tela de login voltou e, no Ubuntu, que o snapd e o Firefox do Snap também.

Cada passo tira uma captura pelo monitor do QEMU. A captura precisa mostrar alguma coisa: tela de uma cor só, ou ainda em modo texto, reprova. As capturas ficam 30 dias no artefato `telas-<distro>` da execução, com a do momento da falha (`falhou.png`), quando há uma. O registro na `main` e a issue de domingo funcionam como no outro workflow.

```sh
testes/vm/qemu/tela.sh ubuntu-24.04 target/x86_64-unknown-linux-musl/release/bora
testes/vm/qemu/tela.sh debian-13 target/x86_64-unknown-linux-musl/release/bora lightdm
```

Nenhuma das duas substitui os roteiros abaixo. Se o painel do Xfce está no lugar, se o vídeo toca, se a loja abre e se os favoritos e as senhas vieram no Firefox, só alguém olhando confere.

## Distros

Cada roteiro roda nas quatro distros abaixo.

- As três primeiras são as bases que o `bora` testa a cada mudança.
- O Linux Mint é a derivada mais usada da família Ubuntu, e entra para conferir o que muda numa derivada.
- O Pop!_OS e o Zorin OS continuam como "herdada" e não entram nesta rodada.

| Distro | Imagem | Observação |
|---|---|---|
| Ubuntu 24.04 LTS | [ubuntu.com/download/desktop](https://ubuntu.com/download/desktop) | a base da maior parte das derivadas |
| Ubuntu 26.04 LTS | [ubuntu.com/download/desktop](https://ubuntu.com/download/desktop) | |
| Debian 13 | [debian.org/download](https://www.debian.org/download) | instale com o GNOME para os rolês 1 e 3, e com o Xfce ou o LXQt para o rolê 2 |
| Linux Mint 22 | [linuxmint.com/download.php](https://linuxmint.com/download.php) | Cinnamon para os rolês 1 e 3, Xfce para o rolê 2. Já vem sem Snap e com o Flathub ligado. Não tem imagem de nuvem para as máquinas do CI. Os testes em contêiner rodam nele à mão ([como](../conteiner/README.md#no-linux-mint)) |

## Preparar a máquina virtual

Qualquer programa de VM serve. Os mais simples:

- **GNOME Boxes**, no Linux: `flatpak install flathub org.gnome.Boxes`. Escolha a imagem `.iso`, e ele cria a VM sozinho.
- **virt-manager**, no Linux, para quem quer escolher tudo: `sudo apt install virt-manager`.
- **VirtualBox**, no Windows e no Mac.

Configuração da VM:

- 2 processadores, 4 GB de memória e 40 GB de disco. Para o rolê 2, 2 GB de memória, para parecer uma máquina antiga.
- Um segundo disco virtual de 10 GB, para o backup da pasta pessoal do rolê 1 (no GNOME Boxes, em Propriedades, Dispositivos).
- Rede no modo padrão (NAT). Para o SSH do rolê 2, use a rede em ponte ou a rede do virt-manager, para outro computador alcançar a VM.

Instale a distro com as opções padrão e crie uma conta comum. Antes de qualquer teste, **tire um snapshot da VM** com o nome `limpa`. Cada roteiro começa dessa foto, para um teste não contaminar o outro (e para você não precisar instalar o Ubuntu cinco vezes numa tarde).

## Instalar o bora na VM

Pelo terminal da VM, como no README:

```sh
wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/bora-linux-x86_64
wget https://github.com/brahm/linux-para-todos-os-roles/releases/latest/download/SHA256SUMS
sha256sum --check --ignore-missing SHA256SUMS
chmod +x bora-linux-x86_64
sudo mv bora-linux-x86_64 /usr/local/bin/bora
bora diag
```

Para testar uma versão que ainda não saiu, baixe o binário do pull request na aba Actions, artefato `bora-x86_64`.

## Registrar o resultado

Para cada distro e cada receita que passou, acrescente uma linha em `testes` no `receita.yaml` da receita:

```yaml
  - distro: ubuntu          # ubuntu, debian ou linuxmint
    versao: "24.04"         # para o Mint, a versão do Mint, como "22.2"
    data: 2026-11-10
    por: seu-usuario-do-github
    onde: vm
    resultado: ok           # ou o que falhou, em poucas palavras
```

Mande num pull request, ou abra uma issue com o formulário [Relato de teste](https://github.com/brahm/linux-para-todos-os-roles/issues/new?template=5-relato-de-teste.yml), que alguém do projeto transforma em pull request. Se algo falhar, junte a saída do `bora` e a do `bora ajuda`.

Depois de registrar, rode `python3 ferramentas/catalogo/gerar.py` para o site mostrar o teste novo.
