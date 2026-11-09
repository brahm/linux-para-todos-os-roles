#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-lm-studio.sh
source ./comum-lm-studio.sh

nada_faltando() { [ -z "$(bibliotecas_faltando)" ]; }
sandbox_do_root() { [ ! -f "$LMS_DIR/chrome-sandbox" ] || [ "$(stat -c '%U %a' "$LMS_DIR/chrome-sandbox")" = "root 4755" ]; }
ninguem_escreve() { [ -z "$(find "$LMS_DIR" -perm -o+w ! -type l -print -quit)" ]; }
atalho_valido() {
    if command -v desktop-file-validate >/dev/null 2>&1; then
        desktop-file-validate "$LMS_ATALHO"
    else
        grep -qx "Exec=$LMS_BIN %U" "$LMS_ATALHO"
    fi
}

conferir "o comando lm-studio abre o LM Studio $LMS_VERSAO" lms_instalado
conferir "o atalho no menu de aplicativos ($LMS_ATALHO)" atalho_valido
conferir "o ícone do atalho existe" test -f "$(lms_icone)"
conferir "o sistema tem as bibliotecas que o LM Studio pede (ldd)" nada_faltando
conferir "a caixa de areia do Chromium é do root, com setuid" sandbox_do_root
conferir "só o root muda os arquivos do LM Studio" ninguem_escreve
resultado_dos_testes
