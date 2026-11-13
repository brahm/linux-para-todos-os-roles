# shellcheck shell=bash disable=SC2034
# Variáveis e funções comuns aos scripts da receita desktop/ambiente-leve.
# Não é executável: verificar, aplicar, testar e desfazer carregam com `source`,
# depois do comum.sh do bora.

PASTA_CONTAS=/var/lib/AccountsService/users

# O ambiente pedido no parâmetro (xfce ou lxqt). Qualquer outro valor para tudo.
ambiente() {
    case "${BORA_AMBIENTE:-xfce}" in
        xfce | lxqt) echo "${BORA_AMBIENTE:-xfce}" ;;
        *) falha "ambiente precisa ser xfce ou lxqt (veio $BORA_AMBIENTE)" ;;
    esac
}

# O nome da sessão, como aparece em /usr/share/xsessions.
sessao() { ambiente; }

# O nome para mostrar nas mensagens.
nome_do_ambiente() {
    case "$(ambiente)" in
        xfce) echo Xfce ;;
        lxqt) echo LXQt ;;
    esac
}

# O que o ambiente precisa para funcionar no dia a dia, sem os extras que
# viriam junto como recomendação (jogos, protetores de tela, outra tela de login).
pacotes_do_ambiente() {
    case "$(ambiente)" in
        xfce) echo xfce4 xfce4-terminal xfce4-notifyd xfce4-power-manager xfce4-screensaver mate-polkit tango-icon-theme ;;
        lxqt) echo lxqt-core qterminal openbox lxqt-powermanagement pavucontrol-qt xscreensaver ;;
    esac
    # O servidor gráfico: os desktops novos usam Wayland e podem não ter o Xorg.
    command -v Xorg >/dev/null || pacote_instalado xserver-xorg || echo xserver-xorg
    # Sem o applet, não dá para escolher a rede Wi-Fi fora do GNOME e do KDE.
    # O nome mudou: network-manager-applet nas versões novas, network-manager-gnome no Ubuntu 24.04.
    if pacote_instalado network-manager; then primeiro_disponivel network-manager-applet network-manager-gnome; fi
}

# O primeiro pacote da lista que já está instalado ou, senão, que existe nos repositórios.
primeiro_disponivel() {
    local p
    for p in "$@"; do
        if pacote_instalado "$p"; then
            echo "$p"
            return 0
        fi
    done
    for p in "$@"; do
        if [ -n "$(apt-cache policy "$p" 2>/dev/null | awk '/Candidate:/ && $2 != "(none)" {print $2}')" ]; then
            echo "$p"
            return 0
        fi
    done
    echo "$1"
}

# O programa que abre a sessão do ambiente.
programa_da_sessao() {
    case "$(ambiente)" in
        xfce) echo startxfce4 ;;
        lxqt) echo startlxqt ;;
    esac
}

# As pessoas do computador: contas com UID de 1000 para cima e um shell de verdade.
pessoas() {
    getent passwd | awk -F: '$3 >= 1000 && $3 < 60000 && $7 !~ /(nologin|false)$/ {print $1}'
}

# A sessão que o AccountsService guarda para a pessoa (GDM e LightDM leem daqui).
sessao_de() {
    local arq="$PASTA_CONTAS/$1"
    [ -f "$arq" ] || return 0
    awk -F= '/^\[/ {dentro = ($0 == "[User]")} dentro && $1 == "Session" {print $2}' "$arq"
}

# Põe Session e XSession na seção [User], mantendo o resto do arquivo.
definir_sessao() {
    local arq="$PASTA_CONTAS/$1" valor=$2 tmp
    tmp=$(mktemp)
    if [ -f "$arq" ]; then cat "$arq" >"$tmp"; fi
    python3 - "$tmp" "$valor" <<'PY'
import sys
caminho, valor = sys.argv[1], sys.argv[2]
linhas = open(caminho, encoding="utf-8").read().splitlines()
saida, dentro, achou, feitos = [], False, False, set()
def completar():
    for chave in ("Session", "XSession"):
        if chave not in feitos:
            saida.append(f"{chave}={valor}")
for l in linhas:
    if l.startswith("["):
        if dentro:
            completar()
        dentro = l.strip() == "[User]"
        achou = achou or dentro
    elif dentro and l.split("=", 1)[0] in ("Session", "XSession"):
        chave = l.split("=", 1)[0]
        feitos.add(chave)
        l = f"{chave}={valor}"
    saida.append(l)
if dentro:
    completar()
if not achou:
    saida += ["[User]", f"Session={valor}", f"XSession={valor}"]
open(caminho, "w", encoding="utf-8").write("\n".join(saida) + "\n")
PY
    escrever_arquivo "$arq" 0600 <"$tmp"
    rm -f "$tmp"
}
