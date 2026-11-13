#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita ia/lm-studio (LM Studio, para modelos de IA com janela).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-lm-studio.sh
source ./comum-lm-studio.sh

if { [ -e "$LMS_BIN" ] || [ -L "$LMS_BIN" ]; } && [[ "$(readlink "$LMS_BIN" 2>/dev/null)" != "$LMS_RAIZ"/* ]]; then
    falha "já existe $LMS_BIN, que não veio do bora; tire de lá e rode de novo"
fi

# shellcheck disable=SC2086
instalar_pacotes curl ca-certificates $LMS_PACOTES

if ! lms_instalado; then
    tmp=$(mktemp -d -p /var/tmp bora-lm-studio.XXXXXX)
    trap 'rm -rf "${tmp:?}"' EXIT
    msg "Baixando o LM Studio $LMS_VERSAO de $LMS_URL"
    curl -fsSL --proto '=https' --tlsv1.2 --retry 3 -o "$tmp/$LMS_NOME" "$LMS_URL" ||
        falha "não consegui baixar o LM Studio; confira a conexão com a internet e rode de novo"
    # A soma está gravada na receita: o que chega precisa ser exatamente o arquivo testado.
    echo "$LMS_SHA256  $tmp/$LMS_NOME" | sha256sum --check --quiet ||
        falha "o arquivo baixado não bate com a soma SHA256 que a receita conhece; nada foi instalado"
    msg "Soma SHA256 conferida."
    # Extraído, o AppImage não precisa do FUSE e abre como um programa comum.
    chmod +x "$tmp/$LMS_NOME"
    (cd "$tmp" && "./$LMS_NOME" --appimage-extract >/dev/null) ||
        falha "não consegui extrair o AppImage do LM Studio"
    [ -x "$tmp/squashfs-root/AppRun" ] || falha "o AppImage do LM Studio não trouxe o AppRun; a receita precisa ser atualizada"
    if [ ! -d "$LMS_RAIZ" ]; then
        mkdir -p "$LMS_RAIZ"
        echo "$LMS_RAIZ" >>"$BORA_ESTADO/pastas-novas"
    fi
    rm -rf "${LMS_DIR:?}"
    mv "$tmp/squashfs-root" "$LMS_DIR"
    chown -R root:root "$LMS_DIR"
    chmod -R go-w "$LMS_DIR"
    chmod 755 "$LMS_DIR"
    # A caixa de areia do Chromium, que isola as páginas da janela, precisa ser do root com setuid.
    if [ -f "$LMS_DIR/chrome-sandbox" ]; then chmod 4755 "$LMS_DIR/chrome-sandbox"; fi
    echo "$LMS_DIR" >"$BORA_ESTADO/lm-studio-instalado"
    msg "LM Studio $LMS_VERSAO instalado em $LMS_DIR"
fi

if [ "$(readlink "$LMS_BIN" 2>/dev/null)" != "$LMS_DIR/AppRun" ]; then
    if [ -L "$LMS_BIN" ]; then readlink "$LMS_BIN" >"$BORA_ESTADO/link-anterior"; fi
    ln -sfn "$LMS_DIR/AppRun" "$LMS_BIN"
    echo "$LMS_BIN" >"$BORA_ESTADO/link-criado"
fi
atalho_esperado | escrever_arquivo "$LMS_ATALHO"

libs_ausentes=$(bibliotecas_faltando)
if [ -n "$libs_ausentes" ]; then
    aviso "o LM Studio pede bibliotecas que não estão no sistema: $(echo "$libs_ausentes" | tr '\n' ' ')"
fi
msg "Pronto: o LM Studio $LMS_VERSAO está no menu de aplicativos, e abre também com o comando lm-studio."
msg "Para baixar um modelo, abra a aba Discover. O bora modelos diz qual cabe nesta máquina."
