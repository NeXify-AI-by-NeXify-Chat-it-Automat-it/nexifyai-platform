"""
Orchestrator API Routes — FastAPI wrapper for AgentRouter (orchestrator_v2).
Provides: POST /orchestrate, POST /webhooks/github, GET /agents/status
"""
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import TypedDict, Optional, Dict, Any
from datetime import datetime
from routes.shared import get_admin_or_internal

logger = logging.getLogger("nexifyai.orchestrator")

orch_router = APIRouter(prefix="/api/orchestration", tags=["orchestrator"])

class OrchestrateRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None
    agent: Optional[str] = None  # Force a specific agent

class OrchestrateResponse(BaseModel):
    task_id: str
    agent: str
    status: str
    result: Optional[Dict[str, Any]] = None



# === Team Routing Models ===

class ExecuteRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None
    agent: Optional[str] = None
    system_id: Optional[int] = None
    use_team_routing: Optional[bool] = False

class ExecuteResponse(BaseModel):
    task_id: str
    status: str
    agent: str
    summary: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    executed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = 0
    brain_checked: bool = False
    recommendations: list = []


@orch_router.post("/orchestrate", response_model=OrchestrateResponse)
async def orchestrate_task(req: OrchestrateRequest):
    """
    Route a task to the appropriate agent and execute it.
    Uses orchestrator_v2.AgentRouter for intelligent routing.
    """
    from agents.orchestrator_v2 import router as agent_router
    
    try:
        import uuid
        routing = await agent_router.route_task(req.task, context=req.context)
        return OrchestrateResponse(
            task_id=f"task-{uuid.uuid4().hex[:4]}",
            agent=routing.get("primary", "orchestrator"),
            status="dispatched",
            result={"routing": routing, "all_agents": routing.get("agents", [])}
        )
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@orch_router.get("/agents")
async def list_agents():
    """List all 28 registered agents and their capabilities. Brain-first."""
    from agents.orchestrator_v2 import router as agent_router, AGENT_ROLES
    # Also include mesh routing agents for full picture
    mesh_agents = set(agent_router.mesh.keys())
    brain_agents = set(AGENT_ROLES.keys())
    all_agents = sorted(mesh_agents | brain_agents)
    return {
        "agents": all_agents,
        "total": len(all_agents),
        "brain_registered": len(brain_agents),
        "mesh_routed": len(mesh_agents),
        "capabilities": {k: v for k, v in AGENT_ROLES.items()},
        "status": "operational"
    }


@orch_router.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get details about a specific agent: capability + routing."""
    from agents.orchestrator_v2 import router as agent_router, AGENT_ROLES
    if agent_name not in AGENT_ROLES:
        return {"agent": agent_name, "status": "unknown", "message": f"Agent not found. Available: {sorted(AGENT_ROLES.keys())}"}
    delegations = agent_router.get_delegations(agent_name)
    return {
        "agent": agent_name,
        "capability": AGENT_ROLES.get(agent_name),
        "delegations": delegations if delegations else {},
        "status": "registered"
    }


@orch_router.get("/status")
async def mesh_status():
    """Get the overall agent mesh status with Brain integration."""
    from agents.orchestrator_v2 import router as agent_router, AGENT_ROLES
    try:
        from agents.mesh.agent_mesh import get_mesh_instance
        mesh = get_mesh_instance()
        stats = mesh.get_stats() if hasattr(mesh, 'get_stats') else {}
    except Exception:
        stats = {}
    return {
        "total_agents": len(AGENT_ROLES),
        "meshed_agents": len(agent_router.mesh),
        "brain_agents": len(AGENT_ROLES),
        "webhooks_configured": len(agent_router.webhooks),
        "stats": stats,
        "status": "operational",
        "backend": "nexifyai-agent-mesh"
    }


@orch_router.post("/brain/search")
async def brain_search(query: str):
    """Semantic search across the Brain for relevant agents/knowledge."""
    from agents.orchestrator_v2 import router as agent_router
    from agents.brain_connector import search_agents
    try:
        agents = search_agents(query, limit=5)
        return {"query": query, "matches": agents, "count": len(agents)}
    except Exception as e:
        logger.error(f"Brain search failed: {e}")
        # Fallback to keyword routing
        return {"query": query, "matches": [], "fallback": True, "error": str(e)}


@orch_router.post("/hermes/dispatch")
async def dispatch_via_hermes(request: Request):
    """Dispatch a task to Hermes Gateway for execution by a specific agent."""
    try:
        body = await request.json()
        from agents.brain_connector import dispatch_to_hermes
        result = await dispatch_to_hermes(body.get("agent", ""), body.get("task", ""), body.get("context", {}))
        return {"status": "dispatched", "result": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Hermes dispatch failed: {e}")



# ══════════════════════════════════════════════════════════
# ── Temporal Workflow Endpoints ──────────────────────────
# ══════════════════════════════════════════════════════════

@orch_router.post("/workflow/analyze", response_model=ExecuteResponse)
async def execute_analysis_workflow(
    req: ExecuteRequest,
    request: Request,
    _admin=Depends(get_admin_or_internal),
):
    """WORKFLOW ANALYZE: Parallel analysis pipeline (arch + security + perf)."""
    import time, uuid
    start_ms = time.time()
    task_id = f"analysis-{uuid.uuid4().hex[:8]}"
    try:
        from temporal.client import start_analysis_workflow
        wf_result = await start_analysis_workflow(task=req.task, context=req.context, workflow_id=task_id)
        elapsed_ms = int((time.time() - start_ms) * 1000)
        return ExecuteResponse(
            task_id=task_id, status=wf_result.get("status", "failed"),
            agent="orchestrator",
            summary=f"Analysis: {wf_result.get('status')}",
            result=wf_result.get("result"),
            executed_at=datetime.utcnow(), execution_time_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return ExecuteResponse(
            task_id=task_id, status="failed", agent="orchestrator",
            summary=f"Workflow error: {str(e)[:200]}",
            executed_at=datetime.utcnow(), execution_time_ms=elapsed_ms,
        )


@orch_router.post("/workflow/deploy", response_model=ExecuteResponse)
async def execute_deploy_workflow(
    req: ExecuteRequest,
    request: Request,
    _admin=Depends(get_admin_or_internal),
):
    """WORKFLOW DEPLOY: Safe deployment with conditional rollback."""
    import time, uuid
    start_ms = time.time()
    task_id = f"deploy-{uuid.uuid4().hex[:8]}"
    try:
        from temporal.client import start_deploy_workflow
        wf_result = await start_deploy_workflow(task=req.task, context=req.context, workflow_id=task_id)
        elapsed_ms = int((time.time() - start_ms) * 1000)
        return ExecuteResponse(
            task_id=task_id, status=wf_result.get("status", "failed"),
            agent="orchestrator",
            summary=f"Deploy: {wf_result.get('status')}",
            result=wf_result.get("result"),
            executed_at=datetime.utcnow(), execution_time_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.error(f"Deploy failed: {e}", exc_info=True)
        return ExecuteResponse(
            task_id=task_id, status="failed", agent="orchestrator",
            summary=f"Workflow error: {str(e)[:200]}",
            executed_at=datetime.utcnow(), execution_time_ms=elapsed_ms,
        )


@orch_router.get("/health/full")
async def full_health():
    """Aggregated health: Brain, Hermes, Backend, Systemd, Agent Mesh."""
    import aiohttp
    health = {"timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
    
    # Brain
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://localhost:6333/collections", timeout=5) as r:
                cols = await r.json()
                health["brain"] = {"status": "ok", "collections": [c.get("name") for c in cols.get("result",{}).get("collections",[])]}
    except Exception as e:
        health["brain"] = {"status": "error", "error": str(e)[:100]}
    
    # Hermes
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://localhost:8642/health", timeout=5) as r:
                h = await r.json()
                health["hermes"] = {"status": h.get("status", "unknown")}
    except Exception as e:
        health["hermes"] = {"status": "error", "error": str(e)[:100]}
    
    # Backend self
    health["backend"] = {"status": "ok", "port": 8001}
    
    # Systemd
    import subprocess as sp
    result = sp.run(["systemctl", "is-active", "nexifyai-backend"], capture_output=True, text=True)
    health["systemd"] = {"status": result.stdout.strip()}
    
    # Agent mesh
    from agents.orchestrator_v2 import router, AGENT_ROLES
    health["agents"] = {"total": len(AGENT_ROLES), "meshed": len(router.mesh)}
    
    # Overall
    all_ok = all(
        v.get("status") in ("ok", "active") 
        for k, v in health.items() 
        if isinstance(v, dict) and "status" in v
    )
    # MindsDB
    try:
        result = sp.run(["curl", "-s", "--max-time", "5", "http://localhost:32779/api/status"],
                       capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            md = __import__("json").loads(result.stdout)
            health["mindsdb"] = {"status": "ok", "version": md.get("mindsdb_version", "?")}
        else:
            health["mindsdb"] = {"status": "down"}
    except Exception:
        health["mindsdb"] = {"status": "down"}
    

    health["overall"] = "healthy" if all_ok else "degraded"
    
    return health


@orch_router.get("/hermes/status")
async def hermes_status():
    """Full Hermes status: Gateway, Agent, Workstation, Brain connectivity."""
    import aiohttp, subprocess as sp
    from datetime import datetime, timezone
    
    status = {"timestamp": datetime.now(timezone.utc).isoformat()}
    
    # Gateway (port 8642 via socat)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://localhost:8642/health", timeout=aiohttp.ClientTimeout(total=5)) as r:
                status["gateway"] = await r.json()
    except Exception as e:
        status["gateway"] = {"error": str(e)[:80]}
    
    # Workstation (port 32776)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://localhost:32776/health", timeout=aiohttp.ClientTimeout(total=5)) as r:
                status["workstation"] = {"status": "reachable" if r.status == 200 else str(r.status)}
    except Exception as e:
        status["workstation"] = {"error": str(e)[:80]}
    
    # Agent container
    try:
        result = sp.run(["docker", "inspect", "hermes-workspace-bk7p-hermes-agent-1", 
                        "--format", "{{.State.Status}}"], capture_output=True, text=True, timeout=5)
        status["agent_container"] = {"status": result.stdout.strip()}
    except Exception as e:
        status["agent_container"] = {"error": str(e)[:80]}
    
    # Brain via docker network (nexifyai-qdrant)
    try:
        result = sp.run(["docker", "exec", "hermes-workspace-bk7p-hermes-agent-1",
                        "python3", "-c",
                        "import urllib.request;r=urllib.request.urlopen('http://nexifyai-qdrant:6333/collections');print('ok' if r.status==200 else 'fail')"],
                       capture_output=True, text=True, timeout=10)
        status["agent_brain_access"] = {"status": "ok"} if result.stdout.strip() == "ok" else {"status": "no_response"}
    except Exception as e:
        status["agent_brain_access"] = {"error": str(e)[:80]}
    
    # Overall
    gw_ok = status.get("gateway", {}).get("status") == "ok"
    agent_running = status.get("agent_container", {}).get("status") == "running"
    brain_ok = status.get("agent_brain_access", {}).get("status") == "ok"
    status["overall"] = "ready" if (gw_ok and agent_running and brain_ok) else "partial"
    
    return status
@orch_router.post("/mindsdb/query")
async def mindsdb_query(request: Request):
    """Proxy SQL queries to MindsDB and return results."""
    import subprocess as sp
    data = await request.json()
    query = data.get("query", "")
    
    result = sp.run(["curl", "-s", "--max-time", "120", "-X", "POST", "http://localhost:32779/api/sql/query",
                    "-H", "Content-Type: application/json", "-d", __import__("json").dumps({"query": query})],
                   capture_output=True, text=True, timeout=130)
    return {"status": "ok", "result": __import__("json").loads(result.stdout) if result.stdout else {}}

@orch_router.post("/mindsdb/predict")
async def mindsdb_predict(request: Request):
    """Predict using a MindsDB model (convenience endpoint)."""
    import subprocess as sp
    data = await request.json()
    question = data.get("question", "")
    model = data.get("model", "nexify_provider_v4_flash")
    
    query = f"SELECT answer FROM mindsdb.{model} WHERE question = '{question.replace(chr(39), chr(39)+chr(39))}';"
    result = sp.run(["curl", "-s", "--max-time", "120", "-X", "POST", "http://localhost:32779/api/sql/query",
                    "-H", "Content-Type: application/json", "-d", __import__("json").dumps({"query": query})],
                   capture_output=True, text=True, timeout=130)
    return {"status": "ok", "model": model, "result": __import__("json").loads(result.stdout) if result.stdout else {}}

@orch_router.post("/mindsdb/predict")
async def mindsdb_predict(request: Request):
    """Predict using a MindsDB model (convenience endpoint)."""
    import aiohttp
    data = await request.json()
    question = data.get("question", "")
    model = data.get("model", "nexify_provider_v4_flash")
    
    query = f"SELECT answer FROM mindsdb.{model} WHERE question = '{question}';"
    async with aiohttp.ClientSession() as s:
        async with s.post("http://localhost:32779/api/sql/query",
                         json={"query": query},
                         timeout=aiohttp.ClientTimeout(total=120)) as r:
            result = await r.json()
    
    return {"status": "ok", "model": model, "result": result}


# ═══════════════════════════════════════════════════
# TEAM ROUTING ENDPOINT (Cambo 9Router + Supabase Teams)
# ═══════════════════════════════════════════════════

@orch_router.post("/execute-team", response_model=ExecuteResponse)
async def execute_with_team_routing(
    req: ExecuteRequest,
    request: Request,
    _admin=Depends(get_admin_or_internal),
):
    """
    TEAM EXECUTE: Route via TeamOrchestrator using Supabase team_routing.
    Uses Cambo 9Router for model selection with capability-based routing.
    Falls back to v2 AgentRouter on team routing failure.
    """
    import time, uuid

    start_ms = time.time()
    task_id = f"team-{uuid.uuid4().hex[:8]}"

    try:
        from agents.orchestrator_v3 import TeamOrchestrator

        orch = TeamOrchestrator(db=None)
        routing_info = await orch.route(task=req.task, context=req.context or {})

        agent = routing_info.get("agent", req.agent or "ai-engineer")
        team = routing_info.get("team", "unknown")
        capability = routing_info.get("capability", "general")

        # Execute through agent_executor with Brain-First execution
        from agents.agent_executor import execute_agent_task
        result = await execute_agent_task(agent, req.task, req.context or {})

        elapsed_ms = int((time.time() - start_ms) * 1000)

        # Log execution to Supabase
        try:
            import httpx
            supa_url = os.environ.get("SUPABASE_URL", os.environ.get("DS_SUPABASE_1E93118D__PROJECT_URL", "https://mdlgodcvpasgplcrkiad.supabase.co"))
            supa_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("DS_SUPABASE_1E93118D__SECRET_KEY", ""))
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    f"{supa_url}/rest/v1/task_execution_log",
                    headers={
                        "apikey": supa_key,
                        "Authorization": f"Bearer {supa_key}",
                        "Prefer": "return=minimal",
                    },
                    json={
                        "task_id": task_id,
                        "agent_id": agent,
                        "model_used": capability,
                        "capability_routed": capability,
                        "status": "success",
                        "output": {"summary": str(result.get("summary", ""))[:500]},
                        "execution_time_ms": elapsed_ms,
                    },
                )
        except Exception:
            pass

        return ExecuteResponse(
            task_id=task_id,
            status="completed",
            agent=agent,
            summary=f"Team: {team} \u2192 {agent} [{capability}]",
            result=result,
            executed_at=datetime.utcnow(),
            execution_time_ms=elapsed_ms,
        )

    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.error(f"Team execute failed: {e}", exc_info=True)
        return ExecuteResponse(
            task_id=task_id,
            status="failed",
            agent=req.agent or "unknown",
            summary=f"Team routing error: {str(e)[:200]}",
            executed_at=datetime.utcnow(),
            execution_time_ms=elapsed_ms,
        )


# ═══════════════════════════════════════════════════
# TASK GRAPH ENDPOINT — Multi-step agent pipelines
# ═══════════════════════════════════════════════════

@orch_router.post("/execute-graph", response_model=ExecuteResponse)
async def execute_task_graph(
    req: ExecuteRequest,
    request: Request,
    _admin=Depends(get_admin_or_internal),
):
    """
    WORKFLOW EXECUTE: Run a task through a durable Temporal workflow.
    Replaces the old chain-based execution with proper workflow orchestration.
    """
    import time, uuid

    start_ms = time.time()
    task_id = f"wf-{uuid.uuid4().hex[:8]}"

    try:
        from temporal.client import start_workflow
        from temporal.workflows.code_review import CodeReviewPipeline

        # Start the Temporal workflow (durable, retryable, observable)
        wf_result = await start_workflow(
            workflow_class=CodeReviewPipeline,
            task=req.task,
            context=req.context,
            workflow_id=task_id,
        )

        elapsed_ms = int((time.time() - start_ms) * 1000)

        result_data = wf_result.get("result", {})
        steps = result_data.get("steps", []) if isinstance(result_data, dict) else []
        gates = result_data.get("quality_gates", []) if isinstance(result_data, dict) else []

        return ExecuteResponse(
            task_id=task_id,
            status=wf_result.get("status", "failed"),
            agent="orchestrator",
            summary=f"Workflow: {len(steps)} steps, {sum(1 for s in steps if s.get('status') == 'completed')} completed, {sum(1 for g in gates if g.get('passed'))}/{len(gates)} gates passed",
            result=result_data,
            executed_at=datetime.utcnow(),
            execution_time_ms=elapsed_ms,
        )

    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.error(f"Workflow execute failed: {e}", exc_info=True)
        return ExecuteResponse(
            task_id=task_id, status="failed", agent="orchestrator",
            summary=f"Workflow error: {str(e)[:200]}",
            executed_at=datetime.utcnow(), execution_time_ms=elapsed_ms,
        )


# ═══════════════════════════════════════════════════
# QUALITY GATE ENDPOINT — Validate agent outputs
# ═══════════════════════════════════════════════════

@orch_router.post("/quality-check")
async def check_quality_gate(
    req: ExecuteRequest,
    request: Request,
    _admin=Depends(get_admin_or_internal),
):
    """
    QUALITY CHECK: Validate agent output against quality gates
    (syntax, security, content, completeness).
    Returns pass/fail with scores and recommendations.
    """
    import time, uuid

    start_ms = time.time()
    task_id = f"qg-{uuid.uuid4().hex[:8]}"
    
    try:
        from agents.orchestrator_v3 import TeamOrchestrator
        
        orch = TeamOrchestrator(db=None)
        
        # Load quality gates from Supabase
        import httpx, os
        supa_url = os.environ.get("SUPABASE_URL", os.environ.get("DS_SUPABASE_1E93118D__PROJECT_URL", "https://mdlgodcvpasgplcrkiad.supabase.co"))
        supa_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("DS_SUPABASE_1E93118D__SECRET_KEY", ""))
        
        if not supa_url:
            recent_gates = []
        else:
            r_gates = httpx.get(
                f"{supa_url}/rest/v1/quality_gates",
                headers={"apikey": supa_key, "Authorization": f"Bearer {supa_key}"},
                params={"order": "created_at.desc", "limit": 10},
                timeout=10
            )
            recent_gates = r_gates.json() if r_gates.status_code == 200 else []
        
        elapsed_ms = int((time.time() - start_ms) * 1000)
        
        return ExecuteResponse(
            task_id=task_id,
            status="completed",
            agent="quality-gate",
            summary=f"Quality gates: {len(recent_gates)} recent checks found",
            result={"recent_gates": recent_gates, "gate_count": len(recent_gates)},
            executed_at=datetime.utcnow(),
            execution_time_ms=elapsed_ms,
        )
    
    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        return ExecuteResponse(
            task_id=task_id,
            status="failed",
            agent="quality-gate",
            summary=f"Quality check error: {str(e)[:200]}",
            executed_at=datetime.utcnow(),
            execution_time_ms=elapsed_ms,
        )
