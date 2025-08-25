# Pacote `laaj`

Este é o pacote principal do projeto "LLM as a Judge" (laaj).

## Estrutura de Módulos

O pacote `laaj` é organizado nos seguintes submódulos:

- **`/agents`**: Contém a lógica para a criação de instâncias de LLMs e `chains` do LangChain. É o coração da interação com os modelos de linguagem.

- **`/api`**: Implementa a interface da API RESTful utilizando FastAPI. Este módulo expõe a funcionalidade do sistema para o mundo exterior.

- **`/config`**: Centraliza todas as configurações do projeto, desde chaves de API até a configuração dinâmica de modelos carregada de um arquivo JSON.

- **`/langsmith_integration`**: Gerencia a integração com o LangSmith para tracing e observabilidade, permitindo o monitoramento e depuração das execuções.

- **`/workflow`**: Define o workflow de comparação de LLMs utilizando `LangGraph`. Orquestra a lógica de avaliação, desde a recepção das respostas até o veredito do "judge".

- **`app.py`**: (Se aplicável) Ponto de entrada para uma aplicação de interface de usuário, como um aplicativo Streamlit.
