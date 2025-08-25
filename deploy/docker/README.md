# Docker Deployment - LLM as Judge API

Este diretório contém os arquivos necessários para deploy da LLM as Judge API usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- Python 3.13+ (para desenvolvimento local)

## 🏗️ Arquitetura

- **Dockerfile**: Imagem otimizada ARM64 com Python 3.13-slim
- **Dockerfile-x64**: Imagem otimizada x64 com Python 3.13-slim  
- **docker-compose.yml**: Configuração para ARM64
- **docker-compose-x64.yml**: Configuração para x64

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
# Obrigatório - OpenRouter API para modelos LLM
OPENROUTER_API_KEY=your_openrouter_key_here

# Opcional - LangSmith para tracing
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT_NAME=llm-as-judge-study
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Opcional - Modelos específicos (se necessário)
ANTHROPIC_API_KEY=your_anthropic_key_here
MISTRAL_API_KEY=your_mistral_key_here

# Configuração da aplicação
WORKFLOW_TIMEOUT_SECONDS=120
LOG_LEVEL=INFO
```

### Exemplo de arquivo .env

Copie e personalize o arquivo de exemplo:

```bash
cp .env.example .env
# Edite o .env com suas chaves de API
```

## 🚀 Deploy

### ARM64 (Apple Silicon, ARM servers)

```bash
# Build e start
docker-compose up -d

# Apenas build
docker-compose build

# Logs em tempo real
docker-compose logs -f

# Stop
docker-compose down
```

### x64 (Intel/AMD)

```bash
# Build e start
docker-compose -f docker-compose-x64.yml up -d

# Apenas build
docker-compose -f docker-compose-x64.yml build

# Logs em tempo real
docker-compose -f docker-compose-x64.yml logs -f

# Stop
docker-compose -f docker-compose-x64.yml down
```

## 🏥 Health Checks

A API possui health checks automáticos configurados:

```bash
# Verificar status do container
docker-compose ps

# Health check manual
curl http://localhost:8000/api/v1/health/

# Health check detalhado
curl http://localhost:8000/api/v1/health/detailed
```

## 📊 Monitoramento

### Logs

```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs apenas da API
docker-compose logs -f llm-judge-api

# Últimas 100 linhas
docker-compose logs --tail=100 llm-judge-api
```

### Métricas

```bash
# Status dos containers
docker-compose ps

# Uso de recursos
docker stats

# Inspecionar container
docker-compose exec llm-judge-api bash
```

## 🛠️ Desenvolvimento

### Hot Reload

Para desenvolvimento com hot reload, use um override:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  llm-judge-api:
    volumes:
      - "../../src:/app/src"  # Mount source code
    environment:
      - LOG_LEVEL=DEBUG
    command: uvicorn laaj.api.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
# Start com hot reload
docker-compose up -d

# Os arquivos em src/ serão recarregados automaticamente
```

### Executar comandos no container

```bash
# Bash interativo
docker-compose exec llm-judge-api bash

# Executar testes
docker-compose exec llm-judge-api uv run pytest

# Verificar modelos disponíveis
docker-compose exec llm-judge-api uv run python -c "from laaj.config import LITERAL_MODELS; print(LITERAL_MODELS)"
```

## 🧪 Teste da API

### Endpoints principais

```bash
# Status da API
curl http://localhost:8000/

# Health check
curl http://localhost:8000/api/v1/health/

# Listar modelos
curl http://localhost:8000/api/v1/models/

# Comparação individual
curl -X POST http://localhost:8000/api/v1/compare/ \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Qual a capital do Brasil?",
    "response_a": "A capital do Brasil é Brasília.",
    "response_b": "Brasília é a capital do Brasil desde 1960."
  }'

# Comparação em lote
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

### Swagger UI

Acesse a documentação interativa:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Manutenção

### Atualização

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

### Limpeza

```bash
# Stop e remove containers
docker-compose down

# Remove containers, networks e volumes
docker-compose down -v

# Remove imagens não utilizadas
docker image prune -f

# Limpeza completa do Docker
docker system prune -a
```

### Backup de Logs

```bash
# Export logs
docker-compose logs > llm-judge-api.log

# Export logs com timestamp
docker-compose logs -t > llm-judge-api-$(date +%Y%m%d).log
```

## 🎯 Performance

### Otimizações implementadas

- **Multi-stage build**: Imagem final otimizada
- **Non-root user**: Segurança aprimorada  
- **Health checks**: Monitoramento automático
- **Resource limits**: Controle de recursos
- **Graceful shutdown**: Encerramento seguro

### Configurações recomendadas

Para produção, ajuste os resources no docker-compose:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.25'
      memory: 512M
```

## 📚 Próximos Passos

1. **Kubernetes**: Para deploy em cluster, veja `../helm/llm-judge-api/README.md`
2. **CI/CD**: Integre com GitHub Actions para deploy automatizado
3. **Monitoring**: Configure Prometheus/Grafana para métricas avançadas
4. **Load Testing**: Teste a capacidade com ferramentas como Apache Bench ou k6

---

Para troubleshooting, consulte [../troubleshooting.md](../troubleshooting.md)