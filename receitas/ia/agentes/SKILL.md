---
name: bora
description: Monta um plano do bora (Linux para todos os rolês) para instalar ou configurar algo no Linux da pessoa, como firewall, backup, snapshot, ambiente leve, Git, Python, Node.js, contêineres e agentes de IA. Use quando a pessoa pedir para preparar, consertar ou configurar o computador dela com o bora, ou quando uma mudança no sistema precisaria de sudo.
---

# bora

O `bora` aplica receitas testadas no Linux (Ubuntu, Debian e derivadas). Cada receita sabe verificar, aplicar, testar e desfazer o que fez. Você, agente, só **planeja**: monta e valida um `plano.yaml`. Quem aplica é a pessoa, com `sudo`.

## Regras

- Nunca rode `sudo`, nem `bora aplicar` ou `bora desfazer`. Mostre o comando e peça para a pessoa rodar.
- Não instale nada no sistema por fora do `bora` (`apt`, scripts baixados da internet, `sudo npm`). Se não houver receita para o que a pessoa quer, diga isso.
- Use só rolês e receitas que aparecem em `bora lista`. Não invente parâmetros: cada receita tem uma página no catálogo do site, com a tabela de parâmetros, e o `bora validar` recusa os que não existem.
- Responda em português do Brasil, em linguagem simples.

## O comando

O `bora` pode estar no PATH ou ser o arquivo `bora-linux-x86_64` que a pessoa baixou. Procure com `command -v bora` e, se não achar, pergunte onde ele está.

## Passo a passo

1. Entenda a máquina, sem mudar nada: `bora diag --json`. Mostra a distro, a família, a memória, o disco e o que já está instalado.
2. Veja o que existe: `bora lista`. Mostra os rolês (o que a pessoa quer fazer) e as receitas (cada mudança), com o status de teste.
3. Monte o plano, sem menus:
   - um rolê inteiro: `bora plano <rolê> -r <pergunta>=<resposta> -o plano.yaml`
   - receitas avulsas: `bora plano --receitas <a>,<b> -p <receita>.<parâmetro>=<valor> -o plano.yaml`
4. Confira: `bora validar plano.yaml`. Se der erro, corrija e valide de novo.
5. Mostre o plano para a pessoa, explique cada passo em uma frase e peça para ela rodar:
   - `sudo bora aplicar plano.yaml --simular` para ver o que mudaria;
   - `sudo bora aplicar plano.yaml` para aplicar (o `bora` tira um snapshot antes);
   - `sudo bora desfazer` para voltar a última aplicação.

## Exemplos

```sh
bora plano pronto-para-estudar -o plano.yaml
bora plano comecar-a-programar -r perfil=web -p dev/git.email=ana@exemplo.com.br -o plano.yaml
bora plano --receitas seguranca/firewall -p seguranca/firewall.perfil=servidor-lan -o plano.yaml
```

## Quando algo falhar

Peça para a pessoa rodar `bora ajuda`, que monta uma pergunta com o diagnóstico e o erro, sem dados sensíveis. O registro completo fica em `/var/log/bora/bora.log`.

Catálogo, com os rolês, as receitas e os parâmetros: https://brahm.github.io/linux-para-todos-os-roles/catalogo/
