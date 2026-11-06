#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
exigir_apt

# Compila e roda um programa de verdade, numa pasta temporária.
compilar_c() {
    local d r
    d=$(mktemp -d)
    printf '#include <stdio.h>\nint main(void) { puts("ola"); return 0; }\n' >"$d/ola.c"
    gcc -o "$d/ola" "$d/ola.c" && [ "$("$d/ola")" = ola ]
    r=$?
    rm -rf "${d:?}"
    return $r
}
compilar_cpp() {
    local d r
    d=$(mktemp -d)
    printf '#include <iostream>\nint main() { std::cout << "ola\\n"; }\n' >"$d/ola.cpp"
    g++ -o "$d/ola" "$d/ola.cpp" && [ "$("$d/ola")" = ola ]
    r=$?
    rm -rf "${d:?}"
    return $r
}

conferir "compilador de C (gcc --version)" gcc --version
conferir "compilador de C++ (g++ --version)" g++ --version
conferir "make (make --version)" make --version
conferir "pkg-config acha as bibliotecas do sistema" pkg-config --version
conferir "um programa em C compila e roda" compilar_c
conferir "um programa em C++ compila e roda" compilar_cpp
resultado_dos_testes
