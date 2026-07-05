# ====================================================================
# Pydantic schemas for the Leibniz demo backend
# ====================================================================
from pydantic import BaseModel
from typing import Optional, Dict, Any

class InferenceResponse(BaseModel):
    task: str
    mode: Optional[str]
    prompt: str
    result: str
    latency_seconds: float

class HealthResponse(BaseModel):
    status: str
    gpu_available: bool
    gpu_name: Optional[str]
    model_loaded: bool
    mock_mode: bool
    config: Dict[str, Any]
