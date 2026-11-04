# Firewall

## O que faz

Liga o firewall (ufw) para bloquear as conexões que chegam de fora e libera só o que o perfil escolhido pede. As conexões que saem do computador continuam liberadas.

## Por que

Muitos programas abrem portas sem avisar: compartilhamento de tela, servidores de desenvolvimento, serviços de impressão. Numa rede de casa isso costuma passar despercebido, mas numa rede pública (café, faculdade, aeroporto) qualquer pessoa conectada consegue tentar falar com essas portas. Com o firewall, nada entra sem ter sido liberado.

O Ubuntu traz o ufw instalado, mas desligado, e o Debian não traz firewall nenhum.

## O que muda no sistema

- Instala o `ufw`, se ainda não estiver instalado.
- Guarda uma cópia de `/etc/ufw` e de `/etc/default/ufw` antes de mudar qualquer coisa.
- Define a política padrão: bloquear o que chega (`deny incoming`) e liberar o que sai (`allow outgoing`).
- Adiciona as regras do perfil, todas com um comentário começando em `bora-`:
  - **`desktop`:** se um servidor SSH estiver escutando, libera a porta dele só para a rede local;
  - **`servidor-lan`:** libera o SSH (porta 22, ou a porta em que o sshd escuta) só para a rede local, mesmo que ele ainda não esteja instalado. Outros serviços, como o Samba e o Jellyfin, liberam a própria porta, também só para a rede local, nas receitas deles;
  - **`tailscale`:** como o `desktop`, e libera o que chega pela interface `tailscale0`, que só recebe conexões de dentro da VPN.
- Liga o firewall e habilita o `ufw.service`, para ele subir sozinho no boot.
- Regras que você já tinha continuam lá.

A rede local (o parâmetro `rede_local`) é descoberta pela interface da rota padrão, e só valem as faixas de rede de casa: `10.0.0.0/8`, `172.16.0.0/12` e `192.168.0.0/16`. Uma rede pública ou de CGNAT nunca é liberada, porque nenhuma receita abre porta para a internet.

### Proteção para quem está conectado por SSH

Antes de ligar o firewall, a receita confere quem está conectado por SSH. Se alguma sessão vier de fora da rede local (ou de fora da VPN, no perfil `tailscale`), ela para sem mudar nada e explica o motivo, porque ligar o firewall cortaria esse acesso.

## Como conferir

O `testar.sh` roda:

- `ufw status`: precisa mostrar `Status: active`;
- `ufw status verbose`: a política padrão precisa ser `deny (incoming), allow (outgoing)`;
- `ufw show added`: cada regra do perfil precisa estar na lista;
- `systemctl is-enabled ufw.service`: o firewall precisa subir no boot.

Para ver as regras você mesmo: `sudo ufw status verbose`.

## Como desfazer

O `desfazer.sh` desliga o firewall e:

- se o ufw foi instalado pela receita, remove o pacote e as dependências que vieram com ele;
- se o ufw já existia, volta `/etc/ufw` e `/etc/default/ufw` à cópia guardada e deixa o firewall ligado ou desligado, como ele estava antes.

## Fontes

- [Firewalls, na documentação do Ubuntu Server](https://documentation.ubuntu.com/server/how-to/security/firewalls/)
- [Uncomplicated Firewall, na wiki do Debian](https://wiki.debian.org/Uncomplicated%20Firewall%20%28ufw%29)
- [Manual do ufw](https://manpages.debian.org/trixie/ufw/ufw.8.en.html)
