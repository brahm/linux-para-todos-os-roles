#!/usr/bin/env bash
# Roda dentro da máquina virtual que o rodar.sh liga, como root, em fases:
#
#   aplicar             aplica o rolê 1 (duas vezes) e, depois, cada um dos
#                       outros rolês, sem as receitas que só se conferem com tela
#   depois-do-reinicio  confere que tudo voltou ligado sozinho depois do boot
#   antes-de-conectar   anota a última vez que o backup "ao conectar" rodou
#   depois-de-conectar  espera o backup rodar de novo, com o disco reconectado
#   desfazer            desfaz todas as aplicações, na ordem contrária
#
# Um rolê novo em objetivos/ entra sozinho. Os outros rolês vão com todas as
# receitas de uma vez, como se a pessoa respondesse "sim" a tudo, e com os
# parâmetros padrão, ou os de testes/vm/qemu/parametros.txt para os que não
# têm padrão. As receitas de testes/vm/qemu/so-com-tela.txt ficam de fora. No fim, /root/cobertas.txt lista as receitas que passaram por aqui.
set -euo pipefail
cd /bora
etapa() { printf '\n--- %s ---\n' "$*"; }
falhou() {
    echo "FALHOU: $*"
    exit 1
}
aplicar_sem_mudar() {
    local saida
    saida=$(bora aplicar "$1" --sem-perguntar)
    printf '%s\n' "$saida"
    grep -q "Tudo já estava aplicado" <<<"$saida" || falhou "aplicar de novo mudou alguma coisa ($1)"
}
snapshots() { { LC_ALL=C timeshift --list --scripted 2>/dev/null || true; } | awk '$1 ~ /^[0-9]+$/ && $2 == ">"' | wc -l; }
CONECTAR=bora-backup-pessoal-conectar.service
coberta() { grep -qx "$1" /root/cobertas.txt; }
# As receitas de um plano, uma por linha.
receitas_do_plano() { awk '$1 == "-" && $2 == "receita:" { print $3 }' "$1"; }
# As receitas de um rolê, todas, sem olhar o "quando", e sem as que precisam de tela.
receitas_do_role() {
    awk '/^receitas:/ { r = 1; next } /^[^ #]/ { r = 0 } r && $1 == "-" && $2 == "id:" { print $3 }' "$1" |
        awk 'NR == FNR { if ($1 !~ /^#/ && NF) tela[$1] = 1; next } !($1 in tela) && !visto[$1]++' testes/vm/qemu/so-com-tela.txt -
}

case "${1:?fase}" in
    aplicar)
        etapa "Diagnóstico"
        bora diag
        lsblk -o PATH,TYPE,FSTYPE,TRAN,HOTPLUG,RM,SIZE,MOUNTPOINT

        # Uma pessoa com arquivos, além da conta da imagem de nuvem.
        id aluno >/dev/null 2>&1 || useradd -m -s /bin/bash aluno
        mkdir -p /home/aluno/Documentos
        echo "trabalho de história" >/home/aluno/Documentos/trabalho.txt
        chown -R aluno:aluno /home/aluno

        etapa "Rolê 1, com os padrões: snapshot na própria raiz e backup no disco externo que está conectado"
        bora plano pronto-para-estudar -o /root/role1.yaml
        cat /root/role1.yaml
        # Na primeira vez ainda não há Timeshift para a foto de antes.
        bora aplicar /root/role1.yaml --sem-perguntar --sem-snapshot
        [ "$(snapshots)" -ge 1 ] || falhou "o Timeshift não tirou o primeiro snapshot"
        aplicar_sem_mudar /root/role1.yaml

        receitas_do_plano /root/role1.yaml >/root/cobertas.txt

        for arquivo in objetivos/*.yaml; do
            role=$(basename "$arquivo" .yaml)
            [ "$role" = pronto-para-estudar ] && continue
            receitas=$(receitas_do_role "$arquivo" | paste -sd, -)
            [ -n "$receitas" ] || continue
            etapa "Rolê $role, com o snapshot de antes, que o bora tira pelo Timeshift: $receitas"
            antes=$(snapshots)
            parametros=()
            while IFS= read -r p; do
                [[ "$p" =~ ^[[:space:]]*(#|$) ]] && continue
                if [[ ",$receitas," == *",${p%%.*},"* ]]; then parametros+=(-p "$p"); fi
            done <testes/vm/qemu/parametros.txt
            bora plano --receitas "$receitas" "${parametros[@]}" -o "/root/role-$role.yaml"
            # Com a saída numa variável, ela só aparece no log se for impressa
            # também quando o bora falha.
            if ! saida=$(bora aplicar "/root/role-$role.yaml" --sem-perguntar); then
                printf '%s\n' "$saida"
                falhou "o rolê $role não aplicou"
            fi
            printf '%s\n' "$saida"
            # Se tudo já estava aplicado, o bora nem tira o snapshot.
            if ! grep -q "Tudo já estava aplicado" <<<"$saida"; then
                [ "$(snapshots)" -gt "$antes" ] || falhou "o bora não tirou o snapshot antes de aplicar o rolê $role"
            fi
            aplicar_sem_mudar "/root/role-$role.yaml"
            receitas_do_plano "/root/role-$role.yaml" >>/root/cobertas.txt
        done
        sort -u -o /root/cobertas.txt /root/cobertas.txt
        timeshift --list
        etapa "Receitas que passaram pela máquina"
        cat /root/cobertas.txt
        ;;

    depois-do-reinicio)
        etapa "O que precisa voltar sozinho depois do boot"
        if coberta sistema/zram; then
            grep -q '^/dev/zram' /proc/swaps || falhou "o zram não voltou como swap"
            swapon --show
        fi
        grep -q 'Status: active' <<<"$(ufw status)" || falhou "o firewall não voltou ligado"
        ufw status verbose
        if coberta seguranca/ssh; then
            grep -qx 'permitrootlogin no' <<<"$(sshd -T)" || falhou "o SSH voltou aceitando o root"
            systemctl is-active --quiet ssh.service ssh.socket || falhou "o SSH não voltou ligado"
        fi
        [ "$(git -C /etc rev-list --count HEAD)" -ge 2 ] || falhou "o histórico do /etc não registrou as mudanças"
        git -C /etc log --oneline -n 5
        systemctl is-active --quiet bora-backup-pessoal.timer || falhou "o temporizador do backup não voltou"
        systemctl list-timers --all --no-pager | grep -E 'bora|etckeeper|timeshift|NEXT' || true
        [ "$(snapshots)" -ge 2 ] || falhou "os snapshots sumiram depois do boot"

        etapa "Aplicar de novo depois do boot, sem mudar nada"
        for plano in /root/role1.yaml /root/role-*.yaml; do
            [ -e "$plano" ] && aplicar_sem_mudar "$plano"
        done
        ;;

    antes-de-conectar)
        # O disco estava conectado no boot, então o backup "ao conectar" já
        # está rodando (ele espera até 1 minuto a sessão montar o disco).
        # Enquanto ele roda, conectar de novo não dispara outro.
        for _ in $(seq 1 36); do
            [ "$(systemctl show -p ActiveState --value "$CONECTAR")" != activating ] && break
            sleep 5
        done
        systemctl show -p InvocationID --value "$CONECTAR" >/root/conectar-antes
        echo "Última execução do backup ao conectar: $(cat /root/conectar-antes)"
        ;;

    depois-de-conectar)
        antes=$(cat /root/conectar-antes)
        for _ in $(seq 1 60); do
            agora=$(systemctl show -p InvocationID --value "$CONECTAR")
            estado=$(systemctl show -p ActiveState --value "$CONECTAR")
            if [ -n "$agora" ] && [ "$agora" != "$antes" ] && [ "$estado" != activating ]; then
                break
            fi
            sleep 5
        done
        journalctl -u "$CONECTAR" -b --no-pager -o short-monotonic | tail -n 20
        [ "$agora" != "$antes" ] || falhou "o backup não rodou quando o disco foi conectado"
        [ "$(systemctl show -p Result --value "$CONECTAR")" = success ] || falhou "o backup ao conectar terminou com erro"
        /usr/local/lib/bora/backup-pessoal --conferir
        ;;

    desfazer)
        # Uma aplicação por vez, da última para a primeira, até não sobrar nenhuma.
        for _ in $(seq 1 20); do
            saida=$(bora desfazer --sem-perguntar)
            printf '%s\n' "$saida"
            grep -q "Não há nada para desfazer" <<<"$saida" && break
        done
        if grep -q '^/dev/zram' /proc/swaps; then
            # O que ligou o zram de novo (ou não o deixou desligar).
            swapon --show || true
            systemctl status --no-pager 'dev-zram*.swap' 'systemd-zram-setup@*.service' || true
            journalctl -b --no-pager -u 'dev-zram*.swap' -u 'systemd-zram-setup@*' | tail -n 30 || true
            falhou "o zram continuou ligado depois de desfazer"
        fi
        if command -v ufw >/dev/null; then
            grep -q 'Status: active' <<<"$(ufw status)" && falhou "o firewall continuou ligado depois de desfazer"
        fi
        [ ! -e /etc/timeshift/timeshift.json ] || grep -q '"backup_device_uuid" *: *""' /etc/timeshift/timeshift.json ||
            echo "AVISO: a configuração do Timeshift continua em /etc/timeshift/timeshift.json"
        bora historico
        ;;

    *) falhou "fase desconhecida: $1" ;;
esac
