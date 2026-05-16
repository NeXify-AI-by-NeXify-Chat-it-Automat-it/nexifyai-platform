"""
Adversarial Review API Route — exposes debate engine as backend endpoint.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import logging

from .model_router import run_debate, MODEL_ALIASES, PROVIDER_CONFIGS
from .brain_store import store_debate_result

logger = logging.getLogger("adversarial.routes")
adversarial_router = APIRouter(prefix="/api/adversarial", tags=["adversarial-review"])

class DebateRequest(BaseModel):
    task: str = Field(..., description="Task description for the spec review")
    spec: str = Field(..., description="Specification draft to review")
    models: list[str] = Field(default=["v4", "qwen32"], description="Models to use")
    max_rounds: int = Field(default=3, ge=1, le=5)
    doc_type: str = Field(default="tech-spec")

class DebateResponse(BaseModel):
    success: bool
    task: str
    models_used: list[str]
    rounds: int
    consensus: bool
    final_spec: Optional[str]
    total_cost: float
    duration_seconds: float
    feedback: list[dict]

@adversarial_router.post("/debate", response_model=DebateResponse)
async def debate_spec(request: DebateRequest, background_tasks: BackgroundTasks):
    """Run an adversarial debate on a specification draft."""
    # Validate models
    valid_models = []
    for m in request.models:
        resolved = m in MODEL_ALIASES or m in PROVIDER_CONFIGS
        if not resolved:
            raise HTTPException(400, f"Unknown model: {m}. Available: {list(MODEL_ALIASES.keys())}")
        valid_models.append(m)
    
    # Run debate
    result = run_debate(
        task=request.task,
        spec_draft=request.spec,
        models=valid_models,
        max_rounds=request.max_rounds,
        doc_type=request.doc_type,
    )
    
    # Store in Brain (background)
    background_tasks.add_task(store_debate_result, result)
    
    # Build feedback
    feedback = [
        {
            "model": r.model,
            "agreed": r.agreed,
            "response_preview": (r.response or "")[:300],
            "cost": r.cost,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
        }
        for r in result.responses
    ]
    
    return DebateResponse(
        success=True,
        task=result.task,
        models_used=result.models_used,
        rounds=result.rounds,
        consensus=result.consensus,
        final_spec=result.final_spec,
        total_cost=result.total_cost,
        duration_seconds=result.duration_seconds,
        feedback=feedback,
    )

@adversarial_router.get("/models")
async def list_models():
    """List available models for adversarial debate."""
    return {
        "providers": {k: {"model": v["model_id"], "cost_input_per_1m": v["cost_per_1m_input"], 
                          "cost_output_per_1m": v["cost_per_1m_output"]}
                     for k, v in PROVIDER_CONFIGS.items()},
        "aliases": MODEL_ALIASES,
        "default_models": ["v4", "qwen32", "qwq"],
    }

@adversarial_router.get("/history")
async def debate_history(q: str = "", limit: int = 10):
    """Get past debate results from Brain."""
    from .brain_store import get_past_reviews
    reviews = await get_past_reviews(q, limit)
    return {"query": q, "reviews": reviews, "count": len(reviews)}
