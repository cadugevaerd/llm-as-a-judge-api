# Módulo de Workflow (LangGraph)

Este módulo contém a lógica principal do processo de comparação de LLMs, implementada como um workflow utilizando a biblioteca `LangGraph`.

## Arquivos Principais

- **`__init__.py`**: Arquivo de inicialização do módulo.

- **`workflow.py`**: Define o grafo de execução que orquestra o processo de avaliação. O workflow foi simplificado para focar exclusivamente na **comparação de respostas pré-geradas**.

## Lógica do Workflow

O workflow é composto pelos seguintes passos:

1.  **Estado Inicial (`ComparisonState`)**: O workflow começa com um estado que contém a pergunta original e as duas respostas (A e B) que precisam ser comparadas.

2.  **Nó do Judge (`node_judge`)**: Este é o único nó de processamento principal no grafo. Ele recebe o estado com as respostas, invoca o LLM "judge" (configurado com um prompt específico do LangSmith) e passa as duas respostas para avaliação.

3.  **Parsing da Resposta (`parse_judge_response`)**: A resposta do LLM "judge" é recebida e processada por esta função. Ela é responsável por interpretar a saída do modelo (que pode ser um JSON estruturado ou texto natural) e determinar qual resposta foi a vencedora ("A", "B" ou "Empate"), além de extrair a justificativa do judge.

4.  **Processamento em Lote (`batch_judge_processing`)**: Uma função otimizada que utiliza o método `abatch()` do LangChain para processar múltiplas comparações em paralelo, aumentando significativamente a eficiência para requisições em lote.

5.  **Função Principal (`main`)**: Uma função assíncrona que encapsula a execução do workflow para uma única comparação, aplicando timeouts e tratando exceções para garantir uma execução robusta.

## Principais Características

- **Foco na Avaliação**: Este workflow não gera conteúdo. Seu único propósito é orquestrar a avaliação de respostas que já foram geradas externamente.
- **Robustez**: Inclui tratamento de erros, timeouts e parsing flexível da resposta do judge para lidar com diferentes formatos de saída dos LLMs.
- **Eficiência**: Suporta processamento em lote de forma nativa para lidar com grandes volumes de comparações de forma eficiente.
- **Integração com LangSmith**: O prompt utilizado pelo judge é carregado dinamicamente do LangSmith, permitindo que ele seja atualizado e versionado sem alterações no código.
