"""
FastAPI main application entry point.

This module contains the FastAPI application instance and router configuration.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from laaj.api.routers import compare, models, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="LLM as Judge Study API",
    description="API for comparing and evaluating responses from different language models",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,  # Use ORJSON para UTF-8 adequado
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers with /api/v1 prefix
app.include_router(compare.router, prefix="/api/v1/compare", tags=["compare"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LLM as Judge Study API",
        "version": "0.1.0",
        "endpoints": {
            "compare": "/api/v1/compare",
            "models": "/api/v1/models",
            "health": "/api/v1/health",
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