"""
Admin Chat → Hermes Gateway Bridge
Verbindet den Admin Chat (Web UI) direkt mit dem Hermes Gateway,
sodass Pascal im Admin Chat mit mir (Hermes Agent) sprechen kann
— genau wie auf Telegram oder CLI.

Vorgehen:
Der bestehende Nexify AI Chat Endpoint wird modifiziert,
um Nachrichten an den Hermes Gateway (OpenAI-Compatible API)
weiterzuleiten statt sie intern zu verarbeiten.
"""

import json
import logging
import urllib.request
import urllib.error
import os

from fastapi import APIRouter, HTTPException, Request

from routes.shared import S

logger = logging.getLogger("nexifyai.routes.admin_chat")
router = APIRouter(prefix="/api/admin", tags=["admin_chat"])

# Gateway-Konfiguration
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://127.0.0.1:8642")
GATEWAY_API_KEY = os.environ.get("API_SERVER_KEY", "nxai_local_dev_api_2026")
GATEWAY_MODEL = "hermes-agent"


async def _gateway_chat(messages: list, session_id: str = None) -> dict:
    """Sendet Nachrichten an den Hermes Gateway und gibt Antwort zurück."""
    url = f"{GATEWAY_URL}/v1/chat/completions"
    
    payload = {
        "model": GATEWAY_MODEL,
        "messages": messages,
        "stream": False,
    }
    
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {GATEWAY_API_KEY}")
    if session_id:
        req.add_header("X-Hermes-Session-Id", session_id)
    req.data = json.dumps(payload).encode()
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        logger.error(f"Gateway HTTP {e.code}: {body}")
        raise HTTPException(502, f"Gateway-Fehler: {e.code}")
    except Exception as e:
        logger.error(f"Gateway connection failed: {e}")
        raise HTTPException(502, f"Gateway nicht erreichbar: {e}")


@router.post("/nexify-ai/chat")
async def admin_chat_gateway(request: Request):
    """Leitet Admin Chat Nachrichten an den Hermes Gateway weiter."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, "Ungültiges JSON")
    
    message = data.get("message", "").strip()
    session_id = data.get("session_id") or data.get("conversation_id")
    
    if not message:
        raise HTTPException(400, "Nachricht ist Pflichtfeld")
    
    # Baue Messages-Array für den Gateway
    gateway_messages = [{"role": "user", "content": message}]
    
    # Sende an Gateway
    gateway_response = await _gateway_chat(gateway_messages, session_id)
    
    # Extrahiere Antwort
    choices = gateway_response.get("choices", [])
    if not choices:
        raise HTTPException(502, "Keine Antwort vom Gateway")
    
    reply = choices[0].get("message", {}).get("content", "")
    
    # Extrahiere Session-ID aus Gateway-Response für Kontinuität
    response_session = gateway_response.get("id", session_id)
    
    return {
        "reply": reply,
        "session_id": response_session,
        "model": GATEWAY_MODEL,
    }
