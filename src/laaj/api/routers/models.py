"""
Models router simplificado para gerenciamento básico de modelos LLM.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from laaj.config.config import LITERAL_MODELS
from laaj.config.models_loader import models_loader
from laaj.api.schemas.models import ModelDetailedInfo, ModelPerformanceInfo, ModelCapabilities

router = APIRouter()
logger = logging.getLogger("laaj.api.models")


@router.get("/", summary="Lista todos os modelos disponíveis")
async def list_models() -> Dict[str, Any]:
    """
    Lista todos os modelos LLM disponíveis do sistema dinâmico.
    
    Returns:
        Dictionary com lista de IDs de modelos que o usuário pode usar
    """
    logger.info("📋 [MODELS API] Listando modelos disponíveis")
    
    try:
        # Tentar obter modelos do sistema dinâmico
        available_models = models_loader.get_active_models()
        default_model = models_loader.get_default_model()
        
        if available_models:
            logger.info(f"✅ [MODELS API] Retornando {len(available_models)} modelos via JSON dinâmico")
            return {
                "available_models": available_models,
                "total_models": len(available_models),
                "default_model": default_model,
                "source": "dynamic_config"
            }
        else:
            # Fallback para lista estática
            logger.warning("⚠️ [MODELS API] JSON indisponível, usando fallback estático")
            return {
                "available_models": LITERAL_MODELS,
                "total_models": len(LITERAL_MODELS),
                "default_model": LITERAL_MODELS[0],
                "source": "static_fallback"
            }
    
    except Exception as e:
        logger.error(f"❌ [MODELS API] Erro ao listar modelos: {e}")
        # Emergency fallback
        return {
            "available_models": LITERAL_MODELS,
            "total_models": len(LITERAL_MODELS),
            "default_model": LITERAL_MODELS[0],
            "source": "emergency_fallback",
            "error": str(e)
        }


@router.get("/{model_name:path}", response_model=ModelDetailedInfo, summary="Informações detalhadas de um modelo específico")
async def get_model_info(model_name: str) -> ModelDetailedInfo:
    """
    Obtém informações detalhadas sobre um modelo específico incluindo:
    - Informações básicas (ID, nome, provedor, status)
    - Métricas de performance (tempo médio, ranking nos testes, consistência)
    - Capacidades técnicas (tokens, temperatura, timeout)
    
    Args:
        model_name: Nome do modelo
        
    Returns:
        ModelDetailedInfo: Informações completas do modelo
    """
    logger.info(f"🔍 [MODELS API] Solicitando informações detalhadas para: {model_name}")
    
    try:
        # Tentar obter do sistema dinâmico primeiro
        model_config = models_loader.get_model_config(model_name)
        
        if model_config:
            logger.info(f"✅ [MODELS API] Modelo encontrado no JSON dinâmico: {model_name}")
            
            # Extrair informações de performance
            performance_data = model_config.performance or {}
            performance = ModelPerformanceInfo(
                average_time=performance_data.get('average_time'),
                ranking=performance_data.get('ranking'),
                consistency=performance_data.get('consistency')
            ) if performance_data else None
            
            # Extrair capacidades
            capabilities_data = model_config.capabilities or {}
            capabilities = ModelCapabilities(
                max_tokens=capabilities_data.get('max_tokens'),
                temperature=capabilities_data.get('temperature'),
                timeout=capabilities_data.get('timeout')
            ) if capabilities_data else None
            
            return ModelDetailedInfo(
                model_id=model_config.id,
                display_name=model_config.display_name,
                provider=model_config.provider,
                is_default=model_config.is_default,
                status=model_config.status,
                performance=performance,
                capabilities=capabilities,
                source="dynamic_config"
            )
        else:
            # Fallback para lista estática
            if model_name in LITERAL_MODELS:
                logger.warning(f"⚠️ [MODELS API] Modelo {model_name} encontrado apenas no fallback estático")
                
                # Criar informações básicas para fallback
                fallback_performance = ModelPerformanceInfo(
                    average_time=None,
                    ranking=LITERAL_MODELS.index(model_name) + 1 if model_name in LITERAL_MODELS else None,
                    consistency=None
                )
                
                fallback_capabilities = ModelCapabilities(
                    max_tokens=1024,
                    temperature=0.0,
                    timeout=30
                )
                
                return ModelDetailedInfo(
                    model_id=model_name,
                    display_name=model_name,
                    provider="openrouter",
                    is_default=model_name == LITERAL_MODELS[0],
                    status="active",
                    performance=fallback_performance,
                    capabilities=fallback_capabilities,
                    source="static_fallback"
                )
            else:
                logger.error(f"❌ [MODELS API] Modelo {model_name} não encontrado em nenhum sistema")
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Model not found",
                        "model_name": model_name,
                        "available_models": models_loader.get_active_models() or LITERAL_MODELS,
                        "message": f"O modelo '{model_name}' não está disponível. Use um dos modelos da lista 'available_models'."
                    }
                )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [MODELS API] Erro ao obter informações do modelo {model_name}: {e}")
        
        # Emergency fallback - apenas para modelos na lista estática
        if model_name in LITERAL_MODELS:
            logger.warning(f"🆘 [MODELS API] Usando emergency fallback para: {model_name}")
            
            emergency_performance = ModelPerformanceInfo(
                average_time=None,
                ranking=LITERAL_MODELS.index(model_name) + 1,
                consistency=None
            )
            
            emergency_capabilities = ModelCapabilities(
                max_tokens=1024,
                temperature=0.0,
                timeout=30
            )
            
            return ModelDetailedInfo(
                model_id=model_name,
                display_name=model_name,
                provider="openrouter",
                is_default=model_name == LITERAL_MODELS[0],
                status="active",
                performance=emergency_performance,
                capabilities=emergency_capabilities,
                source="emergency_fallback"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal server error",
                    "message": f"Erro ao recuperar informações do modelo: {e}",
                    "model_name": model_name
                }
            )