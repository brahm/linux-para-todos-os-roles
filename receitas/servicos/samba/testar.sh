#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-samba.sh
source ./comum-samba.sh
exigir_apt

pasta=$(pasta_da_receita)
nome=$(nome_do_compartilhamento)
mapfile -t pessoas < <(pessoas_da_pasta)
rede=$(descobrir_rede_local)

valor() { testparm -s --section-name="$1" --parameter-name="$2" 2>/dev/null; }
config_valida() { testparm -s >/dev/null 2>&1; }
pasta_certa() { [ "$(valor "$nome" path)" = "$pasta" ] && [ -d "$pasta" ]; }
sem_visitante() { [ "$(valor global 'map to guest')" = Never ] && [ "$(valor "$nome" 'guest ok')" = No ]; }
sem_smb1() { [ "$(valor global 'server min protocol')" != NT1 ] && [ "$(valor global 'server min protocol')" != LANMAN1 ]; }
so_a_rede() { [ "$(valor "$nome" 'hosts allow')" = "127.0.0.1 ::1 $rede" ]; }
senha_separada() { [ "$(valor global 'unix password sync')" = No ]; }
todos_no_samba() {
    local n
    for n in "${pessoas[@]}"; do no_samba "$n" || return 1; done
}
senhas_so_do_root() { [ "$(stat -c '%U %a' "$SENHAS")" = "root 600" ]; }
ligado_no_boot() { systemctl is-enabled --quiet smbd.service; }
descoberta_no_boot() { systemctl is-enabled --quiet wsdd2.service; }
escutando() { [ -n "$(ss -Hltn 'sport = :445')" ]; }
regras_no_firewall() {
    local regra
    while read -r regra; do regra_existe "$regra" || return 1; done < <(regras_ufw "$rede")
}

# O "pronto quando" do rolê: entrar com o nome e a senha de uma pessoa, criar
# um arquivo e apagar de novo, pelo mesmo caminho que os outros aparelhos usam.
cria_arquivo_pela_rede() {
    local n=${pessoas[0]} senha auth arquivo teste="bora-teste-$$.txt" r=0
    senha=$(senha_de "$n")
    [ -n "$senha" ] || return 1
    auth=$(mktemp)
    arquivo=$(mktemp)
    printf 'username = %s\npassword = %s\n' "$n" "$senha" >"$auth"
    echo "teste do bora" >"$arquivo"
    smbclient "//127.0.0.1/$nome" -A "$auth" -c "put $arquivo $teste" >/dev/null 2>&1 || r=1
    [ "$r" = 0 ] && [ -f "$pasta/$teste" ] && [ "$(stat -c %U "$pasta/$teste")" = "$(dono_atual "$pasta")" ] || r=1
    smbclient "//127.0.0.1/$nome" -A "$auth" -c "del $teste" >/dev/null 2>&1 || r=1
    [ ! -e "$pasta/$teste" ] || r=1
    rm -f "$auth" "$arquivo"
    return "$r"
}
recusa_senha_errada() { ! smbclient "//127.0.0.1/$nome" -U "${pessoas[0]}%senha-errada" -c ls >/dev/null 2>&1; }
recusa_visitante() { ! smbclient -N "//127.0.0.1/$nome" -c ls >/dev/null 2>&1; }

conferir "Samba instalado (samba e smbclient)" pacote_instalado samba
conferir "o Samba aceita a configuração (testparm)" config_valida
conferir "a pasta $pasta está compartilhada como $nome" pasta_certa
conferir "ninguém entra sem nome e senha (map to guest = Never)" sem_visitante
conferir "o protocolo antigo SMB1 está desligado" sem_smb1
conferir "o Samba só aceita esta máquina e a rede local ($rede)" so_a_rede
conferir "a senha da pasta não troca a senha do computador (unix password sync = No)" senha_separada
conferir "cada pessoa tem acesso: ${pessoas[*]}" todos_no_samba
conferir "as senhas estão num arquivo que só o root lê ($SENHAS)" senhas_so_do_root
conferir "o Samba liga junto com o computador (smbd)" ligado_no_boot
if [ "${BORA_APARECER_NA_REDE:-sim}" = sim ]; then
    conferir "a pasta aparece na Rede do Windows e do Linux (wsdd2)" descoberta_no_boot
fi
if systemd_rodando; then
    conferir "o Samba está esperando conexões na porta 445" escutando
    conferir "${pessoas[0]} entra com a senha, cria um arquivo na pasta e apaga" cria_arquivo_pela_rede
    conferir "uma senha errada não entra" recusa_senha_errada
    conferir "um visitante sem senha não entra" recusa_visitante
fi
if ufw_ativo; then
    conferir "o firewall libera o Samba só para a rede local" regras_no_firewall
fi
resultado_dos_testes
