from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CompareRequest(BaseModel):
    llm_a: str
    llm_b: str
    input: str
    pre_generated_response_a: Optional[str] = None
    pre_generated_response_b: Optional[str] = None

class ComparisonResponse(BaseModel):
    model_llm_a: str
    model_llm_b: str
    response_a: str
    response_b: str
    better_llm: str
    input: str
    pre_generated_response_a: Optional[str] = None
    pre_generated_response_b: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: float