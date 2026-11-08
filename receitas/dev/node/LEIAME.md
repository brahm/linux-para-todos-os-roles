# Node.js

## O que faz

Instala o Node.js LTS oficial, baixado de nodejs.org e conferido pela soma SHA256 gravada na receita, com o `npm` e o `npx`. O `npm install -g` passa a instalar na sua pasta pessoal, sem `sudo`.

## Por que

O Node.js roda JavaScript fora do navegador. É o que os tutoriais de web pedem para criar um projeto com Vite, React, Vue, Svelte ou Astro, e o `npm` é por onde chegam as bibliotecas.

A receita não usa o Node.js da distro porque, no Ubuntu 24.04 e nas derivadas (Linux Mint 22, Pop!_OS, Zorin OS), ele é a versão 18, que já saiu de suporte, e as ferramentas de hoje, como o Vite, pedem uma versão mais nova. Em vez disso, ela instala a versão LTS (de suporte longo) que o projeto testou, igual em todas as distros. Ela segue a regra dos instaladores oficiais: o arquivo vem de nodejs.org, e a receita confere a soma SHA256 antes de instalar. Se o arquivo baixado não for exatamente o que foi testado, nada é instalado.

O `sudo npm install -g` é a origem de muitos problemas: os arquivos ficam do root, e o próximo `npm` sem `sudo` falha com `EACCES`. Com o `prefix` em `~/.local`, cada pessoa instala os seus programas na própria pasta, e eles aparecem em `~/.local/bin`.

A versão instalada não se atualiza sozinha pelo `apt`. Quando o `bora` trouxer uma versão nova, aplique a receita de novo para atualizar.

## O que muda no sistema

- Instala `curl`, `xz-utils` e `ca-certificates`, se faltarem, para baixar e abrir o arquivo.
- Baixa `node-v<versão>-linux-x64.tar.xz` de `https://nodejs.org/dist/`, confere a soma SHA256 e abre em `/usr/local/lib/nodejs/node-v<versão>-linux-<arquitetura>`.
- Cria os links `/usr/local/bin/node`, `/usr/local/bin/npm` e `/usr/local/bin/npx`. Se já existir um desses comandos ali que não veio do `bora`, a receita para sem mudar nada.
- Escreve `etc/npmrc` dentro da pasta do Node.js, com `prefix=${HOME}/.local`.
- Cria `~/.local/bin` na pasta pessoal de quem rodou o `bora`, se ainda não existir. O `~/.profile` do Ubuntu e do Debian põe essa pasta no PATH a cada login.

Se o Node.js da distro estiver instalado, ele fica, e o comando `node` passa a abrir a versão do `bora`, porque `/usr/local/bin` vem antes de `/usr/bin` no PATH.

## Como conferir

O `testar.sh` roda, como a pessoa:

- `node --version`, que precisa mostrar a versão da receita;
- `npm --version` e `npx --version`;
- `node -e 'console.log(1 + 1)'`;
- `npm prefix -g`, que precisa mostrar `~/.local`: é onde o `npm install -g` instala.

Para começar um projeto: `npm create vite@latest meu-site`.

## Como desfazer

O `desfazer.sh` apaga os links em `/usr/local/bin` e a pasta do Node.js em `/usr/local/lib/nodejs`, remove os pacotes que a receita instalou e a pasta `~/.local/bin`, se ela ficou vazia. Os programas que você instalou com `npm install -g` ficam em `~/.local/lib/node_modules`, e as pastas `node_modules` dos seus projetos, nos projetos.

## Fontes

- [Downloads do Node.js](https://nodejs.org/pt/download)
- [Calendário das versões LTS do Node.js](https://nodejs.org/pt/about/previous-releases)
- [Como conferir os arquivos baixados (SHASUMS256.txt)](https://github.com/nodejs/node#verifying-binaries)
- [npm: a configuração prefix](https://docs.npmjs.com/cli/using-npm/config#prefix)
