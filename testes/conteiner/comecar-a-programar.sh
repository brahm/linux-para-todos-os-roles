#!/usr/bin/env bash
# Roda dentro do contêiner de teste: aplica o rolê "Começar a programar" no
# perfil pedido (PERFIL=python ou web), aplica de novo (a segunda vez não pode
# mudar nada), testa e desfaz, conferindo que os pacotes, os arquivos da pessoa
# e o /usr/local voltaram ao que eram.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
PERFIL="${PERFIL:-python}"
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}

etapa "Preparar uma pessoa no computador"
# Uma conta sem faixa de IDs para contêineres, como as criadas com useradd
# antigo, e com um .gitconfig que já tinha alguma coisa.
id aluna >/dev/null 2>&1 || useradd -m -s /bin/bash -c "Ana Aluna,,," aluna
sed -i '/^aluna:/d' /etc/subuid /etc/subgid 2>/dev/null || true
printf '[core]\n\teditor = nano\n' >/home/aluna/.gitconfig
chown aluna:aluna /home/aluna/.gitconfig
cp /home/aluna/.gitconfig /tmp/gitconfig-antes
cp /etc/subuid /tmp/subuid-antes 2>/dev/null || : >/tmp/subuid-antes
pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }

etapa "O rolê monta o plano do perfil $PERFIL"
bora plano comecar-a-programar -r "perfil=$PERFIL" -p dev/git.email=ana@exemplo.com.br -o /tmp/plano-role.yaml
bora validar /tmp/plano-role.yaml
cat /tmp/plano-role.yaml
if [ "$PERFIL" = web ]; then
    grep -q dev/node /tmp/plano-role.yaml || falhou "o perfil web ficou sem o Node.js"
    ! grep -q dev/python /tmp/plano-role.yaml || falhou "o perfil web trouxe a receita do Python"
else
    grep -q dev/python /tmp/plano-role.yaml || falhou "o perfil python ficou sem o Python"
    ! grep -q dev/node /tmp/plano-role.yaml || falhou "o perfil python trouxe o Node.js"
fi

etapa "Atualizar antes"
bora plano --receitas base/atualizar -p base/atualizar.automaticas=nao -o /tmp/so-atualizar.yaml
bora aplicar /tmp/so-atualizar.yaml --sem-perguntar --sem-snapshot
pacotes >/tmp/pacotes-antes
ls /usr/local/bin /usr/local/lib >/tmp/local-antes

etapa "Plano"
# Sem a atualização, que já rodou; o resto como o rolê monta, com a pessoa pelo sudo.
grep -v 'base/atualizar' /tmp/plano-role.yaml >/tmp/plano.yaml
cat /tmp/plano.yaml

etapa "Aplicar"
SUDO_USER=aluna bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot

etapa "Conferir o que mudou"
como() { runuser -u aluna -- env HOME=/home/aluna PATH=/home/aluna/.local/bin:/usr/local/bin:/usr/bin:/bin "$@"; }
[ "$(como git config --global user.name)" = "Ana Aluna" ] || falhou "o nome do Git não veio da conta"
[ "$(como git config --global user.email)" = ana@exemplo.com.br ] || falhou "o e-mail do Git não ficou"
[ "$(como git config --global core.editor)" = nano ] || falhou "o que já estava no .gitconfig sumiu"
[ "$(stat -c %U /home/aluna/.gitconfig)" = aluna ] || falhou "o .gitconfig mudou de dono"
[ "$(stat -c %U /home/aluna/.ssh/id_ed25519)" = aluna ] || falhou "a chave SSH não é da aluna"
grep -q '^aluna:' /etc/subuid || falhou "a aluna ficou sem faixa de IDs"
d=$(como mktemp -d)
como git -C "$d" init -q
if [ "$PERFIL" = web ]; then
    como sh -c "cd $d && npm init -y >/dev/null && node -e 'console.log(require(\"./package.json\").name)'" || falhou "o projeto em Node.js não rodou"
    como npm install -g --no-audit --no-fund cowsay >/dev/null || falhou "npm install -g sem sudo não funcionou"
    [ -x /home/aluna/.local/bin/cowsay ] || falhou "o programa do npm -g não foi para ~/.local/bin"
    como npm uninstall -g cowsay >/dev/null
else
    # O venv do Python 3.13 em diante já se ignora no Git; o projeto é o ola.py.
    como sh -c "cd $d && echo 'import six; print(\"olá\")' >ola.py && python3 -m venv .venv && .venv/bin/pip install -q --disable-pip-version-check six && .venv/bin/python ola.py" || falhou "o projeto em Python não rodou"
fi
como git -C "$d" add -A
como git -C "$d" commit -q -m "projeto de exemplo" || falhou "o commit do projeto de exemplo falhou"
rm -rf "${d:?}"
echo "ok: Git, $PERFIL e Podman como o plano pediu"

etapa "Aplicar de novo (nada pode mudar)"
saida=$(SUDO_USER=aluna bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"
grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "a segunda aplicação mudou alguma coisa"

etapa "Desfazer"
bora desfazer --sem-perguntar

etapa "Conferir que voltou"
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
diff -u /tmp/gitconfig-antes /home/aluna/.gitconfig || falhou "o .gitconfig não voltou ao que era"
diff -u /tmp/subuid-antes /etc/subuid || falhou "o /etc/subuid não voltou ao que era"
# O que o uso cria (o cache do pip, as imagens do Podman) é da pessoa e fica;
# a pasta que a receita criou vazia sai.
[ ! -e /home/aluna/.local/bin ] || falhou "a pasta ~/.local/bin, criada pela receita, ficou"
ls /usr/local/bin /usr/local/lib >/tmp/local-depois
diff -u /tmp/local-antes /tmp/local-depois || falhou "o /usr/local não voltou ao que era"
[ -f /home/aluna/.ssh/id_ed25519 ] || falhou "o desfazer apagou a chave SSH"
[ ! -e /etc/containers/registries.conf.d/50-bora-docker-hub.conf ] || falhou "a configuração dos registros ficou"

echo
echo "Tudo certo: aplicou o perfil $PERFIL, não mudou nada na segunda vez e desfez."
