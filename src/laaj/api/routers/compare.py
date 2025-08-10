"""
Compare router for LLM comparison endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger("laaj.api.compare")

class CompareRequest(BaseModel):
    prompt: str
    model_1: str = "claude-4-sonnet"
    model_2: str = "google-gemini-2.5-pro"

@router.post("/")
async def compare_llms(request: CompareRequest) -> Dict[str, Any]:
    """
    Compare responses from two different LLMs.
    
    Args:
        request: CompareRequest with prompt and model selections
        
    Returns:
        Dictionary containing comparison results
    """
    logger.info(f"LLM comparison requested: {request.model_1} vs {request.model_2}")
    logger.info(f"Prompt length: {len(request.prompt)} characters")
    
    # TODO: Implement actual LLM comparison logic using workflow
    result = {
        "prompt": request.prompt,
        "model_1": request.model_1,
        "model_2": request.model_2,
        "status": "comparison_pending",
        "message": "LLM comparison endpoint - implementation pending"
    }
    
    logger.info("LLM comparison response prepared (pending implementation)")
    return result