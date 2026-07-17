# 🐧 Linux para Todos os Rolês (linux install fest)

> Roteiros de instalação e pós-instalação Linux para transformar computadores comuns, servidores esquecidos e máquinas com ideias mirabolantes em ambientes úteis — preferencialmente sem invocar demônios no `GRUB`.

Este repositório reúne guias **didáticos, reproduzíveis e amigáveis para iniciantes**. A proposta não é apenas entregar uma parede de comandos para copiar e colar: cada roteiro explica **o que será feito, por que aquilo é necessário, como conferir se funcionou e como voltar atrás quando possível**.

Aqui você vai encontrar desde roteiros de instalações de desktop para trabalho e estudo até servidores domésticos, laboratórios de virtualização e casos menos convencionais, como Arch Linux em máquinas cujos discos formam um FakeRAID*.

> [!IMPORTANT]
> Linux dá liberdade. Liberdade inclui a possibilidade de formatar o disco errado com muita eficiência. Leia o roteiro inteiro antes de começar e faça backup dos seus arquivos.

## O que você encontrará por aqui

Os roteiros são organizados por **distribuição**, **objetivo** e **cenário de hardware**. Entre os guias planejados estão:

| Roteiro | Para quem é | Nível | Situação |
|---|---|:---:|:---:|
| Arch Linux com backup automático (snapshots) em FakeRAID 0 | Máquinas com RAID configurado pela BIOS/UEFI e usuários dispostos a aprender bastante | 🧗 Avançado | 👌 Pronto |
| Ubuntu LTS para desenvolvimento com IA local | Quem quer programar, usar contêineres e executar modelos locais com CPU ou GPU | 🛠️ Intermediário | 👌 Pronto |
| Servidor de arquivos com Samba | Casas e pequenos escritórios com clientes Linux, Windows ou macOS | 🌱 Iniciante | 📝 Planejado |
| Servidor multimídia com Jellyfin | Quem deseja organizar e transmitir sua própria biblioteca de mídia | 🌱 Iniciante | 📝 Planejado |
| Homelab com virtualização e contêineres | Quem quer aprender redes, serviços, VMs e automação em casa | 🛠️ Intermediário | 📝 Planejado |
| Debian enxuto para servidor | Quem prefere estabilidade, poucos enfeites e uma máquina que simplesmente trabalhe | 🌱 Iniciante | 📝 Planejado |

### Legenda de dificuldade

- 🌱 **Iniciante:** explicações passo a passo e pouca experiência prévia necessária.
- 🛠️ **Intermediário:** exige alguma familiaridade com terminal, discos, rede ou serviços.
- 🧗 **Avançado:** envolve riscos maiores, recuperação manual ou hardware incomum. Não significa “proibido para iniciantes”; significa “prepare café e não pule etapas”.

## Qual roteiro combina comigo?

| Quero... | Bom ponto de partida | Por quê? |
|---|---|---|
| Um computador para estudar, programar e experimentar IA | **Ubuntu LTS para IA local** | Oferece uma base previsível, ampla documentação e bom suporte às ferramentas de contêiner e GPU. |
| Compartilhar pastas na rede de casa | **Servidor de arquivos com Samba** | O Samba usa o protocolo SMB e conversa bem com computadores Windows e Linux. |
| Assistir à minha biblioteca de mídia em vários dispositivos | **Servidor multimídia com Jellyfin** | O Jellyfin organiza e transmite mídia por uma interface web e aplicativos clientes. |
| Criar VMs, redes e serviços para aprender | **Homelab** | Permite quebrar ambientes virtuais sem necessariamente quebrar o computador da família. “Necessariamente” é a palavra tranquilizadora. |
| Entender cada peça do sistema | **Arch Linux** | A instalação manual é uma excelente aula prática — e também uma excelente forma de descobrir quantas coisas acontecem antes da tela de login. |
| Manter um servidor simples e estável | **Debian enxuto** | É uma base conservadora e adequada para serviços que não precisam de novidades toda terça-feira. |

(*) FakeRAID, também chamado de *firmware RAID* ou *host RAID*, é o RAID configurado no firmware da placa-mãe, mas processado em grande parte pelo computador e pelo sistema operacional. No Linux, o conjunto pode aparecer por caminhos diferentes dos discos físicos comuns.
