#!/usr/bin/env bash
# Roda dentro do contêiner de teste: o cenário de vibecode local do rolê
# "Vibecodar". Confere que o plano troca "modelo: sugerido" pelo modelo que
# cabe na máquina, aplica o Ollama (com um modelo pequeno) e o LM Studio,
# aplica de novo (a segunda vez não pode mudar nada), confere que o modelo
# responde e desfaz, conferindo que os pacotes, o /usr/local, o /opt e a
# conta do serviço voltaram ao que eram.
# Precisa de rede: baixa o Ollama do GitHub, o modelo de registry.ollama.ai e
# o LM Studio de installers.lmstudio.ai, uns 3 GB no total.
set -euo pipefail
cd /bora
BORA="${BORA:-/bora/target/x86_64-unknown-linux-musl/release/bora}"
# Um modelo pequeno, que responde rápido sem placa de vídeo.
MODELO="${MODELO:-qwen3:0.6b}"
bora() { "$BORA" "$@"; }
etapa() { printf '\n=== %s ===\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}
pacotes() { dpkg-query -W -f='${db:Status-Abbrev} ${Package}\n' | awk '$1 == "ii" {print $2}' | sort; }

etapa "Preparar uma pessoa no computador"
id dev >/dev/null 2>&1 || useradd -m -s /bin/bash -c "Dani Dev,,," dev

etapa "O bora mede a máquina e sugere um modelo"
bora modelos
bora modelos --json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["modelos"] and "sugestao" in d' ||
    falhou "o bora modelos --json não trouxe a lista e a sugestão"

etapa "O rolê monta o plano de cada resposta"
role() { bora plano vibecodar -p dev/git.email=dani@exemplo.com.br "$@"; }
role -r local=ollama -o /tmp/plano-ollama.yaml
grep -q 'receita: ia/ollama' /tmp/plano-ollama.yaml || falhou "o Ollama ficou fora do plano"
! grep -q 'modelo: sugerido' /tmp/plano-ollama.yaml || falhou "o plano salvo ainda diz modelo: sugerido"
! grep -q 'ia/lm-studio' /tmp/plano-ollama.yaml || falhou "o LM Studio entrou sem ser pedido"
role -r local=ollama-sem-modelo -o /tmp/plano-sem-modelo.yaml
grep -q 'modelo: nenhum' /tmp/plano-sem-modelo.yaml || falhou "o Ollama sem modelo ainda baixa um modelo"
role -r local=lmstudio -o /tmp/plano-lms.yaml
grep -q 'ia/lm-studio' /tmp/plano-lms.yaml || falhou "o LM Studio ficou fora do plano"
! grep -q 'ia/ollama' /tmp/plano-lms.yaml || falhou "o Ollama entrou sem ser pedido"
role -r local=os-dois -o /tmp/plano-os-dois.yaml
grep -q 'ia/ollama' /tmp/plano-os-dois.yaml || falhou "a resposta os-dois não trouxe o Ollama"
grep -q 'ia/lm-studio' /tmp/plano-os-dois.yaml || falhou "a resposta os-dois não trouxe o LM Studio"
role -o /tmp/plano-padrao.yaml
! grep -Eq 'ia/(ollama|lm-studio)' /tmp/plano-padrao.yaml || falhou "o padrão do rolê instalou modelos locais"
! bora plano --receitas ia/ollama -p 'ia/ollama.modelo=qwen3;id' -o /tmp/plano-errado.yaml 2>/dev/null ||
    falhou "o plano aceitou um nome de modelo que não é de modelo"

etapa "Antes"
pacotes >/tmp/pacotes-antes
ls /usr/local/bin /usr/local/lib /opt >/tmp/local-antes
ls /usr/share/applications >/tmp/atalhos-antes 2>/dev/null || true

etapa "Aplicar"
bora plano --receitas ia/ollama,ia/lm-studio -p "ia/ollama.modelo=$MODELO" -o /tmp/plano.yaml
cat /tmp/plano.yaml
SUDO_USER=dev bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot

etapa "Aplicar de novo (nada pode mudar)"
saida=$(SUDO_USER=dev bora aplicar /tmp/plano.yaml --sem-perguntar --sem-snapshot)
printf '%s\n' "$saida"
grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "a segunda aplicação mudou alguma coisa"

etapa "Conferir o que a pessoa vai usar"
grep -qx 'Environment=OLLAMA_HOST=127.0.0.1:11434' /etc/systemd/system/ollama.service ||
    falhou "o Ollama não ficou só para este computador"
# Sem systemd no contêiner, o serviço não roda: o teste sobe o servidor na
# conta do serviço, como a receita faz, e pergunta ao modelo.
runuser -u ollama -- env HOME=/usr/share/ollama OLLAMA_HOST=127.0.0.1:11434 ollama serve >/tmp/ollama.log 2>&1 &
servidor=$!
for _ in $(seq 1 60); do curl -fsS http://127.0.0.1:11434/api/version >/dev/null 2>&1 && break; sleep 0.5; done
resposta=$(runuser -u dev -- env HOME=/home/dev OLLAMA_HOST=127.0.0.1:11434 ollama run "$MODELO" --think=false "Responda só: oi" 2>/dev/null) ||
    falhou "o modelo $MODELO não respondeu"
echo "O modelo respondeu: $resposta"
[ -n "$resposta" ] || falhou "o modelo respondeu vazio"
kill "$servidor"
wait "$servidor" 2>/dev/null || true
[ -x /usr/local/bin/lm-studio ] || falhou "o comando lm-studio não existe"
grep -q '^Exec=/usr/local/bin/lm-studio' /usr/share/applications/lm-studio.desktop || falhou "o atalho do LM Studio não abre o programa"

etapa "Desfazer"
bora desfazer --sem-perguntar
# Um pacote essencial ou importante do sistema que veio junto fica, de
# propósito (veja remover_pacotes_instalados no comum.sh), como no Debian o
# linux-sysctl-defaults, que chega com o procps.
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
diff -u /tmp/pacotes-antes /tmp/pacotes-depois || falhou "sobraram ou faltaram pacotes"
ls /usr/local/bin /usr/local/lib /opt >/tmp/local-depois
diff /tmp/local-antes /tmp/local-depois || falhou "sobrou alguma coisa em /usr/local ou /opt"
ls /usr/share/applications >/tmp/atalhos-depois 2>/dev/null || true
diff /tmp/atalhos-antes /tmp/atalhos-depois || falhou "sobrou o atalho do LM Studio"
! getent passwd ollama >/dev/null || falhou "a conta ollama ficou"
[ ! -e /usr/share/ollama ] || falhou "a pasta dos modelos ficou"
[ ! -e /etc/systemd/system/ollama.service ] || falhou "o serviço do Ollama ficou"
echo
echo "Vibecode local: tudo conferido."
