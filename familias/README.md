# Famílias de distro

O `bora` agrupa as distros pela base de onde vieram. Uma receita é escrita uma vez e, só onde o comportamento muda de verdade, ganha um script próprio para a família.

## Famílias e ondas

| Família | Gerenciador | Distros | Particularidades | Onda |
|---|---|---|---|:-:|
| `ubuntu` | apt | Ubuntu LTS, Linux Mint, Pop!_OS, Zorin OS | Boa parte das derivadas ainda usa a base 24.04, então são duas bases ativas (24.04 e 26.04). O Mint bloqueia o Snap; o Pop!_OS tem repositório próprio | 1 |
| `debian` | apt | Debian estável | Não traz firewall por padrão; com Xfce ou LXQt, é a melhor base para máquinas antigas | 1 |
| `fedora` | dnf | Fedora, Nobara | Versão nova a cada seis meses; SELinux e firewalld por padrão; codecs pelo RPM Fusion | 2 |
| `arch` | pacman | Arch, CachyOS, EndeavourOS, Manjaro | Rolante; o CachyOS tem repositórios próprios e o Manjaro segura os pacotes do Arch por algumas semanas | 3 |
| `fedora-imutavel` | rpm-ostree ou bootc, mais Flatpak | Bazzite, Silverblue, Kinoite, Bluefin, Aurora | O sistema base não se mexe: apps por Flatpak, serviços em contêiner, desenvolvimento em toolbox ou distrobox; rollback nativo | 3 |
| `opensuse` | zypper | Tumbleweed, Leap | Snapper por padrão; SELinux nas instalações novas; codecs pelo Packman | 4 (comunidade) |

## O que muda entre famílias

| Assunto | `ubuntu` e `debian` | `arch` | `fedora` | `fedora-imutavel` | `opensuse` |
|---|---|---|---|---|---|
| Instalar pacote | apt | pacman | dnf | Flatpak; rpm-ostree só em último caso | zypper |
| Firewall | ufw | ufw | firewalld | firewalld | firewalld |
| Codecs | restricted-extras no Ubuntu; contrib e non-free no Debian | repositório oficial | RPM Fusion | já vem no Bazzite; RPM Fusion nas outras | Packman |
| Snapshot | Timeshift | Timeshift ou snapper | snapper (btrfs) | rollback nativo | snapper |
| Controle de acesso | AppArmor | nenhum por padrão | SELinux | SELinux | SELinux nas novas, AppArmor nas antigas |
| Ciclo | fixo (LTS e estável) | rolante | a cada seis meses | por imagem | rolante (Tumbleweed) ou fixo (Leap) |

## Como o `bora` reconhece a família

O `bora diag` lê o `/etc/os-release` (campos `ID`, `ID_LIKE`, `VERSION_ID` e `UBUNTU_CODENAME`) e confere o processo de init. Derivadas herdam a família da base; as diferenças conhecidas de cada derivada ficam registradas à parte.

## Níveis de suporte

- **testada:** a receita passa nos testes automáticos dessa família a cada mudança. No site, aparece como "testada em contêiner" enquanto o registro de testes da receita (`testes` no `receita.yaml`) só tiver testes em contêiner. Ela só é recomendada sem ressalva depois de passar numa máquina virtual ou num computador de verdade, pelo [roteiro de teste em VM](../testes/vm/README.md); até lá, o `bora` avisa quando monta o plano.
- **herdada:** a derivada usa a receita da base, e o `bora` avisa quando aquela derivada ainda não foi testada.
- **comunidade:** receitas aceitas com relato de teste, sem garantia do projeto.
- **nao-se-aplica:** aparece no menu como indisponível, com o motivo.

## Fora do escopo

- Máquinas de 32 bits.
- Distros sem systemd por padrão (MX Linux, Slackware, Gentoo, Void, Alpine). O `bora` detecta e avisa que a distro não é suportada.
- NixOS, que tem configuração declarativa, e SteamOS, feito para ser console.
- Pacotes do AUR.
