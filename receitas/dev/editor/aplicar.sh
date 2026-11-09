#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-editor.sh
source ./comum-editor.sh

case $EDITOR_PEDIDO in
    terminal)
        msg "Nenhum editor novo: os agentes rodam no terminal."
        ;;
    vscode)
        if ! cmp -s <(fonte_ms) "$FONTE_MS"; then
            command -v gpg >/dev/null || instalar_pacotes gpg
            tmp=$(mktemp)
            if ! python3 - "$URL_CHAVE_MS" "$tmp" <<'PY'; then
import sys, urllib.request
try:
    with urllib.request.urlopen(sys.argv[1], timeout=60) as r, open(sys.argv[2], "wb") as f:
        f.write(r.read())
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(1)
PY
                rm -f "$tmp"
                falha "não consegui baixar a chave do repositório da Microsoft ($URL_CHAVE_MS). Confira a internet e rode o bora de novo; nada foi mudado"
            fi
            digital=$(gpg --show-keys --with-colons "$tmp" 2>/dev/null | awk -F: '/^fpr/ {print $10; exit}')
            if [ "$digital" != "$DIGITAL_MS" ]; then
                rm -f "$tmp"
                falha "a chave baixada de packages.microsoft.com não é a que a Microsoft publica (${digital:-nenhuma}); nada foi mudado"
            fi
            escrever_arquivo "$CHAVE_MS" 0644 <"$tmp"
            rm -f "$tmp"
            if [ -e /etc/apt/sources.list.d/vscode.list ]; then
                guardar_arquivo /etc/apt/sources.list.d/vscode.list
                rm -f /etc/apt/sources.list.d/vscode.list
            fi
            fonte_ms | escrever_arquivo "$FONTE_MS" 0644
            msg "Atualizando a lista de pacotes, com o repositório da Microsoft."
            apt_get update -q
        fi
        # O pacote pergunta se deve escrever o próprio repositório; ele já existe.
        echo "code code/add-microsoft-repo boolean false" | debconf-set-selections
        instalar_pacotes code
        msg "Pronto: VS Code $(dpkg-query -W -f='${Version}' code). Abra pelo menu ou com code . na pasta do projeto."
        ;;
    vscodium | zed)
        app=$(flatpak_do_editor)
        if ! command -v flatpak >/dev/null || ! grep -qx flathub <<<"$(flatpak remotes --system --columns=name)"; then
            falha "o $EDITOR_PEDIDO vem do Flathub, e o Flathub não está ligado; aplique antes a receita desktop/flatpak"
        fi
        if ! flatpak_instalado "$app"; then
            msg "Instalando $app, do Flathub."
            flatpak install --system -y --noninteractive flathub "$app"
            echo "$app" >>"$BORA_ESTADO/flatpaks-instalados"
        fi
        msg "Pronto: $EDITOR_PEDIDO instalado. Abra pelo menu de aplicativos."
        ;;
esac
