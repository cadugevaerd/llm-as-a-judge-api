"""
Schemas simplificados para endpoints de modelos.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal


class ModelPerformanceInfo(BaseModel):
    """Schema para informações de performance de um modelo."""
    average_time: Optional[float] = Field(None, description="Tempo médio de resposta em segundos")
    ranking: Optional[int] = Field(None, description="Posição nos testes (1 = melhor)")
    consistency: Optional[bool] = Field(None, description="Consistência nas respostas")


class ModelCapabilities(BaseModel):
    """Schema para capacidades de um modelo."""
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens suportados")
    temperature: Optional[float] = Field(None, description="Temperatura padrão")
    timeout: Optional[int] = Field(None, description="Timeout padrão em segundos")


class ModelBasicInfo(BaseModel):
    """Schema básico para informações de um modelo."""
    model_id: str = Field(..., description="ID do modelo")
    display_name: str = Field(..., description="Nome de exibição")
    provider: str = Field(..., description="Provedor")
    status: str = Field(..., description="Status do modelo")


class ModelDetailedInfo(BaseModel):
    """Schema detalhado para informações completas de um modelo."""
    model_id: str = Field(..., description="ID do modelo")
    display_name: str = Field(..., description="Nome de exibição")
    provider: str = Field(..., description="Provedor")
    is_default: bool = Field(..., description="Se é o modelo padrão")
    status: str = Field(..., description="Status do modelo")
    performance: Optional[ModelPerformanceInfo] = Field(None, description="Informações de performance")
    capabilities: Optional[ModelCapabilities] = Field(None, description="Capacidades do modelo")
    source: str = Field(..., description="Fonte das informações (dynamic_config, static_fallback, etc)")


class ModelsListResponse(BaseModel):
    """Schema para resposta da listagem de modelos."""
    available_models: List[str] = Field(..., description="Lista de modelos disponíveis")
    total_models: int = Field(..., description="Total de modelos")
    default_model: str = Field(..., description="Modelo padrão")
    source: str = Field(..., description="Fonte das informações")