# Módulo de Configuração (Config)

Este módulo é o centro nevrálgico para todas as configurações do projeto "LLM as a Judge". Ele foi projetado para ser flexível e robusto, combinando configurações estáticas e dinâmicas.

## Arquivos Principais

- **`__init__.py`**: Serve como a fachada do módulo, exportando as configurações mais importantes e utilitários para o resto da aplicação. Ele decide se deve usar a configuração dinâmica do JSON ou o fallback estático.

- **`config.py`**: Contém as configurações estáticas e essenciais do projeto. Ele é responsável por carregar variáveis de ambiente de um arquivo `.env` (como chaves de API) e definir constantes que raramente mudam, como a lista de modelos de fallback (`LITERAL_MODELS`) e o nome do prompt no LangSmith (`PROMPT_LAAJ`).

- **`models_loader.py`**: Este é o coração do sistema de configuração dinâmica. Ele implementa a classe `ModelsLoader` (como um singleton) que é responsável por:
    - Carregar e validar o arquivo `models_config.json`.
    - Fazer o cache da configuração para melhor performance.
    - Fornecer uma interface para acessar a lista de modelos, o modelo padrão, e as configurações de provedores.
    - Implementar um sistema de fallback caso o arquivo JSON não esteja disponível.
    - Realizar health checks para garantir a integridade da configuração.

## Sistema de Configuração Dinâmica

A principal característica deste módulo é o `models_loader.py`, que permite que a lista de modelos de LLM e suas configurações sejam gerenciadas externamente através de um arquivo `models_config.json`.

**Vantagens:**
- **Flexibilidade**: Novos modelos podem ser adicionados ou removidos apenas modificando o JSON, sem necessidade de alterar o código Python.
- **Performance-driven**: O arquivo JSON é gerado a partir de testes de performance, garantindo que os modelos listados e o modelo padrão sejam escolhidos com base em dados reais.
- **Robustez**: Se o arquivo JSON estiver ausente ou for inválido, o sistema automaticamente utiliza as configurações de fallback definidas em `config.py`, garantindo que a aplicação continue funcionando.
