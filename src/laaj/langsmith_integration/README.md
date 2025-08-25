# Módulo de Integração com LangSmith

Este módulo centraliza a integração com o [LangSmith](https://smith.langchain.com/), a plataforma de observabilidade e tracing da LangChain.

## Arquivos Principais

- **`__init__.py`**: Expõe o `LangSmithClient` para ser facilmente importado e utilizado em outras partes da aplicação.

- **`client.py`**: Implementa a classe `LangSmithClient`, que é um cliente simplificado focado em configurar o ambiente para o tracing automático do LangChain.

## Funcionalidades

- **Configuração Automática de Tracing**: Ao ser instanciado, o `LangSmithClient` verifica a presença de variáveis de ambiente (`LANGSMITH_API_KEY`, `LANGSMITH_PROJECT_NAME`, etc.) e configura automaticamente o ambiente para que todas as execuções de `chains` e LLMs sejam rastreadas no LangSmith.
- **Habilitação/Desabilitação Condicional**: O tracing é habilitado apenas se uma chave de API do LangSmith for encontrada, caso contrário, ele é desabilitado de forma segura, permitindo que a aplicação funcione normalmente sem o tracing.
- **Centralização**: Centraliza a lógica de configuração do LangSmith em um único lugar, tornando o código mais limpo e fácil de manter.

## Como Usar

Para habilitar o tracing em qualquer parte da aplicação, basta criar uma instância do cliente no início do processo:

```python
from laaj.langsmith_integration import LangSmithClient

# Habilita o tracing para o projeto configurado
# (lê as variáveis de ambiente automaticamente)
client = LangSmithClient()
```

Uma vez que o cliente é instanciado, todas as chamadas subsequentes a `chains` e LLMs do LangChain serão automaticamente registradas no projeto correspondente no LangSmith.
