#!/usr/bin/env bash
set -euo pipefail
# aplicar.sh da receita base/atualizar (Sistema atualizado).
# Faz a mudança no sistema. Tudo o que precisa voltar atrás fica anotado em
# $BORA_ESTADO, pelas funções do comum.sh. Rodar duas vezes não muda nada na segunda.
# Os parâmetros da receita chegam como variáveis BORA_<NOME>.
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-atualizar.sh
source ./comum-atualizar.sh
exigir_apt

if precisa_consertar_dpkg; then
    msg "Terminando de configurar pacotes que ficaram pela metade."
    dpkg --configure -a
fi

msg "Atualizando a lista de pacotes."
apt_get update -q
mkdir -p /var/lib/apt/periodic && touch /var/lib/apt/periodic/update-success-stamp

n=$(pacotes_pendentes)
if [ "$n" -gt 0 ]; then
    msg "Atualizando $n pacote(s). Isso pode levar alguns minutos."
    # upgrade --with-new-pkgs instala dependências novas (como um kernel novo),
    # mas nunca remove pacotes. Remoções ficam para a pessoa decidir.
    apt_get upgrade -y -q --with-new-pkgs
else
    msg "Nenhum pacote para atualizar."
fi

if [ "${BORA_AUTOMATICAS:-sim}" = sim ]; then
    instalar_pacotes unattended-upgrades
    if automaticas_ligadas; then
        msg "As atualizações automáticas de segurança já estavam ligadas."
    else
        escrever_arquivo "$ARQUIVO_AUTOMATICAS" <<'CONF'
// Atualizações automáticas, ligadas pelo bora (receita base/atualizar).
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
CONF
    fi
    if command -v systemctl >/dev/null; then
        for t in apt-daily.timer apt-daily-upgrade.timer; do
            if [ "$(systemctl is-enabled "$t" 2>/dev/null || true)" = masked ]; then
                aviso "$t está mascarado; as atualizações automáticas não vão rodar até você desmascarar"
            elif [ -f "/usr/lib/systemd/system/$t" ] || [ -f "/lib/systemd/system/$t" ]; then
                habilitar_unidade "$t"
            fi
        done
    fi
fi

if [ -f /var/run/reboot-required ]; then
    msg "Reinicie o computador quando puder, para começar a usar as atualizações do sistema."
fi
