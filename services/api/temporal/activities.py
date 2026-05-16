"""Temporal Activities — the actual agent execution units.

Each Activity is an idempotent, retry-safe unit of work.
They call the Cambo 9Router LLM provider for actual agent intelligence.
"""
import os, httpx, json, logging
from datetime import datetime, timezone
from temporalio import activity

from temporal.shared import AgentTask, AgentResult, QualityGateResult
from metrics import WORKFLOW_EXECUTIONS, WORKER_HEALTH
from dlq import push_to_dlq
from circuit_breaker import get_breaker


logger = logging.getLogger("nexifyai.temporal.activities")

# Circuit breakers for external services
cambo_breaker = get_breaker("cambo-9router", failure_threshold=5, recovery_timeout=30)

SUPABASE_URL = os.environ.get("SUPABASE_URL", os.environ.get("DS_SUPABASE_1E93118D__PROJECT_URL", "https://mdlgodcvpasgplcrkiad.supabase.co"))
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("DS_SUPABASE_1E93118D__SECRET_KEY", ""))

CAMBRO_URL = os.environ.get("CAMBRO_BASE_URL", os.environ.get("OPENROUTER_BASE_URL", "https://ai-router.nexifyai.cloud"))
CAMBRO_KEY = os.environ.get("DS_CAMBRO_158B458E__API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))


@activity.defn
async def execute_agent_task(task: AgentTask) -> AgentResult:
    """Execute a task via an agent through the Cambo 9Router."""
    import time
    start = time.time()
    wf_type = task.agent if hasattr(task, 'agent') else 'unknown'
    
    headers = {"Authorization": f"Bearer {CAMBRO_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "ds/deepseek-v4-pro",
        "messages": [
            {
                "role": "system",
                "content": f"You are {task.agent} (team: {task.team}, capability: {task.capability}). Execute the task. Deliver actionable output."
            },
            {"role": "user", "content": task.description}
        ],
        "temperature": 0.7,
    }
    
    try:
        r = cambo_breaker.call(
            lambda: httpx.post(
                f"{CAMBRO_URL}/v1/chat/completions",
                headers=headers, json=payload, timeout=60
            )
        )
        elapsed = int((time.time() - start) * 1000)
        
        if r.status_code == 200:
            raw = r.text
            # Cambo may append extra data after JSON (streaming remnants)
            # Find the last complete JSON object
            import re
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = r.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            # Some models put output in reasoning_content
            if not content:
                content = data.get("choices", [{}])[0].get("message", {}).get("reasoning_content", "")
            usage = data.get("usage", {})
            WORKFLOW_EXECUTIONS.labels(workflow_type=wf_type, status="completed").inc()
            return AgentResult(
                task_id=task.task_id,
                agent=task.agent,
                status="completed",
                summary=content[:200] if content else "No content in response",
                result={"output": content, "tokens": usage},
                execution_time_ms=elapsed,
            )
        else:
            body = r.text[:300]
            WORKFLOW_EXECUTIONS.labels(workflow_type=wf_type, status="failed").inc()
            import asyncio
            asyncio.ensure_future(push_to_dlq(
                workflow_id=task.task_id, task_id=task.task_id,
                source="activity.execute_agent_task", error=f"API error: {r.status_code}",
                context={"status": r.status_code, "agent": task.agent}
            ))
            return AgentResult(
                task_id=task.task_id,
                agent=task.agent,
                status="failed",
                summary=f"API error: {r.status_code} - {body}",
                execution_time_ms=elapsed,
            )
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        WORKFLOW_EXECUTIONS.labels(workflow_type=wf_type, status="failed").inc()
        import asyncio
        asyncio.ensure_future(push_to_dlq(
            workflow_id=task.task_id, task_id=task.task_id,
            source="activity.execute_agent_task", error=str(e)[:200],
            context={"agent": task.agent}
        ))
        return AgentResult(
            task_id=task.task_id,
            agent=task.agent,
            status="failed",
            summary=str(e)[:200],
            execution_time_ms=elapsed,
        )


@activity.defn
async def record_quality_gate(gate: QualityGateResult) -> dict:
    """Record a quality gate check in Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"status": "skipped", "reason": "no Supabase config"}
    
    try:
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/quality_gates",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "return=minimal",
            },
            json={
                "gate_type": gate.gate_type,
                "passed": gate.passed,
                "score": gate.score,
                "criteria": gate.criteria,
                "notes": gate.notes,
            },
            timeout=10
        )
        return {"status": "recorded" if r.status_code == 201 else f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


@activity.defn
async def log_task_execution(task_id: str, agent_id: str, status: str, 
                              output: dict = None) -> dict:
    """Log task execution to Supabase task_execution_log."""
    if not SUPABASE_URL:
        return {"status": "skipped"}
    
    try:
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/task_execution_log",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "return=minimal",
            },
            json={
                "task_id": task_id,
                "agent_id": agent_id,
                "status": status,
                "output": output or {},
            },
            timeout=10
        )
        return {"status": "logged" if r.status_code == 201 else f"HTTP {r.status_code}"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


@activity.defn
async def fetch_rules(agent_id: str) -> list:
    """Fetch applicable rules for an agent from Supabase rules_registry."""
    if not SUPABASE_URL:
        return []
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/rules_registry?or=(scope.eq.global"
        if agent_id:
            url += f",agent_id.eq.{agent_id}"
        url += ")&enabled=eq.true&order=priority.desc"
        
        r = httpx.get(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        }, timeout=10)
        
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        logger.warning(f"Fetch rules failed: {e}")
        return []
