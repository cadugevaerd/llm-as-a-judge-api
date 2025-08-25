"""
Health router simplificado para health checks básicos.
"""

from fastapi import APIRouter
from typing import Dict, Any
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger("laaj.api.health")


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Health check básico da API.
    
    Returns:
        Dictionary com status de saúde da API
    """
    logger.info("🏥 [HEALTH] Health check solicitado")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "LLM as Judge Study API",
        "version": "0.2.0"
    }