# Receitas

Uma receita é a menor unidade de mudança que o `bora` aplica: instalar e configurar o firewall, ativar o Flatpak, criar um compartilhamento Samba. Os rolês são feitos de receitas.

Toda receita sabe fazer quatro coisas: **verificar** se já está aplicada, **aplicar**, **testar** se funcionou e **desfazer**.

## Estrutura

```text
receitas/<area>/<id>/
  receita.yaml          metadados, parâmetros e registro de testes
  verificar.sh          já está aplicada?
  aplicar.sh            caminho comum a todas as famílias
  aplicar.<familia>.sh  opcional, só quando a família muda o comportamento
  testar.sh             a saída esperada vira teste
  desfazer.sh           volta ao estado anterior
  LEIAME.md             o porquê, em português, para quem quer aprender
```

As áreas planejadas são `base`, `sistema`, `seguranca`, `desktop`, `dev`, `ia`, `containers`, `servicos` e `rede`.

## `receita.yaml`

```yaml
id: seguranca/firewall
nome: Firewall
descricao: Bloqueia conexões de entrada e libera só o que o perfil pede.
risco: medio                 # baixo | medio | alto
precisa_root: true
familias:
  ubuntu: testada            # testada | herdada | comunidade | planejada | nao-se-aplica
  debian: testada
  fedora: planejada
  arch: planejada
  fedora-imutavel: planejada
  opensuse: comunidade
parametros:
  perfil:
    tipo: escolha
    opcoes: [desktop, servidor-lan, tailscale]
    padrao: desktop
    pergunta: Este computador é de uso pessoal, um servidor da casa ou fica acessível pela VPN?
  rede_local:
    tipo: cidr
    padrao: auto             # o bora descobre a rede local
testes:
  - distro: ubuntu
    versao: "26.04"
    data: 2026-11-10
    por: nome-ou-usuario
    resultado: ok
```

## Contrato dos scripts

- Todos começam com `#!/usr/bin/env bash` e `set -euo pipefail`.
- O `bora` roda os scripts a partir da pasta da receita, como root quando `precisa_root: true`.
- Os parâmetros chegam como variáveis de ambiente com o prefixo `BORA_` e o nome em maiúsculas, por exemplo `BORA_PERFIL` e `BORA_REDE_LOCAL`.
- O `bora` também informa `BORA_FAMILIA`, `BORA_DISTRO`, `BORA_VERSAO` e `BORA_ESTADO`, uma pasta onde a receita guarda o que precisa para desfazer (cópias de arquivos, lista de pacotes instalados).
- Se existir `aplicar.<familia>.sh` para a família da máquina, o `bora` usa esse no lugar do `aplicar.sh`. Vale o mesmo para `verificar`, `testar` e `desfazer`.

| Script | Código de saída |
|---|---|
| `verificar.sh` | `0` já está aplicada, `1` precisa aplicar, outro valor é erro |
| `aplicar.sh` | `0` aplicou; precisa ser idempotente, então rodar duas vezes não muda nada na segunda |
| `testar.sh` | `0` está funcionando; imprime em português o que conferiu |
| `desfazer.sh` | `0` voltou ao estado anterior, usando o que ficou em `BORA_ESTADO` |

## Regras

- Só repositórios oficiais da distro e Flatpak. Nada de AUR.
- Nada de `curl ... | sh`, exceto instaladores oficiais listados pelo projeto, que o `bora` baixa, confere e mostra antes de rodar.
- Nenhuma receita abre porta para a internet.
- Nenhuma receita guarda senha, token ou chave no repositório.
- Mensagens em português do Brasil.

## `LEIAME.md`

Use estas seções:

1. **O que faz:** uma ou duas frases.
2. **Por que:** o motivo, para quem quer aprender.
3. **O que muda no sistema:** pacotes, arquivos e serviços.
4. **Como conferir:** os comandos que o `testar.sh` roda, explicados.
5. **Como desfazer:** o que o `desfazer.sh` faz.
6. **Fontes:** documentação oficial consultada.
