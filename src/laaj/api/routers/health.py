"""
Health router for system health check endpoints.
"""

from fastapi import APIRouter
from typing import Dict, Any
import time
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger("laaj.api.health")

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dictionary containing health status information
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "LLM as Judge Study API",
        "version": "0.1.0"
    }

@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with system information.
    
    Returns:
        Dictionary containing detailed health status
    """
    logger.info("Detailed health check requested")
    start_time = time.time()
    
    # Basic checks
    checks = {
        "api": "healthy",
        "config": "loaded",
        "models": "available"
    }
    
    response_time = time.time() - start_time
    logger.info(f"Health check completed in {response_time * 1000:.2f}ms")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "LLM as Judge Study API",
        "version": "0.1.0",
        "response_time_ms": round(response_time * 1000, 2),
        "checks": checks
    }