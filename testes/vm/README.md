# Roteiros de teste em máquina virtual

Os testes automáticos rodam num contêiner, que não tem kernel, disco, rede nem tela de login de verdade. Eles conferem que cada receita aplica, não muda nada na segunda vez e desfaz, mas não conferem, por exemplo, se o zram liga de fato ou se o Xfce aparece na tela de login. Estes roteiros cobrem o que falta, um por rolê, para rodar numa máquina virtual (VM).

Uma receita só passa de "testada em contêiner" para recomendada sem ressalva depois de passar por aqui.

| Rolê | Roteiro | Tempo |
|---|---|---|
| Pronto para estudar e trabalhar | [`pronto-para-estudar.md`](pronto-para-estudar.md) | cerca de 1 hora |
| Dar vida nova a uma máquina antiga | [`maquina-antiga.md`](maquina-antiga.md) | cerca de 1 hora |
| Começar a programar | [`comecar-a-programar.md`](comecar-a-programar.md) | cerca de 40 minutos |

## Distros

Cada roteiro roda nas quatro distros abaixo. As três primeiras são as bases que o `bora` testa a cada mudança; o Linux Mint é a derivada mais usada da família Ubuntu, e entra para conferir o que muda numa derivada. O Pop!_OS e o Zorin OS continuam como "herdada" e não entram nesta rodada.

| Distro | Imagem | Observação |
|---|---|---|
| Ubuntu 24.04 LTS | [ubuntu.com/download/desktop](https://ubuntu.com/download/desktop) | a base da maior parte das derivadas |
| Ubuntu 26.04 LTS | [ubuntu.com/download/desktop](https://ubuntu.com/download/desktop) | |
| Debian 13 | [debian.org/download](https://www.debian.org/download) | instale com o GNOME para os rolês 1 e 3, e com o Xfce ou o LXQt para o rolê 2 |
| Linux Mint 22 | [linuxmint.com/download.php](https://linuxmint.com/download.php) | Cinnamon para os rolês 1 e 3, Xfce para o rolê 2. Já vem sem Snap e com o Flathub ligado |

## Preparar a máquina virtual

Qualquer programa de VM serve. Os mais simples:

- **GNOME Boxes**, no Linux: `flatpak install flathub org.gnome.Boxes`. Escolha a imagem `.iso`, e ele cria a VM sozinho.
- **virt-manager**, no Linux, para quem quer escolher tudo: `sudo apt install virt-manager`.
- **VirtualBox**, no Windows e no Mac.

Configuração da VM:

- 2 processadores, 4 GB de memória e 40 GB de disco. Para o rolê 2, 2 GB de memória, para parecer uma máquina antiga.
- Um segundo disco virtual de 10 GB, para o backup da pasta pessoal do rolê 1 (no GNOME Boxes, em Propriedades, Dispositivos).
- Rede no modo padrão (NAT). Para o SSH do rolê 2, use a rede em ponte ou a rede do virt-manager, para outro computador alcançar a VM.

Instale a distro com as opções padrão, crie uma conta comum e, antes de qualquer teste, **tire um snapshot da VM** com o nome `limpa`. Cada roteiro começa dessa foto, para um teste não influenciar o outro.

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
