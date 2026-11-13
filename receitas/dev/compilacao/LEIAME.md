# Ferramentas de compilação

## O que faz

Instala o compilador de C e C++ (`gcc` e `g++`), o `make` e o `pkg-config`.

## Por que

Mesmo quem programa só em Python ou em JavaScript esbarra no compilador. Muitos pacotes do `pip` e do `npm` trazem um pedaço escrito em C ou C++, e quando não existe uma versão pronta para a sua máquina, eles são compilados na hora da instalação. Sem o compilador, a instalação para com um erro como `gcc: command not found` ou `make: not found`, que não diz nada para quem está começando (e pouco para quem não está).

O `build-essential` é o pacote que o Debian e o Ubuntu fazem para isso: ele traz o `gcc`, o `g++`, o `make` e as bibliotecas básicas do C. O `pkg-config` é o programa que os scripts de compilação usam para achar as outras bibliotecas instaladas no sistema.

## O que muda no sistema

- Instala os pacotes `build-essential` e `pkg-config`, com as dependências que faltarem.

Nada é configurado: são só programas novos.

## Como conferir

O `testar.sh` roda `gcc --version`, `g++ --version`, `make --version` e `pkg-config --version`, e depois compila e roda um programa de uma linha em C e outro em C++, numa pasta temporária.

Para ver você mesmo: `gcc --version`.

## Como desfazer

O `desfazer.sh` remove os pacotes que a receita instalou, com as dependências que vieram junto. O que já estava instalado antes, ou que outro programa passou a usar depois, fica.

## Fontes

- [O pacote build-essential no Debian](https://packages.debian.org/stable/build-essential)
- [pkg-config](https://www.freedesktop.org/wiki/Software/pkg-config/)
