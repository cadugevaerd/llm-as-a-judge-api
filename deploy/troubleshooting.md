# Troubleshooting Guide - LLM as Judge API

Guia completo para diagnóstico e resolução de problemas nos deployments Docker e Kubernetes.

## 🔍 Diagnóstico Geral

### Verificações Básicas

```bash
# Status da aplicação
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/detailed

# Verificar variáveis de ambiente
curl http://localhost:8000/api/v1/models/

# Teste de comparação simples
curl -X POST http://localhost:8000/api/v1/compare/ \
  -H "Content-Type: application/json" \
  -d '{"input":"Teste","response_a":"A","response_b":"B"}'
```

## 🐳 Problemas Docker

### 1. Container não inicia

#### Sintomas
```bash
$ docker-compose up -d
Creating llm-judge-api_llm-judge-api_1 ... error
```

#### Diagnóstico
```bash
# Logs do container
docker-compose logs llm-judge-api

# Logs detalhados
docker-compose logs -f --tail=50 llm-judge-api

# Status dos containers
docker-compose ps
```

#### Possíveis Causas e Soluções

**Porta já em uso:**
```bash
# Verificar quem está usando a porta 8000
lsof -i :8000
netstat -tulpn | grep :8000

# Solução: parar processo ou mudar porta
docker-compose down
# ou editar docker-compose.yml para usar porta diferente
```

**Arquivo .env inexistente:**
```bash
# Verificar se .env existe
ls -la .env

# Criar .env baseado no exemplo
cp .env.example .env
# Editar .env com suas API keys
```

**Problema de permissões:**
```bash
# Verificar permissões dos arquivos
ls -la deploy/docker/

# Corrigir permissões se necessário
chmod +x deploy/docker/Dockerfile*
```

### 2. API retorna erro 500

#### Sintomas
```bash
$ curl http://localhost:8000/api/v1/health/
{"detail":"Internal Server Error"}
```

#### Diagnóstico
```bash
# Logs em tempo real
docker-compose logs -f llm-judge-api

# Executar bash no container
docker-compose exec llm-judge-api bash

# Testar Python dentro do container
docker-compose exec llm-judge-api python -c "from laaj.config import OPENROUTER_API_KEY; print('OK' if OPENROUTER_API_KEY else 'MISSING')"
```

#### Possíveis Causas e Soluções

**API Key inválida:**
```bash
# Testar API key manualmente
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models

# Verificar variáveis de ambiente no container
docker-compose exec llm-judge-api env | grep API_KEY
```

**Dependências não instaladas:**
```bash
# Rebuild sem cache
docker-compose build --no-cache

# Verificar instalação dentro do container
docker-compose exec llm-judge-api uv list
```

### 3. Hot reload não funciona

#### Sintomas
- Mudanças no código não são refletidas automaticamente

#### Soluções
```bash
# Verificar se override existe
cat docker-compose.override.yml

# Criar override para desenvolvimento
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  llm-judge-api:
    volumes:
      - "../../src:/app/src"
    environment:
      - LOG_LEVEL=DEBUG
    command: uvicorn laaj.api.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Restart com override
docker-compose down && docker-compose up -d
```

### 4. Performance lenta

#### Diagnóstico
```bash
# Monitor recursos
docker stats

# Logs de performance
docker-compose logs | grep -i "slow\|timeout\|error"
```

#### Soluções
```bash
# Ajustar recursos no docker-compose.yml
services:
  llm-judge-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'  
          memory: 1G
```

## ☸️ Problemas Kubernetes

### 1. Pod em CrashLoopBackOff

#### Sintomas
```bash
$ kubectl get pods
NAME                            READY   STATUS             RESTARTS   AGE
llm-judge-api-xxx-yyy          0/1     CrashLoopBackOff   5          5m
```

#### Diagnóstico
```bash
# Logs do pod atual
kubectl logs llm-judge-api-xxx-yyy

# Logs do container anterior (se crashou)
kubectl logs llm-judge-api-xxx-yyy --previous

# Describe pod para ver eventos
kubectl describe pod llm-judge-api-xxx-yyy

# Eventos do namespace
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### Possíveis Causas e Soluções

**API Key não configurada:**
```bash
# Verificar se secret existe
kubectl get secret

# Verificar conteúdo do secret
kubectl get secret llm-judge-secrets -o yaml

# Recriar secret
kubectl delete secret llm-judge-secrets
python deploy_helm.py  # Recria com .env atual
```

**Resource limits muito baixos:**
```bash
# Ver resource usage atual
kubectl top pod llm-judge-api-xxx-yyy

# Aumentar limits no values.yaml
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

# Upgrade
helm upgrade llm-judge-api deploy/helm/llm-judge-api/
```

**Imagem não encontrada:**
```bash
# Verificar se imagem existe
kubectl describe pod llm-judge-api-xxx-yyy | grep -i image

# Build e push da imagem
docker build -t llm-judge-api:latest .
docker tag llm-judge-api:latest localhost:30500/llm-judge-api:latest  
docker push localhost:30500/llm-judge-api:latest
```

### 2. Service não responde

#### Sintomas
```bash
$ kubectl port-forward svc/llm-judge-api 8080:8000
# Connection refused ou timeout
```

#### Diagnóstico
```bash
# Verificar service
kubectl get svc llm-judge-api

# Endpoints do service  
kubectl get endpoints llm-judge-api

# Describe service
kubectl describe svc llm-judge-api
```

#### Soluções

**Labels não coincidem:**
```bash
# Verificar labels do deployment
kubectl get deployment llm-judge-api -o yaml | grep -A5 labels

# Verificar selector do service
kubectl get svc llm-judge-api -o yaml | grep -A5 selector

# Devem coincidir - se não, corrigir templates Helm
```

**Porta incorreta:**
```bash
# Verificar porta no deployment
kubectl get deployment llm-judge-api -o yaml | grep containerPort

# Verificar porta no service
kubectl get svc llm-judge-api -o yaml | grep port

# Corrigir values.yaml se necessário
```

### 3. Readiness probe falha

#### Sintomas
```bash
$ kubectl get pods
NAME                            READY   STATUS    RESTARTS   AGE
llm-judge-api-xxx-yyy          0/1     Running   0          2m
```

#### Diagnóstico
```bash
# Ver eventos do pod
kubectl describe pod llm-judge-api-xxx-yyy | grep -A10 Events

# Testar endpoint de health manualmente
kubectl exec -it llm-judge-api-xxx-yyy -- curl localhost:8000/api/v1/health
```

#### Soluções

**Health endpoint não responde:**
```bash
# Aumentar initialDelaySeconds
readinessProbe:
  httpGet:
    path: /api/v1/health
    port: http
  initialDelaySeconds: 30  # Era 5
  periodSeconds: 10
```

**API demora para inicializar:**
```bash
# Verificar logs de startup
kubectl logs llm-judge-api-xxx-yyy | grep -i "started\|ready"

# Ajustar probe delays
livenessProbe:
  initialDelaySeconds: 60
readinessProbe:
  initialDelaySeconds: 30
```

### 4. Ingress não funciona

#### Sintomas
- curl para host retorna 404 ou timeout

#### Diagnóstico
```bash
# Verificar ingress
kubectl get ingress

# Describe ingress
kubectl describe ingress llm-judge-api

# Verificar ingress controller
kubectl get pods -n ingress-nginx
```

#### Soluções

**Host não configurado no /etc/hosts:**
```bash
# Adicionar host local (desenvolvimento)
echo "127.0.0.1 llm-judge-api.local" | sudo tee -a /etc/hosts

# Testar
curl http://llm-judge-api.local/api/v1/health/
```

**Ingress class incorreta:**
```bash
# Verificar classes disponíveis
kubectl get ingressclass

# Atualizar values.yaml
ingress:
  enabled: true
  className: "nginx"  # ou a classe correta
```

### 5. HPA não escala

#### Sintomas
```bash
$ kubectl get hpa
NAME            REFERENCE                  TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
llm-judge-api   Deployment/llm-judge-api   <unknown>/70%   2         10        2          5m
```

#### Diagnóstico
```bash
# Verificar metrics-server
kubectl top nodes
kubectl top pods

# Describe HPA
kubectl describe hpa llm-judge-api
```

#### Soluções

**Metrics-server não instalado:**
```bash
# Instalar metrics-server (k3s, minikube)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Para k3s, pode precisar de flags específicos
```

**Resource requests não definidas:**
```bash
# HPA precisa de requests definidas
resources:
  requests:
    cpu: 250m      # Obrigatório para HPA
    memory: 512Mi
```

## 🧪 Problemas da API

### 1. Timeout em comparações

#### Sintomas
```bash
$ curl -X POST .../compare/ -d '{...}' 
{"detail":"Request timeout"}
```

#### Soluções
```bash
# Aumentar timeout no .env
WORKFLOW_TIMEOUT_SECONDS=180

# Redeploy
docker-compose down && docker-compose up -d
# ou
helm upgrade llm-judge-api deploy/helm/llm-judge-api/
```

### 2. Modelo judge não responde

#### Sintomas
- API retorna erro sobre modelo não disponível

#### Diagnóstico
```bash
# Testar API do OpenRouter diretamente
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models | jq '.data[] | select(.id | contains("llama-4-maverick"))'
```

#### Soluções
```bash
# Verificar modelos disponíveis
curl http://localhost:8000/api/v1/models/

# Testar modelo específico
curl -X POST http://localhost:8000/api/v1/compare/ \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Test", 
    "response_a": "A", 
    "response_b": "B"
  }'
```

### 3. LangSmith tracing não funciona

#### Sintomas
- Logs não mostram tracing ativo
- LangSmith dashboard não recebe dados

#### Soluções
```bash
# Verificar variáveis LangSmith
echo $LANGSMITH_API_KEY
echo $LANGSMITH_PROJECT_NAME

# Testar conectividade
curl -H "x-api-key: $LANGSMITH_API_KEY" \
  https://api.smith.langchain.com/info

# Ativar tracing explicitamente
export LANGSMITH_TRACING=true
```

## 📊 Monitoring e Logs

### Coleta de Logs para Suporte

#### Docker
```bash
# Export all logs
docker-compose logs > debug-docker-$(date +%Y%m%d-%H%M).log

# Com timestamps
docker-compose logs -t > debug-docker-timestamps-$(date +%Y%m%d-%H%M).log
```

#### Kubernetes
```bash
# Export pod logs
kubectl logs deployment/llm-judge-api > debug-k8s-$(date +%Y%m%d-%H%M).log

# Export cluster info
kubectl describe deployment llm-judge-api > debug-deployment-$(date +%Y%m%d-%H%M).txt
kubectl get events --sort-by=.metadata.creationTimestamp > debug-events-$(date +%Y%m%d-%H%M).txt
```

### Debugging Checklist

#### Antes de solicitar ajuda:

1. **Logs coletados** ✅
2. **Configuração testada** ✅
3. **API Keys validadas** ✅
4. **Health checks verificados** ✅
5. **Versões documentadas** ✅

```bash
# Version info
echo "=== ENVIRONMENT INFO ===" > debug-info.txt
date >> debug-info.txt
echo "Docker version:" >> debug-info.txt
docker --version >> debug-info.txt
echo "Docker Compose version:" >> debug-info.txt  
docker-compose --version >> debug-info.txt
echo "Kubernetes version:" >> debug-info.txt
kubectl version --client >> debug-info.txt
echo "Helm version:" >> debug-info.txt
helm version >> debug-info.txt
echo "=======================" >> debug-info.txt
```

---

## 🆘 Recursos de Emergência

### Reset Completo Docker
```bash
docker-compose down -v
docker system prune -a -f
docker-compose build --no-cache
docker-compose up -d
```

### Reset Completo Kubernetes  
```bash
helm uninstall llm-judge-api
kubectl delete secret llm-judge-secrets
kubectl delete configmap llm-judge-api-config
helm install llm-judge-api deploy/helm/llm-judge-api/ \
  --values deploy/helm/llm-judge-api/values-dev.yaml
```

### Contato
- Para problemas críticos, documente: logs, configuração, versões e passos reprodutíveis
- Anexe arquivos debug-*.txt e debug-*.log gerados acima