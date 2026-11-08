# Git

## O que faz

Instala o Git, põe o seu nome e o seu e-mail nos commits e cria uma chave SSH para você entrar no GitHub ou no GitLab sem digitar senha.

## Por que

O Git guarda a história de um projeto: cada mudança vira um commit, com quem fez, quando e por quê. É a primeira ferramenta que qualquer tutorial de programação pede, e o GitHub e o GitLab são onde os projetos ficam guardados e compartilhados.

Sem nome e e-mail configurados, o primeiro `git commit` para com uma mensagem em inglês pedindo para configurar. A receita já deixa isso pronto, e ajusta dois padrões que confundem quem começa:

- `init.defaultBranch = main`: repositórios novos começam no ramo `main`, o mesmo nome que o GitHub e o GitLab usam. Sem isso, o Git do Ubuntu 24.04 cria o ramo `master` e mostra um aviso longo a cada `git init`;
- `pull.rebase = false`: quando o `git pull` encontra mudanças dos dois lados, ele junta as duas com um commit de merge, o comportamento clássico. Sem isso, o Git para e pede que você escolha entre três opções que quem está começando ainda não conhece.

A chave SSH é o jeito recomendado de entrar no GitHub e no GitLab pelo terminal: o GitHub não aceita mais a senha da conta no `git push`. A receita cria uma chave do tipo ed25519, a recomendada hoje, e mostra a linha pública para você colar no site.

A chave é criada sem senha, porque a receita não faz perguntas no meio do caminho. Ela só abre as suas contas no GitHub ou no GitLab, e só de quem tem acesso à sua pasta pessoal. Para pôr uma senha nela depois, rode `ssh-keygen -p -f ~/.ssh/id_ed25519`.

## O que muda no sistema

- Instala os pacotes `git` e `openssh-client`, se faltarem.
- No `~/.gitconfig` da pessoa (ou no `~/.config/git/config`, se for o único que existir), grava `user.name`, `user.email` e, se ainda não estiverem definidos, `init.defaultBranch` e `pull.rebase`. O que já estava no arquivo fica.
- Com `chave_ssh: sim` (o padrão), cria `~/.ssh/id_ed25519` e `~/.ssh/id_ed25519.pub`, se a pessoa ainda não tiver uma chave `id_ed25519`, `id_ecdsa` ou `id_rsa`. Se tiver, usa a que existe.

A receita configura a conta de quem rodou o `bora` com `sudo`. Para configurar outra conta, use o parâmetro `usuario`. Com `nome: auto`, vale o nome que já estiver no Git ou, se não houver, o nome completo da conta no computador.

## Como conferir

O `testar.sh` roda, como a pessoa:

- `git --version`: o Git está instalado;
- `git config --global user.name`, `user.email`, `init.defaultBranch` e `pull.rebase`: cada um tem um valor;
- um commit de verdade num repositório de teste, criado numa pasta temporária e apagado no fim;
- `ssh-keygen -l -f ~/.ssh/id_ed25519.pub`: a chave é válida.

Para ver você mesmo: `git config --global --list`. Para testar a chave depois de cadastrar no GitHub: `ssh -T git@github.com`, que responde com o seu usuário.

## Como desfazer

O `desfazer.sh` volta o `~/.gitconfig` ao que era, ou apaga o arquivo, se foi a receita que o criou, e remove os pacotes que ela instalou.

A chave SSH fica: ela pode já estar cadastrada no GitHub ou no GitLab, e apagar cortaria o seu acesso. Para remover, apague `~/.ssh/id_ed25519` e `~/.ssh/id_ed25519.pub` e tire a chave da sua conta no site.

## Fontes

- [Primeiros passos: configuração inicial do Git (Pro Git, em português)](https://git-scm.com/book/pt-br/v2/Primeiros-Passos-Configura%C3%A7%C3%A3o-inicial-do-Git)
- [git-config: init.defaultBranch e pull.rebase](https://git-scm.com/docs/git-config)
- [Gerar uma chave SSH e adicionar ao GitHub](https://docs.github.com/pt/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [Chaves SSH no GitLab](https://docs.gitlab.com/user/ssh/)
