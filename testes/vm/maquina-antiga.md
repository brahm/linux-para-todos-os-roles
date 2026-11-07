# Roteiro em VM: Dar vida nova a uma máquina antiga

Comece do snapshot `limpa` de uma VM com **2 GB de memória**, para parecer uma máquina antiga. No Debian, instale com o Xfce ou o LXQt; no Mint, use a edição Xfce. Rode nas quatro distros do [README](README.md).

## 1. Antes

Anote como a máquina está, para comparar depois:

```sh
free -h
swapon --show
systemd-analyze
systemctl is-enabled bluetooth.service ModemManager.service NetworkManager-wait-online.service
```

## 2. Aplicar o rolê

```sh
sudo bora
```

Escolha "Dar vida nova a uma máquina antiga". Na primeira rodada, responda **não** para o SSH, Xfce como ambiente e **sim** para entrar nele por padrão. Repita a partir do `limpa` com o LXQt e com **sim** para o SSH.

- [ ] O plano termina com "cada receita passou no teste".
- [ ] `sudo bora aplicar` de novo, com o mesmo plano, diz "Tudo já estava aplicado".

## 3. Conferir o que o contêiner não confere

**Memória comprimida (`sistema/zram`)**

- [ ] Depois de reiniciar, `swapon --show` mostra `/dev/zram0` com prioridade maior que a swap do disco.
- [ ] `zramctl` mostra o algoritmo `zstd` e o tamanho perto de metade da memória.
- [ ] `bora diag` mostra o zram ligado e o tipo de disco (SSD ou HDD).
- [ ] Abra o Firefox com 10 abas e um vídeo: `zramctl` mostra dados comprimidos, e a VM não trava.

**Ambiente leve (`desktop/ambiente-leve`)**

- [ ] Depois de sair da sessão, a tela de login mostra o Xfce (ou o LXQt) como opção, e o ambiente antigo continua na lista.
- [ ] Com "entrar no leve por padrão", a sessão já vem escolhida no próximo login.
- [ ] O ambiente leve abre com o painel, o gerenciador de arquivos, o applet de rede e o som funcionando.
- [ ] A tela de login continua a mesma de antes (o GDM no Ubuntu, o LightDM no Mint e no Debian).

**Navegador enxuto (`desktop/navegador-leve`)**

- [ ] O Firefox abre com o uBlock Origin instalado (ícone na barra), baixado da loja da Mozilla.
- [ ] Um site com anúncios aparece sem eles.
- [ ] `about:policies` mostra as políticas do `bora` ativas.
- [ ] No Ubuntu, vale para o Firefox do Snap; no Debian e no Mint, para o Firefox do apt.

**Serviços enxutos (`sistema/servicos-enxutos`)**

- [ ] `systemctl is-enabled` mostra desligado só o que a máquina não usa (numa VM, normalmente o Bluetooth e o ModemManager).
- [ ] `systemd-analyze` mostra o boot igual ou mais rápido que antes.
- [ ] A rede, o som e a impressão (se houver) continuam funcionando.

**Acesso por SSH (`seguranca/ssh`), na rodada com SSH**

- [ ] De outro computador da mesma rede: `ssh <conta>@<ip da VM>` entra com a senha da conta.
- [ ] `ssh root@<ip da VM>` é recusado.
- [ ] Depois de reiniciar, o SSH continua respondendo.
- [ ] Copie uma chave com `ssh-copy-id`, rode o rolê de novo com `-p seguranca/ssh.so_chave=sim` e confira que entrar com senha é recusado e com a chave funciona.

## 4. Desfazer

```sh
sudo bora desfazer
```

- [ ] Depois de reiniciar, `swapon --show` não mostra mais o zram, e a tela de login abre o ambiente de antes.
- [ ] O Firefox abre sem o uBlock Origin (se não estava antes) e com os favoritos.
- [ ] Os serviços desligados voltam a estar ligados, iguais ao passo 1.
- [ ] Na rodada com SSH, `ssh` não conecta mais.

## 5. Registrar

Siga o [README](README.md#registrar-o-resultado), com uma linha por receita e por distro.
