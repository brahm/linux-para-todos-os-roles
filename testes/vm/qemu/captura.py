#!/usr/bin/env python3
"""Confere uma captura de tela da máquina virtual e grava a versão em PNG.

    captura.py tela.ppm tela.png

O monitor do QEMU grava a tela em PPM (o formato mais simples que existe).
Este script lê esse arquivo, recusa uma tela que é quase toda de uma cor só
(preta, por exemplo, quando nada desenhou nada) e grava um PNG, que é o que
vai para os artefatos do workflow. Sem bibliotecas além da padrão do Python.
"""
import struct
import sys
import zlib
from collections import Counter


def ler_ppm(caminho):
    dados = open(caminho, "rb").read()
    campos, pos = [], 0
    # Cabeçalho: P6, largura, altura e o valor máximo, separados por espaços
    # (com comentários começando em #), e um único espaço antes dos pixels.
    while len(campos) < 4:
        while dados[pos : pos + 1].isspace():
            pos += 1
        if dados[pos : pos + 1] == b"#":
            pos = dados.index(b"\n", pos) + 1
            continue
        fim = pos
        while not dados[fim : fim + 1].isspace():
            fim += 1
        campos.append(dados[pos:fim])
        pos = fim
    pos += 1
    if campos[0] != b"P6" or campos[3] != b"255":
        sys.exit(f"{caminho}: não é um PPM de 8 bits ({campos[0]!r})")
    largura, altura = int(campos[1]), int(campos[2])
    return largura, altura, dados[pos : pos + largura * altura * 3]


def gravar_png(caminho, largura, altura, pixels):
    linha = largura * 3
    cru = b"".join(b"\x00" + pixels[y * linha : (y + 1) * linha] for y in range(altura))

    def pedaco(tipo, conteudo):
        return (
            struct.pack(">I", len(conteudo))
            + tipo
            + conteudo
            + struct.pack(">I", zlib.crc32(tipo + conteudo) & 0xFFFFFFFF)
        )

    with open(caminho, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(pedaco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0)))
        f.write(pedaco(b"IDAT", zlib.compress(cru, 9)))
        f.write(pedaco(b"IEND", b""))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip().splitlines()[2].strip())
    entrada, saida = sys.argv[1], sys.argv[2]
    largura, altura, pixels = ler_ppm(entrada)
    gravar_png(saida, largura, altura, pixels)
    # Um pixel a cada 7, para contar as cores sem demorar.
    cores = Counter(pixels[i : i + 3] for i in range(0, len(pixels) - 2, 3 * 7))
    total = sum(cores.values())
    mais_comum = cores.most_common(1)[0][1] / total
    print(f"{saida}: {largura}x{altura}, {len(cores)} cores, a mais comum em {mais_comum:.0%} da tela")
    if largura < 800 or altura < 600:
        sys.exit(f"{saida}: a tela está em {largura}x{altura}, ainda em modo texto")
    if len(cores) < 16 or mais_comum > 0.98:
        sys.exit(f"{saida}: a tela está praticamente vazia")


if __name__ == "__main__":
    main()
