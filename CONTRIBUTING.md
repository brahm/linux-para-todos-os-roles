# Como contribuir

Chegou ontem no Linux? Ótimo, você é exatamente quem a gente precisa. Quem acabou de tropeçar num problema costuma explicar a solução melhor do que quem já esqueceu que ele existia.

## Formas de ajudar

- **Testar.** Rode uma receita numa distro em que ela ainda não foi testada e conte como foi. É a ajuda que mais faz falta. Os [roteiros de teste em VM](testes/vm/README.md) dizem o que conferir em cada rolê, e o formulário [Relato de teste](https://github.com/brahm/linux-para-todos-os-roles/issues/new?template=5-relato-de-teste.yml) recebe o resultado, sem precisar de pull request.
- **Propor um rolê.** Abra uma issue com o objetivo em linguagem de gente ("quero que este PC vire o lugar das fotos da família"), para quem ele serve e em que máquina você pensou.
- **Escrever ou melhorar uma receita.** O formato está em [`receitas/README.md`](receitas/README.md).
- **Revisar textos.** Se uma explicação ficou confusa para você, vai ficar confusa para outras pessoas. O jeito de escrever está no [guia de estilo](docs/estilo.md).

## Antes de abrir um pull request

1. Teste numa máquina virtual ou num computador que possa ser formatado sem dor.
2. Rode a receita duas vezes seguidas. A segunda vez não pode mudar nada (idempotência).
3. Rode o `desfazer.sh` e confira que o sistema voltou ao estado anterior.
4. Registre no `receita.yaml` a distro, a versão, a data e onde foi o teste (`vm`, `conteiner` ou `maquina`).
5. Na descrição do pull request, diga o que foi testado, onde, e o que ainda falta validar.

## Rodar os testes

O `bora` é escrito em Rust, e as receitas são scripts bash. Com o [Rust](https://rustup.rs/) instalado:

```sh
cargo test                       # testes do bora, com um catálogo de mentira
cargo run -- conferir            # confere o formato de todas as receitas e rolês
shellcheck -x -P SCRIPTDIR receitas/comum.sh receitas/*/*/*.sh
ferramentas/pipes/conferir.sh    # barra "| grep -q" e "| head", que às vezes falham com pipefail
ferramentas/estilo/conferir.sh   # barra os clichês que o guia de estilo proíbe
```

Para testar uma receita mudada sem recompilar, aponte o `bora` para a pasta do repositório:

```sh
BORA_RAIZ=$PWD cargo run -- lista
```

### O que o CI faz por você

- **A cada pull request:** aplica, confere e desfaz cada receita em contêineres com systemd, no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13. Veja [`testes/conteiner/README.md`](testes/conteiner/README.md). Teste em contêiner é registrado com `onde: conteiner` e não substitui a máquina virtual.
- **Toda semana, e nos pull requests que mexem nas receitas:** roda a parte dos rolês que não depende de tela numa máquina virtual com QEMU. Veja [a parte automática no CI](testes/vm/README.md#a-parte-automática-no-ci).
- **Receita que só se confere com tela:** entra em [`testes/vm/qemu/so-com-tela.txt`](testes/vm/qemu/so-com-tela.txt) e passa a rodar na [máquina virtual com tela](testes/vm/README.md#a-máquina-com-tela), que vai até a tela de login e tira capturas. Se precisar de uma conferência própria, ela entra no [`testes/vm/qemu/tela-na-vm.sh`](testes/vm/qemu/tela-na-vm.sh).

## Regras para receitas

- Nada de pacotes do AUR. Use os repositórios oficiais da distro ou Flatpak.
- Nada de `curl ... | sh`, exceto instaladores oficiais listados e conferidos pelo projeto.
- Nenhuma receita abre porta para a internet. Acesso de fora só por VPN.
- Nenhuma receita pede ou guarda senha, token ou chave dentro do repositório.
- Mensagens para o usuário em português do Brasil.

## Ao relatar um problema

"Não funciona" é o equivalente digital de levar o carro na oficina e dizer que "tá fazendo um barulho". Prefira:

```text
Distro e versão: ...
Rolê ou receita: ...
O que eu esperava: ...
O que aconteceu: ...
Saída do bora diag: ...
```

Antes de colar qualquer saída, tire IPs públicos, nomes de usuário, tokens e chaves.

## Publicar uma versão

1. Suba o `version` do `Cargo.toml` no mesmo pull request da mudança, e atualize o `Cargo.lock` com `cargo check`.
2. Quando o pull request entra na `main`, o workflow [`publicar.yml`](.github/workflows/publicar.yml) vê que a versão ainda não tem tag, compila os binários e cria a tag `vX.Y.Z` e a página da versão com o `SHA256SUMS`.

Ninguém precisa rodar `git tag` na própria máquina. Para publicar de novo à mão: Actions, Publicar, Run workflow na `main`.

O projeto segue em 0.x. Quem decide quando isso muda é o Brahm.

## Licença das contribuições

O projeto usa a licença [0BSD](LICENSE). Ao enviar uma contribuição, você concorda que ela seja distribuída sob a mesma licença: qualquer pessoa pode copiar, modificar e usar o que você escreveu, sem pedir e sem citar.
