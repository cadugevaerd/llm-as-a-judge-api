import asyncio
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from laaj.api.schemas import CompareRequest, ComparisonResponse, BatchCompareRequest, BatchComparisonResponse, BatchComparisonResult
from laaj.workflow.workflow import main as workflow_main, batch_judge_processing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ComparisonResponse, response_class=ORJSONResponse)
async def compare_models(request: CompareRequest):
    """
    Compara duas respostas pré-geradas usando um modelo judge.
    Não gera novas respostas - apenas avalia respostas já existentes.
    """
    logger.info(f"Received comparison request for pre-generated responses")
    logger.info(f"Input: {request.input[:100]}...")
    logger.info(f"Response A: {len(request.response_a)} chars")
    logger.info(f"Response B: {len(request.response_b)} chars")
    
    try:
        # Executar workflow simplificado (apenas judge)
        result = await workflow_main(
            input_question=request.input,
            response_a=request.response_a,
            response_b=request.response_b,
            model_a_name=request.model_a_name,
            model_b_name=request.model_b_name,
            timeout_seconds=30
        )
        
        logger.info(f"Comparison completed with result: {result['better_response']}")
        return ComparisonResponse(**result)
        
    except asyncio.TimeoutError:
        logger.error("Comparison timed out.")
        raise HTTPException(status_code=408, detail="Comparison timed out")
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@router.post("/batch", response_model=BatchComparisonResponse, response_class=ORJSONResponse)
async def compare_models_batch(request: BatchCompareRequest):
    """
    Compara uma lista de respostas pré-geradas usando um modelo judge em paralelo.
    Usa LangChain abatch() para processamento eficiente e não gera novas respostas.
    """
    import time
    start_time = time.time()
    
    logger.info(f"🔥 [API-BATCH] Recebida requisição batch com {len(request.comparisons)} comparações")
    
    # Log das comparações recebidas (primeira linha de cada para debugging)
    for i, comp in enumerate(request.comparisons):
        logger.info(f"📝 [API-BATCH] Comparação {i+1}: {comp.input[:50]}... | A={len(comp.response_a)} chars | B={len(comp.response_b)} chars")
    
    try:
        # Aplicar timeout de 90 segundos para batch (mais que individual)
        async with asyncio.timeout(90):
            
            # Executar processamento batch usando workflow
            logger.info(f"🚀 [API-BATCH] Iniciando processamento paralelo...")
            batch_results = await batch_judge_processing(request.comparisons)
            
            # Calcular estatísticas de performance
            model_a_wins = 0
            model_b_wins = 0
            ties = 0
            errors = 0
            successful_count = 0
            
            for result in batch_results:
                if result.better_response.startswith("ERRO") or result.better_response.startswith("TIMEOUT"):
                    errors += 1
                else:
                    successful_count += 1
                    if result.better_response == "A":
                        model_a_wins += 1
                    elif result.better_response == "B":
                        model_b_wins += 1
                    elif result.better_response == "Empate":
                        ties += 1
                    else:
                        # Outras respostas também são consideradas erros
                        errors += 1
                        successful_count -= 1
            
            # Determinar melhor modelo geral
            if model_a_wins > model_b_wins:
                best_model = "A"
            elif model_b_wins > model_a_wins:
                best_model = "B"
            elif model_a_wins == model_b_wins and (model_a_wins > 0 or model_b_wins > 0):
                best_model = "Empate"
            else:
                best_model = "N/A"
            
            elapsed_time = time.time() - start_time
            logger.info(f"🏁 [API-BATCH] Processamento concluído em {elapsed_time:.2f}s")
            logger.info(f"📊 [API-BATCH] Estatísticas: A={model_a_wins} | B={model_b_wins} | Empates={ties} | Erros={errors} | Melhor={best_model}")
            
            # Response estruturado que bate com o schema
            return BatchComparisonResponse(
                results=batch_results,
                total_comparisons=len(request.comparisons),
                successful=successful_count,
                execution_time=elapsed_time,
                model_a_wins=model_a_wins,
                model_b_wins=model_b_wins,
                ties=ties,
                errors=errors,
                best_model=best_model
            )
            
    except asyncio.TimeoutError:
        elapsed_time = time.time() - start_time
        error_msg = f"Processamento batch excedeu timeout de 90s após {elapsed_time:.2f}s"
        
        logger.error(f"⏰ [API-BATCH] TIMEOUT: {error_msg}")
        
        # Retornar resultados de timeout para todas as comparações
        timeout_results = []
        for comparison in request.comparisons:
            timeout_results.append(BatchComparisonResult(
                input=comparison.input,
                response_a=comparison.response_a,
                response_b=comparison.response_b,
                model_a_name=comparison.model_a_name,
                model_b_name=comparison.model_b_name,
                better_response=f"TIMEOUT - Excedeu 90s",
                judge_reasoning=f"O processamento batch foi interrompido por timeout após {elapsed_time:.2f}s"
            ))
        
        return BatchComparisonResponse(
            results=timeout_results,
            total_comparisons=len(request.comparisons),
            successful=0,
            execution_time=elapsed_time,
            model_a_wins=0,
            model_b_wins=0,
            ties=0,
            errors=len(request.comparisons),
            best_model="N/A"
        )
        
    except ValueError as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ [API-BATCH] Erro de validação: {str(e)}")
        
        raise HTTPException(status_code=422, detail=f"Validation error in batch processing: {e}")
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_type = type(e).__name__
        logger.error(f"❌ [API-BATCH] Erro inesperado ({error_type}): {str(e)}", exc_info=True)
        
        # Retornar resultados de erro para todas as comparações
        error_results = []
        for comparison in request.comparisons:
            error_results.append(BatchComparisonResult(
                input=comparison.input,
                response_a=comparison.response_a,
                response_b=comparison.response_b,
                model_a_name=comparison.model_a_name,
                model_b_name=comparison.model_b_name,
                better_response=f"ERRO - {error_type}",
                judge_reasoning=f"Falha inesperada durante processamento batch: {str(e)}"
            ))
        
        return BatchComparisonResponse(
            results=error_results,
            total_comparisons=len(request.comparisons),
            successful=0,
            execution_time=elapsed_time,
            model_a_wins=0,
            model_b_wins=0,
            ties=0,
            errors=len(request.comparisons),
            best_model="N/A"
        )