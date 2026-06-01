"""
MCP Router — Model Context Protocol Integration für NeXifyAI.

Alle externen Services (GitHub, Vercel, Supabase, Cloudflare, NeXify AI, MongoDB, Resend, Revolut)
werden über MCP-Protokoll (JSON-RPC 2.0) angebunden. Jeder Service registriert Tools,
die von Agenten über den Orchestrator aufgerufen werden.

Endpunkte:
  POST /mcp/rpc          — JSON-RPC 2.0 Entrypoint
  GET  /mcp/tools        — Alle registrierten Tools auflisten
  GET  /mcp/tools/{name} — Tool-Detail mit Schema
  POST /mcp/tools/{name}/call — Direkter Tool-Aufruf
  GET  /mcp/health       — MCP-Status + verbundene Services
"""

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger("nexifyai.mcp")
mcp_router = APIRouter(prefix="/mcp", tags=["mcp"])

# ──────────────────────────────────────────────
# MCP TOOL REGISTRY
# ──────────────────────────────────────────────

MCP_TOOLS: Dict[str, dict] = {}


def register_mcp_tool(
    name: str,
    description: str,
    service: str,
    endpoint: str,
    method: str = "POST",
    input_schema: dict = None,
    auth_env: str = None,
    priority: str = "P1"
):
    """Registriere ein MCP-Tool im zentralen Registry."""
    MCP_TOOLS[name] = {
        "name": name,
        "description": description,
        "service": service,
        "endpoint": endpoint,
        "method": method,
        "input_schema": input_schema or {"type": "object", "properties": {}},
        "auth_env": auth_env,
        "priority": priority,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    logger.info(f"MCP Tool registriert: {name} ({service})")
    return MCP_TOOLS[name]


# ──────────────────────────────────────────────
# REGISTER ALLE SERVICES ALS MCP TOOLS
# ──────────────────────────────────────────────

# --- Qdrant / Brain ---
register_mcp_tool(
    name="brain.search",
    description="Semantische Suche im NeXifyAI Brain (Qdrant nexifyai_brain)",
    service="qdrant",
    endpoint="http://localhost:6333/collections/nexifyai_brain/points/search",
    method="POST",
    input_schema={
        "type": "object",
        "properties": {
            "vector": {"type": "array", "items": {"type": "number"}, "description": "4096-dim Embedding"},
            "limit": {"type": "integer", "default": 10},
            "query_filter": {"type": "object", "description": "Payload-Filter (category, agent_id, etc.)"},
        },
        "required": ["vector"],
    },
    priority="P0",
)

register_mcp_tool(
    name="brain.write",
    description="Wissenseintrag ins NeXifyAI Brain schreiben",
    service="qdrant",
    endpoint="http://localhost:6333/collections/nexifyai_brain/points?wait=true",
    method="PUT",
    input_schema={
        "type": "object",
        "properties": {
            "payload": {"type": "object"},
            "vector": {"type": "array", "items": {"type": "number"}},
        },
    },
    priority="P0",
)

register_mcp_tool(
    name="brain.scroll",
    description="Brain-Inhalt durchscrollen (Inventory, Audit)",
    service="qdrant",
    endpoint="http://localhost:6333/collections/nexifyai_brain/points/scroll",
    method="POST",
    input_schema={
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "default": 50},
            "filter": {"type": "object"},
        },
    },
    priority="P0",
)

# --- GitHub ---
register_mcp_tool(
    name="github.list_repos",
    description="GitHub-Repositories auflisten",
    service="github",
    endpoint="https://api.github.com/user/repos",
    method="GET",
    auth_env="DS_GITHUB_35B6CCD0__TOKEN",
    priority="P0",
)

register_mcp_tool(
    name="github.create_issue",
    description="GitHub-Issue erstellen",
    service="github",
    endpoint="https://api.github.com/repos/{owner}/{repo}/issues",
    method="POST",
    auth_env="DS_GITHUB_35B6CCD0__TOKEN",
    input_schema={
        "type": "object",
        "properties": {
            "owner": {"type": "string"},
            "repo": {"type": "string"},
            "title": {"type": "string"},
            "body": {"type": "string"},
            "labels": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["owner", "repo", "title"],
    },
    priority="P0",
)

# --- Vercel ---
register_mcp_tool(
    name="vercel.list_projects",
    description="Vercel-Projekte auflisten",
    service="vercel",
    endpoint="https://api.vercel.com/v9/projects",
    method="GET",
    auth_env="DS_VERCEL_F2F9EC1F__TOKEN",
    priority="P0",
)

register_mcp_tool(
    name="vercel.list_deployments",
    description="Deployments eines Vercel-Projekts abrufen",
    service="vercel",
    endpoint="https://api.vercel.com/v9/deployments",
    method="GET",
    auth_env="DS_VERCEL_F2F9EC1F__TOKEN",
    input_schema={
        "type": "object",
        "properties": {
            "projectId": {"type": "string"},
            "limit": {"type": "integer", "default": 10},
        },
    },
    priority="P0",
)

# --- Supabase ---
register_mcp_tool(
    name="supabase.query",
    description="Supabase-Datenbankabfrage (REST)",
    service="supabase",
    endpoint="{SUPABASE_URL}/rest/v1/{table}",
    method="GET",
    auth_env="DS_SUPABASE_1E93118D__PUBLISHABLE_KEY",
    input_schema={
        "type": "object",
        "properties": {
            "table": {"type": "string"},
            "select": {"type": "string", "default": "*"},
            "limit": {"type": "integer", "default": 10},
        },
        "required": ["table"],
    },
    priority="P0",
)

# --- MongoDB ---
register_mcp_tool(
    name="mongodb.find",
    description="MongoDB-Dokumente abrufen",
    service="mongodb",
    endpoint="mongodb://localhost:27017",
    method="DB",
    auth_env="DS_MONGODB_80FC6526__URI",
    priority="P1",
)

# --- Resend (Email) ---
register_mcp_tool(
    name="resend.send",
    description="E-Mail über Resend versenden",
    service="resend",
    endpoint="https://api.resend.com/emails",
    method="POST",
    auth_env="DS_RESEND_443B8456__API_KEY",
    input_schema={
        "type": "object",
        "properties": {
            "from": {"type": "string"},
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "html": {"type": "string"},
        },
        "required": ["from", "to", "subject"],
    },
    priority="P2",
)

# --- Cloudflare ---
register_mcp_tool(
    name="cloudflare.purge_cache",
    description="Cloudflare-Cache purgen",
    service="cloudflare",
    endpoint="https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache",
    method="POST",
    auth_env="DS_CLOUDFLARE_57D167E2__API_TOKEN",
    priority="P1",
)

# --- Agent Orchestration ---
register_mcp_tool(
    name="orchestrator.execute",
    description="Agent-Task im NCEL ausführen",
    service="nexifyai",
    endpoint="http://localhost:8001/api/orchestration/execute",
    method="POST",
    input_schema={
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "task": {"type": "string"},
            "context": {"type": "object"},
        },
        "required": ["agent", "task"],
    },
    priority="P0",
)

# --- Health (lokal) ---
register_mcp_tool(
    name="system.health",
    description="System-Health aller internen Services",
    service="nexifyai",
    endpoint="http://localhost:8001/api/health",
    method="GET",
    priority="P1",
)


# ──────────────────────────────────────────────
# MCP ENDPUNKTE
# ──────────────────────────────────────────────

@mcp_router.get("/health")
async def mcp_health():
    """MCP-Router Health + Service-Übersicht."""
    services = {}
    for tool in MCP_TOOLS.values():
        svc = tool["service"]
        if svc not in services:
            services[svc] = {"tools": 0, "priority": tool["priority"]}
        services[svc]["tools"] += 1
    
    return {
        "status": "ok",
        "protocol": "mcp-v1",
        "tools_registered": len(MCP_TOOLS),
        "services": services,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp_router.get("/tools")
async def list_tools(service: str = None, priority: str = None):
    """Alle registrierten MCP-Tools auflisten (optional filterbar)."""
    tools = list(MCP_TOOLS.values())
    if service:
        tools = [t for t in tools if t["service"] == service]
    if priority:
        tools = [t for t in tools if t["priority"] == priority]
    
    return {
        "count": len(tools),
        "total": len(MCP_TOOLS),
        "tools": [
            {
                "name": t["name"],
                "service": t["service"],
                "description": t["description"],
                "priority": t["priority"],
                "input_schema": t["input_schema"],
            }
            for t in tools
        ],
    }


@mcp_router.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    """Einzelnes MCP-Tool mit vollständigem Schema."""
    if tool_name not in MCP_TOOLS:
        raise HTTPException(404, f"Tool nicht gefunden: {tool_name}")
    return MCP_TOOLS[tool_name]


@mcp_router.post("/tools/{tool_name}/call")
async def call_tool(tool_name: str, body: dict):
    """Direkter Tool-Aufruf via MCP."""
    if tool_name not in MCP_TOOLS:
        raise HTTPException(404, f"Tool nicht gefunden: {tool_name}")
    
    tool = MCP_TOOLS[tool_name]
    start = time.monotonic()
    
    # Auth-Header aus Env holen
    headers = {"Content-Type": "application/json"}
    if tool["auth_env"]:
        token = os.environ.get(tool["auth_env"], "")
        if token:
            headers["Authorization"] = f"Bearer {token}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            url = tool["endpoint"]
            
            # URL-Parameter ersetzen ({owner}, {repo}, etc.)
            if tool["method"] == "GET":
                resp = await client.get(url, headers=headers)
            elif tool["method"] == "PUT":
                resp = await client.put(url, json=body, headers=headers)
            else:
                resp = await client.post(url, json=body, headers=headers)
        
        latency_ms = int((time.monotonic() - start) * 1000)
        
        return {
            "tool": tool_name,
            "status": resp.status_code,
            "latency_ms": latency_ms,
            "result": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text[:1000],
        }
    
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        return {
            "tool": tool_name,
            "status": "error",
            "latency_ms": latency_ms,
            "error": str(e),
        }


@mcp_router.post("/rpc")
async def mcp_jsonrpc(request: Request):
    """JSON-RPC 2.0 Entrypoint — Model Context Protocol Standard."""
    body = await request.json()
    
    rpc_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params", {})
    
    start = time.monotonic()
    
    # Method dispatch
    if method == "tools/list":
        result = await list_tools()
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = await call_tool(tool_name, arguments)
    elif method == "tools/detail":
        tool_name = params.get("name", "")
        result = await get_tool(tool_name)
    elif method == "health":
        result = await mcp_health()
    else:
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    
    latency_ms = int((time.monotonic() - start) * 1000)
    
    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": result,
        "meta": {"latency_ms": latency_ms, "service": "nexifyai-mcp"},
    }


logger.info(f"MCP Router initialisiert: {len(MCP_TOOLS)} Tools registriert")
