#!/usr/bin/env bash
# Roda dentro da máquina virtual que o rodar.sh liga, como root, em fases:
#
#   aplicar             aplica o rolê 1 (duas vezes) e, à parte, o zram e o SSH
#   depois-do-reinicio  confere que tudo voltou ligado sozinho depois do boot
#   antes-de-conectar   anota a última vez que o backup "ao conectar" rodou
#   depois-de-conectar  espera o backup rodar de novo, com o disco reconectado
#   desfazer            desfaz as duas aplicações, na ordem contrária
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

        etapa "zram e SSH, com o snapshot de antes, que o bora tira pelo Timeshift"
        antes=$(snapshots)
        bora plano --receitas sistema/zram,seguranca/ssh -o /root/extras.yaml
        bora aplicar /root/extras.yaml --sem-perguntar
        [ "$(snapshots)" -gt "$antes" ] || falhou "o bora não tirou o snapshot antes de aplicar"
        timeshift --list
        ;;

    depois-do-reinicio)
        etapa "O que precisa voltar sozinho depois do boot"
        grep -q '^/dev/zram' /proc/swaps || falhou "o zram não voltou como swap"
        swapon --show
        grep -q 'Status: active' <<<"$(ufw status)" || falhou "o firewall não voltou ligado"
        ufw status verbose
        grep -qx 'permitrootlogin no' <<<"$(sshd -T)" || falhou "o SSH voltou aceitando o root"
        systemctl is-active --quiet ssh.service ssh.socket || falhou "o SSH não voltou ligado"
        [ "$(git -C /etc rev-list --count HEAD)" -ge 2 ] || falhou "o histórico do /etc não registrou as mudanças"
        git -C /etc log --oneline -n 5
        systemctl is-active --quiet bora-backup-pessoal.timer || falhou "o temporizador do backup não voltou"
        systemctl list-timers --all --no-pager | grep -E 'bora|etckeeper|timeshift|NEXT' || true
        [ "$(snapshots)" -ge 2 ] || falhou "os snapshots sumiram depois do boot"

        etapa "Aplicar de novo depois do boot, sem mudar nada"
        aplicar_sem_mudar /root/role1.yaml
        aplicar_sem_mudar /root/extras.yaml
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
        bora desfazer --sem-perguntar
        grep -q '^/dev/zram' /proc/swaps && falhou "o zram continuou ligado depois de desfazer"
        bora desfazer --sem-perguntar
        if command -v ufw >/dev/null; then
            grep -q 'Status: active' <<<"$(ufw status)" && falhou "o firewall continuou ligado depois de desfazer"
        fi
        [ ! -e /etc/timeshift/timeshift.json ] || grep -q '"backup_device_uuid" *: *""' /etc/timeshift/timeshift.json ||
            echo "AVISO: a configuração do Timeshift continua em /etc/timeshift/timeshift.json"
        bora historico
        ;;

    *) falhou "fase desconhecida: $1" ;;
esac
