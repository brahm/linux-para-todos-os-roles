#!/usr/bin/env bash
# Roda dentro da máquina virtual que o tela.sh liga, como root, em fases:
#
#   preparar        instala a tela de login (GDM) e o Firefox, como num
#                   desktop, cria a pessoa "aluno" e liga a tela no boot
#   tela-de-login   espera a tela de login aparecer
#   aplicar         aplica as receitas de so-com-tela.txt (duas vezes, a
#                   segunda sem mudar nada), com o ambiente leve como padrão,
#                   e liga a entrada automática do aluno
#   sessao          espera o aluno entrar sozinho no ambiente leve
#   firefox         abre o Firefox na sessão do aluno e espera o uBlock Origin
#                   ser instalado pela política da receita
#   sair            desliga a entrada automática e fecha o Firefox
#   desfazer        desfaz tudo, confere no Ubuntu que o Snap e o Firefox do
#                   Snap voltaram e espera a tela de login voltar
#
# O ambiente leve é o Xfce no Ubuntu e o LXQt no Debian, como nos testes em
# contêiner. No fim, /root/cobertas.txt lista as receitas que passaram por aqui.
set -euo pipefail
cd /bora
etapa() { printf '\n--- %s ---\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}
. /etc/os-release
if [ "$ID" = debian ]; then AMBIENTE=lxqt; else AMBIENTE=xfce; fi
case "$AMBIENTE" in
    xfce) PROCESSO=xfce4-session ;;
    lxqt) PROCESSO=lxqt-session ;;
esac
PESSOA=aluno

# O arquivo de configuração do GDM: custom.conf no Ubuntu, daemon.conf no Debian.
conf_do_gdm() {
    local f
    for f in /etc/gdm3/custom.conf /etc/gdm3/daemon.conf; do
        if [ -f "$f" ]; then
            echo "$f"
            return 0
        fi
    done
    falhou "não achei a configuração do GDM em /etc/gdm3"
}

# A sessão gráfica de uma classe (greeter, a tela de login, ou user), com o
# usuário dela: "id usuario tipo", uma por linha.
sessoes() {
    local s
    for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do
        if [ "$(loginctl show-session "$s" -p Class --value)" = "$1" ]; then
            echo "$s $(loginctl show-session "$s" -p Name --value) $(loginctl show-session "$s" -p Type --value)"
        fi
    done
}

esperar_tela_de_login() {
    for _ in $(seq 1 60); do
        if systemctl is-active --quiet display-manager.service && [ -n "$(sessoes greeter)" ]; then
            sessoes greeter
            # Dá tempo de a tela terminar de desenhar antes da captura.
            sleep 10
            return 0
        fi
        sleep 3
    done
    systemctl status display-manager.service --no-pager || true
    loginctl list-sessions --no-legend || true
    falhou "a tela de login não apareceu"
}

# O uBlock Origin está no perfil do Firefox da pessoa? O perfil fica em
# ~/.mozilla ou, nas versões novas, em ~/.config/mozilla.
ublock_instalado() {
    local f
    while IFS= read -r f; do
        grep -q uBlock0@raymondhill.net "$f" && return 0
    done < <(find "/home/$PESSOA/.mozilla" "/home/$PESSOA/.config/mozilla" -name extensions.json 2>/dev/null)
    return 1
}

aplicar_sem_mudar() {
    local saida
    saida=$(bora aplicar "$1" --sem-perguntar)
    printf '%s\n' "$saida"
    grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "aplicar de novo mudou alguma coisa ($1)"
}

case "${1:?fase}" in
    preparar)
        etapa "Uma máquina com tela de login, como um desktop"
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -q
        if [ "$ID" = ubuntu ]; then
            # A imagem de nuvem usa o kernel enxuto; os módulos de vídeo que
            # faltarem vêm no linux-modules-extra, quando ele existe.
            extra=linux-modules-extra-$(uname -r)
            if [ -n "$(apt-cache policy "$extra" 2>/dev/null | awk '/Candidate:/ && $2 != "(none)" {print $2}')" ]; then
                apt-get install -y -q "$extra"
            fi
            apt-get install -y -q gdm3
            # O Firefox do Ubuntu é o do Snap, que a receita sem-snap troca.
            snap install firefox
        else
            apt-get install -y -q gdm3 firefox-esr
        fi
        id "$PESSOA" >/dev/null 2>&1 || useradd -m -s /bin/bash "$PESSOA"
        systemctl set-default graphical.target
        ;;

    tela-de-login)
        etapa "A tela de login"
        esperar_tela_de_login
        ;;

    aplicar)
        receitas=$(awk '$1 !~ /^#/ && NF { print $1 }' testes/vm/qemu/so-com-tela.txt | paste -sd, -)
        etapa "Aplicar $receitas, com o $AMBIENTE como padrão"
        bora plano --receitas "$receitas" \
            -p "desktop/ambiente-leve.ambiente=$AMBIENTE" \
            -p desktop/ambiente-leve.entrar_no_leve=sim \
            -o /root/tela.yaml
        cat /root/tela.yaml
        bora aplicar /root/tela.yaml --sem-perguntar
        aplicar_sem_mudar /root/tela.yaml
        awk '$1 == "-" && $2 == "receita:" { print $3 }' /root/tela.yaml | sort -u >/root/cobertas.txt

        etapa "Entrada automática do $PESSOA, para a tela mostrar a sessão"
        conf=$(conf_do_gdm)
        cp "$conf" /root/gdm.conf.antes
        sed -i "/^\[daemon\]/a AutomaticLoginEnable=true\nAutomaticLogin=$PESSOA" "$conf"
        grep -A3 '^\[daemon\]' "$conf"
        ;;

    sessao)
        etapa "O $PESSOA entra sozinho no $AMBIENTE (a sessão que a receita escolheu)"
        for _ in $(seq 1 60); do
            if pgrep -u "$PESSOA" -x "$PROCESSO" >/dev/null; then break; fi
            sleep 3
        done
        sessoes user
        if ! pgrep -u "$PESSOA" -x "$PROCESSO" >/dev/null; then
            ps -u "$PESSOA" -o pid,cmd || true
            journalctl -b -u display-manager.service --no-pager | tail -n 40 || true
            falhou "o $PESSOA não entrou no $AMBIENTE"
        fi
        grep -q " $PESSOA x11$" <<<"$(sessoes user)" || falhou "a sessão do $PESSOA não é uma sessão gráfica"
        # Dá tempo de o painel e o papel de parede aparecerem.
        sleep 20
        ;;

    firefox)
        etapa "O Firefox na sessão do $PESSOA, com o uBlock Origin que a política instala"
        firefox=$(command -v firefox || command -v firefox-esr) || falhou "o Firefox não está instalado"
        echo "Firefox: $firefox ($(dpkg -S "$(readlink -f "$firefox")" 2>/dev/null | cut -d: -f1 || echo snap))"
        pid=$(pgrep -o -u "$PESSOA" -x "$PROCESSO")
        # O Firefox abre com o mesmo ambiente da sessão: a tela, o Xauthority e o D-Bus.
        mapfile -t ambiente < <(tr '\0' '\n' <"/proc/$pid/environ" | grep -E '^(DISPLAY|XAUTHORITY|DBUS_SESSION_BUS_ADDRESS|XDG_RUNTIME_DIR|XDG_SESSION_TYPE)=')
        printf '%s\n' "${ambiente[@]}"
        runuser -u "$PESSOA" -- env HOME="/home/$PESSOA" "${ambiente[@]}" \
            setsid "$firefox" about:policies </dev/null >/tmp/firefox.log 2>&1 &
        for _ in $(seq 1 60); do
            ublock_instalado && break
            sleep 3
        done
        find "/home/$PESSOA/.mozilla" "/home/$PESSOA/.config/mozilla" -name extensions.json 2>/dev/null || true
        if ! ublock_instalado; then
            tail -n 30 /tmp/firefox.log || true
            falhou "o Firefox abriu, mas o uBlock Origin não foi instalado"
        fi
        pgrep -u "$PESSOA" firefox >/dev/null || falhou "o Firefox fechou sozinho"
        # Dá tempo de a página das políticas aparecer.
        sleep 15
        ;;

    sair)
        etapa "Desligar a entrada automática e fechar o Firefox"
        cp /root/gdm.conf.antes "$(conf_do_gdm)"
        pkill -u "$PESSOA" firefox || true
        ;;

    desfazer)
        etapa "Desfazer, sem ninguém dentro do ambiente leve"
        pgrep -u "$PESSOA" -x "$PROCESSO" >/dev/null && falhou "o $PESSOA ainda está no $AMBIENTE"
        for _ in $(seq 1 10); do
            saida=$(bora desfazer --sem-perguntar)
            printf '%s\n' "$saida"
            grep -q "Não há nada para desfazer" <<<"$saida" && break
        done
        [ ! -e "/usr/share/xsessions/$AMBIENTE.desktop" ] || falhou "o $AMBIENTE continuou na tela de login depois de desfazer"
        if [ "$ID" = ubuntu ]; then
            # O Sem Snap desfeito devolve o Snap e o Firefox do Snap, que a máquina tinha antes.
            dpkg -s snapd >/dev/null 2>&1 || falhou "o snapd não voltou depois de desfazer"
            systemctl is-active --quiet snapd.service || falhou "o snapd voltou, mas não está rodando"
            snap list firefox || falhou "o Firefox do Snap não voltou depois de desfazer"
        fi
        bora historico

        etapa "A tela de login volta depois de desfazer"
        systemctl restart display-manager.service
        esperar_tela_de_login
        ;;

    *) falhou "fase desconhecida: $1" ;;
esac
