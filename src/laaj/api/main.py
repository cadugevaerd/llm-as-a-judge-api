"""
FastAPI main application entry point simplificado para LLM as Judge API.

API simplificada focada no core da aplicação:
- Comparação de respostas pré-geradas (individual e batch)
- Gerenciamento básico de modelos LLM
- Health checks essenciais
- Documentação OpenAPI otimizada
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from laaj.api.routers import compare, models, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("laaj.api.main")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan event handler para startup e shutdown."""
    # Startup
    logger.info("🚀 [MAIN API] Iniciando LLM as Judge API")
    logger.info("🏥 [MAIN API] Sistema de health checks ativo")
    
    yield
    
    # Shutdown
    logger.info("🛑 [MAIN API] Encerrando LLM as Judge API")
    logger.info("💾 [MAIN API] Limpeza de recursos concluída")


app = FastAPI(
    title="LLM as a Judge API",
    description="""API para comparação e avaliação de respostas de diferentes modelos de linguagem.

## Recursos:
- **Comparação individual**: Avalie duas respostas pré-geradas usando modelo judge
- **Comparação em lote**: Processe múltiplas comparações em paralelo com estatísticas
- **Gerenciamento básico de modelos**: Lista modelos disponíveis via OpenRouter
- **Health checks**: Monitoramento básico da saúde da API

Focada na comparação de respostas já existentes, sem geração de novo conteúdo.""",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc", 
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    contact={
        "name": "LLM as Judge Study",
        "description": "Sistema de avaliação de modelos de linguagem"
    },
    license_info={
        "name": "MIT",
    }
)

# Configure CORS middleware com configurações otimizadas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers with /api/v1 prefix
app.include_router(
    compare.router, 
    prefix="/api/v1/compare", 
    tags=["compare"],
    responses={
        404: {"description": "Comparação não encontrada"},
        422: {"description": "Erro de validação"},
        500: {"description": "Erro interno do servidor"}
    }
)

app.include_router(
    models.router, 
    prefix="/api/v1/models", 
    tags=["models"],
    responses={
        404: {"description": "Modelo não encontrado"},
        503: {"description": "Serviço indisponível - configuração JSON não encontrada"},
        500: {"description": "Erro interno do servidor"}
    }
)

app.include_router(
    health.router, 
    prefix="/api/v1/health", 
    tags=["health"],
    responses={
        200: {"description": "Sistema saudável"},
        503: {"description": "Sistema com problemas"}
    }
)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint com informações básicas da API.
    
    Returns:
        Dictionary com informações da API e endpoints disponíveis
    """
    logger.info("🏠 [MAIN API] Root endpoint acessado")
    
    return {
        "message": "LLM as Judge Study API",
        "version": "0.2.0",
        "description": "API para comparação de respostas de modelos de linguagem",
        "endpoints": {
            "compare": {
                "individual": "/api/v1/compare/",
                "batch": "/api/v1/compare/batch"
            },
            "models": {
                "list": "/api/v1/models/",
                "info": "/api/v1/models/{model_name}"
            },
            "health": "/api/v1/health/",
            "docs": "/docs"
        }
    }

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        # Configurações para UTF-8 adequado
        access_log=True,
        use_colors=True,
        server_header=False
    )