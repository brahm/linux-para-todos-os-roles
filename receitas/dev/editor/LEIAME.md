# Editor de código

## O que faz

Instala o editor que você escolher: o VS Code, do repositório oficial da Microsoft, ou o VSCodium ou o Zed, do Flathub. Com `terminal`, não instala nada.

## Por que

Dá para vibecodar só no terminal, e muita gente prefere. Mas um editor ajuda a ler o que o agente escreveu, ver as diferenças antes do commit e usar as extensões dos agentes.

- **VS Code**: o mais usado, com as extensões do Claude Code, do Codex e do Copilot. Vem do repositório APT da Microsoft, que é o caminho que ela recomenda e entrega as atualizações junto com o `apt upgrade`. A chave do repositório é conferida pela impressão digital publicada, e o pacote não escreve um segundo repositório. É uma exceção à regra dos repositórios da distro e do Flathub, nos mesmos termos da do Firefox da Mozilla: o arquivo vem do fabricante. O VS Code do Flathub não é da Microsoft, e o terminal dele roda dentro do Flatpak, sem enxergar os agentes instalados na sua conta.
- **VSCodium**: o mesmo código do VS Code, sem a telemetria e a marca da Microsoft. Vem do Flathub, publicado pelo próprio projeto. Ele usa a loja de extensões Open VSX, que nem sempre tem as extensões oficiais dos agentes.
- **Zed**: leve e rápido, com agentes embutidos. Vem do Flathub, publicado pela Zed Industries.

No VSCodium e no Zed do Flathub, o terminal integrado pode rodar dentro do Flatpak. Se o agente não aparecer nele, use o terminal do sistema, ao lado do editor.

## O que muda no sistema

- **VS Code**: baixa a chave de `https://packages.microsoft.com/keys/microsoft.asc`, confere a impressão digital `BC528686B50D79E339D3721CEB3E94ADBE1229CF` e grava em `/etc/apt/keyrings/packages.microsoft.asc`; escreve o repositório em `/etc/apt/sources.list.d/vscode.sources`; responde "não" à pergunta do pacote sobre escrever o próprio repositório; e instala o pacote `code`. Se a chave baixada não for a publicada, nada muda.
- **VSCodium** ou **Zed**: instala `com.vscodium.codium` ou `dev.zed.Zed` do Flathub, para o sistema todo. Precisa do Flathub ligado (receita `desktop/flatpak`, que o rolê Vibecodar traz quando você escolhe um dos dois).

## Como conferir

O `testar.sh` confere, no VS Code, que o pacote veio do repositório da Microsoft, que a chave gravada é a publicada e que `code --version` responde; no VSCodium e no Zed, que o aplicativo está instalado pelo Flathub (`flatpak info`).

## Como desfazer

O `desfazer.sh` remove o editor que a receita instalou e, no VS Code, o repositório e a chave da Microsoft. As suas configurações e extensões ficam na sua pasta pessoal (`~/.config/Code`, `~/.vscode` e `~/.var/app`).

## Fontes

- [VS Code no Linux (Microsoft)](https://code.visualstudio.com/docs/setup/linux)
- [VSCodium no Flathub](https://flathub.org/apps/com.vscodium.codium)
- [Zed no Flathub](https://flathub.org/apps/dev.zed.Zed)
- [Zed no Linux](https://zed.dev/docs/linux)
