# Módulo da API (FastAPI)

Este módulo contém a aplicação web FastAPI que expõe a funcionalidade do sistema "LLM as a Judge" através de uma API RESTful.

## Estrutura

- **`main.py`**: É o ponto de entrada da aplicação FastAPI. Ele inicializa a aplicação, configura middlewares (como o CORS), e inclui os roteadores dos diferentes endpoints.
- **`/routers`**: Este subdiretório contém os diferentes roteadores da API, organizados por funcionalidade.
    - **`compare.py`**: Define os endpoints `/api/v1/compare` para comparações individuais e em lote de respostas de LLMs.
    - **`models.py`**: Define os endpoints `/api/v1/models` para listar os modelos disponíveis e obter informações detalhadas sobre um modelo específico.
    - **`health.py`**: Define o endpoint `/api/v1/health` para verificações de saúde da API.
- **`/schemas`**: Este subdiretório contém os modelos Pydantic que definem os schemas de dados para as requisições e respostas da API, garantindo a validação e a documentação automática.
    - **`compare.py`**: Schemas para as requisições e respostas dos endpoints de comparação.
    - **`models.py`**: Schemas para as respostas dos endpoints de modelos.

## Endpoints Principais

- **`POST /api/v1/compare/`**: Recebe uma pergunta e duas respostas, e utiliza o workflow de "judge" para avaliar qual é a melhor.
- **`POST /api/v1/compare/batch`**: Permite enviar múltiplas comparações em uma única requisição para processamento em lote.
- **`GET /api/v1/models/`**: Retorna uma lista de todos os modelos de linguagem disponíveis para serem usados como "judge".
- **`GET /api/v1/models/{model_name}`**: Retorna informações detalhadas sobre um modelo específico.
- **`GET /api/v1/health/`**: Endpoint para monitoramento da saúde da aplicação.
- **`GET /docs`**: A interface do Swagger UI para documentação interativa da API.
