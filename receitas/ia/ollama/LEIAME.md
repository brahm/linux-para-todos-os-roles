# Ollama

## O que faz

Instala o Ollama oficial, baixado das versões publicadas no GitHub e conferido pela soma SHA256 gravada na receita, como um serviço que só este computador acessa. Se você quiser, baixa também o modelo que o `bora` sugere para a máquina, ou outro que você escolher.

## Por que

Com um modelo local, o agente de programação roda sem nuvem: sem conta, sem cota diária, sem pagar em dólar e sem o seu código sair do computador. O preço é a memória: um modelo bom para agentes ocupa de 6 a 20 GB, e sem placa de vídeo ele responde mais devagar que um modelo na nuvem.

Por isso o `bora` mede a máquina antes. O comando `bora modelos` lê a RAM, a memória da placa de vídeo (pelo `nvidia-smi` numa NVIDIA com driver, ou pelo `amdgpu` numa AMD) e o disco livre, e confere cada modelo da lista [`modelos.yaml`](modelos.yaml):

- o modelo ocupa na memória o tamanho dele, mais 15% e mais 1,5 GB para a conversa;
- se isso cabe na placa de vídeo, ele roda rápido;
- se não cabe, ele usa a RAM, deixando 3 GB para o sistema, o editor e o navegador. Aí a velocidade depende de quantos parâmetros o modelo usa a cada palavra. Os modelos "mixture of experts", como o `gpt-oss:20b` e o `qwen3-coder:30b`, usam só 3 ou 4 bilhões por vez e andam bem até sem placa de vídeo; um modelo denso de 27 bilhões, não.

A sugestão é o modelo mais capaz que roda bem e dá conta de ser agente (usar ferramentas, ler arquivos, rodar comandos). Se nenhum desses cabe, o `bora` sugere um agente que roda devagar; se nem isso, um modelo pequeno, só para conversar; e, numa máquina de 4 GB, nenhum.

No plano, `modelo: sugerido` vira o nome do modelo escolhido, e o tamanho do download aparece antes de você aceitar. Com `modelo: nenhum`, a receita instala só o Ollama, e você baixa o que quiser com `ollama pull`.

O instalador oficial do Ollama é um script que se baixa e entrega direto ao shell, e o projeto não roda scripts assim. A receita faz o que ele faz, com o arquivo conferido: abre o Ollama em `/opt/ollama`, cria a conta de serviço `ollama` e o serviço do systemd. O serviço escuta só em `127.0.0.1:11434`, então nenhum outro computador da rede fala com ele. Para servir os modelos para a casa, isso vira outro rolê, com o firewall.

A versão instalada não se atualiza sozinha. Quando o `bora` trouxer uma versão nova, aplique a receita de novo.

## O que muda no sistema

- Instala `curl`, `zstd` e `ca-certificates`, se faltarem.
- Baixa `ollama-linux-amd64.tar.zst` de `https://github.com/ollama/ollama/releases`, confere a soma SHA256 e abre em `/opt/ollama/<versão>`. Numa placa AMD com memória própria, baixa e confere também `ollama-linux-amd64-rocm.tar.zst`. As bibliotecas para placas NVIDIA já vêm no arquivo principal; o driver da placa, não.
- Cria o link `/usr/local/bin/ollama`. Se já existir um Ollama instalado de outro jeito, a receita para sem mudar nada.
- Cria a conta de sistema `ollama`, com a pasta `/usr/share/ollama`, onde ficam os modelos (`.ollama/models`), e põe a conta nos grupos `render` e `video`, para usar a placa de vídeo.
- Escreve `/etc/systemd/system/ollama.service`, com `OLLAMA_HOST=127.0.0.1:11434`, e habilita o serviço. O serviço roda sem poder ganhar privilégios e só escreve na própria pasta.
- Com um modelo escolhido, roda `ollama pull` com ele.

## Como conferir

O `testar.sh` confere:

- `ollama --version`, que precisa mostrar a versão da receita;
- que o serviço está habilitado e configurado para atender só `127.0.0.1`;
- com o systemd rodando, que o serviço responde em `http://127.0.0.1:11434` e que nenhuma porta `11434` está aberta para a rede (`ss -ltn`);
- que a pasta dos modelos é da conta `ollama`;
- com um modelo escolhido, que ele aparece no `ollama list`.

Para usar:

```sh
bora modelos                  # os modelos que cabem nesta máquina
ollama run qwen3:4b           # conversa no terminal
ollama launch opencode        # o OpenCode usando o modelo local (também: claude, codex)
```

Agentes de programação pedem um contexto longo, de 32 a 64 mil tokens, e o contexto também ocupa memória. O `ollama launch` já configura o agente; para mudar o contexto do serviço, crie `/etc/systemd/system/ollama.service.d/contexto.conf` com `[Service]` e `Environment=OLLAMA_CONTEXT_LENGTH=32768`.

## Como desfazer

O `desfazer.sh` para e desabilita o serviço, apaga o arquivo dele, o link `/usr/local/bin/ollama` e a pasta `/opt/ollama/<versão>`, e remove os pacotes que a receita instalou. A conta `ollama` sai com a pasta `/usr/share/ollama`, e **os modelos baixados vão junto**, inclusive os que você baixou depois com `ollama pull`. Para guardar um modelo, copie `/usr/share/ollama/.ollama/models` antes.

## Fontes

- [Ollama no Linux: instalação manual](https://docs.ollama.com/linux)
- [Versões do Ollama, com o sha256sum.txt](https://github.com/ollama/ollama/releases)
- [Biblioteca de modelos do Ollama](https://ollama.com/library)
- [Ollama com o Codex](https://docs.ollama.com/integrations/codex) e [compatibilidade com a API da Anthropic](https://docs.ollama.com/api/anthropic-compatibility)
- [Perguntas frequentes do Ollama: contexto e endereço do servidor](https://docs.ollama.com/faq)
