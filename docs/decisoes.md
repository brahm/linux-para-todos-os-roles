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
