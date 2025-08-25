# Módulo de Schemas da API (Pydantic)

Este módulo define os modelos de dados da API utilizando a biblioteca Pydantic. Estes modelos são usados para validação de dados de requisição, serialização de dados de resposta e geração automática da documentação da API (Swagger/OpenAPI).

## Arquivos Principais

- **`__init__.py`**: Expõe os principais schemas para fácil acesso em outros módulos.

- **`compare.py`**: Contém os schemas para os endpoints de comparação:
    - `CompareRequest`: Define a estrutura esperada para uma requisição de comparação individual.
    - `ComparisonResponse`: Define a estrutura da resposta para uma comparação individual.
    - `BatchCompareRequest`: Define a estrutura para uma requisição de comparação em lote.
    - `BatchComparisonResponse`: Define a estrutura da resposta para uma comparação em lote, incluindo estatísticas agregadas.

- **`models.py`**: Contém os schemas para os endpoints de modelos:
    - `ModelDetailedInfo`: Define a estrutura para a resposta que fornece informações detalhadas sobre um modelo.
    - `ModelsListResponse`: Define a estrutura para a resposta que lista todos os modelos disponíveis.

## Benefícios

- **Validação de Dados**: O Pydantic garante que todos os dados recebidos pela API correspondam ao schema definido, retornando erros claros em caso de falha.
- **Documentação Automática**: Estes schemas são a base para a documentação interativa gerada pelo FastAPI, tornando a API fácil de entender e usar.
- **Type Hinting e Autocomplete**: O uso de Pydantic melhora a experiência de desenvolvimento com type hints claros e autocomplete no editor de código.
