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

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()

@app.get("/tasks")
async def list_all_tasks(status: str | None = None, limit: int = 50):
    return [t.model_dump() for t in list_tasks(status=status, limit=limit)]

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

@app.post("/webhooks/github")
async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    verify_signature(body, signature)
    payload = json.loads(body)
    path = store_event(event_type, payload)
    return {"stored": path, "event": event_type}
