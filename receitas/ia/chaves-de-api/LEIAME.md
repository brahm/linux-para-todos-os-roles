# Chaves de API guardadas

## O que faz

Cria um arquivo para as chaves de API dos agentes de IA em `~/.config/chaves-de-api/chaves.env`, que só a sua conta abre, e faz cada terminal novo carregar as chaves que estiverem nele.

## Por que

Uma chave de API é uma senha que gasta dinheiro. Quem começa costuma colar a chave no próprio projeto, num `.env` que acaba no Git, ou direto no `.bashrc`, junto com o resto da configuração. Um arquivo só para as chaves, fora de qualquer projeto e com permissão 600, resolve os dois problemas: nenhum `git add` alcança, e outra conta do computador não lê.

Os agentes procuram as chaves em variáveis de ambiente com nomes conhecidos (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`). Com a chave no terminal, o OpenCode encontra o provedor sozinho, e os outros agentes também.

A receita nunca recebe a chave pelo `bora`: o plano é um arquivo que pode ir para o Git ou ser mostrado a uma IA. Você cola a chave no arquivo, num editor, depois de aplicar. O parâmetro `provedor` só põe o provedor escolhido no topo do arquivo e diz qual linha preencher.

## O que muda no sistema

- Cria a pasta `~/.config/chaves-de-api`, com permissão 700, e o arquivo `chaves.env`, com permissão 600, com uma linha comentada para cada provedor e o endereço onde criar a chave. Se o arquivo já existir, ele fica como está.
- Acrescenta ao `~/.bashrc` um bloco que carrega o arquivo em cada terminal novo.

Para usar uma chave: abra o arquivo, tire o `#` do começo da linha, cole a chave depois do `=` e abra um terminal novo.

## Como conferir

O `testar.sh` confere que a pasta e o arquivo só abrem para você (700 e 600), que outra conta não consegue ler o arquivo, que o arquivo não tem erro de sintaxe, que o bloco está no `.bashrc` e, com uma chave de teste num arquivo temporário, que a chave chega ao terminal (`printenv`).

## Como desfazer

O `desfazer.sh` tira o bloco do `bora` do `.bashrc`. O arquivo de chaves só sai se continuar igual ao modelo, sem nenhuma chave. Se você colou alguma, ele fica: apagar pode cortar o seu acesso. Para apagar de vez, remova o arquivo e revogue as chaves no site de cada provedor.

## Fontes

- [OpenCode: provedores e chaves](https://opencode.ai/docs/providers/)
- [OpenRouter: chaves de API](https://openrouter.ai/docs/api-keys)
- [DeepSeek: primeira chamada à API](https://api-docs.deepseek.com/)
- [Bash: o arquivo .bashrc](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html)
