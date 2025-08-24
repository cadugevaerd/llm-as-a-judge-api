# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

## Project Overview

Este é um projeto de estudo sobre **LLM as Judge** - um sistema simplificado que compara e avalia respostas pré-geradas de diferentes modelos de linguagem usando um modelo judge. O sistema foi redesenhado para trabalhar APENAS com respostas já existentes, focando na comparação e avaliação.

## Architecture

### Core Components

- **laaj.config**: Configuração centralizada de modelos (Claude, Gemini) via OpenRouter API
- **laaj.agents**: 
  - Factory functions simplificadas para criar instâncias de LLMs judge
  - `chain_laaj()`: Única chain necessária para avaliação usando prompt do LangSmith
- **laaj.workflow**: Workflow simplificado contendo apenas o nó `judge` para comparação
- **laaj.api**: FastAPI REST API com endpoint `/api/v1/compare/` para comparação via HTTP
- **laaj.langsmith_integration**: Cliente para tracing e observabilidade

### Simplified Workflow Architecture

O workflow atual (`src/laaj/workflow/workflow.py`) implementa arquitetura simplificada:

1. **Input**: Pergunta + duas respostas pré-geradas (response_a, response_b)
2. **Judge Node**: Único nó que usa modelo judge para comparar as respostas
3. **Output**: Resultado da comparação ("A", "B", "Empate" ou erro)

**Estado**: `ComparisonState` contém apenas input, response_a, response_b e resultado do judge.

### Judge System Details

- **Prompt**: Usa "laaj-prompt" do LangSmith Hub
- **Modelos suportados**: Claude 4 Sonnet (principal), Gemini 2.5 Pro, GPT-5, Qwen 3
- **Output parsing**: Suporta JSON estruturado e texto natural
- **Fallback**: Sistema robusto de interpretação quando JSON falha
- **Timeout**: 30 segundos por comparação

### API Architecture

REST API (`src/laaj/api/`) implementada e funcional:
- **main.py**: FastAPI app com CORS habilitado para desenvolvimento
- **routers/compare.py**: Endpoint POST `/api/v1/compare/` integrado com workflow
- **schemas/compare.py**: Pydantic models `CompareRequest` e `ComparisonResponse`
- **routers/health.py**: Health checks básicos e detalhados
- **routers/models.py**: Lista de modelos disponíveis

### Supported Models

Configurados via OpenRouter API em `laaj.config.LITERAL_MODELS`:
- `claude-4-sonnet` - Anthropic Claude (modelo judge principal)
- `google-gemini-2.5-pro` - Google Gemini (alternativo)

Modelos adicionais disponíveis via factory functions:
- `gpt-5-mini` - OpenAI GPT-5
- `qwen3-30b-a3b-instruct-2507` - Qwen 3 Instruct

## Development Commands

### Environment Setup
```bash
# Instalar dependências
uv sync

# Instalar dependências de desenvolvimento
uv sync --extra dev

# Ativar ambiente virtual
uv shell
```

### Running Code
```bash
# Executar workflow standalone (teste com respostas exemplo)
uv run src/laaj/workflow/workflow.py

# Executar API server (desenvolvimento com reload)
uv run uvicorn laaj.api.main:app --reload --port 8000

# Executar API server (produção)  
uv run src/laaj/api/main.py

# Testar LLMs individuais
uv run src/laaj/agents/llms.py

# Teste de tracing LangSmith
uv run scripts/test_tracing.py

# Executar Streamlit app (se disponível)
uv run streamlit run src/laaj/app.py
```

### Development Tools
```bash
# Formatação de código (Black)
uv run black src/

# Linting (Ruff)
uv run ruff src/

# Testes (pytest - quando disponíveis)
uv run pytest tests/
```

### Testing API Endpoints
```bash
# Testar API manualmente
curl -X POST "http://localhost:8000/api/v1/compare/" \
     -H "Content-Type: application/json" \
     -d '{
       "input": "Qual a capital do Brasil?",
       "response_a": "A capital do Brasil é Brasília.",
       "response_b": "Brasília é a capital do Brasil desde 1960."
     }'

# Health check
curl http://localhost:8000/api/v1/health/

# Swagger UI disponível em
http://localhost:8000/docs
```

## Environment Variables Required

Criar arquivo `.env` na raiz:
```bash
# Required - OpenRouter API para todos os modelos
OPENROUTER_API_KEY=your_openrouter_key

# Optional - LangSmith para tracing e prompt hub
LANGSMITH_API_KEY=your_langsmith_key    
LANGSMITH_PROJECT_NAME=llm-as-judge-study
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Optional - Workflow timeout (default: 120s)
WORKFLOW_TIMEOUT_SECONDS=120
```

## Key Patterns

### LLM Judge Factory Pattern
```python
from laaj.agents.llms import get_llm_anthropic_claude_4_sonnet
from laaj.agents import chain_laaj

# Criar instância do judge
judge_llm = get_llm_anthropic_claude_4_sonnet()
judge_chain = chain_laaj(judge_llm)  # Chain com prompt do LangSmith
```

### Workflow Usage Pattern
```python
from laaj.workflow.workflow import main as workflow_main

# Comparar duas respostas pré-geradas
result = await workflow_main(
    input_question="Qual a capital do Brasil?",
    response_a="A capital do Brasil é Brasília.",
    response_b="Brasília é a capital desde 1960.",
    model_a_name="claude-4-sonnet",  # opcional
    model_b_name="gemini-2.5-pro",  # opcional
    timeout_seconds=30
)
```

### API Request Pattern
```python
# CompareRequest schema
{
    "input": str,           # Pergunta/contexto original
    "response_a": str,      # Resposta A (obrigatória)
    "response_b": str,      # Resposta B (obrigatória)
    "model_a_name": str,    # Nome modelo A (opcional)
    "model_b_name": str     # Nome modelo B (opcional)
}

# ComparisonResponse schema
{
    "input": str,
    "response_a": str,
    "response_b": str,
    "model_a_name": str,
    "model_b_name": str,
    "better_response": str,      # "A", "B", "Empate", ou erro
    "judge_reasoning": str,      # Explicação do judge
    "execution_time": float      # Tempo de execução
}
```

### Error Handling Pattern
- **Timeout**: Retorna `"TIMEOUT - Excedeu Xs"` em better_response
- **Validation**: Retorna `"ERRO - Validação falhou"` para inputs inválidos  
- **LLM Error**: Retorna `"ERRO - Modelo judge não disponível"`
- **Parse Error**: Sistema de fallback tenta extrair resultado do texto

## Project Structure Insights

### Module Organization
```
src/laaj/
├── config/          # Configuração centralizada de API keys e modelos
├── agents/          # LLM factories e chain creation 
├── workflow/        # Workflow simplificado (apenas judge)
├── api/            # FastAPI app com routers modulares
└── langsmith_integration/  # Cliente LangSmith
```

### State Management
- **ComparisonState**: TypedDict com campos mínimos necessários
- **Stateless**: Cada comparação é independente, sem persistência
- **Async**: Workflow totalmente assíncrono com timeout control

### LangSmith Integration
- **Automatic tracing**: Habilitado automaticamente quando LANGSMITH_API_KEY presente
- **Prompt management**: Judge usa prompt "laaj-prompt" do hub
- **Project tracking**: Traces organizados por LANGSMITH_PROJECT_NAME

## Current Development Status

### ✅ Completed
- Workflow simplificado funcionando (apenas judge)
- API FastAPI totalmente integrada com workflow
- Schemas Pydantic implementados e validados
- Sistema robusto de error handling e timeout
- LLM factory functions para múltiplos modelos
- LangSmith integration para tracing

### 🔄 Current Focus
Sistema está funcional e pronto para uso. Próximas melhorias dependem de requisitos específicos.