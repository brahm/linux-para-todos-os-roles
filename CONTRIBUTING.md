# Como contribuir

Contribuições são bem-vindas, inclusive de quem começou ontem. Muitas vezes, quem acabou de passar por um problema é quem melhor explica a solução.

## Licença das contribuições

O projeto usa a licença [0BSD](LICENSE). Ao enviar uma contribuição, você concorda que ela seja distribuída sob a mesma licença. Na prática, isso significa que qualquer pessoa pode copiar, modificar e usar o que você escreveu, sem pedir e sem citar.

## Formas de ajudar

- **Propor um rolê:** abra uma issue descrevendo o objetivo em linguagem de gente ("quero que este PC vire o lugar das fotos da família"), para quem ele serve e em que máquina você pensou.
- **Escrever ou melhorar uma receita:** siga o formato descrito em [`receitas/README.md`](receitas/README.md).
- **Testar:** rodar uma receita numa distro em que ela ainda não foi testada e registrar o resultado é uma das contribuições mais valiosas. Os [roteiros de teste em VM](testes/vm/README.md) dizem o que conferir em cada rolê, e o formulário [Relato de teste](https://github.com/brahm/linux-para-todos-os-roles/issues/new?template=5-relato-de-teste.yml) serve para contar como foi, sem precisar abrir um pull request.
- **Revisar textos:** se uma explicação ficou confusa para você, ela vai ficar confusa para outras pessoas.

## Antes de abrir um pull request

1. Teste numa máquina virtual ou num computador que possa ser formatado sem dor.
2. Rode a receita duas vezes seguidas: a segunda vez não pode mudar nada (idempotência).
3. Rode o `desfazer.sh` e confira que o sistema voltou ao estado anterior.
4. Registre no `receita.yaml` a distro, a versão, a data e onde foi o teste (`vm`, `conteiner` ou `maquina`).
5. Na descrição do pull request, diga o que foi testado, onde, e o que ainda falta validar.

## Rodar os testes

O `bora` é escrito em Rust, e as receitas são scripts bash. Com o [Rust](https://rustup.rs/) instalado:

```sh
cargo test                     # testes do bora, com um catálogo de mentira
cargo run -- conferir          # confere o formato de todas as receitas e rolês
shellcheck -x -P SCRIPTDIR receitas/comum.sh receitas/*/*/*.sh
```

Para testar uma receita mudada sem recompilar, aponte o `bora` para a pasta do repositório: `BORA_RAIZ=$PWD cargo run -- lista`.

As receitas também rodam de verdade em contêineres com systemd, como explica [`testes/conteiner/README.md`](testes/conteiner/README.md). O GitHub Actions faz isso a cada pull request no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13. Um teste em contêiner é registrado com `onde: conteiner` e não substitui o teste numa máquina virtual.

## Regras para receitas

- Nada de pacotes do AUR. Use os repositórios oficiais da distro ou Flatpak.
- Nada de `curl ... | sh`, exceto instaladores oficiais listados e conferidos pelo projeto.
- Nenhuma receita abre porta para a internet. Acesso de fora só por VPN.
- Nenhuma receita pede ou guarda senha, token ou chave dentro do repositório.
- Mensagens para o usuário em português do Brasil.

## Ao relatar um problema

Evite só "não funciona". Prefira:

```text
Distro e versão: ...
Rolê ou receita: ...
O que eu esperava: ...
O que aconteceu: ...
Saída do bora diag: ...
```

Remova IPs públicos, nomes de usuário, tokens e chaves antes de colar qualquer saída.

## Publicar uma versão

Suba o `version` do `Cargo.toml` (e o `Cargo.lock`, com `cargo check`) no mesmo pull request da mudança. Quando ele entra na `main`, o workflow [`publicar.yml`](.github/workflows/publicar.yml) vê que a versão ainda não tem tag, compila os binários, cria a tag `vX.Y.Z` e a página da versão com o `SHA256SUMS`. Ninguém precisa rodar `git tag` na própria máquina. Para publicar de novo à mão, use Actions, Publicar, Run workflow na `main`. O projeto segue em 0.x até o Brahm decidir que chegou a hora da 1.0.0.
