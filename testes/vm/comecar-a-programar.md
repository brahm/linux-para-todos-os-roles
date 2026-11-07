# Roteiro em VM: Começar a programar

Comece do snapshot `limpa` da VM. Rode nas quatro distros do [README](README.md), uma vez com o perfil Python e outra, a partir do `limpa`, com o perfil web.

## 1. Aplicar o rolê

Rode com `sudo`, da sua conta, para as receitas configurarem a sua pasta pessoal:

```sh
sudo bora
```

Escolha "Começar a programar", o perfil, e informe o seu nome e e-mail.

- [ ] O plano termina com "cada receita passou no teste".
- [ ] `sudo bora aplicar` de novo, com o mesmo plano, diz "Tudo já estava aplicado".

## 2. Conferir o que o contêiner não confere

Feche e abra o terminal antes, para o `PATH` novo valer.

**Git (`dev/git`)**

- [ ] `git config --global user.name` e `user.email` mostram o que você informou.
- [ ] `~/.ssh/id_ed25519.pub` existe. Cadastre a chave numa conta de teste do GitHub e confira com `ssh -T git@github.com`.
- [ ] Crie um repositório de teste, faça um commit e um `git push`.

**Ferramentas de compilação (`dev/compilacao`)**

- [ ] `gcc --version`, `make --version` e `pkg-config --version` respondem.

**Python (`dev/python`), no perfil Python**

- [ ] Num projeto novo: `python3 -m venv .venv && source .venv/bin/activate && pip install requests` funciona sem `sudo`.
- [ ] `pipx install cowsay && cowsay oi` funciona, e o comando fica no `PATH` depois de abrir outro terminal.
- [ ] `pip install requests` fora de um ambiente virtual é recusado pela distro (PEP 668), como esperado.

**Node.js (`dev/node`), no perfil web**

- [ ] `node --version` mostra a versão da receita, e não a da distro.
- [ ] `npm install -g cowsay` funciona sem `sudo`, e `cowsay oi` responde.
- [ ] `npm create vite@latest teste -- --template vanilla && cd teste && npm install && npm run dev` sobe o servidor, e o navegador abre a página.

**Contêineres (`containers/podman`)**

- [ ] `podman run --rm hello-world` mostra a mensagem do contêiner de teste, sem `sudo`.
- [ ] `podman run --rm -it docker.io/library/alpine sh -c 'echo ok'` funciona.
- [ ] Depois de reiniciar, os dois comandos continuam funcionando.

## 3. Desfazer

```sh
sudo bora desfazer
```

- [ ] `git config --global --list` volta ao que era (vazio, numa VM limpa).
- [ ] `node`, `pipx` e `podman` não estão mais instalados; a chave SSH e os projetos continuam na pasta pessoal.

## 4. Registrar

Siga o [README](README.md#registrar-o-resultado), com uma linha por receita e por distro.
