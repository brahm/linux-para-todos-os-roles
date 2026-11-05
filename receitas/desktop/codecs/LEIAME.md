# Codecs de áudio e vídeo

## O que faz

Instala os plugins do GStreamer que tocam os formatos mais comuns de áudio e vídeo: MP3, MP4, MKV, WMV, os vídeos em H.264 e H.265 que vêm do celular e o áudio AC-3 dos filmes.

## Por que

O Ubuntu e o Debian não instalam esses codecs por padrão. Alguns formatos são cobertos por patentes em certos países, e as distros deixam a escolha para você. Sem eles, o player de vídeo abre o arquivo e mostra só um erro, ou toca o áudio sem a imagem.

Os players que vêm com os ambientes gráficos (o Vídeos e o Showtime do GNOME, o Parole do Xfce, o Dragon Player e o Haruna do KDE) e muitos outros programas usam o GStreamer, então um conjunto de plugins resolve todos eles de uma vez.

## O que muda no sistema

Instala quatro pacotes dos repositórios oficiais, com as dependências:

- `gstreamer1.0-libav`: os decodificadores do FFmpeg, que tocam H.264, H.265, AAC e quase tudo o que vem da internet e do celular;
- `gstreamer1.0-plugins-good`: MP4, MKV, WebM, MP3 e FLAC;
- `gstreamer1.0-plugins-bad`: os analisadores que separam o vídeo H.264 e H.265 de dentro do arquivo, além de formatos menos comuns;
- `gstreamer1.0-plugins-ugly`: WMV, WMA, AC-3 e DVD.

No Ubuntu, esses pacotes ficam no repositório `universe`, que vem ligado numa instalação normal. Se ele estiver desligado, a receita para e explica como ligar.

A receita não instala o `ubuntu-restricted-extras`. Ele traz junto as fontes da Microsoft, que pedem para aceitar uma licença no meio da instalação e são baixadas de fora dos repositórios. Também não troca a biblioteca `libavcodec` pela versão `libavcodec-extra`, que só acrescenta codificadores e mexe num pacote que outros programas usam.

No Linux Mint, se você marcou a opção de codecs na instalação, esses pacotes já estão lá, e a receita só confere.

## Como conferir

O `testar.sh` confere que os quatro pacotes estão instalados e que os arquivos dos plugins principais estão no lugar, cada um com o que ele toca:

- `libav`: H.264, H.265 e AAC;
- `isomp4`: MP4 e MOV;
- `matroska`: MKV e WebM;
- `mpg123`: MP3;
- `videoparsersbad`: H.264 e H.265 dentro do MP4 e do MKV;
- `asf`: WMV e WMA;
- `a52dec`: AC-3.

Para conferir você mesmo, com o pacote `gstreamer1.0-tools`: `gst-inspect-1.0 avdec_h264`. O teste de verdade é abrir um vídeo do celular no player.

## Como desfazer

O `desfazer.sh` remove só os pacotes que a receita instalou, com as dependências que vieram junto. O que já estava instalado antes continua.

## Fontes

- [Restricted formats, na documentação do Ubuntu](https://help.ubuntu.com/community/RestrictedFormats)
- [Multimedia codecs, na wiki do Debian](https://wiki.debian.org/MultimediaCodecs)
- [Lista de plugins do GStreamer](https://gstreamer.freedesktop.org/documentation/plugins_doc.html)
