# Pasta compartilhada com Samba

## O que faz

Compartilha uma pasta deste computador com os outros computadores e celulares da casa, pelo Samba. Cada pessoa entra com um nome e uma senha que servem só para a pasta, e só a rede local é aceita, pelo próprio Samba e pelo firewall.

## Por que

O Samba fala SMB, o protocolo de pastas de rede que o Windows, o Mac, o Linux, o Android e o iPhone já sabem abrir, sem instalar nada neles. É o jeito mais simples de juntar as fotos, os documentos e os trabalhos da casa num lugar só.

A configuração padrão das distros é pensada para qualquer uso e ainda deixa visitantes sem senha chegarem até a lista de pastas. A receita fecha isso:

- **Ninguém entra sem nome e senha.** Visitante (`map to guest`) e acesso anônimo ficam desligados.
- **A senha da pasta é separada da senha do computador.** As pessoas que ainda não têm conta ganham uma conta sem pasta pessoal e sem login, que só serve para a pasta. Quem já tem conta usa a mesma conta, com outra senha. Se a senha da pasta vazar, ela não abre o computador, e dá para tirar o acesso de uma pessoa sem mexer nas outras. Por isso a receita desliga também o `unix password sync`, que, no padrão do Ubuntu e do Debian, trocaria a senha do computador quando a pessoa trocasse a da pasta pelo Windows.
- **Só a rede de casa.** O compartilhamento aceita só este computador e a rede local (`hosts allow`), e o firewall, quando está ligado, libera as portas só para ela. Nenhuma receita abre porta para a internet; para abrir a pasta de fora, o caminho é o rolê "Acessar de fora sem abrir portas".
- **Nada do SMB1 nem do NetBIOS.** São as partes antigas do protocolo, que o Windows 10 e 11 já não usam e que tiveram as falhas mais graves (como a que o WannaCry usou). O Samba passa a escutar só na porta 445.

Os arquivos criados pela rede ficam com o dono da pasta (`force user`), quem quer que tenha criado. Assim eles continuam abrindo e mudando neste computador, e uma pessoa nunca fica sem conseguir apagar o arquivo que outra criou.

As senhas são geradas pela receita, fáceis de ditar (três blocos de quatro letras e números), e ficam num arquivo que só o root lê. Elas não aparecem na tela, não vão para o log do `bora` e não vão para o `/etc`, para não entrarem no histórico do etckeeper.

## O que muda no sistema

- Instala `samba` e `smbclient` e, com `aparecer_na_rede`, o `wsdd2`, que faz a pasta aparecer em "Rede" no Windows e no Linux (WS-Discovery) e deixa o Windows achar o computador pelo nome (LLMNR). Sem ele, a pasta abre pelo endereço.
- Cria a pasta, se ela não existir (por padrão `/srv/compartilhado`), com dono de quem rodou o `bora` com `sudo`. Numa pasta que já existe, o dono continua o mesmo; se ela for do root e estiver vazia, passa para essa pessoa.
- Escreve `/etc/samba/bora-pasta-compartilhada.conf`, com o compartilhamento e os ajustes de segurança, e acrescenta no fim do `/etc/samba/smb.conf` a linha `include` que lê esse arquivo. Um Samba que já existia continua com as próprias pastas. Os ajustes do `[global]` valem para o Samba inteiro.
- Para cada nome em `usuarios` sem conta neste computador, cria uma conta com `/usr/sbin/nologin` e sem pasta pessoal, marcada como "Pasta compartilhada da casa (bora)".
- Gera uma senha para cada pessoa, cadastra com `smbpasswd` e guarda em `/var/lib/bora/pasta-compartilhada/senhas` (só o root lê). Quem já tinha acesso fica com a senha que tinha.
- Liga o `smbd` (e o `wsdd2`) no boot.
- Se o firewall (ufw) estiver ligado, acrescenta as regras com o comentário `bora-samba`: a porta 445/tcp e, com `aparecer_na_rede`, as portas 3702/udp, 5357/tcp e 5355/udp, todas só para a rede local.

## Como conferir

O `testar.sh` roda:

- `testparm -s`: a configuração é válida, e os valores que valem de verdade são os da receita (a pasta, sem visitante, sem SMB1, só a rede local e a senha separada);
- `pdbedit -L`: cada pessoa tem acesso;
- `systemctl is-enabled smbd wsdd2`: o Samba liga no boot;
- `ss -ltn 'sport = :445'`: o Samba espera conexões (quando o systemd está rodando);
- `smbclient`: entra com o nome e a senha da primeira pessoa, cria um arquivo na pasta e apaga, e confere que uma senha errada e um visitante não entram;
- `ufw show added`: as regras da rede local, quando o firewall está ligado.

Para ver você mesmo: num Windows da casa, abra o Explorador de Arquivos e digite `\\endereço\Compartilhado` na barra de endereço, com o endereço que o `bora` mostrou no fim (ou o que `ip -4 addr` mostra). No Mac, Finder, "Ir", "Conectar ao Servidor", `smb://endereço/Compartilhado`. No celular, o app Arquivos do iPhone ("Conectar ao Servidor") ou um app de arquivos com SMB no Android. As senhas: `sudo cat /var/lib/bora/pasta-compartilhada/senhas`. Para trocar a de uma pessoa: `sudo smbpasswd nome`.

## Como desfazer

O `desfazer.sh` remove as regras do firewall, tira o acesso de cada pessoa que a receita cadastrou no Samba, apaga as contas que ela criou (as contas que já existiam ficam), apaga o arquivo de senhas e o arquivo da receita, tira a linha do `smb.conf` (ou volta o que havia antes), devolve a pasta ao dono anterior, se a receita mudou, e remove os pacotes que ela instalou. **A pasta e os arquivos dela ficam**; só sai a pasta que a receita criou e que continua vazia.

## Fontes

- [Manual do smb.conf](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html)
- [Configurar o Samba como servidor de arquivos, na wiki do Samba](https://wiki.samba.org/index.php/Setting_up_Samba_as_a_Standalone_Server)
- [Samba como servidor de arquivos, na documentação do Ubuntu Server](https://documentation.ubuntu.com/server/how-to/samba/file-server/)
- [SambaServerSimple, na wiki do Debian](https://wiki.debian.org/Samba/ServerSimple)
- [wsdd2, no GitHub](https://github.com/Netgear/wsdd2)
