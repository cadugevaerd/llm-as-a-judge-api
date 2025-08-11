# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

## Project Overview

Este é um projeto de estudo sobre LLM as Judge - um sistema que compara e avalia respostas de diferentes modelos de linguagem. O projeto utiliza LangGraph para criar workflows comparativos entre LLMs.

## Architecture

### Core Components

- **laaj.config**: Configuração centralizada de modelos e API keys
- **laaj.agents**: Factory functions para criar instâncias de LLMs e chains  
- **laaj.workflow**: LangGraph workflow para comparação de LLMs
- **laaj.api**: FastAPI REST API com endpoints para comparação via HTTP
- **laaj.langsmith_integration**: Cliente simplificado para tracing e observabilidade

### LLM Comparison Workflow

O workflow principal (`src/laaj/workflow/workflow.py`) implementa:

1. **Parallel LLM Execution**: Dois nós executam em paralelo (llm_1, llm_2)
2. **Judge Evaluation**: Um terceiro LLM avalia qual resposta é melhor
3. **State Management**: BestResponseState gerencia o estado do workflow

### API Architecture

REST API (`src/laaj/api/`) com estrutura modular:
- **main.py**: Aplicação FastAPI principal com CORS e logging
- **routers/**: Endpoints organizados por funcionalidade (compare, models, health)
- **schemas/**: Pydantic models para request/response (em desenvolvimento)
- **core/**: Utilitários compartilhados (em desenvolvimento)

### Supported Models

Configurados em `laaj.config.LITERAL_MODELS`:
- claude-4-sonnet (Anthropic)
- google-gemini-2.5-pro (Google)

Todos os modelos são acessados via OpenRouter API (openrouter.ai/api/v1) usando ChatOpenAI interface.

## Development Commands

### Environment Setup
```bash
# Instalar dependências
uv sync

# Ativar ambiente virtual
uv shell

# Executar com uv
uv run <script>
```

### Running Code
```bash
# Executar workflow principal
uv run src/laaj/workflow/workflow.py

# Testar agentes individuais
uv run src/laaj/agents/agents.py

# Testar LLMs individuais
uv run src/laaj/agents/llms.py

# Executar API server (desenvolvimento)
uv run uvicorn laaj.api.main:app --reload --port 8000

# Executar API server (produção)  
uv run src/laaj/api/main.py

# Executar Streamlit app (se disponível)
uv run streamlit run src/laaj/app.py

# Teste de tracing
uv run scripts/test_tracing.py
```

### Development Tools
```bash
# Formatação de código
uv run black src/

# Linting
uv run ruff src/

# Testes (quando disponíveis)
uv run pytest tests/

# Instalar dependências de desenvolvimento
uv sync --extra dev
```

## Environment Variables Required

Criar arquivo `.env` na raiz:
```bash
OPENROUTER_API_KEY=your_openrouter_key  # Required - para acessar todos os modelos
LANGSMITH_API_KEY=your_langsmith_key    # Optional, para tracing e observabilidade  
LANGSMITH_PROJECT_NAME=llm-as-judge-study  # Optional, nome do projeto no LangSmith
LANGSMITH_ENDPOINT=https://api.smith.langchain.com  # Optional, endpoint customizado
```

## Project Philosophy

Segue abordagem **Just-in-Time Directory Creation**:
- Diretórios criados apenas quando necessários
- Estrutura evolui organicamente conforme necessidades
- Evita estruturas vazias ou placeholder
- Development usando Task Master AI para gestão de tarefas

## Key Patterns

### LLM Factory Pattern
```python
from laaj.agents import get_llm_anthropic_claude_4_sonnet, get_llm_google_gemini_pro
llm = get_llm_anthropic_claude_4_sonnet()
llm2 = get_llm_google_gemini_pro()
# Judge LLM será configurado quando implementado
```

### Chain Creation Pattern
```python
from laaj.agents import chain_story, chain_laaj
story_chain = chain_story(llm)  # Para gerar histórias
judge_chain = chain_laaj(llm)   # Para avaliar respostas (usa prompt do LangSmith)
```

### Workflow State Management
- Use `BestResponseState` TypedDict para type safety
- Return dicionários diretamente dos nós (não usar Command)
- State é atualizado via merge automático do LangGraph
- Nodes: `llm_1`, `llm_2` (paralelos) → `judge` (avaliação)

### Judge System
- Judge usa prompt "laaj-prompt" do LangSmith
- Retorna `Preference` com valor 1 (modelo A) ou 2 (modelo B)
- Em caso de empate ou erro, retorna "Empate" ou mensagem de erro

### LangSmith Integration
Tracing automático habilitado quando LANGSMITH_API_KEY está disponível:
```python
from laaj.langsmith_integration import LangSmithClient
client = LangSmithClient()  # Auto-configura tracing
```

### FastAPI Structure
```python
# API endpoints disponíveis:
GET  /                           # Info da API
POST /api/v1/compare/            # Comparar LLMs (implementação pendente)
GET  /api/v1/models/             # Listar modelos disponíveis
GET  /api/v1/models/{model_name} # Info de modelo específico
GET  /api/v1/health/             # Health check básico
GET  /api/v1/health/detailed     # Health check detalhado
GET  /docs                       # Swagger UI
```

### API Development Patterns
- Routers modulares em `src/laaj/api/routers/`
- CORS habilitado para desenvolvimento  
- Logging estruturado em cada endpoint
- Pydantic models para validação de request/response
- Endpoint `/docs` sempre disponível para testing

## Current Development Status

### Completed
- ✅ Configuração base do projeto com uv
- ✅ Estrutura modular da API FastAPI 
- ✅ CORS middleware configurado
- ✅ Logging estruturado em todos os endpoints
- ✅ Endpoints básicos: health, models, compare (skeleton)

### Next Priority
- 🔄 Integração do LangGraph workflow com API endpoints
- 🔄 Implementação completa do endpoint `/api/v1/compare/`
- 🔄 Schemas Pydantic para request/response
- 🔄 Conectar workflow de comparação existente com a API
