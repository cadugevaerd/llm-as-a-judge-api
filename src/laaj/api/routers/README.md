# Módulo de Roteadores da API (Routers)

Este módulo contém os roteadores da API FastAPI, que são responsáveis por definir os endpoints da aplicação. Cada arquivo neste diretório corresponde a um grupo de endpoints relacionados.

## Arquivos Principais

- **`__init__.py`**: Expõe os roteadores para que possam ser incluídos na aplicação principal em `main.py`.

- **`compare.py`**: Define os endpoints relacionados à comparação de modelos. Inclui:
    - `POST /`: Para uma única comparação de duas respostas.
    - `POST /batch`: Para comparar múltiplas respostas em uma única requisição.

- **`models.py`**: Define os endpoints para gerenciamento e visualização dos modelos de linguagem disponíveis. Inclui:
    - `GET /`: Lista todos os modelos disponíveis no sistema.
    - `GET /{model_name}`: Fornece informações detalhadas sobre um modelo específico.

- **`health.py`**: Define o endpoint de verificação de saúde da API.
    - `GET /`: Retorna o status de saúde da aplicação, útil para monitoramento e load balancers.

## Design

A estrutura de roteadores modulares permite uma organização limpa e escalável da API. Cada roteador é um `APIRouter` do FastAPI, que é então incluído na aplicação principal com um prefixo de rota, garantindo que os endpoints estejam bem organizados e versionados (ex: `/api/v1/...`).
