"""
Models router for listing available LLM models.
"""

from fastapi import APIRouter
from typing import List, Dict, Any
import logging
from laaj.config.config import LITERAL_MODELS

router = APIRouter()
logger = logging.getLogger("laaj.api.models")

@router.get("/")
async def list_models() -> Dict[str, Any]:
    """
    List all available LLM models.
    
    Returns:
        Dictionary containing list of available models
    """
    logger.info(f"Models list requested - returning {len(LITERAL_MODELS)} models")
    return {
        "available_models": LITERAL_MODELS,
        "total_count": len(LITERAL_MODELS)
    }

@router.get("/{model_name}")
async def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get information about a specific model.
    
    Args:
        model_name: Name of the model to get info for
        
    Returns:
        Dictionary containing model information
    """
    logger.info(f"Model info requested for: {model_name}")
    
    if model_name not in LITERAL_MODELS:
        logger.warning(f"Model not found: {model_name}")
        return {
            "error": "Model not found",
            "available_models": LITERAL_MODELS
        }
    
    logger.info(f"Model info found for: {model_name}")
    # TODO: Add more detailed model information
    return {
        "model_name": model_name,
        "status": "available",
        "provider": "openrouter" if model_name in LITERAL_MODELS else "unknown"
    }