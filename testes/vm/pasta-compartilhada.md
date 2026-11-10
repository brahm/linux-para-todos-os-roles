# Roteiro em VM: Pasta compartilhada da casa

Comece do snapshot `limpa` da VM. Rode nas quatro distros do [README](README.md). A VM precisa estar na mesma rede de um outro aparelho seu: no GNOME Boxes ou no virt-manager, troque a rede da VM para "bridge" (ponte) com a placa do computador, para ela pegar um endereço do roteador da casa, como `192.168.0.x`. Na rede padrão (NAT), só o próprio computador que roda a VM enxerga a pasta.

## 1. Aplicar o rolê

Rode com `sudo`, da sua conta:

```sh
sudo bora
```

Escolha "Pasta compartilhada da casa", aceite a pasta padrão (`/srv/compartilhado`) e informe dois nomes: o da sua conta na VM e um nome novo, como `beto`.

- [ ] O plano termina com "cada receita passou no teste", e a última mensagem mostra o endereço `\\192.168.0.x\Compartilhado`.
- [ ] `sudo bora aplicar` de novo, com o mesmo plano, diz "Tudo já estava aplicado".
- [ ] `sudo cat /var/lib/bora/pasta-compartilhada/senhas` mostra uma senha para cada nome, e `cat` sem `sudo` é recusado.

## 2. Conferir de outro aparelho da casa

**Windows 10 ou 11**

- [ ] Em "Rede", no Explorador de Arquivos, a VM aparece sozinha (pode levar um minuto). Se a descoberta de rede estiver desligada no Windows, ele mesmo oferece ligar.
- [ ] Digitando `\\192.168.0.x\Compartilhado` na barra de endereço, o Windows pede nome e senha; com `beto` e a senha do arquivo, a pasta abre.
- [ ] Crie uma pasta e um arquivo de texto; na VM, `ls -l /srv/compartilhado` mostra os dois com o dono da pasta.
- [ ] Com a senha errada, ou com a senha da sua conta na VM, a pasta não abre.

**Mac, Linux ou celular (pelo menos um)**

- [ ] Mac: Finder, "Ir", "Conectar ao Servidor", `smb://192.168.0.x/Compartilhado`, com o nome e a senha da pasta.
- [ ] Linux com GNOME: em Arquivos, "Outros locais", a VM aparece; ou digite `smb://192.168.0.x/Compartilhado` em "Conectar ao servidor".
- [ ] iPhone: app Arquivos, "…", "Conectar ao Servidor", `smb://192.168.0.x`. Android: um app de arquivos com SMB, como o Material Files ou o gerenciador do próprio celular.
- [ ] O arquivo criado no Windows aparece e abre.

**Na VM**

- [ ] `sudo ufw status` mostra a porta 445 liberada só para a rede da casa.
- [ ] A sua senha de login na VM continua a mesma (saia e entre de novo).
- [ ] Depois de reiniciar a VM, a pasta continua abrindo no outro aparelho.

## 3. Desfazer

```sh
sudo bora desfazer
```

- [ ] O outro aparelho não abre mais a pasta.
- [ ] `/srv/compartilhado` continua lá, com os arquivos criados pela rede.
- [ ] `getent passwd beto` não mostra nada, e a sua conta continua entrando com a senha de sempre.
- [ ] `samba` e `wsdd2` não estão mais instalados, e `/var/lib/bora/pasta-compartilhada` não existe.

## 4. Registrar

Siga o [README](README.md#registrar-o-resultado), com uma linha por receita e por distro. Diga também de que aparelho você abriu a pasta.
