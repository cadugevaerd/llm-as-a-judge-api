# 🤖 LLM as Judge - AI Model Comparison System

![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=flat-square&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Native-blue?style=flat-square&logo=kubernetes)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Linux%20ARM64%20%7C%20AMD64-lightgrey?style=flat-square)

Sistema avançado de **comparação e avaliação de modelos de linguagem** usando arquitetura Judge com suporte a múltiplos provedores de LLM. Focado na **comparação de respostas pré-geradas** com deployment production-ready em Docker e Kubernetes.

## 📖 O que faz este sistema

O **LLM as Judge** é uma solução completa para **avaliação objetiva de modelos de IA**:

## ⭐ Características Principais

### 🎯 Inteligência Artificial Avançada
- **Sistema Judge Multi-Modelo** com suporte dinâmico via testes automatizados
- **Comparação Individual e em Lote** com processamento paralelo otimizado
- **Parsing Inteligente** com fallback robusto para interpretação de respostas
- **Estatísticas de Performance** dos modelos em tempo real

### 🛡️ Arquitetura Production-Ready
- **FastAPI** com documentação OpenAPI automática
- **Docker Multi-Arch** (ARM64 + x64) com imagens otimizadas
- **Kubernetes Nativo** com Helm Charts e HPA
- **Health Checks Avançados** com monitoramento detalhado

### 💻 Tecnologias Utilizadas
- **Backend**: FastAPI, Python 3.13, Uvicorn, Pydantic
- **AI/ML**: OpenRouter API, LangSmith, LangChain, Multiple LLM Providers  
- **Deploy**: Docker, Kubernetes, Helm Charts
- **Observability**: Structured logging, LangSmith tracing, Health checks
- **Testing**: Pytest, Model compatibility tests, Stress testing

### 🚀 Funcionalidades
- ⚖️ **Comparação de Respostas** usando modelos judge especializados
- 📊 **Processamento em Lote** com até 5 comparações paralelas
- 🔄 **Multi-Provider Support** via OpenRouter API
- 📈 **Estatísticas Automáticas** de vitórias/empates/erros por modelo
- 🛠️ **Deploy Automatizado** com script Python integrado
- 🔍 **Tracing Completo** via LangSmith para debugging

## 🤔 O que são LLM Judges

**LLM as Judge** é uma metodologia onde um modelo de linguagem especializado avalia e compara respostas de outros LLMs de forma objetiva. Principais características:

- 🎯 **Avaliação Objetiva** - Remove viés humano na comparação
- ⚡ **Escalabilidade** - Processa milhares de comparações rapidamente
- 🏆 **Ranking Automático** - Identifica automaticamente o melhor modelo
- 📋 **Critérios Consistentes** - Aplica os mesmos padrões de qualidade
- 🔄 **Reprodutibilidade** - Resultados consistentes entre execuções

**Casos de uso:**
- Benchmark de modelos para seleção em produção
- A/B testing de diferentes versões de LLMs
- Avaliação de fine-tuning e prompt engineering
- Quality assurance em sistemas de IA

## 📁 Estrutura do Projeto

```
llm-as-judge-study/
├── README.md                           # Este arquivo de documentação
├── src/laaj/                          # Código fonte principal
│   ├── api/                           # FastAPI REST API
│   │   ├── main.py                    # Aplicação principal
│   │   ├── routers/                   # Endpoints da API
│   │   └── schemas/                   # Modelos Pydantic
│   ├── agents/                        # Factory de LLMs e chains
│   ├── config/                        # Configuração centralizada
│   └── workflow/                      # Engine de comparação
├── deploy/                            # Configurações de deployment
│   ├── docker/                        # Docker e Docker Compose
│   │   ├── README.md                  # Guia de deploy Docker
│   │   ├── Dockerfile                 # Imagem ARM64
│   │   ├── Dockerfile-x64             # Imagem x64
│   │   ├── docker-compose.yml         # Compose ARM64
│   │   └── docker-compose-x64.yml     # Compose x64
│   ├── helm/                          # Helm Charts para K8s
│   │   └── llm-judge-api/             # Chart completo
│   │       ├── README.md              # Guia de deploy Kubernetes
│   │       ├── values.yaml            # Configuração padrão
│   │       ├── values-dev.yaml        # Ambiente desenvolvimento
│   │       ├── values-prod.yaml       # Ambiente produção
│   │       └── templates/             # Templates Kubernetes
│   └── troubleshooting.md             # Guia de troubleshooting
├── deploy_helm.py                     # Script automatizado de deploy
├── tests/                             # Testes automatizados
└── requests.ipynb                     # Notebook de testes interativos
```

## 🚀 Como Usar - Início Rápido

### Pré-requisitos

- Python 3.13+ ou Docker
- Chave da API OpenRouter (obrigatória)
- Chaves LangSmith, Anthropic, Mistral (opcionais)

### Setup Local com uv

```bash
# 1. Clonar repositório
git clone https://github.com/cadugevaerd/llm-as-ajudge-study.git
cd llm-as-ajudge-study/

# 2. Configurar ambiente
cp .env.example .env
# Editar .env com suas API keys

# 3. Instalar dependências
uv sync

# 4. Executar API
uv run uvicorn laaj.api.main:app --reload --port 8000
```

### Teste Rápido da API

```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Listar modelos disponíveis
curl http://localhost:8000/api/v1/models/

# Comparação individual
curl -X POST http://localhost:8000/api/v1/compare/ \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Qual a capital do Brasil?",
    "response_a": "A capital do Brasil é Brasília.",
    "response_b": "Brasília é a capital do Brasil desde 1960."
  }'

# Comparação em lote com estatísticas
curl -X POST http://localhost:8000/api/v1/compare/batch \
  -H "Content-Type: application/json" \
  -d '{
    "comparisons": [
      {
        "input": "Pergunta 1",
        "response_a": "Resposta A1",
        "response_b": "Resposta B1"
      },
      {
        "input": "Pergunta 2", 
        "response_a": "Resposta A2",
        "response_b": "Resposta B2"
      }
    ]
  }'
```

### Deploy com Docker

```bash
# ARM64 (Apple Silicon)
docker-compose up -d

# x64 (Intel/AMD)
docker-compose -f docker-compose-x64.yml up -d

# Acesse: http://localhost:8000/docs
```

### Deploy em Kubernetes

```bash
# Deploy automatizado
python deploy_helm.py

# Deploy customizado
python deploy_helm.py --environment production --namespace ai-systems

# Monitoramento
kubectl get pods -l app.kubernetes.io/name=llm-judge-api
kubectl logs -f deployment/llm-judge-api
```

## 📚 Funcionalidades Principais

### ⚖️ Sistema Judge Inteligente
- **Prompt Otimizado** via LangSmith Hub (langchain-ai/pairwise-evaluation-2)
- **Múltiplos Modelos Judge** com fallback automático
- **Parsing Robusto** com interpretação de JSON + texto natural
- **Timeout Configurável** para controle de performance

### 📊 API REST Completa
- **Swagger UI** interativo em `/docs`
- **Comparação Individual** com detalhes do raciocínio
- **Comparação em Lote** com estatísticas agregadas
- **Health Checks** básicos e detalhados
- **Gerenciamento de Modelos** com status em tempo real

### 🔄 Processamento Otimizado
- **Concorrência Controlada** para evitar rate limits
- **Batch Processing** com até 5 comparações paralelas
- **Error Handling** robusto com retry automático
- **Performance Metrics** integradas nas respostas

### 🛡️ Deploy Production-Ready
- **Multi-Arch Support** (ARM64 + x64)
- **Security Best Practices** com non-root containers
- **Health Checks** automáticos
- **Resource Limits** configuráveis
- **Graceful Shutdown** para zero downtime
- **Auto Scaling** com HPA no Kubernetes

## ⚠️ Configurações Importantes

### Variáveis de Ambiente Obrigatórias
```bash
# Obrigatório - OpenRouter para modelos LLM
OPENROUTER_API_KEY=your_openrouter_key_here

# Opcional mas recomendado - LangSmith para tracing
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT_NAME=llm-as-judge-study

# Opcional - Modelos específicos
ANTHROPIC_API_KEY=your_anthropic_key_here  
MISTRAL_API_KEY=your_mistral_key_here

# Configuração da aplicação
WORKFLOW_TIMEOUT_SECONDS=120
LOG_LEVEL=INFO
```

### Limites e Recomendações
- **Batch máximo**: 5 comparações por request
- **Timeout padrão**: 30s individual, 90s batch
- **Rate limits**: Respeitados automaticamente via OpenRouter
- **Modelos testados**: Gerados dinamicamente via testes de compatibilidade

## 📖 Documentação Detalhada

Para informações completas sobre deployment e troubleshooting:

📄 **[Deploy com Docker](deploy/docker/README.md)**  
📄 **[Deploy com Kubernetes](deploy/helm/llm-judge-api/README.md)**  
📄 **[Guia de Troubleshooting](deploy/troubleshooting.md)**

## 🧪 Exemplos de Uso

### Comparação de Respostas de Chatbots
```python
# Avaliar qualidade de diferentes chatbots
response_data = {
    "input": "Como configurar SSL em nginx?",
    "response_a": "Use certbot com Let's Encrypt...",
    "response_b": "Configure manualmente os certificados..."
}
```

### Benchmark de Fine-tuning
```python
# Comparar modelo base vs fine-tuned
comparisons = [
    {
        "input": "Explique machine learning",
        "response_a": modelo_base_response,
        "response_b": modelo_fine_tuned_response
    }
    # ... mais comparações
]
```

### A/B Testing de Prompts
```python
# Testar diferentes estratégias de prompt
for pergunta in dataset:
    resultado = comparar_respostas(
        pergunta,
        prompt_strategy_a(pergunta),
        prompt_strategy_b(pergunta)
    )
```

## 🏗️ Arquitetura da Solução

### Stack Tecnológico
```
┌─────────────────────────────────────────────────┐
│                 Frontend                        │
│   Swagger UI  │  ReDoc  │  Curl/Postman        │
└─────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────┐
│                FastAPI Layer                    │
│  Compare  │  Models  │  Health  │  Batch        │
└─────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────┐
│              Workflow Engine                    │
│    Judge Node  │  State Management              │
└─────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────┐
│               LLM Providers                     │
│  OpenRouter │ Anthropic │ Mistral │ LangSmith   │
└─────────────────────────────────────────────────┘
```

### Fluxo de Comparação
1. **Recepção** - API recebe pergunta + duas respostas
2. **Validação** - Pydantic valida entrada e formata dados
3. **Judge** - Modelo LLM avalia qual resposta é melhor
4. **Parsing** - Sistema extrai resultado (A/B/Empate) de forma robusta
5. **Resposta** - JSON estruturado com resultado e reasoning
6. **Tracing** - LangSmith registra toda a operação (se configurado)

### 🔬 Sistema de Testes de Modelos

Os modelos suportados são **determinados automaticamente** através do sistema de testes `tests/test_judge_models.py`:

#### **Processo Automatizado de Seleção**
1. **Rodada 1**: Teste de compatibilidade com pergunta de complexidade média
2. **Rodada 2**: Apenas modelos aprovados testam pergunta complexa
3. **Geração de Config**: Modelos finalistas são incluídos em `models_config.json`

#### **Critérios de Aprovação**
- ✅ **JSON estruturado válido** com campo `Preference`
- ✅ **Tempo de resposta < 5 segundos**
- ✅ **Consistência de votação** entre as rodadas
- ✅ **Conformidade com formato esperado**

#### **Modelos Testados Atualmente**
```python
# Lista atual em tests/test_judge_models.py (linha 25-45)
MODELS_TO_TEST = [
    "claude-sonnet-4-0",
    "claude-3-5-haiku-latest", 
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "openai/gpt-5",
    "openai/gpt-5-mini",
    "deepseek/deepseek-chat-v3.1",
    "mistral-large-latest",
    "x-ai/grok-4",
    "moonshotai/kimi-k2",
    # ... mais modelos testados automaticamente
]
```

#### **Executar Testes de Compatibilidade**
```bash
# Executar teste completo de duas rodadas
uv run tests/test_judge_models.py

# Resultados salvos em:
# - judge_models_two_rounds_results.json (detalhado)
# - src/laaj/config/models_config.json (config gerada)
```

#### **Relatório Automático**
O sistema gera relatórios detalhados incluindo:
- 🏆 **Ranking de velocidade** dos modelos finalistas
- 📊 **Análise de votação** e consistência
- ⚖️ **Recomendação final** baseada em performance
- 🔧 **Configuração automática** para produção

**Vantagem**: Modelos são validados continuamente e a configuração é atualizada automaticamente conforme novos modelos ficam disponíveis.

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. **Fork** este repositório
2. **Crie uma branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)  
5. **Abra um Pull Request**

### 📝 Guidelines
- Siga as convenções de código Python (Black + Ruff)
- Adicione testes para novas funcionalidades
- Atualize documentação quando necessário
- Mantenha commits semânticos e descritivos

### 🧪 Executando Testes
```bash
# Testes de compatibilidade de modelos
uv run tests/test_judge_models.py

# Testes unitários (quando disponíveis)
uv run pytest tests/

# Testes de stress via notebook
jupyter notebook requests.ipynb
```

### 🐛 Reportando Bugs
- Use as [Issues](../../issues) para reportar bugs
- Inclua detalhes do ambiente (Python, Docker, K8s)
- Anexe logs relevantes da API
- Descreva passos para reproduzir o problema

## 👨‍💻 Autor

**Carlos Araujo** - Engenheiro DevOps & AI/ML  
Especialista em sistemas de IA, automação de infraestrutura e Kubernetes

- 🤖 **Expertise**: LLMs, FastAPI, Docker, Kubernetes, AI/ML Operations
- 🎯 **Foco**: Sistemas de IA production-ready e infraestrutura escalável
- 💼 **GitHub**: [@cadugevaerd](https://github.com/cadugevaerd)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⭐ Apoie o Projeto

Se este projeto foi útil para você, considere:
- ⭐ **Dar uma estrela** no repositório
- 🐛 **Reportar bugs** ou sugerir melhorias
- 🤝 **Contribuir** com código ou documentação
- 📢 **Compartilhar** com outros desenvolvedores de IA
- 💡 **Sugerir novos modelos** ou funcionalidades

## 🔗 Links Úteis

- 📊 **Demo interativa**: http://localhost:8000/docs (após deploy)
- 🔗 **OpenRouter Platform**: https://openrouter.ai/
- 🔍 **LangSmith Tracing**: https://smith.langchain.com/
- 📚 **FastAPI Docs**: https://fastapi.tiangolo.com/
- ⚓ **Docker Hub**: `llm-judge-api:latest`

---

<div align="center">

**Desenvolvido por [Carlos Araujo](https://github.com/cadugevaerd) - Engenheiro DevOps & AI/ML**

*"Automatize a comparação, meça a qualidade, escale com confiança"* 🤖⚖️

</div>