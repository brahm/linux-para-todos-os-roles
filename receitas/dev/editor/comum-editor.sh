# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

EDITOR_PEDIDO=${BORA_EDITOR:-terminal}

# VS Code: o repositório APT da Microsoft, com a chave conferida pela
# impressão digital publicada em https://code.visualstudio.com/docs/setup/linux
URL_CHAVE_MS=https://packages.microsoft.com/keys/microsoft.asc
DIGITAL_MS=BC528686B50D79E339D3721CEB3E94ADBE1229CF
CHAVE_MS=/etc/apt/keyrings/packages.microsoft.asc
# O mesmo nome que o pacote code usa, para ele não escrever outro.
FONTE_MS=/etc/apt/sources.list.d/vscode.sources

# VSCodium e Zed: os aplicativos do Flathub publicados pelos próprios projetos.
flatpak_do_editor() {
    case $EDITOR_PEDIDO in
        vscodium) echo com.vscodium.codium ;;
        zed) echo dev.zed.Zed ;;
    esac
}

flatpak_instalado() { flatpak info --system "$1" >/dev/null 2>&1; }

fonte_ms() {
    cat <<'FONTE'
# Escrito pelo bora (receita dev/editor): o VS Code oficial da Microsoft.
Types: deb
URIs: https://packages.microsoft.com/repos/code
Suites: stable
Components: main
Architectures: amd64
Signed-By: /etc/apt/keyrings/packages.microsoft.asc
FONTE
}

editor_pronto() {
    case $EDITOR_PEDIDO in
        terminal) return 0 ;;
        vscode) pacote_instalado code && cmp -s <(fonte_ms) "$FONTE_MS" ;;
        *) command -v flatpak >/dev/null && flatpak_instalado "$(flatpak_do_editor)" ;;
    esac
}
