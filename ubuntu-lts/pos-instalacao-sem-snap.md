# Ubuntu 26.04 LTS (Resolute Raccoon): Roteiro de Pós-Instalação

## 1. Executar a primeira atualização completa do sistema

Elimina todas as falhas de segurança existentes entre a data de lançamento da ISO e o momento atual, garantindo que você esteja utilizando as versões mais recentes do kernel e dos pacotes antes de realizar qualquer outra alteração.

```bash
sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade -y
sudo apt autoremove -y && sudo apt autoclean
sudo systemctl reboot
```

O parâmetro `dist-upgrade` é importante aqui. Ao contrário do comando `apt upgrade` simples, ele gerencia corretamente as alterações de dependência associadas às atualizações do kernel, garantindo que a nova imagem do kernel 7.0 seja efetivamente instalada e definida como padrão no GRUB.

## 2. Desativar a economia de energia do Wi-Fi

O gerenciamento agressivo de energia reduz o desempenho do adaptador para economizar bateria, limitando severamente a largura de banda. - Abra o Terminal e edite a configuração do NetworkManager:

```bash
sudo nano /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf
```

Altere `wifi.powersave = 3` (ativado) para `wifi.powersave = 2` (desativado). - Salve e saia (pressione `Ctrl+O`, `Enter` e, em seguida, `Ctrl+X`). - Reinicie o serviço de rede:

```bash
sudo service NetworkManager restart
```

## 3. Ativar o firewall UFW

O UFW vem instalado por padrão no Ubuntu, mas desativado, deixando sua máquina totalmente exposta.

### Configuração completa para laptop

```bash
# Base segura
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH - apenas rede local
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp

# SMB - apenas rede local (NUNCA abrir em rede pública)
sudo ufw allow from 192.168.1.0/24 to any port 445 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 139 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 137:138 proto udp

# LLM - Servir modelos para outras máquinas (apenas rede local)
sudo ufw allow from 192.168.1.0/24 to any port 11434 proto tcp  # Ollama
sudo ufw allow from 192.168.1.0/24 to any port 1234 proto tcp   # LM Studio
sudo ufw allow from 192.168.1.0/24 to any port 8000 proto tcp   # vLLM / llama.cpp
sudo ufw allow from 192.168.1.0/24 to any port 3000 proto tcp   # Open WebUI

# Desenvolvimento web - apenas rede local (testar de outros dispositivos)
sudo ufw allow from 192.168.1.0/24 to any port 80,443,5173,8080 proto tcp

# BitTorrent - precisa aceitar conexões de qualquer origem para funcionar bem
sudo ufw allow 6881/tcp
sudo ufw allow 6881/udp

# Syncthing - P2P sync
sudo ufw allow 22000/tcp
sudo ufw allow 22000/udp
sudo ufw allow from 192.168.1.0/24 to any port 21027 proto udp  # discovery local

sudo ufw enable
```

Substitua `192.168.1.0/24` pela sua sub-rede real (`ip -4 addr` mostra).

#### Dicas específicas de laptop

1. **Redes públicas**: as regras `from 192.168.1.0/24` já protegem — em outra rede, nada responde. Se quiser desligar tudo rapidamente: `sudo ufw deny 6881 && sudo ufw deny 22000`.
2. **Bateria + torrent**: cliente torrent aberto acordando o rádio Wi-Fi constantemente drena bateria; feche quando não usar.
3. **LLM na rede sem autenticação**: Ollama não tem senha. Restringir à rede local é essencial; para acesso remoto seguro, use túnel SSH (`ssh -L 11434:localhost:11434 usuario@laptop`) ou Tailscale.
4. **Verificar**: `sudo ufw status numbered` e teste de outra máquina com `curl http://IP:11434`.

### Configuração geral

```bash
# SSH
sudo ufw allow 22/tcp

# WEB - Desenvolvimento
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# EMAIL - Cliente
sudo ufw allow 143/tcp   # IMAP
sudo ufw allow 993/tcp   # IMAP-SSL
sudo ufw allow 110/tcp   # POP3
sudo ufw allow 995/tcp   # POP3-SSL
sudo ufw allow 587/tcp   # SMTP (envio)
sudo ufw allow 25/tcp    # SMTP (servidor)

# SMB - Compartilhamento arquivos (Samba)
sudo ufw allow 137,138/udp
sudo ufw allow 139,445/tcp

# SYNCTHING - Sincronização P2P
sudo ufw allow 22000/tcp
sudo ufw allow 22000/udp
sudo ufw allow 21027/udp  # Discovery

# RESILIO SYNC - P2P backup
sudo ufw allow 6881:6889/tcp
sudo ufw allow 6881:6889/udp

# SYNOLOGY/NAS Virtual - WebDAV
sudo ufw allow 8008/tcp   # HTTP alt
sudo ufw allow 8443/tcp   # HTTPS alt

# NEXTCLOUD/Owncloud - Cloud P2P
sudo ufw allow 8080/tcp

# IPFS - Peer-to-peer file system
sudo ufw allow 4001/tcp
sudo ufw allow 4001/udp
sudo ufw allow 5001/tcp   # API local

# TRANSMISSION/qBittorrent - Torrent (já tem acima, mas mantém)
sudo ufw allow 6881:6999/tcp
sudo ufw allow 6881:6999/udp

# GIT Server (Gitea/Gitolite)
sudo ufw allow 3000/tcp   # Gitea web
sudo ufw allow 2222/tcp   # Git SSH alternativo

# MINECRAFT/Game Servers
sudo ufw allow 25565/tcp  # Minecraft Java

# VNC/Remote Desktop
sudo ufw allow 5900/tcp
sudo ufw allow 5901/tcp

# Applicar
sudo ufw reload
```

### UFW para Homelab

Num homelab a lista de portas cresce rápido. Duas abordagens abaixo — recomendo a primeira.

#### Abordagem recomendada: reverse proxy

Em vez de abrir 20 portas, rode um reverse proxy (Nginx Proxy Manager, Caddy ou Traefik) e exponha só ele. Cada serviço vira `jellyfin.home.lan`, `paperless.home.lan`, etc.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp

# Reverse proxy - todo acesso web passa por aqui
sudo ufw allow from 192.168.1.0/24 to any port 80,443 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 81 proto tcp  # admin do NPM

sudo ufw enable
```

Só serviços que não falam HTTP (SMB, torrent, DLNA) precisam de regras próprias.

#### Abordagem direta: porta por serviço

Se preferir acessar cada serviço pela porta:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

LAN=192.168.1.0/24

# ACESSO E ARQUIVOS
sudo ufw allow from $LAN to any port 22 proto tcp            # SSH
sudo ufw allow from $LAN to any port 445,139 proto tcp       # SMB
sudo ufw allow from $LAN to any port 137:138 proto udp       # SMB discovery
sudo ufw allow 22000/tcp                                     # Syncthing
sudo ufw allow 22000/udp
sudo ufw allow from $LAN to any port 21027 proto udp         # Syncthing discovery

# MÍDIA
sudo ufw allow from $LAN to any port 8096 proto tcp          # Jellyfin
sudo ufw allow from $LAN to any port 32400 proto tcp         # Plex
sudo ufw allow from $LAN to any port 1900 proto udp          # DLNA discovery
sudo ufw allow from $LAN to any port 8324,32469 proto tcp    # Plex DLNA
sudo ufw allow from $LAN to any port 4533 proto tcp          # Navidrome (música)
sudo ufw allow from $LAN to any port 2283 proto tcp          # Immich (fotos)

# DOWNLOADS / *ARR
sudo ufw allow from $LAN to any port 8081 proto tcp          # qBittorrent WebUI
sudo ufw allow 6881/tcp                                      # BitTorrent (qualquer origem)
sudo ufw allow 6881/udp
sudo ufw allow from $LAN to any port 7878 proto tcp          # Radarr
sudo ufw allow from $LAN to any port 8989 proto tcp          # Sonarr
sudo ufw allow from $LAN to any port 9696 proto tcp          # Prowlarr
sudo ufw allow from $LAN to any port 5055 proto tcp          # Jellyseerr

# DOCUMENTOS E CLOUD
sudo ufw allow from $LAN to any port 8000 proto tcp          # Paperless-ngx
sudo ufw allow from $LAN to any port 8443 proto tcp          # Nextcloud
sudo ufw allow from $LAN to any port 8065 proto tcp          # Vaultwarden (senhas)

# LLM
sudo ufw allow from $LAN to any port 11434 proto tcp         # Ollama
sudo ufw allow from $LAN to any port 3000 proto tcp          # Open WebUI
sudo ufw allow from $LAN to any port 8188 proto tcp          # ComfyUI (imagens)

# INFRAESTRUTURA
sudo ufw allow from $LAN to any port 9443 proto tcp          # Portainer (Docker)
sudo ufw allow from $LAN to any port 8123 proto tcp          # Home Assistant
sudo ufw allow from $LAN to any port 53 proto tcp            # Pi-hole/AdGuard DNS
sudo ufw allow from $LAN to any port 53 proto udp
sudo ufw allow from $LAN to any port 3001 proto tcp          # Uptime Kuma (monitoramento)
sudo ufw allow from $LAN to any port 19999 proto tcp         # Netdata (métricas)

sudo ufw enable
```

### UFW para Homelab com Tailscale/NetBird

Isso simplifica drasticamente o firewall: em vez de uma regra por serviço, você libera **a interface da VPN inteira** e deixa o controle de acesso para as ACLs do Tailscale/NetBird.

#### Configuração enxuta

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Confiar na interface da VPN mesh (todos os serviços acessíveis via VPN)
sudo ufw allow in on tailscale0     # Tailscale
# ou
sudo ufw allow in on wt0            # NetBird

# Conexões diretas P2P da VPN (evita passar por relay = mais rápido)
sudo ufw allow 41641/udp            # Tailscale
sudo ufw allow 51820/udp            # NetBird (WireGuard)

# SSH direto pela LAN (fallback caso a VPN caia)
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp

# BitTorrent - P2P precisa de porta pública real, VPN não resolve
sudo ufw allow 6881/tcp
sudo ufw allow 6881/udp

sudo ufw enable
```

Pronto — Jellyfin, Ollama, Paperless, Immich, SMB e tudo mais ficam acessíveis de qualquer dispositivo na sua tailnet, sem uma regra por porta.

#### Acesso pela LAN sem VPN (opcional)

Se dispositivos da casa (TV, celular da família) acessarem sem cliente VPN instalado, mantenha as regras de LAN dos serviços que eles usam:

```bash
LAN=192.168.1.0/24
sudo ufw allow from $LAN to any port 8096 proto tcp     # Jellyfin p/ TV
sudo ufw allow from $LAN to any port 445,139 proto tcp  # SMB
sudo ufw allow from $LAN to any port 137:138 proto udp
sudo ufw allow from $LAN to any port 53 proto tcp       # Pi-hole (se usar)
sudo ufw allow from $LAN to any port 53 proto udp
```

Alternativa à interface: liberar pela sub-rede da VPN (ambos usam a faixa CGNAT):

```bash
sudo ufw allow from 100.64.0.0/10
```

Prefira a regra por interface (`allow in on tailscale0`) — é mais segura, pois ninguém consegue forjar a interface.

#### Notas específicas

1. **Controle de acesso migra para as ACLs.** No Tailscale, use ACLs para dizer "o laptop da família só acessa a porta 8096, meu notebook acessa tudo". No NetBird, use policies por grupos. É mais granular e gerenciável que UFW.
2. **Docker continua ignorando o UFW** — mas com VPN isso importa menos: publique os containers como `-p 127.0.0.1:PORTA:PORTA` ou na interface da VPN, e nada vaza para a LAN/internet.
3. **BitTorrent é a exceção**: precisa de porta aberta de verdade (e port-forward no roteador) para boa conectividade. Todo o resto deixa de precisar de qualquer porta exposta no roteador.
4. **Tailscale extras úteis**: `tailscale serve` publica um serviço com HTTPS automático dentro da tailnet; MagicDNS dá nomes tipo `homelab:8096`; Taildrop transfere arquivos. NetBird tem DNS interno equivalente.
5. **Pi-hole como DNS da tailnet**: configure o IP da VPN do homelab como DNS global no painel do Tailscale/NetBird e tenha ad-blocking fora de casa também.
6. **Verifique**: `tailscale status` (ou `netbird status`), depois de outro dispositivo na VPN: `curl http://100.x.x.x:11434`.

A superfície de ataque cai para: SSH na LAN, BitTorrent e as portas UDP da VPN. Todo o resto fica invisível para quem não está na sua rede mesh.

#### Servir LLMs — além do firewall

Abrir a porta não basta; os servidores LLM escutam só em localhost por padrão:

```bash
# Ollama: fazer escutar na rede
sudo systemctl edit ollama
# adicione:
# [Service]
# Environment="OLLAMA_HOST=0.0.0.0"

# llama.cpp
llama-server --host 0.0.0.0 --port 8000

# LM Studio: Settings > Server > "Serve on Local Network"
```

**Acessar LLM de outra máquina**: nenhuma regra necessária. Só aponte o cliente para `http://IP_DO_SERVIDOR:11434`.

### Verificar e gerenciar

```bash
# Ver todas as regras numeradas
sudo ufw status numbered

# Ver logs de bloqueios
sudo tail -f /var/log/ufw.log

# Desabilitar temporariamente
sudo ufw disable

# Deletar regra específica
sudo ufw delete allow 25/tcp
```

### Dicas de segurança

1. **Email SMTP entrada (porta 25)** - abra apenas se rodar servidor de email próprio
2. **SSH (porta 22)** - considere mudar para porta não-padrão:

```bash
   sudo ufw delete allow 22/tcp
   sudo ufw allow 2222/tcp
```

3. **Syncthing/IPFS** - exigem porta pública, configure senha
4. **Serviços locais apenas** - use `sudo ufw allow from 192.168.1.0/24` para rede interna
5. **Fail2ban** - para brute force SSH:

```bash
   sudo apt install fail2ban
```

Pronto para um servidor full-stack!

## 4. Ativar a Criptografia de Disco Completo Baseada em TPM

No Ubuntu 26.04 isso ficou mais simples porque o dracut virou o initramfs padrão, com suporte nativo a desbloqueio via TPM — não é mais preciso gambiarra com initramfs-tools.

### Pré-requisitos

1. No BIOS (F2 na inicialização): ative **Security Chip / AMD fTPM** e mantenha o **Secure Boot ativado** (o PCR 7 depende dele).
2. O disco já deve estar criptografado com LUKS2 (opção marcada na instalação do Ubuntu).

### Passos

```bash
# 1. Confirme o TPM 2.0
systemd-analyze has-tpm2

# 2. Identifique a partição LUKS (geralmente nvme0n1p3)
lsblk
sudo cryptsetup luksDump /dev/nvme0n1p3 | head   # deve mostrar "Version: 2"

# 3. Instale as ferramentas
sudo apt install tpm2-tools tpm2-tss

# 4. (Recomendado) Gere uma chave de recuperação antes
sudo systemd-cryptenroll --recovery-key /dev/nvme0n1p3

# 5. Registre o TPM no LUKS (pedirá a senha atual)
sudo systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs=7 /dev/nvme0n1p3
```

6. Edite `/etc/crypttab` e adicione `tpm2-device=auto` às opções da linha existente, por exemplo:

```
dm_crypt-0 UUID=xxxx-xxxx none luks,discard,tpm2-device=auto
```

7. Regenere o initramfs e reinicie:

```bash
sudo dracut -f
sudo reboot
```

O sistema deve inicializar direto para a tela de login, sem pedir a senha do disco.

### Avisos importantes

- **Não remova a senha original do LUKS** — ela é o fallback se o TPM falhar.
- Atualizações de BIOS ou mudança no estado do Secure Boot alteram o PCR 7 e o boot volta a pedir a senha. Refaça o passo 5 com `--wipe-slot=tpm2` adicionado.
- No fTPM da AMD, um "Reset fTPM" no BIOS apaga as chaves — mesma solução: re-registrar.
- Segurança: com TPM sem PIN, qualquer pessoa que ligar o notebook chega à tela de login. Use senha de usuário forte, ou use `--tpm2-with-pin=yes` no passo 5 para exigir um PIN (mais curto que a senha LUKS) no boot.

## 5. Remover Snap e pacotes pré-instalados

Se você deseja remover o Snap no Ubuntu 26.04, tem duas opções: remover pacotes Snap individuais ou remover completamente todo o daemon snapd e o ecossistema do seu sistema. Muitos usuários optam por remover o snapd para reduzir a complexidade do sistema, evitar atualizações automáticas ou substituir pacotes Snap por alternativas tradicionais via APT.

## Listar Snaps Instalados

Antes de remover um snap no Ubuntu 26.04, é importante saber exatamente quais pacotes snap estão instalados atualmente no seu sistema. Remover o snapd enquanto ainda há snaps ativos pode deixar para trás pontos de montagem e diretórios órfãos. Para ver todos os snaps instalados, execute:

```bash
snap list

Name                       Version          Rev    Tracking       Publisher   Notes
bare                       1.0              5      latest/stable  canonical✓  base
core24                     20260211         1499   latest/stable  canonical✓  base
desktop-security-center    0+git.d4994c6    105    1/stable/…     canonical✓  -
firefox                    148.0.2-1        7966   latest/stable  mozilla✓    -
firmware-updater           0+git.fd7581a    212    1/stable/…     canonical✓  -
gnome-46-2404              0+git.f1cd5fa    153    latest/stable  canonical✓  -
gtk-common-themes          0.1-81-g442e511  1535   latest/stable  canonical✓  -
mesa-2404                  25.0.7-snap211   1165   latest/stable  canonical✓  -
prompting-client           0+git.e482705    185    1/stable/…     canonical✓  -
snap-store                 0+git.515109e7   1310   2/stable/…     canonical✓  -
snapd                      2.74.1           26698  latest/edge    canonical✓  snapd
snapd-desktop-integration  0.9              ...    latest/stable  canonical✓  -
```

## Remover pacotes Snap individuais

Se você deseja remover apenas pacotes Snap específicos, em vez de desativar todo o sistema Snap, utilize o comando `snap remove`. A flag `--purge` remove o pacote Snap juntamente com todos os seus dados salvos, o que é recomendado para uma remoção completa.

1. Remover os pacores Snap: Utilize o comando a seguir, substituindo o nome do pacote pelo Snap que você deseja remover:
  

```bash
sudo snap remove --purge firefox
sudo snap remove --purge snap-store
sudo snap remove --purge firmware-updater
sudo snap remove --purge desktop-security-center
sudo snap remove --purge prompting-client
sudo snap remove --purge snapd-desktop-integration
sudo snap remove --purge gnome-46-2404
sudo snap remove --purge gtk-common-themes
sudo snap remove --purge mesa-2404
sudo snap remove --purge core24
sudo snap remove --purge bare
```

Confirme se o snap foi removido executando `snap list` novamente. O pacote não deve mais aparecer na saída:

```bash
snap list
```

## Remover completamente o snapd no Ubuntu 26.04

A remoção completa do snapd envolve interromper seus serviços, remover o pacote (incluindo arquivos de configuração) e limpar as configurações residuais. Esta é a maneira mais eficaz de realizar uma remoção total do snap no Ubuntu 26.04.

Antes de remover o pacote completamente (*purge*), recarregue as unidades do *systemd* para evitar avisos e, em seguida, interrompa todos os serviços em execução relacionados ao snapd:

```bash
sudo systemctl daemon-reload
sudo systemctl stop snapd snapd.socket snapd.seeded.service
```

Pular a etapa de recarregamento do *daemon* (*daemon-reload*) não impede que a interrupção ocorra com sucesso, mas gera avisos sobre arquivos de unidade alterados no disco.

Use o subcomando `purge` para remover o pacote juntamente com todos os seus arquivos de configuração:

```bash
sudo apt purge snapd
```

O comando `purge` vai além do comando `remove`, pois também exclui arquivos de configuração de todo o sistema associados ao snapd. Após remover o snapd, limpe quaisquer pacotes que tenham sido instalados como dependências e que não sejam mais necessários:

```bash
sudo apt autoremove --purge
```

Confirme se a remoção foi bem-sucedida:

```bash
which snapd
snap --version
```

Ambos os comandos não devem retornar nenhuma saída ou devem exibir um erro de "comando não encontrado" (*command not found*), confirmando que o snapd foi totalmente removido.

## Impedir a reinstalação do Snapd

Uma frustração comum é que o snapd pode ser instalado silenciosamente como uma dependência ao instalar certos pacotes via APT. Para evitar isso, você pode utilizar duas técnicas complementares.

Utilize o mecanismo de bloqueio (*hold*) do APT para marcar o snapd, impedindo que ele seja instalado, atualizado ou reinstalado automaticamente:

```bash
sudo apt-mark hold snapd
```

Consequentemente, qualquer operação do APT que acionasse a instalação do snapd será bloqueada. Para uma solução mais robusta, crie um arquivo de preferências do APT que proíba explicitamente o snapd:

```bash
sudo tee /etc/apt/preferences.d/no-snap.pref > /dev/null <<'EOF'
Package: snapd
Pin: release a=*
Pin-Priority: -10
EOF
```

Salve e feche o arquivo. Essa configuração instrui o APT a sempre atribuir uma prioridade negativa ao snapd, bloqueando efetivamente sua instalação a partir de qualquer repositório.

Confirme que está bloqueado:

```bash
apt-cache policy snapd
```

> **IMPORTANTE:** Se você decidir reinstalar o snapd mais tarde, deverá primeiro remover o arquivo de preferências e liberar o pacote com o comando `sudo apt-mark unhold snapd` para que o APT permita a instalação.

## Remover diretórios residuais do Snap

Mesmo após remover o snapd, vários diretórios podem permanecer no sistema de arquivos. Isso inclui pontos de montagem, diretórios de dados do snap e pastas de cache. Removê-los garante um sistema totalmente limpo.

Os todos os diretórios onde o snap armazenava, respectivamente, snaps montados e dados de snaps, cache e dados de usuário:

```bash
sudo rm -rf /snap /var/snap /var/lib/snapd /var/cache/snapd ~/snap
```

Se houver várias contas de usuário no sistema, repita este passo para o diretório home de cada usuário.

Após remover os pontos de montagem do snap, recarregue o systemd para limpar quaisquer referências obsoletas de unidades:

```bash
sudo systemctl daemon-reload
sudo reboot
```

Confirme que está bloqueado:

```bash
apt-cache policy snapd
```

> A partir de agora, qualquer `apt install` que dependa de snapd vai avisar em vez de instalar silenciosamente.

### O impacto de remover o suporte a Snaps usando o Ubuntu Pro

O impacto é **significativo**, especialmente se você depende dos recursos do Ubuntu Pro:

1. **Perda do Livepatch** — O recurso mais crítico do Ubuntu Pro:
  

- O `canonical-livepatch` é distribuído como snap
- Sem snaps, você **não pode aplicar atualizações de kernel ao vivo**
- Seu sistema precisará de reinicializações completas para patches de segurança do kernel
- Reduz o tempo de atividade em servidores/laptops que exigem continuidade

2. **Aplicações Forçadas como Snaps em 26.04**:
  

- Firefox, Software Store, e ferramentas do sistema agora vêm como snaps por padrão
- Remover snapd quebrará essas dependências
- Canonical adicionou hooks para **reinstalar automaticamente snapd** — muito difícil manter removido

Os impactos secundários da remoção do Snap são:

- Conflito constante entre APT e snapd (snapd se reinstala sozinho)
- Restrições do Ubuntu Pro podem não funcionar corretamente
- Ferramentas de segurança/monitoramento podem depender de snaps
- Atualizações futuras podem quebrar ao tentar restaurar snapd

**Recomendação:**

Se você precisa de Ubuntu Pro, **não remova suporte a snaps completamente**. Em vez disso:

- Use `snap remove` para desinstalacões específicas (não snapd)
- Crie bloqueios seletivos no APT para apps específicas
- Mantenha snapd para aproveitar o Livepatch e segurança

A remoção completa de snaps em Ubuntu 26.04 com Ubuntu Pro é contraproducente.

## 6. Substituir os aplicativos que eram Snap

### Instalar o pacote DEB do Firefox

Para instalar o pacote DEB através do repositório APT, faça o seguinte:

1. Crie um diretório para armazenar as chaves do repositório APT, caso ele ainda não exista:
  

```bash
sudo install -d -m 0755 /etc/apt/keyrings
```

2. Importe a chave de assinatura do repositório APT da Mozilla:
  

```bash
wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
```

Se você não tiver o wget instalado, pode instalá-lo com: sudo apt-get install wget

3. A impressão digital (fingerprint) deve ser **35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3**. Você pode verificá-la com o seguinte comando:
  

```
gpg -n -q --import --import-options import-show /etc/apt/keyrings/packages.mozilla.org.asc | awk '/pub/{getline; gsub(/^ +| +$/,""); if($0 == "35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3") print "\nThe key fingerprint matches ("$0").\n"; else print "\nVerification failed: the fingerprint ("$0") does not match the expected one.\n"}'
```

4. Em seguida, adicione o repositório APT da Mozilla ao seu sources.list:
  

```bash
sudo tee /etc/apt/sources.list.d/mozilla.sources > /dev/null << EOF
Types: deb
URIs: https://packages.mozilla.org/apt
Suites: mozilla
Components: main
Signed-By: /etc/apt/keyrings/packages.mozilla.org.asc
EOF
```

5. Configure o APT para priorizar pacotes do repositório da Mozilla:
  

```bash
sudo tee /etc/apt/preferences.d/mozilla > /dev/null << EOF
Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000
EOF
```

6. Atualize sua lista de pacotes e instale o Firefox (ou uma das versões firefox-esr, -beta, -nightly, -devedition):
  

```bash
sudo apt-get update
sudo apt-get install firefox 
```

#### Usar idiomas diferentes no pacote DEB do Firefox

Para aqueles que desejam usar o Firefox em um idioma diferente do inglês americano, também criamos pacotes DEB contendo os pacotes de idioma do Firefox. Para instalar um pacote de idioma específico, substitua `fr` no exemplo abaixo pelo código do idioma desejado. Neste exemplo, estamos instalando o pacote de idioma francês do Firefox.

```bash
sudo apt-get install firefox-l10n-fr
```

Para listar todos os pacotes de idioma disponíveis, você pode usar este comando após adicionar o repositório da Mozilla e executar `sudo apt-get update`:

```bash
apt-cache search firefox-l10n
```

Localizações também estão disponíveis como pacotes `firefox-esr-l10n`, `-beta-l10n`, `-nightly-l10n` e `-devedition-l10n` para outras versões/edições.

#### Migração de dados

Se você utilizava o Snap anteriormente, é necessário importar seu perfil.

Copie os arquivos existentes no seu computador. Certifique-se de que todas as instâncias do Firefox no seu computador estejam completamente fechadas antes de realizar este procedimento:

```bash
mkdir -p ~/.mozilla/firefox/ && cp -a ~/snap/firefox/common/.mozilla/firefox/* ~/.mozilla/firefox/
```

Após mover os perfis, inicie o Firefox pelo terminal com o comando `firefox -P`. Selecione o perfil desejado. Após essa configuração inicial, o comando `-P` não será mais necessário.

### Central de apps (substitui a Snap Store)

```bash
sudo apt install gnome-software
```

## 7. Habilitar o Flatpak e o repositório Flathub

O Flatpak oferece um vasto catálogo de aplicativos de desktop em ambiente isolado (*sandbox*) e com atualização automática — muitas vezes mais recentes do que suas versões via APT —, sem depender da controversa infraestrutura do Snap. O repositório Flathub conta atualmente com mais de 3.000 aplicativos.

```bash
sudo apt install flatpak gnome-software-plugin-flatpak
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
sudo systemctl reboot
```

Após reiniciar o sistema, o aplicativo GNOME Software carregará o catálogo do Flathub, permitindo que você instale aplicativos como VLC, Inkscape e Kdenlive diretamente pela interface gráfica, com permissões em ambiente isolado (*sandbox*).

## 8. Codecs de áudio e vídeo (suporte completo)

```bash
echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | sudo debconf-set-selections

sudo apt install -y ubuntu-restricted-extras \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav gstreamer1.0-vaapi \
  ffmpeg x264 x265 libavcodec-extra \
  libdvd-pkg
```

Durante a instalação do `ubuntu-restricted-extras`, aceite a licença das fontes Microsoft quando solicitado.

Finalize a configuração do DVD (CSS):

```bash
sudo dpkg-reconfigure libdvd-pkg
```

Aceleração de vídeo por hardware (VA-API):

```bash
sudo apt install vainfo mesa-va-drivers
vainfo   # confirma se a aceleração está ativa
```

## 9. Install Essential Development Tools

O metapacote `build-essential`, combinado com um conjunto selecionado de utilitários para desenvolvedores, proporciona um ambiente de desenvolvimento totalmente funcional em poucos minutos, abrangendo compilação em C/C++, controle de versão com Git e gerenciamento de ambientes Python.

Mesmo que você não seja um desenvolvedor em tempo integral, muitos scripts de administração e ferramentas de terceiros exigem um ambiente de compilação funcional.

```bash
sudo apt install build-essential git curl wget python3-pip python3-venv ca-certificates gnupg lsb-release btop neofetch autoconf bison patch libssl-dev libyaml-dev libreadline-dev zlib1g-dev libncurses-dev libffi-dev libgdbm-dev libpq-dev sqlite3 libsqlite3-dev redis-server meson ninja-build pkg-config libgtk-4-dev libadwaita-1-dev libglib2.0-dev libgirepository1.0-dev gettext desktop-file-utils appstream-util blueprint-compiler gnome-devel-docs gnome-builder
```

O pacote `python3-venv` é particularmente importante porque o Ubuntu 26.04 aplica a PEP 668 por padrão, impedindo instalações globais via `pip` fora de um ambiente virtual. Ter o `venv` pré-instalado garante que você possa criar ambientes de projeto isolados sem etapas adicionais.

## 10. Containers — Docker Engine + Compose

Chave e repositório oficiais:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Verifique se o repositório já reconhece o codename do 26.04 (`resolute`):

```bash
curl -fsSL "https://download.docker.com/linux/ubuntu/dists/resolute/Release"
```

- Se retornar conteúdo → use `resolute` no comando abaixo.
- Se der erro 404 → use `noble` no lugar (é comum logo após o lançamento de uma LTS nova, antes de o Docker publicar o repositório correspondente).

```bash
CODENAME=resolute   # ou "noble" se o teste acima falhou

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $CODENAME stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Instalação:

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Usar o Docker sem `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```

**(Opcional)** Podman como alternativa sem daemon:

```bash
sudo apt install -y podman
```

## 11. Servidor LAMP (Apache + MariaDB + PHP)

```bash
sudo apt install -y apache2
sudo systemctl enable --now apache2
```

```bash
sudo apt install -y mariadb-server mariadb-client
sudo systemctl enable --now mariadb
sudo mysql_secure_installation
```

Siga o assistente interativo do `mysql_secure_installation` (defina senha de root, remova usuários anônimos, etc).

```bash
sudo apt install -y php libapache2-mod-php php-mysql php-cli php-curl php-gd php-mbstring php-xml php-zip php-bcmath
sudo systemctl restart apache2
```

Teste criando um arquivo:

```bash
echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/info.php
```

Acesse `http://localhost/info.php` no navegador. **Depois de testar, apague o arquivo** (expõe informação sensível do servidor):

```bash
sudo rm /var/www/html/info.php
```

## 12.Ambiente de desenvolvimento — Ruby on Rails

Dependências de build:

```bash
sudo apt install -y autoconf bison patch libssl-dev libyaml-dev libreadline-dev \
  zlib1g-dev libncurses-dev libffi-dev libgdbm-dev libpq-dev sqlite3 libsqlite3-dev redis-server
```

** rbenv + ruby-build:

```bash
git clone https://github.com/rbenv/rbenv.git ~/.rbenv
git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build

echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(rbenv init -)"' >> ~/.bashrc
source ~/.bashrc
```

** Instale a versão mais recente do Ruby:

```bash
rbenv install -l                 # veja a última versão estável listada
rbenv install 3.4.x               # troque 3.4.x pela versão que apareceu
rbenv global 3.4.x
ruby -v                           # confirma
```

** Rails e Bundler:

```bash
gem install bundler rails
```

** Node.js LTS + Yarn (assets do Rails):

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
corepack enable
corepack prepare yarn@stable --activate
```

** PostgreSQL (banco padrão recomendado para Rails):

```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

** Teste tudo criando um projeto novo:

```bash
rails new meuapp --database=postgresql
cd meuapp
bin/rails server
```

## 13. Ambiente de desenvolvimento — Rust + GNOME 50

Instale o Rust via rustup:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup component add rust-analyzer clippy rustfmt
```

Toolchain de build e bibliotecas GTK4/libadwaita:

```bash
sudo apt install -y meson ninja-build pkg-config \
  libgtk-4-dev libadwaita-1-dev \
  libglib2.0-dev libgirepository1.0-dev \
  gettext desktop-file-utils appstream-util \
  blueprint-compiler gnome-devel-docs
```

Ferramenta para gerar projetos a partir de templates:

```bash
cargo install cargo-generate
```

Crie um app GNOME 50 em Rust a partir do template oficial:

```bash
cargo generate --git https://gitlab.gnome.org/World/rust-template
```

> Para publicar via Flathub, use o GNOME Builder (instalado no passo 5.4) — ele já empacota em sandbox Flatpak automaticamente, sem precisar de configuração manual adicional.

## 14. IA local — ROCm + NPU (Ryzen AI) + FastFlowLM

FastFlowLM é um runtime otimizado para executar LLMs (Large Language Models) em NPUs AMD XDNA 2.

> Pré-requisitos: GPU/APU AMD compatível para o ROCm; NPU Ryzen AI 300/400 com **AMD XDNA 2 NPU** (Strix Point/Strix Halo); XRT stack (AMD Runtime). Confira antes:

```bash
lspci -nn | grep -i 1022:17f0   # presença de NPU Ryzen AI (STX/KRK)
```

ROCm nativo do repositório do 26.04:

```bash
sudo apt install -y rocm rocm-dev
```

**Reinicie o sistema** para os módulos de kernel do `amdgpu` carregarem corretamente:

```bash
sudo reboot
```

### Instalação do FastFlowLM no Ubuntu 26.04

1. Adicionar repositório AMD XRT. O stack XRT (X Runtime) é necessário para suporte a NPU/XDNA:
  

```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt update
```

2. Instalar XRT (runtime da AMD para NPU) e drivers NPU (driver DKMS para XDNA)
  

```bash
sudo apt install libxrt-npu2 amdxdna-dkms
```

3. Reboot do Sistema
  

```bash
sudo reboot
```

4. Instalar FastFlowLM via Pacote .deb
  

Baixe a versão mais recente do [GitHub Releases](https://github.com/FastFlowLM/FastFlowLM/releases):

```bash
# Navegue até o diretório onde baixou o arquivo .deb
cd ~/Downloads

# Instale o pacote
sudo apt install ./fastflowlm_0.9.45_ubuntu26.04_amd64.deb
```

5. Configurar Limite de Memlock
  

NPUs requerem limite de memlock alto. Verifique:

```bash
ulimit -l
```

Se não retornar `unlimited`, configure:

```bash
# Edite o arquivo de limites do sistema
sudo nano /etc/security/limits.conf
```

Adicione as seguintes linhas no final do arquivo:

```
*    soft    memlock    unlimited
*    hard    memlock    unlimited
```

Salve (Ctrl+O, Enter, Ctrl+X) e reboot:

```bash
sudo reboot
```

### Validação da Instalação

1. Validar setup do NPU
  

```bash
flm validate
```

Saída esperada:

```
[Linux]  Kernel: 7.0.0-xxxx
[Linux]  NPU: /dev/accel/accel0
[Linux]  NPU FW Version: 1.1.x.xx
[Linux]  Memlock Limit: infinity
```

2. Verificar se XRT vê o NPU
  

```bash
xrt-smi examine
```

Você deve ver informações sobre o seu NPU listado.

### Primeiros Passos com FastFlowLM

#### Modo CLI - Executar um modelo

```bash
flm run gemma4-it:e4b
```

#### Modo Servidor - API OpenAI compatível

Inicie o servidor:

```bash
flm server
```

Por padrão, roda em `http://localhost:8000`

Teste com curl:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4-it:e4b",
    "messages": [{"role": "user", "content": "Olá, como você está?"}]
  }'
```

---

### Troubleshooting

#### Problema: "No such device with index '0'"

**Solução:**

- Verifique se XRT encontra o NPU: `xrt-smi examine`
  
- Reinstale o plugin XRT para AMDXDNA:
  
  ```bash
  sudo apt install --reinstall xrt-plugin-amdxdnasudo reboot
  ```
  

#### Problema: Firmware não é 1.1

**Solução:**

- Atualize firmware e drivers:
  
  ```bash
  sudo apt updatesudo apt upgradesudo reboot
  ```
  

#### Problema: Permissão negada ao executar `flm`

**Solução:**

- Execute com `sudo`:
  
  ```bash
  sudo flm validatesudo flm run gemma4-it:e4b
  ```
  
- Ou adicione seu usuário ao grupo `video`:
  
  ```bash
  sudo usermod -a -G video $USER# Faça logout e login novamente
  ```
