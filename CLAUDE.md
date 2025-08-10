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
- **laaj.langsmith_integration**: Cliente simplificado para tracing e observabilidade

### LLM Comparison Workflow

O workflow principal (`src/laaj/workflow/workflow.py`) implementa:

1. **Parallel LLM Execution**: Dois nós executam em paralelo (llm_1, llm_2)
2. **Judge Evaluation**: Um terceiro LLM avalia qual resposta é melhor
3. **State Management**: BestResponseState gerencia o estado do workflow

### Supported Models

Configurados em `laaj.config.LITERAL_MODELS`:
- claude-4-sonnet (Anthropic) - via anthropic/claude-sonnet-4
- google-gemini-2.5-pro (Google) - via google/gemini-2.5-pro
- gpt-5-mini (OpenAI) - via openai/gpt-5-mini - usado como juiz padrão
- qwen-3-instruct (Alibaba) - via qwen/qwen3-30b-a3b-instruct-2507

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

# Executar API server
uv run src/laaj/api/main.py
# Ou com uvicorn diretamente
uv run uvicorn laaj.api.main:app --reload --host 0.0.0.0 --port 8000

# Executar Streamlit app (se disponível)
uv run streamlit run src/laaj/app.py

# Teste de tracing
uv run scripts/test_tracing.py
```

### Development Tools
```bash
# Formatação de código
uv run black src/

# Testes
uv run pytest tests/

# Linting
uv run ruff src/
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

Segue abordagem **Just-in-Time Directory Creation** conforme documentado em `DESENVOLVIMENTO.md`:
- Diretórios criados apenas quando necessários
- Estrutura evolui organicamente
- Evita estruturas vazias ou placeholder

## Key Patterns

### LLM Factory Pattern
```python
from laaj.agents import get_llm_anthropic_claude_4_sonnet, get_llm_google_gemini_pro, get_llm_gpt_5, get_llm_qwen_3_instruct
llm = get_llm_anthropic_claude_4_sonnet()
judge_llm = get_llm_gpt_5()  # GPT-5 usado como juiz padrão
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
GET  /                     # Info da API
POST /api/v1/compare       # Comparar LLMs
GET  /api/v1/models        # Listar modelos
GET  /api/v1/health        # Health check
GET  /docs                 # Swagger UI
```
