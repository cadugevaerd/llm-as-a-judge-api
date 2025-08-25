from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List
import uuid

class CompareRequest(BaseModel):
    """Request schema para comparação de respostas pré-geradas apenas."""
    
    # Campo de entrada obrigatório para contexto
    input: str = Field(..., description="Pergunta ou contexto usado para gerar as respostas", min_length=1)
    
    # Respostas pré-geradas obrigatórias
    response_a: str = Field(..., description="Resposta pré-gerada do modelo A", min_length=1)
    response_b: str = Field(..., description="Resposta pré-gerada do modelo B", min_length=1)
    
    # Metadados opcionais sobre os modelos que geraram as respostas (apenas para referência)
    model_a_name: Optional[str] = Field(None, description="Nome do modelo que gerou response_a (opcional, apenas para referência)")
    model_b_name: Optional[str] = Field(None, description="Nome do modelo que gerou response_b (opcional, apenas para referência)")
    
    # Modelo judge a ser usado na comparação
    judge_model: Optional[str] = Field(None, description="ID do modelo judge para fazer a comparação (opcional, usa modelo padrão se não especificado)")
    
    @field_validator('input', 'response_a', 'response_b')
    @classmethod
    def validate_non_empty_strings(cls, v):
        if not v or not v.strip():
            raise ValueError('Campo não pode ser vazio')
        return v.strip()

class ComparisonResponse(BaseModel):
    """Response schema para resultado da comparação."""
    
    # Dados de entrada ecoados para referência
    input: str = Field(..., description="Input original usado na comparação")
    response_a: str = Field(..., description="Resposta A que foi comparada")
    response_b: str = Field(..., description="Resposta B que foi comparada")
    
    # Resultado da comparação
    better_response: str = Field(..., description="Qual resposta foi considerada melhor (A, B, Empate, ou mensagem de erro)")
    judge_reasoning: Optional[str] = Field(None, description="Explicação do juiz sobre a decisão (quando disponível)")
    
    # Metadados
    model_a_name: Optional[str] = Field(None, description="Nome do modelo A (se fornecido na requisição)")
    model_b_name: Optional[str] = Field(None, description="Nome do modelo B (se fornecido na requisição)")
    judge_model_used: str = Field(..., description="ID do modelo judge utilizado na comparação")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp da comparação")
    execution_time: float = Field(..., description="Tempo de execução em segundos", ge=0)
    

class BatchCompareRequest(BaseModel):
    """Request para comparação em batch."""
    comparisons: List[CompareRequest] = Field(..., max_items=5, min_items=2, description="Lista de comparações (mínimo 2, máximo 5)")
    
    @field_validator('comparisons')
    @classmethod
    def validate_comparisons(cls, v):
        if len(v) == 1:
            raise ValueError('Para uma única comparação, use o endpoint /api/v1/compare/ (sem /batch)')
        return v

class BatchComparisonResult(BaseModel):
    """Resultado individual de uma comparação no batch."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único da comparação")
    input: str = Field(..., description="Input original usado na comparação")
    response_a: str = Field(..., description="Resposta A que foi comparada")
    response_b: str = Field(..., description="Resposta B que foi comparada")
    model_a_name: Optional[str] = Field(None, description="Nome do modelo A")
    model_b_name: Optional[str] = Field(None, description="Nome do modelo B")
    judge_model_used: str = Field(..., description="ID do modelo judge utilizado na comparação")
    better_response: str = Field(..., description="Qual resposta foi considerada melhor")
    judge_reasoning: Optional[str] = Field(None, description="Explicação do juiz")

class BatchComparisonResponse(BaseModel):
    """Response do batch comparison."""
    results: List[BatchComparisonResult] = Field(..., description="Resultados das comparações")
    total_comparisons: int = Field(..., description="Total de comparações enviadas")
    successful: int = Field(..., description="Número de comparações bem-sucedidas")
    execution_time: float = Field(..., description="Tempo total de execução", ge=0)
    
    # Estatísticas de performance dos modelos
    model_a_wins: int = Field(..., description="Número de vitórias do modelo A")
    model_b_wins: int = Field(..., description="Número de vitórias do modelo B")
    ties: int = Field(..., description="Número de empates")
    errors: int = Field(..., description="Número de comparações com erro")
    best_model: str = Field(..., description="Modelo com melhor performance geral (A, B, Empate ou N/A)")