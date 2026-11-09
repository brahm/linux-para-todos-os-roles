# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

# A versão que esta receita instala e testa. O LM Studio não publica as somas,
# então a soma abaixo é a do arquivo baixado de installers.lmstudio.ai e
# conferida com a do pacote do LM Studio no nixpkgs. Ao trocar a versão, baixe
# o AppImage novo, calcule a soma com sha256sum e confira com outra fonte.
LMS_VERSAO=0.4.28-2
LMS_SHA256=a3e6cf8233697be0a8ad6871197b424242af3c5a346671aeed59959ed7eebf11

[ "$(uname -m)" = x86_64 ] || falha "a receita do LM Studio só existe para x86_64, e esta máquina é $(uname -m)"
LMS_NOME=LM-Studio-$LMS_VERSAO-x64.AppImage
LMS_URL=https://installers.lmstudio.ai/linux/x64/$LMS_VERSAO/$LMS_NOME
LMS_RAIZ=/opt/lm-studio
LMS_DIR=$LMS_RAIZ/$LMS_VERSAO
LMS_BIN=/usr/local/bin/lm-studio
LMS_ATALHO=/usr/share/applications/lm-studio.desktop
# O que o Electron precisa para abrir a janela. Um desktop já tem quase tudo.
LMS_PACOTES="libgtk-3-0t64 libnss3 libgbm1 libasound2t64"

lms_instalado() {
    [ -x "$LMS_DIR/AppRun" ] && [ "$(readlink "$LMS_BIN" 2>/dev/null)" = "$LMS_DIR/AppRun" ]
}

# O ícone que veio no AppImage.
lms_icone() {
    local i
    for i in "$LMS_DIR"/*.png "$LMS_DIR"/usr/share/icons/hicolor/512x512/apps/*.png; do
        if [ -f "$i" ]; then
            echo "$i"
            return 0
        fi
    done
}

atalho_esperado() {
    cat <<ATALHO
[Desktop Entry]
# Instalado pelo bora (receita ia/lm-studio).
Type=Application
Name=LM Studio
Comment=Modelos de IA neste computador
Exec=$LMS_BIN %U
Icon=$(lms_icone)
Terminal=false
Categories=Development;
ATALHO
}

# Bibliotecas que o programa pede e o sistema não tem.
bibliotecas_faltando() {
    local exe
    exe=$(find "$LMS_DIR" -maxdepth 1 -type f -name 'lm-studio' -perm -u+x -print -quit)
    [ -n "$exe" ] || exe=$(find "$LMS_DIR" -maxdepth 1 -type f -perm -u+x ! -name AppRun ! -name chrome-sandbox ! -name '*.so*' -size +10M -print -quit)
    [ -n "$exe" ] || return 0
    LD_LIBRARY_PATH=$LMS_DIR ldd "$exe" 2>/dev/null | awk '/not found/ {print $1}' || true
}
