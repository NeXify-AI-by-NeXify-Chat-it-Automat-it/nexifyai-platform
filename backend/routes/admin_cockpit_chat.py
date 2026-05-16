"""
POST /api/admin/chat — Admin Cockpit Chat Endpoint
SSE-Streaming via Cambo 9Router (OpenRouter Fallback), Supabase Auth + Backend JWT Fallback
Erstellt: 08.05.2026 für AdminCockpit v2
"""
import os
import json
import logging
import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger("nexifyai.routes.admin_cockpit_chat")

router = APIRouter(prefix="/api/admin", tags=["admin-cockpit-chat"])

# ── Env ──────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("CAMBRO_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
OPENROUTER_BASE_URL = os.getenv("CAMBRO_BASE_URL", os.getenv("OPENROUTER_BASE_URL", "https://ai-router.nexifyai.cloud/v1"))
OPENROUTER_MODEL = os.getenv("CAMBRO_DEFAULT_MODEL", os.getenv("OPENROUTER_MODEL", "ds/deepseek-v4-pro-max"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "p.courbois@icloud.com")

# ── Models ────────────────────────────────────────
class AdminChatRequest(BaseModel):
    message: str
    conversation_id: str = ""
    history: list = []

# ── Auth Helper ───────────────────────────────────
async def get_admin_session(request: Request) -> dict:
    """
    Supabase-first auth, Backend JWT fallback.
    Returns admin dict with email, role.
    """
    # 1) Try Supabase session token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Try Supabase GoTrue verification
        try:
            supabase_url = os.getenv("ALT_SUPABASE_URL", "http://localhost:8002")
            supabase_key = os.getenv("ALT_SUPABASE_SERVICE_ROLE_KEY", "")
            if supabase_url and supabase_key:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        f"{supabase_url}/auth/v1/user",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "apikey": supabase_key,
                        },
                    )
                    if resp.status_code == 200:
                        user_data = resp.json()
                        email = user_data.get("email", "")
                        if email == ADMIN_EMAIL:
                            return {"email": email, "role": "admin"}
        except Exception as e:
            logger.debug(f"Supabase auth attempt failed: {e}")

        # 2) Fallback: Backend JWT verification
        try:
            from routes.shared import decode_token
            payload = decode_token(token)
            if payload and payload.get("role") == "admin":
                return {"email": payload.get("email", ""), "role": "admin"}
        except Exception as e:
            logger.debug(f"JWT fallback failed: {e}")

    raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/chat", operation_id="admin_cockpit_chat_v2")
async def admin_cockpit_chat(body: AdminChatRequest, request: Request):
    """
    Admin Cockpit Chat — SSE-Streaming via Cambo 9Router.
    Lightweight version of nexify-ai/chat for the new AdminCockpit.
    """
    admin = await get_admin_session(request)

    conversation_id = body.conversation_id or f"acp_{os.urandom(6).hex()}"

    # Build messages from history + new message
    messages = []
    for h in body.history[-30:]:  # Last 30 messages for context
        if isinstance(h, dict) and h.get("role") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": body.message})

    # System prompt
    system_prompt = {
        "role": "system",
        "content": (
            "Du bist der NeXifyAI Admin Assistant. Du unterstützt Pascal Courbois (CEO) "
            "bei der Verwaltung der NeXifyAI-Plattform. Antworte präzise, technisch und "
            "auf Deutsch. Nutze Fettschrift für wichtige Punkte. Fasse Daten in Listen "
            "zusammen. Bei Problemen: Lösungsorientiert, kein Geschwafel. "
            f"Admin: {admin.get('email', 'unknown')}. "
            "Du hast Zugriff auf alle System-Metriken, Kundendaten und Backend-Routen."
        ),
    }

    llm_messages = [system_prompt] + messages

    async def stream():
        full_response = ""
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://www.nexify-automate.com",
                        "X-Title": "NeXifyAI Admin Cockpit",
                    },
                    json={
                        "model": OPENROUTER_MODEL,
                        "messages": llm_messages,
                        "stream": True,
                        "temperature": 0.5,
                        "max_tokens": 6000,
                    },
                ) as resp:
                    if resp.status_code != 200:
                        err = await resp.aread()
                        yield f"data: {json.dumps({'error': f'LLM Error {resp.status_code}'})}\n\n"
                        return
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        chunk = line[6:]
                        if chunk.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_response += content
                                yield f"data: {json.dumps({'content': content, 'conversation_id': conversation_id})}\n\n"
                        except json.JSONDecodeError:
                            continue
            yield f"data: {json.dumps({'content': '', 'conversation_id': conversation_id, 'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Admin chat stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
