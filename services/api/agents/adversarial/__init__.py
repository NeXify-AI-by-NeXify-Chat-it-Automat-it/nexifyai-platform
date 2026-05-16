"""
NeXifyAI Adversarial Review — adapted from zscole/adversarial-spec.
Multi-model debate engine for spec refinement using DeepSeek + Nscale models.
"""
from .model_router import run_debate, call_model, call_models_parallel, ModelResponse, DebateResult
from .prompts import get_debate_system_prompt, get_review_prompt, DOC_TYPES, FOCUS_AREAS
from .brain_store import store_debate_result, get_past_reviews
from .routes import adversarial_router

__all__ = [
    "run_debate", "call_model", "call_models_parallel",
    "ModelResponse", "DebateResult",
    "get_debate_system_prompt", "get_review_prompt",
    "DOC_TYPES", "FOCUS_AREAS",
    "store_debate_result", "get_past_reviews",
    "adversarial_router",
]
