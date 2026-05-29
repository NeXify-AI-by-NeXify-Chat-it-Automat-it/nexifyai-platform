"""
NeXifyAI — Model Router (OpenRouter ONLY)
NUR OpenRouter: https://openrouter.ai/api/v1
NUR Modell: deepseek/deepseek-v4-flash
Alle Tasks nutzen dasselbe Modell. Unterschiedliche Temperaturen pro Task-Typ.

NUR OpenRouter: https://openrouter.ai/api/v1
"""
import os, json, time, logging
from typing import Optional, AsyncGenerator
from dataclasses import dataclass, field

logger = logging.getLogger("nexifyai.model_router")

# ═══ KONFIGURATION ═══
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "deepseek/deepseek-v4-flash"

# Capability → Temperatur
CAPABILITY_CONFIG = {
    "chat":        {"temperature": 0.7, "max_tokens": 2048},
    "code":        {"temperature": 0.2, "max_tokens": 4096},
    "analyze":     {"temperature": 0.3, "max_tokens": 4096},
    "plan":        {"temperature": 0.3, "max_tokens": 2048},
    "classify":    {"temperature": 0.0, "max_tokens": 1024},
    "summarize":   {"temperature": 0.3, "max_tokens": 2048},
    "extract":     {"temperature": 0.0, "max_tokens": 4096},
    "default":     {"temperature": 0.7, "max_tokens": 2048},
}


async def complete(
    messages: list, system_prompt: str = "",
    capability: str = "default", max_tokens: int = None,
    temperature: float = None, tools: list = None,
    response_format: dict = None
) -> dict:
    """Single completion via OpenRouter. Alle Tasks nutzen deepseek-v4-flash."""
    if not OPENROUTER_API_KEY:
        return {"error": "Model Router: OPENROUTER_API_KEY nicht konfiguriert"}

    cfg = CAPABILITY_CONFIG.get(capability, CAPABILITY_CONFIG["default"])
    temp = temperature if temperature is not None else cfg["temperature"]
    tokens = max_tokens if max_tokens is not None else cfg["max_tokens"]

    import httpx

    msgs = []
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})
    msgs.extend(messages)

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": msgs,
        "max_tokens": tokens,
        "temperature": temp,
    }
    if tools:
        payload["tools"] = tools
    if response_format:
        payload["response_format"] = response_format

    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload
            )

            latency = (time.time() - start) * 1000

            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}: {resp.text[:300]}"}

            data = resp.json()
            if "error" in data:
                return {"error": data["error"].get("message", str(data["error"]))}

            choices = data.get("choices", [])
            if not choices:
                return {"error": "No choices in response"}

            msg = choices[0].get("message", {})
            return {
                "content": msg.get("content", ""),
                "reasoning_content": msg.get("reasoning_content", ""),
                "tool_calls": msg.get("tool_calls", []),
                "usage": data.get("usage", {}),
                "finish_reason": choices[0].get("finish_reason", ""),
                "model": data.get("model", OPENROUTER_MODEL),
                "latency_ms": round(latency, 1),
            }
    except Exception as e:
        logger.error(f"OpenRouter exception: {e}")
        return {"error": str(e)}


def get_info() -> dict:
    return {
        "provider": "OpenRouter",
        "model": OPENROUTER_MODEL,
        "base_url": OPENROUTER_BASE_URL,
        "configured": bool(OPENROUTER_API_KEY),
    }