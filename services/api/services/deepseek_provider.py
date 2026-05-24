"""
DEPRECATED: Wird durch services/langchain_config.py ersetzt.
            ChatOpenAI(model="deepseek/deepseek-v4-flash", ...) via OpenRouter.
            Entfernung geplant: 2026-06-21
"""

"""
NeXifyAI — Cambo 9Router LLM Provider (Zentrale LLM-Infrastruktur).
ALLE Agenten-Calls laufen über ai-router.nexifyai.cloud.
OpenRouter = Legacy-Fallback. Arcee AI = Dritt-Fallback.
"""
import os, json, logging
from typing import Optional, AsyncGenerator

import httpx

logger = logging.getLogger("nexifyai.services.llm")

CAMRO_API_KEY = os.environ.get("CAMBRO_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))
CAMRO_BASE_URL = os.environ.get("CAMBRO_BASE_URL", "https://ai-router.nexifyai.cloud/v1")
CAMRO_DEFAULT_MODEL = os.environ.get("CAMRO_DEFAULT_MODEL", "ds/deepseek-v4-pro-max")

# Legacy compat
OPENROUTER_API_KEY = CAMRO_API_KEY
OPENROUTER_BASE_URL = CAMRO_BASE_URL
OPENROUTER_MODEL = CAMRO_DEFAULT_MODEL


def is_configured() -> bool:
    return bool(CAMRO_API_KEY)


async def chat_completion(
    messages: list, model: str = None, temperature: float = 0.7,
    max_tokens: int = 4096, stream: bool = False
) -> dict:
    """Chat completion via Cambo 9Router."""
    if not CAMRO_API_KEY:
        return {"error": "CAMBRO_API_KEY nicht konfiguriert"}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{CAMRO_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {CAMRO_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or CAMRO_DEFAULT_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
            )
            if resp.status_code != 200:
                logger.error(f"Cambo error {resp.status_code}: {resp.text[:300]}")
                return {"error": f"Cambo API Fehler ({resp.status_code})"}
            
            # Parse SSE response
            text = resp.text.strip()
            if text.endswith("data: [DONE]"):
                text = text[:-(len("data: [DONE]"))].strip()
            
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                return {"error": f"JSON parse: {str(e)[:200]}"}
            
            choices = data.get("choices", [])
            if not choices:
                return {"error": "No choices in response"}
            
            msg = choices[0].get("message", {})
            content = msg.get("content", "")
            if not content and msg.get("reasoning_content"):
                content = msg.get("reasoning_content", "")
            
            return {
                "content": content,
                "usage": data.get("usage", {}),
                "model": data.get("model", ""),
                "reasoning": msg.get("reasoning_content", ""),
                "tool_calls": msg.get("tool_calls", []),
            }
    except Exception as e:
        logger.error(f"Cambo exception: {e}")
        return {"error": str(e)}


async def stream_completion(
    messages: list, model: str = None, temperature: float = 0.7,
    max_tokens: int = 4096
) -> AsyncGenerator[str, None]:
    """Streaming via Cambo — passthrough for now (Cambo returns complete SSE)."""
    if not CAMRO_API_KEY:
        yield json.dumps({"error": "CAMBRO_API_KEY nicht konfiguriert"})
        return

    try:
        result = await chat_completion(messages, model, temperature, max_tokens, stream=False)
        if "error" in result:
            yield json.dumps(result)
        else:
            yield json.dumps({"choices": [{"delta": {"content": result.get("content", "")}}]})
    except Exception as e:
        yield json.dumps({"error": str(e)})
