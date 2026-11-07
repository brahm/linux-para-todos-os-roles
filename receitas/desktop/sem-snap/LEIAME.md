# Sem Snap

## O que faz

Tira o Snap do Ubuntu e impede que o apt o traga de volta. O Firefox do Snap vira o pacote oficial da Mozilla, e o Thunderbird do Snap vira o do Flathub, os dois com os seus favoritos, senhas e e-mails. A loja de aplicativos do Snap vira o GNOME Software. No Debian e no Linux Mint, que não usam o Snap, a receita só deixa o apt bloqueado para ele.

## Por que

O Snap é o jeito do Ubuntu de distribuir aplicativos, e funciona. Mas ele tem custos que pesam numa máquina modesta: cada snap é uma imagem montada no boot, os programas abrem mais devagar na primeira vez, o `snapd` fica rodando o tempo todo, e as atualizações acontecem quando ele decide. Com o Flatpak já ligado pelo rolê, há duas lojas fazendo o mesmo trabalho.

É uma escolha, e não um conserto, por isso a receita só entra quando você pede. Ela é a mais arriscada do rolê: mexe no navegador e nos metapacotes do Ubuntu. Por isso ela para, sem mudar nada, quando encontra um snap que não sabe trocar, ou quando tirar o `snapd` levaria junto um pacote que não é do Snap.

Por que o Firefox da Mozilla, e não o do Flathub? O repositório da Mozilla é o caminho que ela mesma recomenda para Debian e Ubuntu, entrega as atualizações no mesmo dia, e o Firefox continua lendo as políticas de `/etc/firefox/policies`, que a receita `desktop/navegador-leve` usa. A chave do repositório é conferida pela impressão digital que a Mozilla publica antes de entrar no sistema.

## O que muda no sistema

- Lê os snaps instalados em `/var/lib/snapd/snaps`. Se houver algum além das bases, da loja, do atualizador de firmware, do Firefox e do Thunderbird, a receita para e diz qual é.
- Copia o perfil do Firefox de `~/snap/firefox/common/.mozilla/firefox` para `~/.mozilla/firefox`, e o do Thunderbird de `~/snap/thunderbird/common/.thunderbird` para `~/.var/app/org.mozilla.Thunderbird/.thunderbird`, de cada pessoa, antes de tirar o Snap, que apagaria a pasta `~/snap`. Um perfil que já existe no destino não é tocado.
- Marca como instalados de propósito os pacotes que o `ubuntu-desktop` e o `ubuntu-desktop-minimal` puxavam, para o `apt autoremove` nunca levar o ambiente gráfico quando esses metapacotes saem junto com o `snapd`.
- Remove os snaps e o pacote `snapd` (`apt purge snapd`). O snapd guarda um instantâneo automático dos dados de cada snap por 31 dias.
- Escreve `/etc/apt/preferences.d/bora-sem-snap.pref`, com prioridade -10 para o `snapd`: o apt passa a recusar qualquer pacote que o peça, como o `firefox` de transição do Ubuntu.
- Se o Firefox era do Snap: baixa a chave da Mozilla para `/etc/apt/keyrings/packages.mozilla.org.asc`, confere a impressão digital `35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3`, cria `/etc/apt/sources.list.d/mozilla.sources` e `/etc/apt/preferences.d/mozilla.pref` (prioridade 1000 para o repositório da Mozilla) e instala `firefox` e `firefox-l10n-pt-br`.
- Se o Thunderbird era do Snap: instala `org.mozilla.Thunderbird` do Flathub. Precisa do Flathub ligado, pela receita `desktop/flatpak`.
- Se a loja do Snap estava instalada: instala `gnome-software` e, com o Flatpak, o `gnome-software-plugin-flatpak`.

## Como conferir

O `testar.sh` confere:

- que o pacote `snapd` não está instalado e que `/var/lib/snapd/snaps` não tem nenhum snap;
- `apt-cache policy snapd`: o candidato é `(none)`, então o apt não traz o Snap de volta;
- se o Firefox era do Snap, `apt-cache policy firefox`: a versão instalada vem de `packages.mozilla.org`;
- se o Thunderbird era do Snap, `flatpak info org.mozilla.Thunderbird`;
- que os perfis copiados estão nas pastas novas.

Para ver você mesmo: `snap list` responde que o comando não existe, e `firefox --version` mostra a versão da Mozilla.

## Como desfazer

O `desfazer.sh` remove o Firefox da Mozilla, o GNOME Software e o Thunderbird do Flathub que a receita instalou, apaga os arquivos do apt que ela criou, instala de volta o `snapd`, os pacotes de transição e os metapacotes que saíram, e reinstala os snaps de programas (o Firefox, o Thunderbird, a loja e o atualizador de firmware). Os perfis voltam para a pasta do Snap, se ela ainda não tiver um.

As cópias dos perfis em `~/.mozilla` e em `~/.var/app` ficam onde estão: são os seus dados. O desfazer precisa de internet, para baixar os snaps de novo.

## Fontes

- [Instalar o Firefox no Linux, pela Mozilla](https://support.mozilla.org/kb/install-firefox-linux)
- [Repositório APT da Mozilla](https://packages.mozilla.org/apt)
- [apt_preferences(5)](https://manpages.debian.org/stable/apt/apt_preferences.5.en.html)
- [Snap, na documentação do Ubuntu](https://snapcraft.io/docs/getting-started)
