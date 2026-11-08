# shellcheck shell=bash disable=SC2034
# Funções usadas pelos scripts desta receita.

# Os plugins do GStreamer, que os players do GNOME, do KDE e do Xfce usam.
# O libav traz os decodificadores do FFmpeg (H.264, H.265, AAC); o ugly, o bad
# e o good completam com MP4, MKV, WMV, AC-3 e os analisadores de vídeo.
PACOTES=(gstreamer1.0-libav gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly)

# plugin do GStreamer -> o que ele toca, para o teste explicar o que conferiu.
declare -A PLUGINS=(
    [libav]="H.264, H.265 e AAC (vídeos do celular e da internet)"
    [isomp4]="arquivos MP4 e MOV"
    [matroska]="arquivos MKV e WebM"
    [mpg123]="música em MP3"
    [videoparsersbad]="leitura de H.264 e H.265 dentro do MP4 e do MKV"
    [asf]="arquivos WMV e WMA"
    [a52dec]="áudio AC-3 (Dolby Digital) de filmes e DVDs"
)

# O arquivo do plugin, achado pela lista de arquivos dos pacotes. A lista vem
# inteira antes do grep: com pipefail, um "dpkg -L | grep -m1" falha quando o
# grep sai cedo e o dpkg leva SIGPIPE, o que depende da sorte.
arquivo_do_plugin() {
    local nome=$1 p
    for p in "${PACOTES[@]}"; do
        grep -m1 "/gstreamer-1.0/libgst$nome\.so$" <<<"$(dpkg -L "$p" 2>/dev/null)" && return 0
    done
    return 1
}

plugin_presente() {
    local f
    f=$(arquivo_do_plugin "$1") && [ -f "$f" ]
}
