#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=../../comum.sh
source "$BORA_LIB"
# shellcheck source=comum-samba.sh
source ./comum-samba.sh
exigir_apt

# Tudo o que pode recusar vem antes de mudar qualquer coisa.
pasta=$(pasta_da_receita)
nome=$(nome_do_compartilhamento)
exigir_pessoas
mapfile -t pessoas < <(pessoas_da_pasta)
rede=$(exigir_rede)
for n in "${pessoas[@]}"; do
    if conta_existe "$n" && ! conta_de_pessoa "$n" && ! conta_da_receita "$n"; then
        falha "já existe uma conta $n do sistema neste computador; escolha outro nome para essa pessoa"
    fi
done

# A pasta e o dono dos arquivos. O Samba grava tudo como o dono da pasta
# (force user), então os arquivos criados pela rede continuam abrindo e
# mudando aqui, e a permissão da pasta pessoal não atrapalha.
if [ -d "$pasta" ]; then
    dono=$(dono_atual "$pasta")
    if [ "$(stat -c %u "$pasta")" -eq 0 ]; then
        [ -z "$(ls -A "$pasta")" ] ||
            falha "a pasta $pasta é do root e já tem arquivos; passe ela para a sua conta (sudo chown -R voce: $pasta) ou escolha outra pasta"
        dono=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
        [ -f "$BORA_ESTADO/dono-antigo" ] || printf '%s %s\n' "$(stat -c '%U:%G %a' "$pasta")" "$pasta" >"$BORA_ESTADO/dono-antigo"
        chown "$dono:" "$pasta"
        msg "A pasta $pasta passou a ser de $dono."
    elif ! conta_de_pessoa "$dono"; then
        falha "a pasta $pasta é da conta $dono, do sistema; escolha uma pasta de uma pessoa"
    fi
else
    dono=$(descobrir_pessoa "${BORA_USUARIO:-auto}")
    d=$pasta
    novas=()
    while [ ! -d "$d" ]; do
        novas+=("$d")
        d=$(dirname "$d")
    done
    mkdir -p "$pasta"
    printf '%s\n' "${novas[@]}" >>"$BORA_ESTADO/pastas-novas"
    chown "$dono:" "$pasta"
    chmod 0755 "$pasta"
    msg "Pasta criada: $pasta, de $dono."
fi

mapfile -t pacotes < <(pacotes_da_receita)
instalar_pacotes --sem-recomendados "${pacotes[@]}"

# A configuração: o arquivo da receita e a linha que o inclui no smb.conf.
mudou=nao
if [ ! -f "$CONFIG" ] || ! cmp -s <(conteudo_config "$pasta" "$dono" "$rede") "$CONFIG"; then
    conteudo_config "$pasta" "$dono" "$rede" | escrever_arquivo "$CONFIG" 0644
    mudou=sim
fi
if ! include_presente; then
    { cat "$SMB_CONF"; printf '\n# Acrescentado pelo bora (receita servicos/samba).\n%s\n' "$INCLUDE"; } | escrever_arquivo "$SMB_CONF" 0644
    mudou=sim
fi
if ! testparm -s >/dev/null 2>&1; then
    restaurar_arquivos
    falha "o Samba recusou a configuração (testparm); nada foi mudado"
fi

# Um acesso para cada pessoa. Quem já tem conta de gente neste computador
# usa a mesma conta, com uma senha só para a pasta; os outros ganham uma
# conta sem pasta pessoal e sem login, que só serve para a pasta.
for d in "$(dirname "$SENHAS")" "$(dirname "$(dirname "$SENHAS")")"; do
    [ -d "$d" ] || printf '%s\n' "$d" >>"$BORA_ESTADO/pastas-novas"
done
mkdir -p "$(dirname "$SENHAS")"
chmod 0700 "$(dirname "$SENHAS")"
for n in "${pessoas[@]}"; do
    if ! conta_existe "$n"; then
        useradd --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin --comment "$MARCA" "$n"
        printf '%s\n' "$n" >>"$BORA_ESTADO/contas-criadas"
        msg "Conta criada só para a pasta: $n"
    fi
    if ! no_samba "$n"; then
        senha=$(gerar_senha)
        guardar_arquivo "$SENHAS"
        { [ ! -f "$SENHAS" ] || awk -v n="$n" '$1 != n' "$SENHAS"; printf '%s %s\n' "$n" "$senha"; } >"$SENHAS.novo"
        install -m 0600 "$SENHAS.novo" "$SENHAS"
        rm -f "$SENHAS.novo"
        printf '%s\n%s\n' "$senha" "$senha" | smbpasswd -s -a "$n" >/dev/null
        printf '%s\n' "$n" >>"$BORA_ESTADO/samba-usuarios"
        msg "Acesso à pasta criado para $n."
    fi
done

if [ "$mudou" = sim ] && systemd_rodando; then
    # A porta e o NetBIOS só mudam com o smbd reiniciado; o nmbd para sozinho
    # quando o NetBIOS está desligado (a condição da própria unidade).
    systemctl restart smbd.service
    systemctl try-restart nmbd.service 2>/dev/null || true
fi
habilitar_unidade smbd.service
if [ "${BORA_APARECER_NA_REDE:-sim}" = sim ]; then
    habilitar_unidade wsdd2.service
fi
if systemd_rodando; then
    # O teste entra pela porta 445 logo em seguida: espera o smbd abrir.
    for _ in $(seq 1 20); do
        [ -z "$(ss -Hltn 'sport = :445')" ] || break
        sleep 0.5
    done
fi

if ufw_ativo; then
    while read -r regra; do
        if ! regra_existe "$regra"; then
            # shellcheck disable=SC2086
            ufw $regra >/dev/null
            printf '%s\n' "$regra" >>"$BORA_ESTADO/regras-ufw"
        fi
    done < <(regras_ufw "$rede")
    msg "Firewall: o Samba aceita só a rede local ($rede)."
else
    aviso "o firewall não está ligado. O próprio Samba só aceita a rede local ($rede), mas, para bloquear o resto, aplique também a receita seguranca/firewall"
fi

ip=$(endereco_ip)
ip=${ip:-este-computador}
msg "Pronto. Nos outros aparelhos da casa, abra \\\\$ip\\$nome no Windows ou smb://$ip/$nome no Mac, no Linux e no celular."
msg "A senha de cada pessoa está em $SENHAS: veja com sudo cat $SENHAS e troque com sudo smbpasswd nome."
