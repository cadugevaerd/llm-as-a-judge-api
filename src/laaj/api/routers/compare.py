import asyncio
import logging
from fastapi import APIRouter, HTTPException
from laaj.api.schemas.compare import CompareRequest, ComparisonResponse
from laaj.workflow.workflow import main as workflow_main

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ComparisonResponse)
async def compare_models(request: CompareRequest):
    """
    Receives a comparison request, runs the LLM as a Judge workflow,
    and returns the result.
    """
    logger.info(f"Received comparison request: {request.model_dump()}")
    try:
        # Run the workflow asynchronously
        result = await workflow_main(
            llm_a=request.llm_a,
            llm_b=request.llm_b,
            input=request.input,
            pre_generated_response_a=request.pre_generated_response_a,
            pre_generated_response_b=request.pre_generated_response_b,
        )
        logger.info(f"Workflow finished with result: {result}")
        return ComparisonResponse(**result)
    except asyncio.TimeoutError:
        logger.error("Workflow timed out.")
        raise HTTPException(status_code=408, detail="Request timed out")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
