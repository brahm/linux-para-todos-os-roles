# Roteiro em VM: Pronto para estudar e trabalhar

Comece do snapshot `limpa` da VM, com o segundo disco virtual conectado. Rode nas quatro distros do [README](README.md). Marque cada caixa; o que falhar vira uma linha `resultado` com o problema.

## 1. Preparar o disco do backup

O `bora` nunca formata disco. No terminal da VM, ache o segundo disco com `lsblk` (normalmente `/dev/vdb` ou `/dev/sdb`) e formate em ext4:

```sh
sudo mkfs.ext4 -L backup /dev/vdb
```

## 2. Aplicar o rolê

```sh
sudo bora
```

Escolha "Pronto para estudar e trabalhar", responda **não** para tirar o Snap e aceite os outros padrões. Depois, numa segunda rodada no Ubuntu, repita com **sim** (passo 5).

- [ ] O `bora` mostra o plano com oito receitas (sete, sem o Sem Snap) e termina com "cada receita passou no teste".
- [ ] `sudo bora aplicar` de novo, com o mesmo plano, diz "Tudo já estava aplicado".

## 3. Conferir o que o contêiner não confere

**Sistema atualizado (`base/atualizar`)**

- [ ] `systemctl list-timers apt-daily-upgrade.timer` mostra o próximo disparo.
- [ ] Depois de reiniciar, o sistema sobe normalmente.

**Histórico do /etc (`sistema/etckeeper`)**

- [ ] `sudo git -C /etc log --oneline` mostra registros, inclusive os das receitas seguintes (por exemplo, "saving uncommitted changes" do apt).
- [ ] `systemctl list-timers etckeeper.timer` mostra o próximo disparo.

**Firewall (`seguranca/firewall`)**

- [ ] `sudo ufw status verbose` mostra "Status: active" e "deny (incoming)".
- [ ] Depois de reiniciar, o firewall continua ligado.
- [ ] De outro computador ou do host, `nc -zv <ip da VM> 631` (ou outra porta aberta por um programa) não conecta.

**Snapshot (`sistema/snapshot`)**

- [ ] `sudo timeshift --list` mostra o primeiro snapshot.
- [ ] `systemctl list-timers bora-snapshot.timer` mostra o próximo disparo; no dia seguinte (ou adiantando o relógio da VM), aparece um snapshot novo.
- [ ] Restaurar: crie um arquivo `/etc/teste-bora`, rode `sudo timeshift --restore` com o snapshot anterior, reinicie e confira que o arquivo sumiu.

**Codecs (`desktop/codecs`)**

- [ ] Um vídeo MP4 com H.264 e um MP3 tocam no player padrão da distro (Vídeos/Totem no Ubuntu e no Debian, Celluloid no Mint).

**Flatpak (`desktop/flatpak`)**

- [ ] Instale um aplicativo pequeno, como `flatpak install flathub org.gnome.Calculator`, saia e entre de novo na sessão, e confira que ele aparece no menu.
- [ ] No Ubuntu, a loja do Snap continua lá; no Debian, o GNOME Software mostra os aplicativos do Flathub.

**Backup da pasta pessoal (`sistema/backup-pessoal`)**

- [ ] O disco de backup tem `bora-backup/<máquina>/<conta>/ultimo/` com os seus arquivos.
- [ ] Desconecte o disco virtual, crie um arquivo na pasta pessoal, conecte de novo: em alguns minutos aparece uma cópia nova, com o arquivo.
- [ ] Recupere um arquivo abrindo a pasta da data no gerenciador de arquivos e copiando.

## 4. Desfazer

```sh
sudo bora desfazer
```

- [ ] O firewall volta a estar desligado (como era), `timeshift`, `etckeeper` e `flatpak` não estão mais instalados, e o `/etc/.git` saiu (com uma cópia em `/var/backups`).
- [ ] As cópias do backup continuam no disco externo.
- [ ] Depois de reiniciar, o sistema sobe normalmente.

## 5. Sem Snap (só Ubuntu, a partir do snapshot `limpa`)

Use uma instalação do Ubuntu com a opção "instalação completa" (ou "extended"), que já traz o Thunderbird do Snap. Se ele não vier, instale com `sudo snap install thunderbird`.

Antes, abra o Firefox, entre num site, salve um favorito e uma senha, e feche o Firefox. Abra o Thunderbird, configure uma conta de e-mail de teste (ou só um perfil local, em "Pastas locais"), crie uma pasta com o nome `teste-bora` e feche o Thunderbird.

```sh
sudo bora
```

Escolha o rolê e responda **sim** para tirar o Snap.

- [ ] `snap list` responde que o comando não existe.
- [ ] O Firefox abre pelo menu, em português, com o favorito e a senha salvos.
- [ ] `apt-cache policy firefox` mostra a versão de `packages.mozilla.org`.
- [ ] `sudo apt install snapd` recusa instalar.
- [ ] `flatpak list` mostra o `org.mozilla.Thunderbird`, e o `snap list` não mostra mais o Thunderbird.
- [ ] O Thunderbird abre pelo menu e mostra a conta de teste e a pasta `teste-bora`; o perfil está em `~/.var/app/org.mozilla.Thunderbird/.thunderbird`.
- [ ] A loja de aplicativos (GNOME Software) abre e mostra aplicativos do Flathub.
- [ ] Depois de reiniciar, o boot não mostra montagens de snap (`systemd-analyze blame | grep snap` não mostra nada).
- [ ] `sudo bora desfazer`: o Snap, o Firefox e o Thunderbird do Snap voltam. O Firefox abre com o favorito, e o Thunderbird com a pasta `teste-bora`; o Thunderbird do Flathub saiu de `flatpak list`.

No Linux Mint e no Debian, o Sem Snap só bloqueia o apt:

- [ ] `apt-cache policy snapd` mostra "Candidate: (none)".

## 6. Registrar

Siga o [README](README.md#registrar-o-resultado), com uma linha por receita e por distro.
