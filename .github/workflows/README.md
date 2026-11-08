# Workflows do GitHub Actions

| Workflow | Arquivo | Quando roda | O que faz |
|---|---|---|---|
| Testes | [`testes.yml`](testes.yml) | a cada push na `main` e a cada pull request | Testes do `bora`, shellcheck, binário estático e as receitas em contêiner no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13 |
| Máquina virtual | [`vm.yml`](vm.yml) | **agendado**: todo domingo; também nos pull requests que mexem nos scripts das receitas, nos rolês ou no próprio teste | Liga uma VM com QEMU e KVM no Ubuntu 24.04, no Ubuntu 26.04 e no Debian 13 e roda o que não depende de tela: aplica o rolê 1 e os outros rolês (sem as receitas de [`so-com-tela.txt`](../../testes/vm/qemu/so-com-tela.txt)), reinicia, confere que tudo voltou sozinho, reconecta o disco externo do backup e desfaz. Na main, quando passa, grava nas receitas o registro com `onde: vm` (um commit do `github-actions[bot]`) e publica o site; quando o agendamento falha, abre uma issue com a etiqueta `vm` (ou comenta na que estiver aberta). Ver [`../../testes/vm/qemu/`](../../testes/vm/qemu/) |
| Publicar | [`publicar.yml`](publicar.yml) | a cada push na `main` (só publica se a versão do `Cargo.toml` ainda não tiver tag) e em tags `v*` | Compila para x86_64, cria a tag e a página da versão, com o `SHA256SUMS` e as notas em português ([`escrever.sh`](../../ferramentas/notas/escrever.sh)) |
| Site | [`site.yml`](site.yml) | quando `docs/` muda na `main` | Publica o site no GitHub Pages |
| Etiquetas | [`etiquetas.yml`](etiquetas.yml) | quando [`../etiquetas.txt`](../etiquetas.txt) muda na `main` | Cria ou atualiza as etiquetas que os formulários de issue e os workflows usam |
| Links | [`links.yml`](links.yml) | **agendado**: dia 1 de cada mês | Confere os links do site e da documentação e abre uma issue `links-quebrados` quando algum quebra |
| Node.js | [`node.yml`](node.yml) | **agendado**: toda segunda-feira | Compara a versão do Node.js da receita `dev/node` com nodejs.org e abre uma issue `node` quando sai uma versão nova da mesma linha |

Todos também rodam à mão, em Actions, escolhendo o workflow e "Run workflow".

## Atenção: os agendados param depois de 60 dias sem commits

Num repositório público, o GitHub **desliga sozinho os workflows agendados** (Links, Node.js e Máquina virtual) quando o repositório passa 60 dias sem nenhum commit. Ele manda um e-mail avisando antes, e o workflow aparece como desativado na aba Actions.

Para religar: em Actions, escolha o workflow e clique em "Enable workflow". Qualquer commit novo na `main` também zera a contagem. Se o projeto ficar parado por muito tempo, vale olhar a aba Actions de vez em quando, porque um aviso de segurança do Node.js pode passar despercebido.

## Permissões

Cada workflow pede só o que usa. Os que abrem issues (Links, Node.js e Etiquetas) têm `issues: write`; o Publicar tem `contents: write` só no passo que cria a versão; o Site tem `pages: write`. Nenhum usa segredos além do `GITHUB_TOKEN` que o próprio GitHub entrega.
