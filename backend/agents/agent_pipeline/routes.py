"""Agent Pipeline API Routes."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from .pipeline import (
    AgentPipeline, PipelineContext, PipelineStage,
    create_standard_pipeline, default_enricher, default_validator, default_reporter,
)
import time

pipeline_router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

class PipelineRunRequest(BaseModel):
    task: str
    agent_name: str
    project: str = ""
    session_id: str = ""
    enable_review: bool = False

@pipeline_router.post("/run")
async def run_pipeline(request: PipelineRunRequest):
    ctx = PipelineContext(
        task=request.task, agent_name=request.agent_name,
        project=request.project or None, session_id=request.session_id or None,
    )
    pipeline = create_standard_pipeline(enable_review=request.enable_review)
    result = await pipeline.run(ctx)
    return {
        "agent": result.agent_name, "task": result.task,
        "stages_completed": list(result.stage_timings.keys()),
        "stage_timings": result.stage_timings, "errors": result.errors,
        "brain_matches": result.brain_context.get("matches", 0) if result.brain_context else 0,
        "validated": result.validated_input,
        "duration_total": time.time() - result.started_at,
        "success": len(result.errors) == 0,
    }

@pipeline_router.get("/stages")
async def list_stages():
    return {"stages": [s.value for s in PipelineStage],
            "default_enabled": ["enrich", "validate", "report"],
            "optional": ["execute", "review"]}

@pipeline_router.post("/enrich/test")
async def test_brain_enrichment(task: str = "", agent: str = "test"):
    ctx = PipelineContext(task=task or "test task", agent_name=agent)
    ctx = await default_enricher(ctx)
    return {"task": task, "brain_context": ctx.brain_context}
