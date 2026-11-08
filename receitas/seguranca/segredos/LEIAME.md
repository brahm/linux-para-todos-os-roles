# Verificação de segredos

## O que faz

Antes de cada commit, o `gitleaks` confere o que vai entrar e barra o commit que leva uma chave de API, um token ou uma senha. E o Git passa a ignorar, em todos os projetos, os arquivos `.env` e as chaves privadas.

## Por que

Colar uma chave de API num arquivo e fazer commit é o acidente mais comum de quem programa com agentes de IA. Num repositório público, robôs acham a chave em minutos e gastam o crédito da conta. Apagar o arquivo depois não resolve, porque a chave continua no histórico do Git. O jeito é não deixar entrar.

A receita usa dois cuidados, um atrás do outro:

1. **O `.gitignore` global** faz o Git nem oferecer os arquivos `.env` e as chaves no `git add`.
2. **O gitleaks** confere o conteúdo do que vai no commit, para pegar a chave que foi parar num arquivo comum, como `config.py`.

O gancho fica numa pasta da sua conta (`core.hooksPath`), e não em cada projeto, então vale também para os projetos que você clonar depois. Como o Git deixa de olhar o `.git/hooks` de cada projeto quando há uma pasta global, o gancho do `bora` chama o do projeto depois do gitleaks, e os ganchos que o projeto já tinha continuam funcionando.

Quando o gitleaks errar (um texto de exemplo que parece chave, por exemplo), faça o commit com `git commit --no-verify`.

## O que muda no sistema

- Instala os pacotes `git` e `gitleaks`.
- Acrescenta um bloco ao arquivo de exclusões globais do Git: o que estiver em `core.excludesFile` ou, se não houver, `~/.config/git/ignore`, que o Git lê sem precisar de configuração. O bloco ignora `.env`, `.env.*`, `*.env` (mas não `.env.example`), `*.pem`, `*.key`, as chaves SSH e o `.netrc`.
- Cria `~/.config/git/ganchos-bora`, com o gancho e um link para cada nome de gancho do Git.
- Configura `core.hooksPath` no `~/.gitconfig` (ou `~/.config/git/config`) para essa pasta. Se já houver outro `core.hooksPath`, a receita para sem mudar nada: você já usa ganchos globais, e ela não passa por cima.

Um projeto que define o próprio `core.hooksPath` (como os que usam o husky) usa os ganchos dele, e o gitleaks não roda ali. Nesses projetos, chame `gitleaks protect --staged` a partir do gancho do projeto.

## Como conferir

O `testar.sh` cria um repositório de teste e, como você:

- cria um `.env` e confere que o Git ignora (`git check-ignore .env`);
- tenta um commit com um token do GitHub inventado, que precisa ser barrado;
- faz um commit sem segredo, que precisa passar;
- confere que um gancho do próprio projeto (`.git/hooks/post-commit`) continua rodando.

Para conferir um projeto inteiro, com todo o histórico: `gitleaks detect`.

## Como desfazer

O `desfazer.sh` tira o `core.hooksPath`, se ainda for o do `bora`, apaga o gancho e os links, tira o bloco do `bora` do arquivo de exclusões (e o arquivo, se ele foi criado pela receita e ficou vazio) e remove os pacotes que a receita instalou. As outras linhas que você escreveu nesses arquivos ficam.

## Fontes

- [gitleaks](https://github.com/gitleaks/gitleaks)
- [Git: core.hooksPath e os ganchos](https://git-scm.com/docs/githooks)
- [Git: o arquivo de exclusões global (core.excludesFile)](https://git-scm.com/docs/gitignore)
- [GitHub: o que fazer quando um segredo vaza](https://docs.github.com/pt/code-security/secret-scanning/working-with-secret-scanning-and-push-protection)
