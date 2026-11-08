# Decisões

Registro das decisões que definem o projeto, com o porquê de cada uma. Quando uma decisão mudar, ela é atualizada aqui com a nova data.

## 4 de novembro de 2026: recomeço

| Decisão | Por quê |
|---|---|
| O projeto deixa de ser uma coleção de roteiros e vira um catálogo de rolês com uma ferramenta, o `bora` | Assistentes de IA já resolvem o passo a passo genérico. O que eles não têm são passos testados, com verificação e caminho de volta, organizados pelo que a pessoa quer fazer |
| O repositório recomeça do zero | O escopo mudou por completo, e nada do conteúdo antigo se aplica |
| Um motor, três portas: menus, pergunta pronta e agente | O motor funciona sem IA, para quem não tem conta nem cartão; a IA acelera para quem tem |
| A IA só planeja; quem aplica é a pessoa, pelo `bora` | Um modelo de linguagem com root é o maior risco do projeto, e cada agente lida com permissões de um jeito diferente |
| Qualquer IA serve, incluindo modelos chineses, o OpenRouter e modelos locais | Como a IA só planeja, poucas chamadas bastam, e até cotas gratuitas pequenas dão conta |
| Três públicos: curiosos, estudantes e entusiastas | Do computador doado sem plano pago até quem mantém várias máquinas |
| Distros por família, em ondas: Ubuntu e Debian, depois Fedora, depois Arch e Fedora imutável; openSUSE pela comunidade | A onda 1 cobre cinco das dez distros mais vistas no DistroWatch com um só gerenciador de pacotes. O Fedora vem antes do Arch porque é, com o Ubuntu LTS, a distro de uso diário de quem mantém o projeto |
| Só distros com systemd | Outro init multiplica as receitas, e quem usa distros sem systemd costuma se virar sozinho |
| Sem AUR | Pacotes feitos pela comunidade sem revisão, com casos de malware em 2025 |
| Nenhuma receita abre porta para a internet | Depende de roteador, provedor e CGNAT; acesso de fora só por VPN |
| Sete rolês na primeira versão, incluindo o "Vibecodar" | Atendem aos três públicos e cobrem estudo, máquina antiga, programação, casa e acesso remoto |
| Nome do projeto: Linux para todos os rolês. Nome da ferramenta: `bora` | O nome do projeto descreve o catálogo e o público. O `bora` é curto, sem acento, e os comandos se leem como frases |
| Licença 0BSD para tudo | Equivale a domínio público, passa nas distros, funciona na lei brasileira, que não permite renunciar aos direitos morais, e não cria atrito para quem copia trechos de receitas |

## 4 de novembro de 2026: `bora` v0

| Decisão | Por quê |
|---|---|
| O `bora` é escrito em Rust e publicado como um binário único, estático, para x86_64 e aarch64 | Um arquivo que roda em qualquer distro suportada, sem depender da versão do Python ou de bibliotecas da máquina. As receitas vão embutidas, então a versão do `bora` e a das receitas andam juntas |
| As receitas continuam em bash | É a língua de quem administra Linux, e quem lê o LEIAME aprende os mesmos comandos que rodaria na mão |
| Menus em texto simples, com números | Funcionam em qualquer terminal, por SSH e com leitor de tela |
| O que o `bora` fez fica em `/var/lib/bora`, com uma cópia de cada receita aplicada | O desfazer funciona mesmo depois de o `bora` ser atualizado |
| Desfazer sempre a aplicação mais recente primeiro, com as receitas na ordem contrária | Desfazer fora de ordem pode deixar o sistema num estado que nenhuma receita conhece |
| O snapshot usa o Timeshift, com um timer próprio do systemd | O Timeshift é o que as distros da onda 1 já recomendam, e o timer evita depender do cron |
| O firewall usa o ufw e guarda uma cópia de `/etc/ufw` antes de mudar | Volta exatamente às regras que a pessoa já tinha |
| Os testes têm três níveis: contêiner, máquina virtual e máquina de verdade | O contêiner testa a cada mudança, mas não tem kernel, disco nem rede reais. Uma receita só é recomendada sem ressalva depois de passar numa máquina virtual |

## 5 de novembro de 2026: rolê "Pronto para estudar e trabalhar"

| Decisão | Por quê |
|---|---|
| O prompt de copiloto para colar em chats gratuitos virou o `bora ajuda`, que já saiu no v0 | A proposta consolidada trocou o prompt fixo por uma pergunta montada com o diagnóstico da máquina, a etapa e o erro, que serve para qualquer chat, gratuito ou pago |
| Os codecs são os plugins do GStreamer (`libav`, `good`, `bad` e `ugly`), sem o `ubuntu-restricted-extras` e sem a `libavcodec-extra` | Os players dos ambientes gráficos usam o GStreamer. O `ubuntu-restricted-extras` para a instalação para pedir que se aceite a licença das fontes da Microsoft, baixadas de fora dos repositórios, e a `libavcodec-extra` só acrescenta codificadores, trocando um pacote que outros programas usam |
| O Flatpak liga o Flathub para o sistema todo e não remove o Snap | Os aplicativos servem para todas as pessoas do computador, e remover o Snap é uma decisão maior, para uma receita própria |
| O desfazer do Flatpak não remove o Flathub se houver aplicativos instalados por ele | Remover deixaria esses aplicativos sem atualização |
| O backup da pasta pessoal usa rsync com hardlinks, numa pasta comum do disco externo | Recuperar um arquivo é abrir a pasta da data e copiar, em qualquer computador com Linux, sem programa especial. As versões não repetem o que não mudou |
| O backup só aceita disco em ext4, xfs ou btrfs, e o `bora` nunca formata disco | exFAT, NTFS e FAT não guardam dono, permissões nem hardlinks. Formatar apagaria o que está no disco, e isso é decisão da pessoa |
| O backup roda de hora em hora (copiando se a última cópia tiver mais de 20 horas) e ao conectar o disco | Num notebook, o disco externo quase nunca está conectado na hora marcada |
| O desfazer do backup nunca apaga as cópias do disco | São os arquivos da pessoa |

## 6 de novembro de 2026: rolê "Dar vida nova a uma máquina antiga"

| Decisão | Por quê |
|---|---|
| O zram usa o `systemd-zram-generator`, com até 50% da memória (no máximo 8 GB), zstd e prioridade acima da swap no disco | É o que o Fedora usa por padrão, existe no Ubuntu e no Debian, e configura tudo num arquivo só. A swap no disco fica como reserva |
| A receita do zram não mexe num zram que já existia | O Pop!_OS e quem instalou o `zram-tools` já têm um, configurado de propósito |
| O ambiente leve é o Xfce ou o LXQt, instalado ao lado do atual e sem os pacotes recomendados | Com os recomendados viria outra tela de login, que mudaria o jeito de entrar no computador. Ao lado, dá para testar sem perder nada |
| A sessão padrão vai pelo AccountsService, e só quando a pessoa pede | É de onde o GDM e o LightDM tiram a sessão de cada pessoa, e o arquivo é guardado e restaurado como qualquer outro |
| O navegador enxuto é o próprio Firefox, configurado por `/etc/firefox/policies/policies.json` | O Firefox já vem nas distros da onda 1, e o arquivo de políticas vale para o Snap e para o pacote do apt. Trocar de navegador mudaria o dia a dia da pessoa |
| O uBlock Origin vem da loja oficial da Mozilla, pela política `ExtensionSettings` | O bloqueador precisa de atualizações frequentes, que a loja entrega sozinha. O pacote do Debian demora a chegar e não serve para o Firefox do Snap. É a única exceção à regra de só usar os repositórios da distro e o Flathub, e vale porque quem baixa é o próprio Firefox, da loja do fabricante. Confirmado por Brahm em 7/11/2026 |
| Os serviços só são desligados quando a máquina comprovadamente não usa: Bluetooth sem placa, ModemManager sem modem e a espera da rede sem pastas da rede no `fstab` | Impressão, som e busca de arquivos dependem do uso, e desligar errado quebraria algo sem aviso. A receita usa `disable`, e não `mask`, para um comando ligar de volta |
| O `bora diag` mostra o zram e se o disco do sistema é SSD ou disco rígido | É o que o rolê precisa para dizer quando um SSD faria mais diferença do que qualquer ajuste |

## 6 de novembro de 2026: rolê "Começar a programar"

| Decisão | Por quê |
|---|---|
| O rolê tem dois perfis, Python e web, escolhidos numa pergunta com opções; as receitas do perfil entram no plano com `quando` | Quem vai para dados e automação precisa do Python preparado; quem vai para web, do Node.js. Instalar só o que a pessoa vai usar deixa o computador mais simples de entender. O formato de rolê ganhou `opcoes` nas perguntas e `quando` nas receitas para isso |
| O Node.js é o LTS oficial de nodejs.org, numa versão fixada (26.13.0), conferida pela soma SHA256 gravada na receita, em `/usr/local/lib/nodejs` | O Node.js do Ubuntu 24.04, a base da maior parte da onda 1, é a versão 18, que já saiu de suporte e não roda o Vite atual. Escolhido por Brahm em 6/11/2026. É mais uma exceção à regra dos repositórios da distro, nos termos da regra dos instaladores oficiais: o arquivo vem do fabricante e só é instalado se a soma bater. A versão sobe com o `bora` |
| O `npm install -g` instala em `~/.local`, pelo `prefix` no `npmrc` do Node.js | É o fim do `sudo npm install -g`, que deixa arquivos do root na pasta do npm e quebra o próximo `npm` sem sudo |
| O Python é o da distro, com `venv`, `pip`, `pipx` e `python-is-python3`, sem trocar a versão | A distro usa o próprio Python, e o PEP 668 já impede o `pip` fora de um ambiente virtual. Um ambiente por projeto é o que os tutoriais ensinam |
| Os contêineres são do Podman, sem root, com o Docker Hub como registro dos nomes curtos | O Podman não tem um serviço como root por trás e aceita os comandos do Docker. No Docker, estar no grupo `docker` equivale a ser root |
| As receitas que mexem na pasta pessoal configuram a conta de quem rodou o `bora` com `sudo`, que o `bora` passa em `BORA_PESSOA` | O `bora` roda como root, mas o Git, o pipx, o npm e os contêineres são de uma pessoa. Sem `sudo`, vale a única conta com pasta em `/home`, ou o parâmetro `usuario` |
| A chave SSH é criada sem senha, e o desfazer não apaga | A receita não faz perguntas no meio, e o LEIAME ensina a pôr uma senha depois. A chave pode já estar cadastrada no GitHub, e apagar cortaria o acesso |

## 7 de novembro de 2026: pendências da v0.4.0

Decididas por Brahm em 7/11/2026, a partir do levantamento do que ficou sem plano depois da v0.4.0.

| Decisão | Por quê |
|---|---|
| O nível `testada` aparece no site como "testada em contêiner" enquanto a receita só tiver testes em contêiner | A definição antiga dizia "roda em máquina virtual", e nenhuma receita tinha passado numa ainda. O rótulo diz o que foi feito de verdade |
| Cada rolê tem um roteiro de teste em máquina virtual, em `testes/vm/`, rodado no Ubuntu 24.04, no Ubuntu 26.04, no Debian 13 e no Linux Mint | O contêiner não confere kernel, disco, rede nem tela de login. Das derivadas, só o Mint entra, por ser a mais usada; o Pop!_OS e o Zorin OS continuam como "herdada" |
| O formulário "Relato de teste" recebe testes em máquina virtual e em computador de verdade | Quem testa não precisa saber abrir um pull request para contribuir com a parte mais valiosa |
| O histórico do `/etc` (etckeeper) entra no rolê 1, logo depois da atualização | Assim, tudo o que as receitas seguintes mudam na configuração fica registrado. O desfazer guarda uma cópia do histórico em `/var/backups` antes de remover |
| O Sem Snap entra no rolê 1 como opcional, perguntado com o padrão "não" | Tirar o Snap é uma escolha, e não um conserto. A receita para sem mudar nada se encontrar um snap que não sabe trocar ou se tirar o `snapd` levaria um pacote que não é do Snap |
| No Sem Snap, o Firefox vem do repositório APT da Mozilla, com a chave conferida pela impressão digital publicada, e o Thunderbird vem do Flathub | O pacote `firefox` do Ubuntu só instala o Snap. O repositório da Mozilla é o caminho que ela recomenda, entrega as atualizações no mesmo dia e mantém as políticas de `/etc/firefox/policies`. É a segunda exceção à regra dos repositórios da distro, nos mesmos termos da do uBlock Origin: o arquivo vem do fabricante. O repositório é ligado antes de qualquer coisa sair, para uma falha de rede não deixar a pessoa sem navegador |
| O acesso por SSH entra no rolê 2 como opcional, só para a rede local, sem login do root e, se pedido, só com chave | Uma máquina antiga que vira servidor da casa fica num canto, sem tela. A receita só desliga a senha se a conta já tiver uma chave, e a regra do firewall vale só para a rede local. A mesma receita vai servir ao rolê 7 |
| Os links do site e da documentação são conferidos todo mês pelo GitHub Actions, que abre uma issue quando algum quebra | As páginas da distro apontam para sites de fora, que mudam de endereço sem avisar |
| A versão do Node.js da receita é comparada toda semana com nodejs.org, e uma versão nova da mesma linha LTS abre uma issue, com destaque para as correções de segurança | A versão fixada só sobe com o `bora`, e uma correção de segurança não pode esperar alguém lembrar de olhar |

## 8 de novembro de 2026: segunda rodada de pendências

| Decisão | Por quê |
|---|---|
| Um rolê vira `testado` quando o roteiro de teste em VM dele passa inteiro no Ubuntu 24.04 e no Debian 13. Escolhido por Brahm em 8/11/2026 | São as duas bases de que as outras distros da onda 1 dependem. O Ubuntu 26.04 e o Linux Mint seguem no roteiro, mas um problema neles vira issue em vez de segurar o status |
| As etiquetas do repositório ficam em `.github/etiquetas.txt`, e um workflow as cria quando o arquivo muda | Os formulários de issue apontavam para etiquetas que não existiam, e o GitHub abria as issues sem elas, sem avisar |
| As actions de artefato sobem para a v7 (`upload-artifact` e `download-artifact`) | A v5, proposta antes, ainda roda no Node.js 20, que o GitHub está desligando; a v7 é a primeira das duas que roda no Node.js 24 |
| A parte dos rolês que não depende de tela roda numa VM de verdade no CI, com QEMU e KVM, no Ubuntu 24.04 e no Debian 13 (workflow Máquina virtual) | Os runners do GitHub têm KVM, e as imagens de nuvem das duas distros sobem em segundos com cloud-init. Cada distro leva de 9 a 12 minutos, então roda todo domingo e nos pull requests que mexem nas receitas que ela cobre, e não em todo push. Ela não substitui o roteiro manual: a tela, o player, a loja e os perfis só se conferem olhando |
| O que a VM achou nas primeiras rodadas foi corrigido no mesmo pull request | Quatro defeitos que o contêiner não via: o zram não ligava no Ubuntu sem reiniciar (o módulo só carregava no boot) e não tinha o módulo nas instalações de servidor e de nuvem; as receitas do firewall e do SSH trocavam o comentário da regra do SSH uma da outra, e a segunda aplicação nunca dizia "nada mudou"; e o teste dos codecs falhava às vezes por um `dpkg -L \| grep -m1` com pipefail |

## 8 de novembro de 2026: terceira rodada de pendências

| Decisão | Por quê |
|---|---|
| A versão sobe para 0.5.1. Escolhido por Brahm em 8/11/2026 | As correções que a VM achou já estavam na `main`, mas a versão publicada era a 0.5.0, sem elas |
| A VM do CI aplica, além do rolê 1, todos os outros rolês, com todas as receitas de uma vez e sem as que só se conferem com tela (`testes/vm/qemu/so-com-tela.txt`). Um rolê novo entra sozinho | Hoje isso cobre o rolê 3 inteiro e a parte sem tela do rolê 2. Aplicar todas as receitas, como se a pessoa respondesse "sim" a tudo, cobre os dois caminhos do rolê 3 (Python e Node.js) numa só máquina |
| O Ubuntu 26.04 entra na VM do CI, pela imagem de nuvem oficial | É a outra LTS da família Ubuntu, e a imagem oficial sobe do mesmo jeito que a da 24.04 |
| Quando a VM passa na `main`, o próprio workflow grava nas receitas o registro com `onde: vm` e `por: testes-automaticos`, e publica o site | Sem o registro, o `bora` seguia avisando que a receita não tinha passado numa máquina virtual. O registro é um por distro e só muda de data, para a lista não crescer toda semana, e não substitui o relato de uma pessoa, que tem outro autor |
| Quando a VM falha no domingo, o workflow abre uma issue com a etiqueta `vm`, ou comenta na que estiver aberta | É o que os workflows de links e do Node.js já fazem. Um e-mail do GitHub se perde fácil |
| Nenhum script usa mais `\| grep -q`, `\| grep -m` ou `\| head`, e o CI barra os novos (`ferramentas/pipes/conferir.sh`) | Com pipefail, eles falham às vezes por SIGPIPE, como o teste dos codecs. No lugar, `grep -q x <<<"$(cmd)"`, um `awk` que lê até o fim ou a opção da própria ferramenta que limita a saída |
| O zram continua trazendo o `linux-image-extra-virtual` em servidor e em nuvem, com o aviso no LEIAME de que ele puxa o `linux-firmware` | É o que mantém o zram depois da próxima atualização do kernel. Quem tem pouco disco pode instalar só os módulos do kernel de agora |
| O segfault do Timeshift no contêiner do Ubuntu 24.04 fica sendo acompanhado na [issue #16](https://github.com/brahm/linux-para-todos-os-roles/issues/16) | Aconteceu uma vez e não se repetiu |
| Os rolês continuam `rascunho` até os roteiros manuais passarem | A VM do CI não confere a tela, então não basta para o `testado` |

## 8 de novembro de 2026: quarta rodada de pendências

| Decisão | Por quê |
|---|---|
| O `bora` deixa de ser publicado para ARM (aarch64) e passa a aceitar só x86_64. Escolhido por Brahm em 8/11/2026 | O ARM não passa de 5% das instalações de Linux, e o binário ARM nunca rodou em teste nenhum. Mais adiante, o `bora` vai ser distribuído também como pacote nas distros compatíveis |
| As notas de cada versão saem em português, escritas pelo próprio workflow de publicação (`ferramentas/notas/escrever.sh`) | As notas automáticas do GitHub só existem em inglês. A lista de pull requests continua vindo delas |
| As diferenças conhecidas do Linux Mint, do Pop!_OS e do Zorin OS ficam registradas em `familias/README.md` | O plano previa um `familias/derivadas.yaml`, mas o `bora` ainda não lê essas diferenças. Enquanto forem só informação, o README basta |
| A issue #16 (segfault do Timeshift) é fechada em 8/2/2027 se não se repetir | Três meses de testes semanais sem o erro bastam para considerar que foi do contêiner |
| O rolê 4, Vibecodar, começa quando Brahm pedir | Ele fecha a primeira versão útil, mas não tem data |

## 8 de novembro de 2026: quinta rodada de pendências

| Decisão | Por quê |
|---|---|
| A versão sobe para 0.5.2. Escolhido por Brahm em 8/11/2026 | A 0.5.1 ainda trazia o binário ARM, e as notas em português só rodam numa versão nova |
| A VM também roda nos pull requests que mexem no código do `bora` (`src/`) e no `Cargo.toml` ou no `Cargo.lock` | Uma mudança no executor pode quebrar o que só a VM confere, e antes ela só apareceria no domingo seguinte |
| O workflow de testes grava sozinho, na `main`, o registro `onde: conteiner` das receitas marcadas como "testada" em cada família que passou | O registro em contêiner tinha sido escrito à mão em 6/11 e não acompanhava os testes que rodam a cada pull request |
| Os registros automáticos só mudam quando o resultado muda ou quando passam de 30 dias | Assim, o histórico e a lista "Últimas mudanças" do site não ganham um commit por semana só para trocar a data. O site mostra a data do último registro, que nunca tem mais de um mês |
| O `bora` como pacote nas distros compatíveis entra na fase "A casa, o Fedora e os agentes", junto do instalador único | Foi a direção dada ao tirar o ARM. Instalar e atualizar pelo gerenciador de pacotes é o caminho natural para quem não quer baixar binário |
| Uma tarefa agendada confere a issue #16 em 8/2/2027 e a fecha se o segfault não voltou | O prazo precisava de alguém que lembrasse dele |

## 8 de novembro de 2026: a máquina virtual com tela

| Decisão | Por quê |
|---|---|
| Um segundo workflow, Máquina virtual com tela, liga uma VM com a tela de login do GNOME e confere o ambiente leve, o navegador enxuto e o Sem Snap, com capturas da tela de cada passo. Pedido por Brahm em 8/11/2026 | Eram as três receitas que nenhum teste automático aplicava. Os roteiros manuais continuam em paralelo |
| A tela de login é a do GNOME (GDM), instalada sobre a imagem de nuvem, com a entrada automática da pessoa ligada só durante o teste | É a tela de login do Ubuntu e do Debian com GNOME, onde a pessoa escolhe o ambiente leve. A entrada automática deixa conferir, sem teclado, que a receita fez o ambiente leve abrir por padrão |
| O Xfce é testado no Ubuntu e o LXQt no Debian | É a mesma divisão dos testes em contêiner, e assim os dois ambientes passam por uma máquina de verdade |
| A captura reprova uma tela quase toda de uma cor só ou ainda em modo texto; o resto é conferido de dentro da máquina (sessões do systemd-logind, processos e o perfil do Firefox) | Uma imagem não diz sozinha se é a tela certa, mas prova que algo foi desenhado. Quem quiser ver, abre o artefato |
| O registro `onde: vm` dessas receitas conta para o `testado` como o das outras, mas não dispensa o roteiro manual | A regra de quando um rolê vira `testado` continua a mesma até Brahm decidir outra coisa |
| A parte que liga a máquina saiu do `rodar.sh` para o `maquina.sh`, que as duas VMs usam | Assim, uma correção no boot ou no SSH vale para as duas |
