# Navegador enxuto

## O que faz

Deixa o Firefox mais leve: instala o bloqueador de anúncios uBlock Origin, tira da memória as abas paradas quando ela acaba e desliga a telemetria, os estudos e os atalhos patrocinados da página inicial.

## Por que

Numa máquina antiga, o navegador é o programa que mais gasta memória e processador, e boa parte disso são anúncios e rastreadores: numa página de notícias comum, eles são mais da metade do que é baixado. Bloquear os anúncios deixa as páginas mais leves, mais rápidas e mais seguras.

A receita mexe no Firefox, e não troca de navegador, porque ele já vem no Ubuntu, no Mint e no Debian, e nada muda para quem usa. O Firefox também é dos poucos navegadores em que o uBlock Origin completo ainda funciona: no Chrome e nos outros baseados no Chromium, só a versão limitada.

Outros ajustes ajudam quem tem pouca memória ou um disco lento:

- `browser.tabs.unloadOnLowMemory`: quando a memória acaba, o Firefox descarrega as abas que você não está vendo. Elas continuam na barra e recarregam quando você clica;
- `browser.sessionstore.restore_on_demand`: ao abrir o Firefox, as abas da última vez só carregam quando você clica nelas;
- `browser.sessionstore.interval` em 60 segundos: o Firefox grava a sessão no disco a cada minuto, e não a cada 15 segundos, o que alivia um disco rígido antigo.

## O que muda no sistema

- Cria ou completa `/etc/firefox/policies/policies.json`, o arquivo de políticas que o Firefox lê em qualquer distro, inclusive o Snap do Ubuntu. Se o arquivo já existir, a receita só acrescenta o que falta, sem tirar nada.
- Com `bloquear_anuncios: sim` (o padrão), a política `ExtensionSettings` pede o uBlock Origin no modo `normal_installed`: o Firefox baixa a extensão da loja oficial da Mozilla (addons.mozilla.org) na primeira vez que abrir, e ela se atualiza sozinha. Você pode desativar, mas não remover, enquanto a política estiver lá.
- As preferências vão com `"Status": "default"`: elas viram o novo padrão, e você ainda pode mudar qualquer uma em `about:config`.
- Liga `DisableTelemetry` e `DisableFirefoxStudies`, e tira os atalhos patrocinados da página inicial.

Nenhum pacote é instalado. Se o Firefox não estiver instalado, as políticas ficam prontas para quando ele for. O Firefox do Flatpak não lê esse arquivo; a receita avisa se encontrar um.

## Como conferir

O `testar.sh` confere que o arquivo de políticas é um JSON válido e que tem cada política e preferência da receita, inclusive o uBlock Origin, com `bloquear_anuncios: sim`.

Para ver você mesmo, no Firefox: `about:policies` lista as políticas ativas, e `about:addons` mostra o uBlock Origin depois da primeira abertura.

## Como desfazer

O `desfazer.sh` volta o `policies.json` ao que era, ou apaga o arquivo, se foi a receita que o criou. O uBlock Origin, se já tiver sido instalado, fica no Firefox como uma extensão comum, que você remove em `about:addons` se quiser.

## Fontes

- [Políticas do Firefox para empresas](https://mozilla.github.io/policy-templates/)
- [uBlock Origin](https://github.com/gorhill/uBlock)
- [O Firefox descarrega abas quando a memória acaba](https://support.mozilla.org/kb/unload-inactive-tabs-save-system-memory-firefox)
