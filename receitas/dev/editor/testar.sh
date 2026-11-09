#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-editor.sh
source ./comum-editor.sh

case $EDITOR_PEDIDO in
    terminal)
        conferir "nenhum editor novo pedido" true
        ;;
    vscode)
        # O VS Code se recusa a abrir como root, então o teste roda como outra conta.
        pessoa=${BORA_PESSOA:-nobody}
        responde() { [ -n "$(runuser -u "$pessoa" -- env HOME=/tmp code --version 2>/dev/null)" ]; }
        conferir "VS Code instalado pelo repositório da Microsoft" grep -q packages.microsoft.com <<<"$(LC_ALL=C apt-cache policy code)"
        conferir "a chave da Microsoft é a publicada ($DIGITAL_MS)" test "$(gpg --show-keys --with-colons "$CHAVE_MS" 2>/dev/null | awk -F: '/^fpr/ {print $10; exit}')" = "$DIGITAL_MS"
        conferir "o VS Code responde (code --version)" responde
        ;;
    *)
        conferir "$(flatpak_do_editor) instalado pelo Flathub" flatpak_instalado "$(flatpak_do_editor)"
        ;;
esac
resultado_dos_testes
