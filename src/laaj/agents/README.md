# Módulo de Agentes (Agents)

Este módulo é responsável por criar e gerenciar as instâncias de Modelos de Linguagem (LLMs) e as `chains` do LangChain que formam o núcleo do sistema de avaliação.

## Arquivos Principais

- **`__init__.py`**: Expõe os componentes essenciais do módulo, como a `LLMFactory` e a `chain_laaj`, para fácil importação em outras partes do projeto.

- **`agents.py`**: Define a `chain` principal do "judge". Esta chain é responsável por receber duas respostas e uma pergunta, e então usar um LLM para determinar qual das respostas é a melhor. O prompt para esta chain é puxado diretamente do LangSmith Hub.

- **`llm_factory.py`**: Implementa o padrão de design "Factory" para a criação de instâncias de LLM. A factory é dinâmica, carregando configurações de um arquivo `models_config.json`. Isso permite que novos modelos sejam adicionados e configurados sem a necessidade de alterar o código. A factory também possui um sistema de fallback para garantir a funcionalidade mesmo que o arquivo de configuração não esteja presente.

- **`llms.py`**: Contém as funções de criação de LLMs para múltiplos provedores (Anthropic, OpenRouter, Mistral, etc.). Este módulo foi refatorado para suportar a criação dinâmica de LLMs com base na configuração do `models_config.json`, mantendo funções de fallback para compatibilidade com o sistema legado.

## Como Funciona

1.  A `LLMFactory` é a porta de entrada para a criação de qualquer LLM no sistema.
2.  Ela lê o arquivo `models_config.json` para descobrir quais modelos estão disponíveis e como devem ser configurados (provedor, parâmetros, etc.).
3.  Quando uma instância de LLM é solicitada, a factory utiliza as funções em `llms.py` para criar o objeto `ChatOpenAI`, `ChatAnthropic`, etc., com as configurações corretas.
4.  A `chain_laaj` em `agents.py` recebe uma instância de LLM (criada pela factory) e a combina com um prompt do LangSmith para criar o agente "judge" final.
