# Rolês e receitas do catálogo. As receitas prontas também são lidas dos receita.yaml.
import yaml

from comum import RAIZ_REPO as RAIZ

# id -> (nome, ícone, cor, descrição curta)
RECEITAS = {
    "base/atualizar": ("Sistema atualizado", "atualizar", "l-verde", "Atualiza os programas e liga as atualizações automáticas de segurança."),
    "sistema/snapshot": ("Snapshot do sistema", "snapshot", "l-azul", "Fotos diárias e semanais do sistema, para voltar no tempo se algo quebrar."),
    "seguranca/firewall": ("Firewall", "firewall", "l-vermelho", "Bloqueia o que chega de fora e libera só o que o perfil pede."),
    "desktop/codecs": ("Codecs de áudio e vídeo", "codecs", "l-roxo", "Para tocar MP3, MP4 e os vídeos que vêm do celular."),
    "desktop/flatpak": ("Flatpak e Flathub", "flatpak", "l-azul", "A loja de aplicativos que funciona igual em qualquer distro."),
    "sistema/backup-pessoal": ("Backup da pasta pessoal", "backup", "l-amarelo", "Uma cópia dos seus arquivos num disco externo, todo dia."),
    "sistema/zram": ("Memória comprimida", "memoria", "l-verde", "Usa zram para caber mais programas abertos em pouca memória."),
    "desktop/ambiente-leve": ("Ambiente leve", "janela", "l-verde", "Um ambiente gráfico leve ao lado do atual, escolhido na tela de login."),
    "desktop/navegador-leve": ("Navegador enxuto", "navegador", "l-azul", "O Firefox com bloqueio de anúncios e sem o que pesa à toa."),
    "sistema/servicos-enxutos": ("Serviços enxutos", "desligar", "l-grafite", "Desliga o que a máquina não usa, como Bluetooth sem placa de Bluetooth."),
    "dev/git": ("Git", "git", "l-vermelho", "Git com seu nome, seu e-mail e uma chave SSH para o GitHub ou o GitLab."),
    "dev/compilacao": ("Ferramentas de compilação", "ferramenta", "l-grafite", "Compilador, make e o que mais os pacotes de programação pedem."),
    "dev/python": ("Python com ambientes virtuais", "python", "l-azul", "Python para projetos, sem mexer no Python que a distro usa."),
    "dev/node": ("Node.js", "node", "l-verde", "A versão LTS do Node.js, com npm, sem precisar de sudo."),
    "containers/podman": ("Contêineres com Podman", "conteiner", "l-roxo", "Contêineres que rodam sem permissão de administrador."),
    "ia/agentes": ("Agentes de IA no terminal", "robo", "l-roxo", "Claude Code, Codex, Copilot CLI, OpenCode e outros, pelos instaladores oficiais."),
    "ia/chaves-de-api": ("Chaves de API guardadas", "chave", "l-amarelo", "Um lugar para as chaves, com permissão só do dono."),
    "seguranca/segredos": ("Verificação de segredos", "lupa", "l-vermelho", "O gitleaks confere cada commit, para nenhuma chave ir parar no GitHub."),
    "containers/caixa-de-areia": ("Caixa de areia para os agentes", "caixa", "l-marrom", "Os agentes rodam num contêiner, sem acesso ao sistema todo."),
    "ia/ollama": ("IA local com Ollama", "robo", "l-grafite", "Modelos de IA rodando no próprio computador, se ele aguentar."),
    "servicos/samba": ("Compartilhamento Samba", "pasta", "l-amarelo", "Uma pasta que Windows, Mac, Linux e celulares abrem pela rede."),
    "servicos/jellyfin": ("Servidor Jellyfin", "filme", "l-vermelho", "Filmes e séries para a TV e os celulares da casa."),
    "rede/tailscale": ("Tailscale", "vpn", "l-marrom", "Uma rede privada entre os seus aparelhos, sem abrir portas."),
    "rede/teste-cgnat": ("Teste de CGNAT", "rede", "l-grafite", "Mostra se a sua internet está atrás de CGNAT, e por que isso não importa com a VPN."),
}

PRONTAS = ["base/atualizar", "sistema/snapshot", "seguranca/firewall", "desktop/codecs", "desktop/flatpak", "sistema/backup-pessoal",
           "sistema/zram", "desktop/ambiente-leve", "desktop/navegador-leve", "sistema/servicos-enxutos"]

AREAS = {
    "base": "Base",
    "sistema": "Sistema",
    "seguranca": "Segurança",
    "desktop": "Desktop",
    "dev": "Programação",
    "containers": "Contêineres",
    "ia": "IA",
    "servicos": "Serviços da casa",
    "rede": "Rede",
}

FAMILIAS = [
    ("ubuntu", "Ubuntu", "Ubuntu, Mint, Pop!_OS, Zorin"),
    ("debian", "Debian", "Debian 13"),
    ("fedora", "Fedora", "Fedora, Nobara"),
    ("arch", "Arch", "Arch, CachyOS, EndeavourOS, Manjaro"),
    ("fedora-imutavel", "Fedora imutável", "Bazzite, Silverblue, Kinoite"),
    ("opensuse", "openSUSE", "Tumbleweed, Leap"),
]

NIVEL_TEXTO = {
    "testada": "Testada",
    "herdada": "Herdada",
    "comunidade": "Comunidade",
    "planejada": "Planejada",
    "nao-se-aplica": "Não se aplica",
}


def pagina_receita(rid):
    return "receitas/" + rid.replace("/", "-") + ".html"


def ler_receita(rid):
    return yaml.safe_load(open(f"{RAIZ}receitas/{rid}/receita.yaml", encoding="utf-8"))


# Rolês. "receitas" é a lista de (id, nota). Os da primeira versão, na ordem do site.
ROLES = [
    {
        "id": "pronto-para-estudar", "num": "01", "icone": "livro", "cor": "l-azul",
        "nome": "Pronto para estudar e trabalhar",
        "resumo": "O computador atualizado, protegido e com um jeito fácil de voltar atrás se algo der errado.",
        "para_quem": ["curiosos", "estudantes"],
        "hardware": "2 GB de memória, 20 GB livres e um disco externo",
        "status": "rascunho",
        "receitas": [("base/atualizar", ""), ("seguranca/firewall", "perfil desktop"), ("sistema/snapshot", ""),
                     ("desktop/codecs", ""), ("desktop/flatpak", ""), ("sistema/backup-pessoal", "")],
        "faz": [
            "<strong>Atualiza tudo</strong> e deixa as correções de segurança chegando sozinhas, todo dia.",
            "<strong>Liga o firewall</strong> no perfil de uso pessoal: nada que chega de fora entra sem ser chamado.",
            "<strong>Guarda fotos do sistema</strong> todo dia e toda semana, para voltar no tempo se uma atualização quebrar algo.",
            "<strong>Toca qualquer vídeo e música</strong>, com os codecs que as distros não trazem por questão de licença.",
            "<strong>Abre a loja Flathub</strong>, com os aplicativos de estudo e trabalho na versão mais nova.",
            "<strong>Copia a sua pasta pessoal</strong> para um disco externo, todo dia.",
        ],
        "nao_faz": [
            "Não troca a sua distro nem o seu ambiente gráfico.",
            "Não instala programas que você não pediu, como suíte de escritório ou jogos.",
            "Não manda nada para a nuvem: o backup vai para um disco seu.",
            "Não formata disco nenhum: o disco externo do backup precisa estar em ext4, e o rolê explica como deixar ele assim.",
            "Não abre nenhuma porta para a internet.",
        ],
        "porques": [
            ("Por que começar pela atualização?", "Um computador recém-instalado costuma estar semanas atrás, porque a imagem de instalação foi gerada antes. Atualizar primeiro evita correr atrás de defeitos que já foram corrigidos."),
            ("Por que snapshot e backup, os dois?", "O snapshot guarda o sistema e volta o computador a como estava ontem. O backup guarda os seus arquivos num outro disco, para o dia em que o disco do computador morrer. Um não substitui o outro."),
            ("Por que firewall num notebook de casa?", "Porque o notebook não fica só em casa. Numa rede de café, de faculdade ou de aeroporto, qualquer pessoa conectada pode tentar falar com as portas que os programas abrem sem avisar."),
            ("Por que Flatpak?", "Os aplicativos do Flathub chegam na versão mais nova sem esperar a próxima versão da distro, e rodam isolados do sistema. Os pacotes da distro continuam lá."),
        ],
        "pronto_quando": "O bora diz que tudo está aplicado, um vídeo comum toca, o Timeshift mostra o primeiro snapshot e o disco externo tem a primeira cópia da pasta pessoal.",
        "como_desfazer": "O bora desfaz as receitas na ordem contrária e remove só o que ele mesmo instalou.",
        "perguntas": ["Instalar as atualizações de segurança sozinho, todo dia? (o padrão é sim)", "Em que disco externo guardar a cópia da pasta pessoal? (o padrão usa o disco USB conectado)"],
    },
    {
        "id": "maquina-antiga", "num": "02", "icone": "broto", "cor": "l-verde",
        "nome": "Dar vida nova a uma máquina antiga",
        "resumo": "Um computador de dez anos atrás voltando a abrir o navegador e os vídeos sem travar.",
        "para_quem": ["curiosos", "estudantes"],
        "hardware": "64 bits, 2 GB de memória e 15 GB livres",
        "status": "rascunho",
        "receitas": [("base/atualizar", ""), ("sistema/snapshot", ""), ("sistema/zram", ""), ("desktop/ambiente-leve", "Xfce ou LXQt"),
                     ("desktop/navegador-leve", ""), ("sistema/servicos-enxutos", "")],
        "faz": [
            "<strong>Atualiza tudo e guarda uma foto do sistema</strong> antes de mexer, para voltar atrás se algo der errado.",
            "<strong>Comprime a memória</strong> com zram, para caber mais abas e programas antes de a máquina engasgar.",
            "<strong>Instala um ambiente leve</strong>, o Xfce ou o LXQt, ao lado do que você já tem. Você escolhe qual usar na tela de login.",
            "<strong>Deixa o Firefox mais leve</strong>, com o bloqueador de anúncios uBlock Origin e as abas paradas saindo da memória quando ela acaba.",
            "<strong>Desliga o que a máquina não usa</strong>, como o Bluetooth num computador sem Bluetooth, e faz o boot parar de esperar a rede.",
        ],
        "nao_faz": [
            "Não apaga o ambiente gráfico que você já tem.",
            "Não troca o seu navegador: o Firefox continua o mesmo, com os seus favoritos e senhas.",
            "Não faz uma máquina de 32 bits rodar distros modernas: elas pararam de sair para 32 bits.",
            "Não mexe na BIOS, nem troca peças, nem faz overclock.",
            "Não promete milagre: um disco rígido antigo continua lento, e o <code>bora diag</code> diz quando um SSD faria mais diferença do que qualquer ajuste.",
        ],
        "porques": [
            ("Por que zram, e não mais swap no disco?", "Num disco rígido antigo, usar o disco como memória deixa tudo travando. O zram guarda a memória comprimida na própria memória, o que é muito mais rápido. A swap no disco continua lá, como reserva."),
            ("Por que o ambiente leve fica ao lado do atual?", "Para você testar sem perder nada. Se não gostar, escolhe o antigo na tela de login, ou desfaz o rolê."),
            ("Por que mexer no navegador, e não trocar de navegador?", "Numa máquina antiga, o navegador é o programa que mais gasta memória, e boa parte do peso de uma página são anúncios. O Firefox já vem nas distros da onda 1 e é dos poucos em que o uBlock Origin completo ainda funciona."),
            ("E o SSD?", "Trocar um disco rígido por um SSD, mesmo o mais barato, é o que mais deixa uma máquina antiga rápida: o boot cai de minutos para segundos. O <code>bora diag</code> mostra que tipo de disco a máquina tem."),
        ],
        "pronto_quando": "O Firefox abre cinco abas e toca um vídeo sem a máquina travar, e o bora diag mostra o zram ligado.",
        "como_desfazer": "O bora desliga o zram, religa os serviços que desligou, volta o Firefox ao que era e remove o ambiente leve. O ambiente antigo nunca saiu de lá.",
        "perguntas": ["Qual ambiente leve: Xfce ou LXQt? (o padrão é o Xfce)", "Passar a entrar no ambiente leve por padrão? (o padrão é não: ele aparece como opção na tela de login)", "Instalar o bloqueador de anúncios no Firefox? (o padrão é sim)"],
    },
    {
        "id": "comecar-a-programar", "num": "03", "icone": "terminal", "cor": "l-grafite",
        "nome": "Começar a programar",
        "resumo": "Git, Python, Node.js e contêineres prontos, do jeito que os tutoriais esperam encontrar.",
        "para_quem": ["estudantes", "entusiastas"],
        "hardware": "4 GB de memória e 30 GB livres",
        "status": "planejado",
        "receitas": [("base/atualizar", ""), ("dev/git", ""), ("dev/compilacao", ""), ("dev/python", "perfil Python"),
                     ("dev/node", "perfil web"), ("containers/podman", "")],
        "faz": [
            "<strong>Configura o Git</strong> com seu nome e seu e-mail, e cria uma chave SSH para o GitHub ou o GitLab.",
            "<strong>Instala as ferramentas de compilação</strong> que muitos pacotes de Python e de Node.js pedem na instalação.",
            "<strong>Prepara o Python para projetos</strong>, com ambientes virtuais, sem mexer no Python que a distro usa.",
            "<strong>Instala o Node.js LTS</strong> no seu usuário, para o npm funcionar sem sudo.",
            "<strong>Liga os contêineres com Podman</strong>, que rodam sem permissão de administrador.",
        ],
        "nao_faz": [
            "Não escolhe um editor por você. Use o que quiser; o rolê Vibecodar pergunta qual instalar.",
            "Não usa sudo com pip ou npm, que é a origem de muitos sistemas quebrados.",
            "Não troca o Python do sistema por outra versão.",
            "Não cria contas no GitHub ou no GitLab por você.",
        ],
        "porques": [
            ("Por que ambientes virtuais?", "A distro usa o próprio Python para funcionar. Instalar pacotes nele pode quebrar programas do sistema, e por isso as distros novas já bloqueiam o pip global. Cada projeto ganha o seu ambiente."),
            ("Por que Podman, e não Docker?", "O Podman roda contêineres no seu usuário, sem um serviço como root por trás, e aceita os mesmos comandos do Docker na maioria dos casos."),
            ("Por que dois perfis?", "Quem vai para web precisa de Node.js; quem vai para dados e automação precisa de Python. Instalar só o que você vai usar deixa o computador mais simples de entender."),
        ],
        "pronto_quando": "Um projeto de exemplo é criado, versionado no Git, roda em Python ou em Node.js, e um contêiner de teste sobe.",
        "como_desfazer": "O bora remove o que instalou e volta a configuração do Git. Os seus projetos e a chave SSH ficam onde estão.",
        "perguntas": ["Qual perfil: web (Node.js) ou Python?", "Que nome e que e-mail vão nos seus commits?"],
    },
    {
        "id": "vibecodar", "num": "04", "icone": "brilho", "cor": "l-roxo",
        "nome": "Vibecodar",
        "resumo": "Programar conversando com agentes de IA, com as chaves guardadas e os agentes numa caixa de areia.",
        "para_quem": ["estudantes", "entusiastas"],
        "hardware": "8 GB de memória e 40 GB livres",
        "status": "planejado",
        "receitas": [("base/atualizar", ""), ("dev/git", ""), ("dev/python", ""), ("dev/node", ""), ("ia/agentes", ""),
                     ("ia/chaves-de-api", ""), ("seguranca/segredos", ""), ("containers/caixa-de-areia", "opcional"), ("ia/ollama", "se a máquina aguentar")],
        "faz": [
            "<strong>Tudo do “Começar a programar”</strong>, mais ripgrep, fd, jq e o GitHub CLI, que os agentes usam o tempo todo.",
            "<strong>Instala os agentes que você escolher</strong> (Claude Code, Codex, Copilot CLI, Antigravity CLI, Mistral Vibe ou OpenCode) pelos instaladores oficiais, que o bora baixa, confere e mostra antes de rodar.",
            "<strong>Guarda as chaves de API</strong> num arquivo em <code>~/.config</code> que só você lê, e configura o OpenCode com a sua chave, se você tiver uma.",
            "<strong>Confere cada commit com o gitleaks</strong>, para nenhuma chave ir parar no GitHub por engano.",
            "<strong>Coloca os agentes numa caixa de areia</strong>, se você quiser, onde eles não enxergam o sistema todo.",
        ],
        "nao_faz": [
            "Nenhum agente recebe sudo. Quem aplica mudanças no sistema é sempre você, pelo bora.",
            "Não guarda chave nenhuma no repositório nem manda as suas chaves para lugar nenhum.",
            "Não assina planos pagos nem cria contas por você.",
            "Não esconde que este é o rolê que mais quebra: os agentes mudam de instalador o tempo todo, e as receitas são conferidas a cada versão do bora.",
        ],
        "porques": [
            ("Por que caixa de areia?", "Um agente roda comandos no seu computador. Numa caixa de areia, um comando errado apaga, no máximo, o que está dentro dela."),
            ("Por que o gitleaks?", "Colar uma chave de API num arquivo e fazer commit é o acidente mais comum de quem começa com agentes. O gitleaks barra o commit antes."),
            ("Por que qualquer agente serve?", "O rolê não depende de um fornecedor. Quem não tem cartão consegue usar agentes com cota gratuita ou modelos locais."),
        ],
        "pronto_quando": "Cada agente responde a um “olá” no terminal, e um projeto de exemplo é criado, versionado e passa pela verificação de segredos.",
        "como_desfazer": "O bora remove os agentes, a caixa de areia e o gitleaks que instalou. O arquivo de chaves fica, para você decidir se apaga.",
        "perguntas": ["Quais agentes você quer?", "Vai usar chave de API (OpenRouter, DeepSeek ou outra)?", "Qual editor: VS Code, VSCodium, Zed ou só o terminal?", "Quer isolar os agentes numa caixa de areia?"],
    },
    {
        "id": "pasta-compartilhada", "num": "05", "icone": "pasta", "cor": "l-amarelo",
        "nome": "Pasta compartilhada da casa",
        "resumo": "Uma pasta neste computador que os outros computadores e celulares da casa conseguem abrir.",
        "para_quem": ["curiosos", "entusiastas"],
        "hardware": "2 GB de memória e 10 GB livres",
        "status": "planejado",
        "receitas": [("base/atualizar", ""), ("sistema/snapshot", ""), ("seguranca/firewall", "perfil servidor-lan"), ("servicos/samba", "")],
        "faz": [
            "<strong>Cria a pasta</strong> que você escolher, por padrão <code>/srv/compartilhado</code>.",
            "<strong>Compartilha pela rede com o Samba</strong>, que Windows, Mac, Linux, Android e iPhone já sabem abrir.",
            "<strong>Cria um acesso para cada pessoa</strong>, com nome e senha, sem usar a senha de ninguém no computador.",
            "<strong>Libera o compartilhamento só para a rede de casa</strong> no firewall.",
        ],
        "nao_faz": [
            "Não deixa a pasta acessível pela internet. Para abrir de fora, há o rolê “Acessar de fora sem abrir portas”.",
            "Não compartilha a sua pasta pessoal inteira.",
            "Não apaga os arquivos da pasta quando o rolê é desfeito.",
        ],
        "porques": [
            ("Por que Samba?", "É o jeito que todo sistema já entende de abrir pastas pela rede, sem instalar nada nos outros aparelhos."),
            ("Por que uma senha só para a pasta?", "Se a senha do compartilhamento vazar, ela não abre o computador. Cada pessoa tem a sua, e dá para tirar o acesso de uma sem mexer nas outras."),
        ],
        "pronto_quando": "Outro computador da rede abre a pasta e consegue criar um arquivo nela.",
        "como_desfazer": "O bora desfaz o compartilhamento e as regras de firewall, sem apagar os arquivos da pasta.",
        "perguntas": ["Qual pasta você quer compartilhar?", "Quem vai acessar? Escreva os nomes separados por vírgula."],
    },
    {
        "id": "filmes-e-series", "num": "06", "icone": "filme", "cor": "l-vermelho",
        "nome": "Filmes e séries da casa",
        "resumo": "O Jellyfin servindo os seus filmes e séries para a TV e os celulares, apenas na rede local.",
        "para_quem": ["curiosos", "entusiastas"],
        "hardware": "4 GB de memória e espaço para os filmes",
        "status": "planejado",
        "receitas": [("base/atualizar", ""), ("sistema/snapshot", ""), ("seguranca/firewall", "perfil servidor-lan"), ("servicos/jellyfin", "")],
        "faz": [
            "<strong>Instala o Jellyfin</strong>, um servidor de mídia livre, sem conta e sem assinatura.",
            "<strong>Aponta para as pastas</strong> de filmes, séries e músicas que você escolher.",
            "<strong>Libera o Jellyfin só para a rede de casa</strong> no firewall.",
            "<strong>Mostra o endereço</strong> para abrir na TV, no celular ou no navegador.",
        ],
        "nao_faz": [
            "Não baixa filmes nem séries.",
            "Não abre o Jellyfin para a internet. Para assistir de fora, há o rolê “Acessar de fora sem abrir portas”.",
            "Não apaga a sua coleção quando o rolê é desfeito.",
        ],
        "porques": [
            ("Por que Jellyfin?", "É livre, não pede conta em serviço nenhum e tem aplicativo para as TVs e os celulares mais comuns."),
            ("Por que só na rede de casa?", "Um servidor de mídia aberto na internet é um alvo. Dentro de casa, ou pela VPN, ele fica fora do alcance de quem não é da casa."),
        ],
        "pronto_quando": "A TV ou o celular, na mesma rede, abre o Jellyfin e toca um filme da sua pasta.",
        "como_desfazer": "O bora remove o Jellyfin e as regras de firewall. Os filmes continuam nas pastas.",
        "perguntas": ["Onde estão os filmes, as séries e as músicas?"],
    },
    {
        "id": "acessar-de-fora", "num": "07", "icone": "escudo-chave", "cor": "l-marrom",
        "nome": "Acessar de fora sem abrir portas",
        "resumo": "Os seus aparelhos numa rede privada, para abrir a pasta da casa ou o Jellyfin da rua, sem mexer no roteador.",
        "para_quem": ["curiosos", "entusiastas"],
        "hardware": "Qualquer máquina que rode os outros rolês",
        "status": "planejado",
        "receitas": [("base/atualizar", ""), ("seguranca/firewall", "perfil tailscale"), ("rede/tailscale", ""), ("rede/teste-cgnat", "")],
        "faz": [
            "<strong>Liga o computador à sua rede Tailscale</strong>, onde só entram os aparelhos que você autorizar.",
            "<strong>Ajusta o firewall</strong> para aceitar o que chega pela VPN, e só isso.",
            "<strong>Testa a sua conexão</strong> e mostra se ela está atrás de CGNAT, explicando o que isso quer dizer.",
        ],
        "nao_faz": [
            "Não abre porta nenhuma no roteador.",
            "Não precisa de IP fixo nem de domínio.",
            "Não cria a conta no Tailscale por você: ela é sua, e o plano pessoal é gratuito.",
        ],
        "porques": [
            ("Por que não abrir uma porta no roteador?", "Depende de cada roteador e de cada provedor, e muitas operadoras no Brasil usam CGNAT, que impede de vez. Mesmo quando dá, uma porta aberta fica exposta para a internet inteira."),
            ("O que é CGNAT?", "É quando a operadora divide um mesmo endereço de internet entre muitos clientes. Ninguém de fora consegue chegar até a sua casa por esse endereço. Com a VPN, isso não importa: os aparelhos se encontram por dentro dela."),
        ],
        "pronto_quando": "O celular fora de casa, no 4G, abre a pasta compartilhada ou o Jellyfin pelo nome do computador.",
        "como_desfazer": "O bora tira o computador da rede Tailscale, remove o programa e volta o firewall ao perfil anterior.",
        "perguntas": [],
    },
]

PUBLICOS = {"curiosos": "Curiosos", "estudantes": "Estudantes", "entusiastas": "Entusiastas"}
