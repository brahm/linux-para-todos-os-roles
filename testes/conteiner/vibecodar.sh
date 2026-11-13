#!/usr/bin/env bash
# Roda dentro do contêiner de teste: aplica o rolê "Vibecodar" com todos os
# agentes, o VS Code e a caixa de areia, aplica de novo (a segunda vez não pode
# mudar nada), confere o que a pessoa vai usar e desfaz, conferindo que os
# pacotes, os arquivos da pessoa, o /usr/local e o APT voltaram ao que eram.
# Precisa de rede: baixa o Node.js, os agentes do npm e do PyPI e o VS Code.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
AGENTES="${AGENTES:-claude,codex,copilot,opencode,vibe}"
EDITOR_="${EDITOR_:-vscode}"
# Atalhos: `bora` roda o binário em teste, `etapa` imprime um título para
# achar o passo no log do CI, e `falhou` para tudo com a mensagem.
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}

etapa "Preparar uma pessoa no computador"
# Uma conta com o .bashrc padrão, uma regra própria no ignore global do Git e
# uma configuração do Claude Code, para conferir que o desfazer volta cada um.
id dev >/dev/null 2>&1 || useradd -m -s /bin/bash -c "Dani Dev,,," dev
casa=/home/dev
# Roda um comando como a pessoa dev, com o PATH de uma sessão comum.
como() { runuser -u dev -- env HOME=$casa PATH=$casa/.local/bin:/usr/local/bin:/usr/bin:/bin "$@"; }
[ -f $casa/.bashrc ] || cp /etc/skel/.bashrc $casa/.bashrc
como mkdir -p $casa/.config/git $casa/.claude
echo '*.swp' >$casa/.config/git/ignore
echo '{"theme": "dark"}' >$casa/.claude/settings.json
chown -R dev:dev $casa
for f in .bashrc .config/git/ignore .claude/settings.json; do cp "$casa/$f" "/tmp/antes-$(basename "$f")"; done
# Os pacotes instalados, um por linha. O teste compara o antes e o depois.
pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }

etapa "O rolê monta o plano"
bora plano vibecodar -r "agentes=$AGENTES" -r provedor=openrouter -r "editor=$EDITOR_" -r caixa=sim \
    -p dev/git.email=dani@exemplo.com.br -o /tmp/plano-role.yaml
bora validar /tmp/plano-role.yaml
cat /tmp/plano-role.yaml
grep -q ia/caixa-de-areia /tmp/plano-role.yaml || falhou "a caixa de areia ficou fora do plano"
! grep -q desktop/flatpak /tmp/plano-role.yaml || falhou "o plano trouxe o Flatpak sem o VSCodium ou o Zed"
bora plano vibecodar -r caixa=nao -p dev/git.email=dani@exemplo.com.br -o /tmp/plano-sem-caixa.yaml
! grep -q ia/caixa-de-areia /tmp/plano-sem-caixa.yaml || falhou "a caixa de areia entrou sem ser pedida"
bora plano vibecodar -r editor=zed -p dev/git.email=dani@exemplo.com.br -o /tmp/plano-zed.yaml
grep -q desktop/flatpak /tmp/plano-zed.yaml || falhou "o Zed ficou sem o Flatpak"
! bora plano vibecodar -r agentes=claude,chatgpt -p dev/git.email=dani@exemplo.com.br -o /tmp/plano-errado.yaml 2>/dev/null ||
    falhou "o plano aceitou um agente que não existe"

etapa "Atualizar antes"
bora plano --receitas base/atualizar -p base/atualizar.automaticas=nao -o /tmp/so-atualizar.yaml
bora aplicar /tmp/so-atualizar.yaml --sem-perguntar --sem-snapshot
pacotes >/tmp/pacotes-antes
ls /usr/local/bin /usr/local/lib >/tmp/local-antes
ls /etc/apt/sources.list.d /etc/apt/keyrings 2>/dev/null >/tmp/apt-antes || true

etapa "Aplicar"
grep -v 'base/atualizar' /tmp/plano-role.yaml >/tmp/plano.yaml
SUDO_USER=dev bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot

etapa "Conferir o que a pessoa vai usar"
for a in ${AGENTES//,/ }; do
    v=$(como "$a" --version 2>&1 | awk 'NR == 1') || falhou "o agente $a não respondeu"
    echo "ok: $a $v"
done
[ "$(stat -c '%a %U' $casa/.config/chaves-de-api/chaves.env)" = "600 dev" ] || falhou "o arquivo de chaves não é só da pessoa"
grep -q '^# OPENROUTER_API_KEY=' $casa/.config/chaves-de-api/chaves.env || falhou "o arquivo de chaves ficou sem o OpenRouter"
grep -qx '\*.swp' $casa/.config/git/ignore || falhou "a regra que a pessoa já tinha no ignore sumiu"
if [[ ",$AGENTES," == *,claude,* ]]; then
    python3 -c 'import json,sys; c=json.load(open(sys.argv[1])); sys.exit(0 if c["theme"] == "dark" and c["sandbox"]["enabled"] is True else 1)' $casa/.claude/settings.json ||
        falhou "a configuração do Claude Code perdeu o que tinha ou ficou sem a caixa de areia"
fi
# Um projeto de exemplo, criado dentro da caixa, como um agente faria.
como mkdir -p $casa/projetos/exemplo
(cd $casa/projetos/exemplo && como caixa sh -c 'git init -q && echo "print(\"olá\")" >ola.py && echo "OPENROUTER_API_KEY=sk-or-v1-x" >.env') ||
    falhou "a caixa de areia não deixou o agente criar o projeto"
(cd $casa/projetos/exemplo && como git add -A && como git commit -q -m "projeto de exemplo") || falhou "o commit do projeto de exemplo falhou"
[ -z "$(como git -C $casa/projetos/exemplo ls-files .env)" ] || falhou "o .env foi para o Git"
printf 'TOKEN = "ghp_%s"\n' R7mQ2xK9vB4nL8pT3wY6zC1dF5gH0jS2aE7u >$casa/projetos/exemplo/config.py
chown dev:dev $casa/projetos/exemplo/config.py
(cd $casa/projetos/exemplo && como git add config.py && ! como git commit -q -m "com segredo" 2>/dev/null) || falhou "o gitleaks deixou passar um token"
(cd $casa/projetos/exemplo && como caixa touch $casa/fora-da-caixa 2>/dev/null) && falhou "a caixa deixou escrever fora do projeto"
rm -rf "${casa:?}/projetos"
if [ "$EDITOR_" = vscode ]; then
    como code --version >/dev/null || falhou "o VS Code não respondeu"
fi
echo "ok: agentes, chaves, segredos, caixa de areia e editor"

etapa "Aplicar de novo (nada pode mudar)"
saida=$(SUDO_USER=dev bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"
grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "a segunda aplicação mudou alguma coisa"

etapa "Desfazer"
bora desfazer --sem-perguntar

etapa "Conferir que voltou"
# Pacote essencial ou protegido? O desfazer nunca tira esses (igual ao comum.sh),
# então o teste também não cobra que eles saiam.
do_sistema() {
    case "$(dpkg-query -W -f='${Essential} ${Protected} ${Priority}' "$1" 2>/dev/null)" in
        yes\ * | *\ yes\ * | *\ required | *\ important) return 0 ;;
    esac
    return 1
}
pacotes | while read -r p; do
    if ! grep -qxF "$p" /tmp/pacotes-antes && do_sistema "$p"; then
        echo "(mantido por ser do sistema: $p)" >&2
        continue
    fi
    echo "$p"
done >/tmp/pacotes-depois
diff -u /tmp/pacotes-antes /tmp/pacotes-depois || falhou "os pacotes não voltaram ao que eram"
for f in .bashrc .config/git/ignore .claude/settings.json; do
    diff -u "/tmp/antes-$(basename "$f")" "$casa/$f" || falhou "o $f não voltou ao que era"
done
[ -z "$(como git config --global --get core.hooksPath)" ] || falhou "o Git continuou com os ganchos do bora"
[ ! -e $casa/.config/chaves-de-api/chaves.env ] || falhou "o arquivo de chaves sem nenhuma chave ficou"
[ ! -e $casa/.claude/skills/bora/SKILL.md ] || falhou "a skill do bora ficou"
for a in ${AGENTES//,/ }; do
    [ ! -e "$casa/.local/bin/$a" ] || falhou "o agente $a ficou em ~/.local/bin"
done
ls /usr/local/bin /usr/local/lib >/tmp/local-depois
diff -u /tmp/local-antes /tmp/local-depois || falhou "o /usr/local não voltou ao que era"
ls /etc/apt/sources.list.d /etc/apt/keyrings 2>/dev/null >/tmp/apt-depois || true
diff -u /tmp/apt-antes /tmp/apt-depois || falhou "os repositórios do APT não voltaram ao que eram"

echo
echo "Tudo certo: aplicou o rolê Vibecodar, não mudou nada na segunda vez e desfez."
