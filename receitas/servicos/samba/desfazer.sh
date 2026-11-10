#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-samba.sh
source ./comum-samba.sh
exigir_apt

if [ -f "$BORA_ESTADO/regras-ufw" ]; then
    while read -r regra; do
        [ -n "$regra" ] || continue
        regra_existe "$regra" || continue
        # shellcheck disable=SC2086
        ufw delete $regra >/dev/null 2>&1 || true
        msg "Regra do firewall removida: $regra"
    done <"$BORA_ESTADO/regras-ufw"
    rm -f "$BORA_ESTADO/regras-ufw"
fi

# Os acessos à pasta e as contas que a receita criou. As contas de gente que
# já existiam ficam, só perdem a senha da pasta.
if [ -f "$BORA_ESTADO/samba-usuarios" ]; then
    while read -r n; do
        [ -n "$n" ] || continue
        if command -v smbpasswd >/dev/null && no_samba "$n"; then
            smbpasswd -x "$n" >/dev/null 2>&1 || true
            msg "Acesso à pasta removido: $n"
        fi
    done <"$BORA_ESTADO/samba-usuarios"
    rm -f "$BORA_ESTADO/samba-usuarios"
fi
if [ -f "$BORA_ESTADO/contas-criadas" ]; then
    while read -r n; do
        [ -n "$n" ] || continue
        if conta_existe "$n" && conta_da_receita "$n"; then
            userdel "$n" 2>/dev/null || true
            msg "Conta removida: $n"
        fi
    done <"$BORA_ESTADO/contas-criadas"
    rm -f "$BORA_ESTADO/contas-criadas"
fi

restaurar_arquivos

# A pasta e os arquivos dela ficam. Só volta o dono, se a receita mudou, e
# só sai a pasta que a receita criou e continua vazia.
if [ -f "$BORA_ESTADO/dono-antigo" ]; then
    read -r dono modo pasta <"$BORA_ESTADO/dono-antigo"
    if [ -d "$pasta" ]; then
        chown "$dono" "$pasta" && chmod "$modo" "$pasta"
        msg "A pasta $pasta voltou a ser de ${dono%%:*}."
    fi
    rm -f "$BORA_ESTADO/dono-antigo"
fi
remover_pastas_novas

desabilitar_unidades_habilitadas
if systemd_rodando && pacote_instalado samba; then
    # O Samba que já existia volta com a configuração de antes.
    systemctl try-restart smbd.service 2>/dev/null || true
    if systemctl is-enabled --quiet nmbd.service 2>/dev/null; then
        systemctl restart nmbd.service 2>/dev/null || true
    fi
fi
remover_pacotes_instalados
msg "O compartilhamento foi desfeito. Os arquivos da pasta continuam onde estavam."
