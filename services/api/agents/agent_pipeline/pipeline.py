"""NeXifyAI Agent Pipeline — adapted from agent-sh/agentsys pipeline.js.
5-stage composable pipeline: Enrich → Validate → Execute → Review → Report."""
import asyncio, logging, time, hashlib
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from enum import Enum

logger = logging.getLogger("agent_pipeline")

class PipelineStage(Enum):
    ENRICH = "enrich"
    VALIDATE = "validate"
    EXECUTE = "execute"
    REVIEW = "review"
    REPORT = "report"

@dataclass
class PipelineContext:
    task: str
    agent_name: str
    project: Optional[str] = None
    session_id: Optional[str] = None
    brain_context: Optional[dict] = None
    validated_input: Optional[dict] = None
    execution_result: Optional[Any] = None
    review_findings: list[dict] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    stage_timings: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    
    def add_timing(self, stage: PipelineStage, duration: float):
        self.stage_timings[stage.value] = duration
    def add_error(self, error: str):
        self.errors.append(error)

class AgentPipeline:
    def __init__(self):
        self._stages: dict[PipelineStage, Callable] = {}
        self._enabled_stages: set[PipelineStage] = set()
    
    def add_stage(self, stage: PipelineStage, handler: Callable):
        self._stages[stage] = handler
        self._enabled_stages.add(stage)
        return self
    
    def disable_stage(self, stage: PipelineStage):
        self._enabled_stages.discard(stage)
        return self
    
    async def run(self, ctx: PipelineContext) -> PipelineContext:
        for stage in [PipelineStage.ENRICH, PipelineStage.VALIDATE,
                      PipelineStage.EXECUTE, PipelineStage.REVIEW, PipelineStage.REPORT]:
            if stage not in self._enabled_stages or stage not in self._stages:
                continue
            try:
                start = time.time()
                ctx = await self._stages[stage](ctx)
                ctx.add_timing(stage, time.time() - start)
            except Exception as e:
                ctx.add_error(f"{stage.value}: {str(e)}")
                logger.error(f"Pipeline stage {stage.value} failed: {e}")
        return ctx

async def default_enricher(ctx: PipelineContext) -> PipelineContext:
    import httpx
    try:
        words = ctx.task.split()[:5]
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "http://localhost:6333/collections/nexifyai_brain/points/scroll",
                json={"limit": 10, "with_payload": True, "with_vector": False,
                      "filter": {"should": [{"key": "content", "match": {"text": w}} for w in words]}},
                timeout=10)
            points = r.json().get("result", {}).get("points", [])
            ctx.brain_context = {
                "matches": len(points),
                "categories": list(set(p["payload"].get("category", "?") for p in points)),
                "top": [p["payload"].get("content", "")[:200] for p in points[:5]],
            }
    except Exception as e:
        ctx.brain_context = {"error": str(e)}
    return ctx

async def default_validator(ctx: PipelineContext) -> PipelineContext:
    if not ctx.task: ctx.add_error("Task is empty")
    if not ctx.agent_name: ctx.add_error("Agent name not specified")
    ctx.validated_input = {"task_valid": bool(ctx.task), "agent_valid": bool(ctx.agent_name)}
    return ctx

async def default_reporter(ctx: PipelineContext) -> PipelineContext:
    import httpx
    point_id = hashlib.sha256(f"{ctx.agent_name}:{ctx.task}:{time.time()}".encode()).hexdigest()[:16]
    payload = {"category": "pipeline_execution", "title": f"{ctx.agent_name}: {ctx.task[:120]}",
               "content": f"Pipeline: {list(ctx.stage_timings.keys())}, Errors: {len(ctx.errors)}",
               "agent": ctx.agent_name, "project": ctx.project,
               "timings": ctx.stage_timings, "errors": ctx.errors,
               "timestamp": time.time(), "source": "agent-pipeline"}
    try:
        async with httpx.AsyncClient() as client:
            await client.put("http://localhost:6333/collections/nexifyai_brain/points",
                           json={"points": [{"id": point_id, "vector": [0.0]*1536, "payload": payload}]},
                           timeout=10)
    except Exception as e:
        logger.warning(f"Report storage failed: {e}")
    return ctx

def create_standard_pipeline(enable_review: bool = True) -> AgentPipeline:
    pipeline = AgentPipeline()
    pipeline.add_stage(PipelineStage.ENRICH, default_enricher)
    pipeline.add_stage(PipelineStage.VALIDATE, default_validator)
    pipeline.add_stage(PipelineStage.REPORT, default_reporter)
    if not enable_review:
        pipeline.disable_stage(PipelineStage.REVIEW)
    return pipeline
