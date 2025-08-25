# Helm Chart - LLM as Judge API

Chart do Helm para deploy da LLM as Judge API em clusters Kubernetes.

## 📋 Pré-requisitos

- Kubernetes 1.25+
- Helm 3.8+
- Cluster configurado com kubectl
- Registry de imagens (local ou remoto)

## 🏗️ Arquitetura do Chart

```
llm-judge-api/
├── Chart.yaml              # Metadados do chart
├── values.yaml             # Configuração padrão
├── values-dev.yaml         # Configuração desenvolvimento  
├── values-prod.yaml        # Configuração produção
└── templates/
    ├── deployment.yaml     # Deployment da aplicação
    ├── service.yaml        # Service interno
    ├── configmap.yaml      # ConfigMap para variáveis não-secretas
    ├── secret.yaml         # Secret para API keys
    ├── ingress.yaml        # Ingress para acesso externo
    ├── hpa.yaml           # Horizontal Pod Autoscaler
    └── _helpers.tpl       # Templates auxiliares
```

## ⚙️ Configuração

### Variáveis de Ambiente Obrigatórias

Configure essas variáveis no arquivo `.env` da raiz do projeto:

```bash
# Obrigatório
OPENROUTER_API_KEY=your_openrouter_key_here

# Opcional mas recomendado
LANGSMITH_API_KEY=your_langsmith_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  
MISTRAL_API_KEY=your_mistral_key_here
```

### Customização via Values

#### values.yaml (Padrão)
```yaml
replicaCount: 1

image:
  repository: llm-judge-api
  tag: "latest"
  pullPolicy: IfNotPresent

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

# Environment variables
env:
  WORKFLOW_TIMEOUT_SECONDS: "120"
  LOG_LEVEL: "INFO"
  LANGSMITH_PROJECT_NAME: "llm-as-judge-study"

# Secrets (configuradas via .env)
secrets:
  OPENROUTER_API_KEY: ""    # Preenchida pelo script
  LANGSMITH_API_KEY: ""
  ANTHROPIC_API_KEY: ""
  MISTRAL_API_KEY: ""
```

#### values-dev.yaml (Desenvolvimento)
```yaml
replicaCount: 1

env:
  LOG_LEVEL: "DEBUG"
  
resources:
  limits:
    cpu: 200m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  hosts:
    - host: llm-judge-api.local
```

#### values-prod.yaml (Produção)
```yaml
replicaCount: 3

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
```

## 🚀 Deploy

### Método 1: Script Automatizado (Recomendado)

Use o script `deploy_helm.py` na raiz do projeto:

```bash
# Deploy development
python deploy_helm.py

# Deploy production
python deploy_helm.py --environment production

# Deploy custom
python deploy_helm.py --namespace my-namespace --release-name my-api
```

### Método 2: Comandos Helm Manuais

#### Desenvolvimento

```bash
# Lint do chart
helm lint deploy/helm/llm-judge-api/

# Dry run
helm install llm-judge-api deploy/helm/llm-judge-api/ \
  --dry-run \
  --debug \
  --values deploy/helm/llm-judge-api/values-dev.yaml

# Install
helm install llm-judge-api deploy/helm/llm-judge-api/ \
  --values deploy/helm/llm-judge-api/values-dev.yaml \
  --set secrets.OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  --set secrets.LANGSMITH_API_KEY="$LANGSMITH_API_KEY"
```

#### Produção

```bash
# Install production
helm install llm-judge-api deploy/helm/llm-judge-api/ \
  --values deploy/helm/llm-judge-api/values-prod.yaml \
  --set secrets.OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  --set secrets.LANGSMITH_API_KEY="$LANGSMITH_API_KEY" \
  --set secrets.ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --set secrets.MISTRAL_API_KEY="$MISTRAL_API_KEY" \
  --namespace production \
  --create-namespace
```

## 🔄 Gerenciamento

### Status do Deployment

```bash
# Status do Helm release
helm status llm-judge-api

# History
helm history llm-judge-api

# Listar releases
helm list
```

### Monitoramento com kubectl

```bash
# Pods
kubectl get pods -l app.kubernetes.io/name=llm-judge-api

# Logs
kubectl logs -f deployment/llm-judge-api

# Logs de pod específico
kubectl logs -f pod/llm-judge-api-xxx-yyy

# Describe deployment
kubectl describe deployment llm-judge-api

# Services
kubectl get svc

# ConfigMap e Secrets
kubectl get configmap
kubectl get secret
```

### Health Checks

```bash
# Port forward para teste local
kubectl port-forward svc/llm-judge-api 8080:8000

# Teste em outro terminal
curl http://localhost:8080/api/v1/health/
curl http://localhost:8080/api/v1/health/detailed
```

## 🔄 Atualizações

### Upgrade do Chart

```bash
# Upgrade with new values
helm upgrade llm-judge-api deploy/helm/llm-judge-api/ \
  --values deploy/helm/llm-judge-api/values-dev.yaml

# Upgrade com nova imagem
helm upgrade llm-judge-api deploy/helm/llm-judge-api/ \
  --set image.tag=v1.2.0

# Upgrade com script
python deploy_helm.py --upgrade
```

### Rollback

```bash
# Rollback para versão anterior
helm rollback llm-judge-api

# Rollback para revisão específica
helm rollback llm-judge-api 2

# Ver histórico
helm history llm-judge-api
```

## 📈 Scaling

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment llm-judge-api --replicas=5

# Via Helm
helm upgrade llm-judge-api deploy/helm/llm-judge-api/ \
  --set replicaCount=5
```

### Auto Scaling (HPA)

```bash
# Habilitar HPA via values
helm upgrade llm-judge-api deploy/helm/llm-judge-api/ \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10

# Verificar HPA
kubectl get hpa
kubectl describe hpa llm-judge-api
```

## 🌐 Ingress

### Configuração básica

```yaml
# values.yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
```

### Teste do Ingress

```bash
# Verificar ingress
kubectl get ingress

# Teste
curl http://api.example.com/api/v1/health/
```

## 🗑️ Remoção

```bash
# Uninstall release
helm uninstall llm-judge-api

# Remover namespace (se criado)
kubectl delete namespace production

# Limpeza completa
helm uninstall llm-judge-api
kubectl delete pvc --all
kubectl delete pv --all  # Cuidado: remove todos os PVs
```

## 🔐 Secrets Management

### Via kubectl

```bash
# Criar secret manualmente
kubectl create secret generic llm-judge-secrets \
  --from-literal=OPENROUTER_API_KEY="your_key_here" \
  --from-literal=LANGSMITH_API_KEY="your_key_here"

# Verificar secrets
kubectl get secret llm-judge-secrets -o yaml
```

### Via External Secrets (Produção)

Para produção, considere usar External Secrets Operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
---
apiVersion: external-secrets.io/v1beta1  
kind: ExternalSecret
metadata:
  name: llm-judge-secrets
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: llm-judge-secrets
  data:
    - secretKey: OPENROUTER_API_KEY
      remoteRef:
        key: llm-judge-api
        property: openrouter_api_key
```

## 🎯 Performance Tuning

### Resource Requests/Limits

```yaml
resources:
  limits:
    cpu: 1000m        # Máximo 1 CPU
    memory: 2Gi       # Máximo 2GB RAM
  requests:
    cpu: 500m         # Garantido 0.5 CPU
    memory: 1Gi       # Garantido 1GB RAM
```

### Readiness/Liveness Probes

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/health
    port: http  
  initialDelaySeconds: 5
  periodSeconds: 5
```

## 📊 Observabilidade

### Logs

```bash
# Logs agregados
kubectl logs -f deployment/llm-judge-api

# Logs de múltiplos pods
kubectl logs -f -l app.kubernetes.io/name=llm-judge-api

# Logs com timestamp
kubectl logs --timestamps -f deployment/llm-judge-api
```

### Métricas

```bash
# Resource usage
kubectl top pods
kubectl top nodes

# Eventos
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 🛠️ Development Workflow

### Local Development com Cluster

```bash
# Port forward para desenvolvimento
kubectl port-forward svc/llm-judge-api 8000:8000

# Hot reload (se configurado)
kubectl patch deployment llm-judge-api -p '{"spec":{"template":{"metadata":{"annotations":{"date":"'$(date +'%s')'"}}}}}'
```

### CI/CD Integration

Exemplo para GitHub Actions:

```yaml
- name: Deploy to K8s
  run: |
    python deploy_helm.py --environment production
    kubectl rollout status deployment/llm-judge-api
```

---

Para troubleshooting detalhado, consulte [../../troubleshooting.md](../../troubleshooting.md)