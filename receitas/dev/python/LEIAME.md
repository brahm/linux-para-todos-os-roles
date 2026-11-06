# Python com ambientes virtuais

## O que faz

Prepara o Python para projetos: instala o módulo de ambientes virtuais, o `pip`, os cabeçalhos para compilar pacotes e o `pipx`, e faz o comando `python` abrir o Python 3.

## Por que

O Ubuntu e o Debian já vêm com Python, porque boa parte do sistema é escrita nele. Esse Python é da distro: instalar pacotes nele com `sudo pip install` pode trocar uma biblioteca que um programa do sistema usa e quebrar esse programa. Por isso, desde o Debian 12 e o Ubuntu 23.04, o `pip` fora de um ambiente virtual recusa instalar e mostra o erro `externally-managed-environment`.

O caminho certo é um **ambiente virtual** para cada projeto: uma pasta, em geral `.venv`, com o seu próprio Python e os pacotes que só aquele projeto usa. Cada projeto pode ter a versão de biblioteca que quiser, e apagar a pasta apaga tudo, sem deixar rastro no sistema.

```sh
python3 -m venv .venv          # cria o ambiente, uma vez por projeto
source .venv/bin/activate      # entra nele; o prompt mostra (.venv)
pip install requests           # instala só neste projeto
deactivate                     # sai
```

Para programas de linha de comando escritos em Python, como o `black`, o `ruff` ou o `httpie`, o `pipx` faz o mesmo sozinho: cada programa ganha o seu ambiente, e o comando aparece em `~/.local/bin`.

O `python-is-python3` existe porque muitos tutoriais escrevem `python`, e não `python3`. Sem ele, o comando não existe no Ubuntu nem no Debian.

## O que muda no sistema

- Instala `python3-venv`, `python3-pip`, `python3-dev` (os cabeçalhos para compilar pacotes com partes em C), `pipx` e `python-is-python3`.
- Cria `~/.local/bin` na pasta pessoal de quem rodou o `bora`, se ainda não existir. O `~/.profile` do Ubuntu e do Debian põe essa pasta no PATH a cada login, se ela existir, então os programas do `pipx` funcionam a partir do próximo login, sem mexer em arquivo nenhum.

A versão do Python é a da distro: 3.12 no Ubuntu 24.04, 3.13 no Debian 13. A receita não troca essa versão.

## Como conferir

O `testar.sh` roda:

- `python3 --version` e `python --version`, que precisam mostrar a mesma versão;
- `python3 -m venv`, como a pessoa, numa pasta temporária, e o `pip --version` de dentro do ambiente criado;
- a existência do `Python.h`, o cabeçalho que os pacotes com partes em C usam;
- `pipx --version`, e a pasta `~/.local/bin`.

## Como desfazer

O `desfazer.sh` remove os pacotes que a receita instalou e a pasta `~/.local/bin`, se foi ela que criou e se a pasta ainda estiver vazia. Os ambientes virtuais dos seus projetos ficam nas pastas dos projetos, e os programas do `pipx`, em `~/.local`: para tirar esses, rode `pipx uninstall-all` antes de desfazer.

## Fontes

- [venv: ambientes virtuais (documentação do Python, em português)](https://docs.python.org/pt-br/3/library/venv.html)
- [PEP 668: ambientes gerenciados pela distro](https://peps.python.org/pep-0668/)
- [pipx](https://pipx.pypa.io/)
- [Python no Debian](https://wiki.debian.org/Python)
