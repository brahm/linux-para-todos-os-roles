# LM Studio

## O que faz

Instala o LM Studio oficial, baixado de `installers.lmstudio.ai` e conferido pela soma SHA256 gravada na receita, com um atalho no menu de aplicativos e o comando `lm-studio`. Os modelos você baixa na própria janela, na aba Discover; o `bora` diz qual cabe na máquina.

## Por que

O LM Studio faz o mesmo que o Ollama, com janela: procurar, baixar e conversar com modelos locais, sem terminal. Ele também liga um servidor compatível com a API da OpenAI (na aba Developer, ou com `lms server start`), que agentes como o OpenCode e o Codex sabem usar.

Antes de você escolher o modelo, o `bora` mede a memória da máquina e mostra, no plano e no `bora modelos`, qual roda bem nela, pela mesma conta da [receita do Ollama](../ollama/LEIAME.md#por-que). No LM Studio, procure esse nome na aba Discover; ele mostra as versões do modelo e marca as que cabem.

O LM Studio para Linux vem como AppImage, um arquivo que se monta sozinho com o FUSE. A receita abre o AppImage em `/opt/lm-studio`, uma vez, e o programa passa a rodar como qualquer outro, sem FUSE. O LM Studio não publica as somas dos arquivos; a soma da receita foi conferida com a do pacote do LM Studio no nixpkgs, e se o arquivo baixado não for exatamente esse, nada é instalado.

A versão instalada não se atualiza sozinha. Quando o `bora` trouxer uma versão nova, aplique a receita de novo.

## O que muda no sistema

- Instala `curl`, `ca-certificates` e as bibliotecas que a janela usa (`libgtk-3-0t64`, `libnss3`, `libgbm1` e `libasound2t64`), se faltarem. Um desktop costuma ter todas.
- Baixa `LM-Studio-<versão>-x64.AppImage`, confere a soma SHA256 e abre em `/opt/lm-studio/<versão>`, com os arquivos do root e o `chrome-sandbox` com setuid, que é o que isola as páginas da janela.
- Cria o link `/usr/local/bin/lm-studio` e o atalho `/usr/share/applications/lm-studio.desktop`.

Os modelos e as configurações ficam na sua pasta pessoal, em `~/.lmstudio`, e o LM Studio cria essa pasta na primeira vez que abre.

## Como conferir

O `testar.sh` confere que o comando `lm-studio` aponta para a versão da receita, que o atalho é válido e tem ícone, que o `ldd` não acusa nenhuma biblioteca faltando, que o `chrome-sandbox` é do root com setuid e que só o root muda os arquivos do programa.

Para usar: abra o LM Studio no menu de aplicativos, vá à aba Discover, procure o modelo que o `bora modelos` sugeriu e baixe.

## Como desfazer

O `desfazer.sh` apaga o atalho, o link `/usr/local/bin/lm-studio` e a pasta `/opt/lm-studio/<versão>`, e remove os pacotes que a receita instalou. A pasta `~/.lmstudio`, com os modelos que você baixou, fica onde está; para liberar o espaço, apague essa pasta.

## Fontes

- [Download do LM Studio](https://lmstudio.ai/download)
- [Documentação do LM Studio](https://lmstudio.ai/docs)
- [O comando lms](https://lmstudio.ai/docs/cli)
- [O pacote do LM Studio no nixpkgs, com a soma do AppImage](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/lm/lmstudio/package.nix)
- [AppImage: rodar sem FUSE, com --appimage-extract](https://docs.appimage.org/user-guide/troubleshooting/fuse.html)
