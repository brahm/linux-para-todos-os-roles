# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

CONF_ZRAM=/etc/systemd/zram-generator.conf
CONF_SYSCTL=/etc/sysctl.d/99-bora-zram.conf
MARCA="receita sistema/zram"
# Os ajustes do kernel que o Fedora, o Pop!_OS e a ArchWiki usam com zram:
# trocar para a memória comprimida é barato, então o kernel pode trocar cedo.
AJUSTES=(vm.swappiness=180 vm.watermark_boost_factor=0 vm.watermark_scale_factor=125 vm.page-cluster=0)

porcentagem() {
    local p=${BORA_PORCENTAGEM:-50}
    case "$p" in '' | *[!0-9]*) falha "porcentagem precisa ser um número de 10 a 100 (veio $p)" ;; esac
    if [ "$p" -lt 10 ] || [ "$p" -gt 100 ]; then
        falha "porcentagem precisa ficar entre 10 e 100 (veio $p)"
    fi
    echo "$p"
}

conf_esperada() {
    cat <<CONF
# Memória comprimida, ligada pelo bora ($MARCA).
# Até $(porcentagem)% da memória, nunca mais de 8 GB, comprimida com zstd.
# A prioridade 100 faz o kernel usar o zram antes de qualquer swap no disco.
[zram0]
zram-size = min(ram * $(porcentagem) / 100, 8192)
compression-algorithm = zstd
swap-priority = 100
CONF
}

sysctl_esperado() {
    printf '# Ajustes para o zram, do bora (%s).\n' "$MARCA"
    printf '%s\n' "${AJUSTES[@]}" | sed 's/=/ = /'
}

# A configuração do zram é desta receita?
zram_do_bora() { grep -qF "$MARCA" "$CONF_ZRAM" 2>/dev/null; }

# Outro programa já cuida do zram? Mostra quem, para a mensagem.
outro_zram() {
    zram_do_bora && return 1
    local p
    for p in zram-tools zram-config systemd-zram-generator; do
        if pacote_instalado "$p"; then
            echo "o pacote $p"
            return 0
        fi
    done
    if [ -e "$CONF_ZRAM" ]; then
        echo "o arquivo $CONF_ZRAM"
        return 0
    fi
    if grep -q '^/dev/zram' /proc/swaps 2>/dev/null; then
        echo "um zram que já está ligado"
        return 0
    fi
    return 1
}

zram_ligado() { grep -q '^/dev/zram0 ' /proc/swaps 2>/dev/null; }

# O kernel tem o módulo do zram? No Ubuntu Server e nas imagens de nuvem, o
# kernel vem sem o linux-modules-extra, e o zram mora nele.
modulo_do_zram() { [ -d /sys/module/zram ] || modinfo zram >/dev/null 2>&1; }

# Os pacotes que trazem o módulo: o do kernel de agora e, quando o sistema
# segue o kernel "virtual" (o das imagens de nuvem), o metapacote que traz o
# módulo também nos kernels das próximas atualizações.
pacotes_do_modulo() {
    local p
    for p in "linux-modules-extra-$(uname -r)" linux-image-extra-virtual; do
        if [ "$p" = linux-image-extra-virtual ] && ! pacote_instalado linux-image-virtual; then continue; fi
        if apt-cache show "$p" >/dev/null 2>&1; then echo "$p"; fi
    done
}
