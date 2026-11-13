# Acesso por SSH na rede de casa

## O que faz

Instala e liga o servidor SSH, para entrar neste computador pelo terminal de outro da casa, com `ssh pessoa@endereço`. O root não entra, as tentativas de senha por conexão são poucas e, quando o firewall está ligado, só a rede local é liberada. Com `so_chave: sim`, só entra quem tem uma chave cadastrada.

## Por que

Uma máquina antiga que vira servidor da casa costuma ficar num canto, sem tela nem teclado. O SSH é o jeito de cuidar dela de outro computador: atualizar, ver o espaço em disco, reiniciar um serviço.

A configuração padrão do OpenSSH é segura, mas pensada para qualquer uso. A receita fecha o que uma máquina de casa não precisa:

- o login direto do root (cada pessoa entra com a própria conta e usa `sudo`);
- o login por teclado interativo;
- as senhas vazias;
- o encaminhamento de janelas gráficas.

Como nenhuma receita abre porta para a internet, a liberação no firewall vale só para a rede local. Para entrar de fora de casa, o caminho é uma VPN, como o Tailscale do rolê "Acessar de fora sem abrir portas".

Senha ou chave? A senha funciona na hora e serve para começar. A chave é mais segura, porque não dá para adivinhar, e é o recomendado depois que você copiar a sua com `ssh-copy-id`. A receita só desliga a senha se a conta já tiver uma chave, para ninguém ficar trancado do lado de fora.

## O que muda no sistema

- Instala o pacote `openssh-server`, que cria as chaves do servidor na instalação.
- Escreve `/etc/ssh/sshd_config.d/10-bora.conf` com `PermitRootLogin no`, `PasswordAuthentication yes` (ou `no`, com `so_chave: sim`), `KbdInteractiveAuthentication no`, `PermitEmptyPasswords no`, `MaxAuthTries 4`, `LoginGraceTime 30` e `X11Forwarding no`. O arquivo começa com 10 porque o sshd fica com o primeiro valor que encontra, e assim ele vem antes dos arquivos das distros e do cloud-init.
- Confere a configuração com `sshd -t` antes de recarregar o serviço. Se o sshd recusar, a receita volta o arquivo e para.
- Liga o `ssh.socket` (Ubuntu 24.04 em diante) ou o `ssh.service` (Debian) no boot.
- Se o firewall (ufw) estiver ligado, acrescenta a regra `allow from <rede local> to any port 22 proto tcp`, com o comentário `bora-ssh`. Se não estiver, avisa que o SSH responde em qualquer rede em que o computador estiver, e sugere a receita `seguranca/firewall`.
- Com `so_chave: sim`, confere antes que `~/.ssh/authorized_keys` da conta tem uma chave pública.

## Como conferir

O `testar.sh` roda:

- `sshd -t`: a configuração é válida;
- `sshd -T`: os valores que valem de verdade, conferindo `permitrootlogin no`, `passwordauthentication` e `maxauthtries 4`;
- `systemctl is-enabled ssh.socket` ou `ssh.service`: o SSH liga no boot;
- `ss -ltn 'sport = :22'`: há alguém esperando conexões na porta 22 (quando o systemd está rodando);
- `ufw show added`: a regra da rede local, quando o firewall está ligado.

Para ver você mesmo, de outro computador da casa: `ssh pessoa@endereço`, com o endereço que `ip -4 addr` mostra. Para trocar a senha por chave: `ssh-copy-id pessoa@endereço`, de lá, e depois o `bora` com `so_chave: sim`.

## Como desfazer

O `desfazer.sh` remove a regra do firewall, apaga `/etc/ssh/sshd_config.d/10-bora.conf` (ou volta o que havia antes), desliga no boot o que a receita ligou e remove o `openssh-server`, se foi a receita que o instalou. Quem está conectado por SSH na hora continua conectado, mas uma conexão nova não entra mais.

## Fontes

- [Manual do sshd_config](https://man.openbsd.org/sshd_config)
- [OpenSSH Server, na documentação do Ubuntu Server](https://documentation.ubuntu.com/server/how-to/security/openssh-server/)
- [SSH, na wiki do Debian](https://wiki.debian.org/SSH)
