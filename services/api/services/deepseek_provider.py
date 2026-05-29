"""
NeXifyAI — OpenRouter LLM Provider
NUR OpenRouter: https://openrouter.ai/api/v1
NUR Modell: deepseek/deepseek-v4-flash

Ersetzt: 9Router/Cambo ai-router.nexifyai.cloud (deprecated 2026-05-29)
"""
import os, json, logging
from typing import Optional, AsyncGenerator

import httpx

logger = logging.getLogger("nexifyai.services.llm")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "deepseek/deepseek-v4-flash"


def is_configured() -> bool:
    return bool(OPENROUTER_API_KEY)


async def chat_completion(
    messages: list, model: str = None, temperature: float = 0.7,
    max_tokens: int = 4096, stream: bool = False
) -> dict:
    """Chat completion via OpenRouter."""
    if not OPENROUTER_API_KEY:
        return {"error": "OPENROUTER_API_KEY nicht konfiguriert"}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
            )
            if resp.status_code != 200:
                logger.error(f"OpenRouter error {resp.status_code}: {resp.text[:300]}")
                return {"error": f"OpenRouter API Fehler ({resp.status_code})"}

            data = resp.json()
            if "error" in data:
                return {"error": data["error"].get("message", str(data["error"]))}

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
        logger.error(f"OpenRouter exception: {e}")
        return {"error": str(e)}


async def stream_completion(
    messages: list, model: str = None, temperature: float = 0.7,
    max_tokens: int = 4096
) -> AsyncGenerator[str, None]:
    """Streaming via OpenRouter."""
    if not OPENROUTER_API_KEY:
        yield json.dumps({"error": "OPENROUTER_API_KEY nicht konfiguriert"})
        return

    try:
        result = await chat_completion(messages, model, temperature, max_tokens, stream=False)
        if "error" in result:
            yield json.dumps(result)
        else:
            yield json.dumps({"choices": [{"delta": {"content": result.get("content", "")}}]})
    except Exception as e:
        yield json.dumps({"error": str(e)})
