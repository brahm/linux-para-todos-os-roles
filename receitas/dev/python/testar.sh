#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt
# shellcheck source=comum-python.sh
source ./comum-python.sh

# Cria um ambiente virtual de verdade, como a pessoa, e confere o pip dentro dele.
ambiente_virtual() {
    local d r
    d=$(como_pessoa "$PESSOA" mktemp -d)
    como_pessoa "$PESSOA" python3 -m venv "$d/.venv" &&
        como_pessoa "$PESSOA" "$d/.venv/bin/python" -m pip --version &&
        [ "$(como_pessoa "$PESSOA" "$d/.venv/bin/python" -c 'import sys; print(sys.prefix != sys.base_prefix)')" = True ]
    r=$?
    rm -rf "${d:?}"
    return $r
}
cabecalhos() { python3 -c 'import os, sysconfig; assert os.path.exists(os.path.join(sysconfig.get_paths()["include"], "Python.h"))'; }
python_e_python3() { [ "$(python --version 2>&1)" = "$(python3 --version 2>&1)" ]; }

conferir "Python 3 instalado ($(python3 --version 2>&1))" python3 --version
conferir "o comando python abre o Python 3" python_e_python3
conferir "um ambiente virtual novo funciona, com o pip dentro (python3 -m venv)" ambiente_virtual
conferir "cabeçalhos para compilar pacotes com partes em C (Python.h)" cabecalhos
conferir "pipx instalado (pipx --version)" como_pessoa "$PESSOA" pipx --version
conferir "a pasta dos programas do pipx existe ($BIN_DA_PESSOA)" test -d "$BIN_DA_PESSOA"
resultado_dos_testes
