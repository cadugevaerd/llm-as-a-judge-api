# Multi-stage build para otimização
FROM python:3.13-slim as builder

# Instalar uv para gerenciamento de dependências
RUN pip install --no-cache-dir uv

# Configurar diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração
COPY pyproject.toml uv.lock ./

# Instalar dependências
RUN uv sync --frozen --no-dev

# Stage de produção
FROM python:3.13-slim

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar uv
RUN pip install --no-cache-dir uv

# Configurar diretório de trabalho
WORKDIR /app

# Copiar ambiente virtual do builder
COPY --from=builder /app/.venv /app/.venv

# Copiar código fonte
COPY src/ ./src/

# Configurar PATH para usar o ambiente virtual
ENV PATH="/app/.venv/bin:$PATH"

# Configurar usuário não-root
RUN chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Comando de inicialização
CMD ["uvicorn", "laaj.api.main:app", "--host", "0.0.0.0", "--port", "8000"]