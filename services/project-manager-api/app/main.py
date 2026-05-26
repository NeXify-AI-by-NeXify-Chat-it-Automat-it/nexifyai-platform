"""NeXify Project Manager Control Plane - FastAPI application."""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_token
from app.config import REGISTRY_DIR
from app.schemas import TaskInput, TaskRecord, TaskStatus, WorkerCallback, HealthResponse
from app.task_registry import insert, get, update_status, generate_task_id, now_iso, list_tasks
from app.policy_gate import gate
from app.goose_controller import run_task, DRY_RUN
from app.brain_client import check_health as brain_health, store as brain_store
from app.skill_registry import load_registry, validate_registry
from app.project_tracker import load_tracker, validate_tracker
from app.github_client import verify_signature, store_event
from app.task_generator import generate_task
from app.schemas import AutoMergeEvaluation
from app import VERSION

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("pm.api")

async def worker_poll_loop():
    """Background worker: polls queued tasks every 30s and auto-dispatches."""
    logger.info("Worker poll loop started (dry_run=%s, worker_enabled=%s)", DRY_RUN, not DRY_RUN)
    while True:
        try:
            pending = list_tasks(status=TaskStatus.queued.value, limit=5)
            for task_rec in pending:
                task = get(task_rec.task_id)
                if not task or task.status != TaskStatus.queued:
                    continue
                update_status(task.task_id, TaskStatus.running)
                logger.info("Auto-dispatch task %s (goal=%s)", task.task_id, (task_rec.goal or "")[:60])
                await run_task(task)
        except Exception as e:
            logger.error("Worker poll error: %s", e)
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Project Manager Control Plane v%s starting (dry_run=%s)", VERSION, DRY_RUN)
    task = asyncio.create_task(worker_poll_loop())
    yield
    task.cancel()
    logger.info("Shutting down")

app = FastAPI(title="NeXify Project Manager", version=VERSION, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health", response_model=HealthResponse)
async def health():
    brain_ok = await brain_health()
    reg = load_registry()
    reg_ok, reg_msg = validate_registry(reg)
    tracker_ok, _, tracker_msg = load_tracker()
    total_skills = reg.get("skills", {}).get("meta", {}).get("total_skills", 0) if reg_ok else 0
    return HealthResponse(
        api="ok",
        brain="ok" if brain_ok else "unreachable",
        registry="ok" if reg_ok else "invalid",
        skill_registry="ok" if reg_ok else f"invalid: {reg_msg}",
        project_tracker="ok" if tracker_ok else f"invalid: {tracker_msg}",
        worker_enabled=not DRY_RUN,
        dry_run=DRY_RUN,
        version=VERSION,
        total_skills=total_skills,
    )

@app.post("/tasks")
async def create_task(task_in: TaskInput, _token: str = Depends(verify_token)):
    task = TaskRecord(
        task_id=generate_task_id(),
        status=TaskStatus.queued,
        created_at=now_iso(), updated_at=now_iso(),
        goal=task_in.goal, mode=task_in.mode, priority=task_in.priority,
        project=task_in.project, repo=task_in.repo,
        branch_strategy=task_in.branch_strategy, context=task_in.context,
        allowed_actions=task_in.allowed_actions,
        denied_actions=task_in.denied_actions,
        acceptance_criteria=task_in.acceptance_criteria,
        evidence_required=task_in.evidence_required,
        abort_conditions=task_in.abort_conditions,
        brain_context_required=task_in.brain_context_required,
        callback_url=task_in.callback_url,
    )
    insert(task)
    task = gate(task)
    logger.info("Task %s created status=%s", task.task_id, task.status.value)
    return {"task_id": task.task_id, "status": task.status.value}

@app.get("/tasks/next")
async def next_queued_task():
    """Worker polling endpoint: returns next queued task or null."""
    pending = list_tasks(status="queued", limit=1)
    if not pending:
        return {"task": None, "queue_empty": True}
    t = get(pending[0].task_id)
    if not t:
        return {"task": None, "queue_empty": True}
    return {"task": t.model_dump(), "queue_empty": False}


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()

@app.get("/tasks")
async def list_all_tasks(status: str | None = None, limit: int = 50):
    return [t.model_dump() for t in list_tasks(status=status, limit=limit)]


@app.get("/tasks/{task_id}/evidence")
async def get_task_evidence(task_id: str):
    """Return stored evidence for a completed/failed task."""
    from app.config import EVIDENCE_DIR
    from pathlib import Path
    task = get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.evidence_path:
        return {"task_id": task_id, "evidence": None}
    path = Path(EVIDENCE_DIR) / task.evidence_path
    if path.exists():
        return {"task_id": task_id, "evidence": path.read_text()}
    return {"task_id": task_id, "evidence": None, "path_missing": str(path)}

@app.post("/tasks/{task_id}/run")
async def run_task_endpoint(task_id: str, _token: str = Depends(verify_token)):
    task = get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in (TaskStatus.queued, TaskStatus.failed):
        raise HTTPException(status_code=409, detail=f"Task cannot run (status={task.status.value})")
    result = await run_task(task)
    updated = get(task_id)
    return {"task_id": task_id, "status": updated.status.value if updated else "unknown", "result": result}

@app.post("/worker/callback")
async def worker_callback(cb: WorkerCallback, _token: str = Depends(verify_token)):
    task = get(cb.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_status(cb.task_id, cb.status, result=cb.model_dump())
    return {"task_id": cb.task_id, "status": cb.status.value}

@app.post("/worker/auto-merge-evaluation")
async def auto_merge_evaluation(eval_in: AutoMergeEvaluation, _token: str = Depends(verify_token)):
    """Receives auto-merge evaluation from GitHub Actions worker.
    
    This endpoint tracks which PRs were evaluated for auto-merge,
    the decision made, and whether the merge was successful.
    """
    logger.info(
        "Auto-merge eval: PR #%d | status=%s | reason=%s | author=%s | action=%s",
        eval_in.pull_request, eval_in.status, eval_in.reason,
        eval_in.author, eval_in.action,
    )
    
    # Store the auto-merge event in the brain for audit trail
    if brain_health():
        try:
            await brain_store(
                category="governance",
                title=f"Auto-merge evaluation: PR #{eval_in.pull_request}",
                content=eval_in.model_dump_json(),
                source="github-worker",
                tags=f"auto-merge,pr-{eval_in.pull_request},{eval_in.status}",
            )
        except Exception as e:
            logger.warning("Brain store failed for auto-merge eval: %s", e)
    
    return {
        "ok": True,
        "pull_request": eval_in.pull_request,
        "status": eval_in.status,
        "stored": True,
    }

@app.post("/webhooks/github")
async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    delivery_id = request.headers.get("X-GitHub-Delivery")
    verify_signature(body, signature)
    payload = json.loads(body)
    path = store_event(event_type, payload)
    # Generate PM task from event
    task_result = generate_task(event_type, payload, delivery_id=delivery_id)
    logger.info("Webhook %s/%s — task_created=%s task_id=%s reason=%s",
                event_type, payload.get("action", "?"),
                task_result.get("task_created"), task_result.get("task_id"),
                task_result.get("reason", "ok"))
    return {
        "stored": path,
        "event": event_type,
        "delivery_id": delivery_id,
        "task_created": task_result.get("task_created", False),
        "task_id": task_result.get("task_id"),
        "reason": task_result.get("reason", "ok"),
        "ok": task_result.get("ok", True),
    }
