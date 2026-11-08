#!/usr/bin/env python3
"""Grava no receita.yaml de cada receita que um teste passou.

    ferramentas/registros/registrar.py --onde vm --distro ubuntu --versao 24.04 \\
        --data 2026-11-08 sistema/zram seguranca/ssh ...

Cada receita guarda um registro por distro, versão, lugar (contêiner, máquina
virtual ou computador de verdade) e autor: se já existe um com os quatro iguais,
ele é
atualizado com a data e o resultado novos; se não, entra no fim da lista
"testes:". Assim o teste semanal não faz a lista crescer sem fim.

Mexe só no bloco "testes:", que é sempre o último do receita.yaml, e deixa o
resto do arquivo como está.
"""
import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
ORDEM = ["distro", "versao", "data", "por", "onde", "resultado"]


def ler_testes(linhas):
    """Devolve (índice da linha "testes:", lista de registros como dicionários)."""
    inicio = next((i for i, l in enumerate(linhas) if l.rstrip() == "testes:"), None)
    if inicio is None:
        return None, []
    registros = []
    for linha in linhas[inicio + 1:]:
        if not linha.strip():
            continue
        if not linha.startswith(" "):
            sys.exit(f"o bloco testes: precisa ser o último do arquivo (achei {linha.strip()!r} depois dele)")
        m = re.match(r"^\s*(-\s+)?([a-z_]+):\s*(.*?)\s*$", linha)
        if not m:
            sys.exit(f"não entendi a linha {linha.rstrip()!r} do bloco testes:")
        if m.group(1):
            registros.append({})
        registros[-1][m.group(2)] = m.group(3).strip('"')
    return inicio, registros


def escrever(registro):
    texto = []
    chaves = [c for c in ORDEM if c in registro] + [c for c in registro if c not in ORDEM]
    for n, chave in enumerate(chaves):
        valor = registro[chave]
        if chave == "versao":
            valor = f'"{valor}"'
        texto.append(f"{'  - ' if n == 0 else '    '}{chave}: {valor}\n")
    return texto


def registrar(receita, novo):
    arquivo = RAIZ / "receitas" / receita / "receita.yaml"
    if not arquivo.is_file():
        sys.exit(f"receita não encontrada: {receita}")
    linhas = arquivo.read_text().splitlines(keepends=True)
    inicio, registros = ler_testes(linhas)
    if inicio is None:
        linhas.append("testes:\n")
        inicio = len(linhas) - 1
    # O autor entra na chave para o teste automático não apagar o relato de uma pessoa.
    chave = lambda r: (r.get("distro"), r.get("versao"), r.get("onde", "vm"), r.get("por"))
    for r in registros:
        if chave(r) == chave(novo):
            mudou = any(r.get(k) != v for k, v in novo.items())
            r.update(novo)
            break
    else:
        registros.append(dict(novo))
        mudou = True
    if mudou:
        corpo = [l for r in registros for l in escrever(r)]
        arquivo.write_text("".join(linhas[: inicio + 1] + corpo))
    return mudou


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--onde", required=True, choices=["vm", "conteiner", "maquina"])
    p.add_argument("--distro", required=True)
    p.add_argument("--versao", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--por", default="testes-automaticos")
    p.add_argument("--resultado", default="ok")
    p.add_argument("receitas", nargs="+")
    a = p.parse_args()
    novo = {"distro": a.distro, "versao": a.versao, "data": a.data, "por": a.por, "onde": a.onde, "resultado": a.resultado}
    for receita in a.receitas:
        print(f"{receita}: {'registrado' if registrar(receita, novo) else 'já estava registrado'}")


if __name__ == "__main__":
    main()
