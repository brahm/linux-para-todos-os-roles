# Flatpak e Flathub

## O que faz

Instala o Flatpak e liga o Flathub, a maior loja de aplicativos para Linux, para o sistema todo. Se a loja de aplicativos da distro for o GNOME Software ou o Discover, ela passa a mostrar os aplicativos do Flathub ao lado dos da distro.

## Por que

Os pacotes da distro ficam congelados na versão em que ela saiu. Num Ubuntu LTS ou num Debian, isso quer dizer programas com um, dois ou até três anos de atraso. O Flathub traz a versão mais nova de aplicativos como LibreOffice, GIMP, OBS Studio, Zoom e Anki, publicada muitas vezes pelos próprios autores, e ela funciona igual em qualquer distro.

Cada aplicativo do Flatpak roda num ambiente isolado, com as permissões que declarou. Ele não mexe nos pacotes do sistema, então instalar ou remover um aplicativo nunca quebra a distro.

O Linux Mint já vem com o Flatpak e o Flathub ligados; nele, a receita só confere. O Ubuntu usa o Snap no lugar, e o Flatpak entra ao lado, sem tirar nada.

## O que muda no sistema

- Instala o pacote `flatpak`.
- Com `integrar_loja: sim` (o padrão), instala o plugin que faz a loja da distro mostrar o Flathub: `gnome-software-plugin-flatpak`, se o GNOME Software estiver instalado, e `plasma-discover-backend-flatpak`, se o Discover estiver. A App Center do Ubuntu só mostra Snaps, e nela nada muda.
- Liga o repositório `flathub` para o sistema todo, com `flatpak remote-add --system --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo`. O arquivo `.flatpakrepo` traz o endereço e a chave pública que confere a assinatura de cada aplicativo baixado.
- Se já existir um repositório chamado `flathub` com outro endereço ou desativado, a receita para sem mudar nada, porque alguém configurou assim de propósito.

Nenhum aplicativo é instalado. Para instalar um, use a loja ou o terminal, por exemplo `flatpak install flathub org.libreoffice.LibreOffice`.

Os atalhos dos aplicativos do Flathub aparecem no menu depois que você sair e entrar de novo na sessão, porque é no login que a pasta `/var/lib/flatpak/exports/share` entra na lista de lugares onde o menu procura.

## Como conferir

O `testar.sh` roda:

- `flatpak --version`: o Flatpak está instalado;
- `flatpak remotes --system --columns=name,url`: o `flathub` aparece com o endereço `https://dl.flathub.org/repo/`;
- `flatpak remotes --system --columns=name,options`: o `flathub` não tem a opção `no-gpg-verify`, então a assinatura de cada aplicativo é conferida;
- a existência de `/etc/profile.d/flatpak.sh`, que põe os aplicativos no menu a cada login;
- com `integrar_loja: sim`, que o plugin da loja está instalado.

Para ver você mesmo: `flatpak remotes --show-details`.

## Como desfazer

O `desfazer.sh` remove o `flathub` (se foi a receita que o ligou) e os pacotes que ela instalou, com as dependências que vieram junto.

Se você instalou aplicativos do Flathub depois, o desfazer não remove nada: tirar o Flathub deixaria esses aplicativos sem atualização. Ele avisa quais são e explica como remover tudo à mão, se você quiser.

## Fontes

- [Configuração do Flathub para Ubuntu](https://flathub.org/setup/Ubuntu) e [para Debian](https://flathub.org/setup/Debian)
- [Documentação do Flatpak: comando `flatpak remote-add`](https://docs.flatpak.org/en/latest/flatpak-command-reference.html#flatpak-remote-add)
- [Flatpak, na wiki do Debian](https://wiki.debian.org/Flatpak)
