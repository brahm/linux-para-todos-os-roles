# Linux para Todos os Rolês

> Roteiros de instalação e pós-instalação Linux para transformar computadores comuns, servidores esquecidos e máquinas com ideias mirabolantes em ambientes úteis — preferencialmente sem invocar demônios no `GRUB`.

Este repositório reúne guias **didáticos, reproduzíveis e amigáveis para iniciantes**. A proposta não é apenas entregar uma parede de comandos para copiar e colar: cada roteiro explica **o que será feito, por que aquilo é necessário, como conferir se funcionou e como voltar atrás quando possível**.

Aqui você vai encontrar desde roteiros de instalações de desktop para trabalho e estudo até servidores domésticos, laboratórios de virtualização e casos mais exóticos, como Arch Linux em máquinas cujos discos formam um FakeRAID (também chamado de *firmware RAID* ou *host RAID*, é o RAID configurado no firmware da placa-mãe, mas processado em grande parte pelo computador e pelo sistema operacional).

> [!IMPORTANT]
> Linux dá liberdade. Liberdade inclui a possibilidade de formatar o disco errado com muita eficiência. Leia o roteiro inteiro antes de começar e faça backup dos seus arquivos.

## O que você encontrará por aqui

Os roteiros são organizados por **distribuição**, **objetivo** e **cenário de hardware**. Entre os guias planejados estão:

| Roteiro | Para quem é | Nível | Situação |
|---|---|:---:|:---:|
| Arch Linux em FakeRAID 0 | Máquinas com RAID configurado pela BIOS/UEFI e usuários dispostos a aprender bastante | 👨‍🎓 Avançado | 🚧 Rascunho |
| Ubuntu LTS para desenvolvimento com IA local | Quem quer programar, usar contêineres e executar modelos locais com CPU ou GPU | 🥉 Intermediário | 🚀 Pronto |
| Servidor de arquivos com Samba | Casas e pequenos escritórios com clientes Linux, Windows ou macOS | 🌱 Iniciante | 📝 Planejado |
| Servidor multimídia com Jellyfin | Quem deseja organizar e transmitir sua própria biblioteca de mídia | 🌱 Iniciante | 📝 Planejado |
| Homelab com virtualização e contêineres | Quem quer aprender redes, serviços, VMs e automação em casa | 🥉 Intermediário | 📝 Planejado |

### Legenda de dificuldade

- 🌱 **Iniciante:** explicações passo a passo e pouca experiência prévia necessária.
- 🥉 **Intermediário:** exige alguma familiaridade com terminal, discos, rede ou serviços.
- 👨‍🎓 **Avançado:** envolve riscos maiores, recuperação manual ou hardware incomum. Não significa “proibido para iniciantes”; significa “prepare café e não pule etapas”.

## Qual roteiro combina comigo?

| Quero... | Bom ponto de partida | Por quê? |
|---|---|---|
| Um computador para estudar, programar e experimentar IA | **Ubuntu LTS para IA local** | Oferece uma base previsível, ampla documentação e bom suporte às ferramentas de contêiner e GPU. |
| Compartilhar pastas na rede de casa | **Servidor de arquivos com Samba** | O Samba usa o protocolo SMB e conversa bem com computadores Windows e Linux. |
| Assistir à minha biblioteca de mídia em vários dispositivos | **Servidor multimídia com Jellyfin** | O Jellyfin organiza e transmite mídia por uma interface web e aplicativos clientes. |
| Criar VMs, redes e serviços para aprender | **Homelab** | Permite quebrar ambientes virtuais sem necessariamente quebrar o computador da família. “Necessariamente” é a palavra tranquilizadora. |
| Entender cada peça do sistema | **Arch Linux** | A instalação manual é uma excelente aula prática — e também uma excelente forma de descobrir quantas coisas acontecem antes da tela de login. |
| Manter um servidor simples e estável | **Debian enxuto** | É uma base conservadora e adequada para serviços que não precisam de novidades toda terça-feira. |


## Princípios do projeto

- **Ensinar antes de automatizar:** scripts são úteis, mas o leitor deve saber o que eles alteram.
- **Fontes oficiais primeiro:** documentação da distribuição e do projeto tem prioridade sobre receitas antigas encontradas em fóruns.
- **Comandos verificáveis:** cada etapa importante deve incluir uma forma de conferir o resultado.
- **Segurança por padrão:** nada de senha `admin123`, serviço exposto à internet “só para testar” ou permissão `777` distribuída como confete.
- **Segredos fora do Git:** senhas, tokens, chaves privadas e arquivos `.env` reais não devem entrar no repositório.
- **Caminho de recuperação:** alterações arriscadas devem vir acompanhadas de backup ou instruções de retorno quando isso for possível.
- **Versões explícitas:** o guia deve informar em quais versões foi testado e quando ocorreu o último teste.
- **Respeito ao iniciante:** ninguém nasce sabendo sair do Vim. Aliás, algumas pessoas experientes ainda negociam com ele.
- **Escreva em "brasileiro":** até porque já tem material demais em inglês, mas sinta-se a vontade para traduzir este material para qualquer outro idioma.

## Como contribuir

Contribuições são bem-vindas, inclusive de quem começou ontem. Às vezes, a melhor pessoa para notar uma explicação confusa é justamente quem ainda não decorou todos os atalhos.

1. Procure uma *issue* existente ou abra uma descrevendo o cenário.
2. Informe distribuição, versão, arquitetura e hardware relevante.
3. Crie ou atualize o roteiro seguindo o formato abaixo.
4. Teste em uma máquina virtual ou equipamento que possa ser recuperado.
5. Abra um *pull request* explicando o que foi testado e o que ainda precisa de validação.

## Formato recomendado para cada guia

Ao criar um roteiro, use este cabeçalho:

```markdown
# Nome do roteiro

- Distribuição e versão testada:
- Arquitetura:
- Firmware: BIOS ou UEFI
- Hardware relevante:
- Nível de dificuldade:
- Tempo estimado:
- Data do último teste:
- Resultado esperado:
```

Inclua também:

- uma lista de pré-requisitos;
- avisos antes de comandos destrutivos;
- explicação de variáveis e valores que o leitor precisa substituir;
- saída esperada dos testes mais importantes;
- problemas conhecidos;
- fontes consultadas;
- instruções de atualização e remoção, quando aplicáveis.

Ao relatar um problema, evite apenas “não funciona”. Prefira algo como:

```text
Distribuição: Ubuntu LTS
Arquitetura: amd64
Etapa do guia: instalação do serviço
Comando executado: ...
Resultado esperado: ...
Mensagem de erro: ...
O que já tentei: ...
```

Cole saídas como texto sempre que possível e **remova IPs públicos, nomes de usuário, tokens, chaves e outras informações sensíveis**.

> [!TIP]
> Documentação envelhece. Antes de seguir um roteiro, confira a versão testada e compare os pontos sensíveis com a fonte oficial mais recente.

## Aviso de responsabilidade

Os roteiros são material educacional e podem conter erros ou não cobrir particularidades do seu equipamento. Você é responsável por revisar os comandos e manter backups. Em ambientes com dados importantes, valide primeiro em uma máquina de testes e consulte a documentação oficial.

Se este repositório evitar que alguém execute `chmod -R 777 /` para “resolver rapidinho”, ele já terá prestado um grande serviço à humanidade.

---

**Gostou da proposta?** Acompanhe o projeto, sugira novos cenários e contribua com testes. Quanto mais hardware esquisito for documentado, menos gente precisará descobrir sozinha, às três da manhã, por que o sistema parou no initramfs.
