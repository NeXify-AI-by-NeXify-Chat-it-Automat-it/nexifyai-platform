"""
GitHub Webhook → Agent Routing Integration.
Erweitert bestehende webhook_routes.py um Agent-Dispatching.
"""
import logging
from routes.webhook_routes import router as webhook_router
from routes.webhook_routes import _store_event
from fastapi import APIRouter, Request, HTTPException

logger = logging.getLogger("nexifyai.webhooks.agent")

# === AGENT ROUTING WEBHOOK ENDPOINT ===
agent_webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks-agent"])


@agent_webhook_router.post("/github/agent")
async def github_webhook_with_agents(request: Request):
    """
    GitHub Webhook Receiver mit Agent-Dispatching.
    
    Workflow:
    1. Empfange GitHub-Event
    2. Speichere in MongoDB (_store_event)
    3. Route an zuständige Agenten (orchestrator_v2)
    4. Führe Agenten asynchron aus
    5. Logge Ergebnisse
    
    Headers:
      X-GitHub-Event: push, pull_request, etc.
      X-Hub-Signature-256: sha256=<hmac>
    """
    from agents.orchestrator_v2 import router as agent_router
    
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    delivery_id = request.headers.get("X-GitHub-Delivery-ID", "unknown")
    
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # HMAC-Verifikation (vom bestehenden webhook_routes.code)
    import hashlib, hmac, os
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").strip()
    if secret:
        signature = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(secret.encode(), await request.body(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 1. Store event
    await _store_event("github", event_type, payload)
    
    # 2. Route to agents
    action = payload.get("action")
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else None
    
    agents = agent_router.route_webhook(event_type, action=action, branch=branch)
    
    logger.info(
        f"[Webhook-Agent] {delivery_id}: {event_type}/{action} → {agents}"
    )
    
    # 3. Execute agents asynchronously (fire and forget)
    # In production: dispatch to Celery/BullMQ/Hermes worker
    import asyncio
    for agent_name in agents:
        asyncio.create_task(_execute_agent(agent_name, event_type, payload, delivery_id))
    
    return {
        "received": True,
        "event": event_type,
        "delivery": delivery_id,
        "routed_to_agents": agents,
    }


async def _execute_agent(agent_name: str, event_type: str, payload: dict, delivery_id: str):
    """Execute a single agent for a webhook event."""
    try:
        # In production: call Hermes Gateway Agent API
        logger.info(f"[Agent-Exec] {delivery_id}: {agent_name} started for {event_type}")
        
        # Placeholder: actual agent execution via Hermes
        # result = await hermes_client.execute(agent_name, payload)
        
        # Log result
        from datetime import datetime, timezone
        from routes.shared import S
        await S.db.agent_executions.insert_one({
            "agent": agent_name,
            "event_type": event_type,
            "delivery_id": delivery_id,
            "payload": payload,
            "status": "triggered",
            "created_at": datetime.now(timezone.utc),
        })
        
        logger.info(f"[Agent-Exec] {delivery_id}: {agent_name} triggered")
    except Exception as e:
        logger.error(f"[Agent-Exec] {delivery_id}: {agent_name} failed: {e}")


# === HERMES GATEWAY INTEGRATION ENDPOINT ===
@agent_webhook_router.post("/hermes/orchestrate")
async def hermes_orchestrate(request: Request):
    """
    Hermes Gateway Orchestration Endpoint.
    
    POST /api/webhooks/hermes/orchestrate
    {
      "task": "Erstelle ein neues Tenant-Repo für open-notebook",
      "context": {"tenant": "open-notebook", "priority": "P0"},
      "delegated_from": "project-manager"
    }
    """
    from agents.orchestrator_v2 import router as agent_router
    
    body = await request.json()
    task = body.get("task", "")
    context = body.get("context", {})
    
    routing = await agent_router.route_task(task, context)
    
    return {
        "task": task,
        "routing": routing,
        "suggested_agent": routing.get("primary"),
        "all_matches": routing.get("agents", []),
    }
