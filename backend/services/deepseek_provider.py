"""
NeXifyAI — OpenRouter LLM Provider (DeepSeek V4 Flash)
OpenRouter = Primary Master + alle Sub-Agenten. Arcee AI = Fallback.
"""
import os
import json
import logging
from typing import Optional, AsyncGenerator

import httpx

logger = logging.getLogger("nexifyai.services.openrouter")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")


def is_configured() -> bool:
    return bool(OPENROUTER_API_KEY)


async def chat_completion(
    messages: list,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    stream: bool = False
) -> dict:
    """Non-streaming chat completion via OpenRouter."""
    if not OPENROUTER_API_KEY:
        return {"error": "OPENROUTER_API_KEY nicht konfiguriert"}

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://nexifyai.de",
                    "X-Title": "NeXifyAI"
                },
                json={
                    "model": model or OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return {"content": content, "usage": usage, "model": model or OPENROUTER_MODEL}
            logger.error(f"OpenRouter error {resp.status_code}: {resp.text[:300]}")
            return {"error": f"OpenRouter API Fehler ({resp.status_code})"}
    except Exception as e:
        logger.error(f"OpenRouter exception: {e}")
        return {"error": str(e)}


async def stream_completion(
    messages: list,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4096
) -> AsyncGenerator[str, None]:
    """Streaming chat completion via OpenRouter. Yields content chunks."""
    if not OPENROUTER_API_KEY:
        yield json.dumps({"error": "OPENROUTER_API_KEY nicht konfiguriert"})
        return

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://nexifyai.de",
                    "X-Title": "NeXifyAI"
                },
                json={
                    "model": model or OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                }
            ) as resp:
                if resp.status_code != 200:
                    error_body = await resp.aread()
                    yield json.dumps({"error": f"OpenRouter ({resp.status_code}): {error_body.decode()[:300]}"})
                    return
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"OpenRouter stream error: {e}")
        yield json.dumps({"error": str(e)})


async def invoke_agent(
    agent_name: str,
    agent_role: str,
    system_prompt: str,
    user_message: str,
    context: str = "",
    model: str = None,
    temperature: float = 0.5
) -> dict:
    """Invoke a sub-agent with OpenRouter. Returns the agent's response."""
    full_system = f"""Du bist {agent_name}, ein spezialisierter KI-Agent im NeXifyAI-Team.
Rolle: {agent_role}
Arbeitssprache: Deutsch
Qualitätsstandard: Professionell, präzise, handlungsorientiert.

{system_prompt}"""

    messages = [{"role": "system", "content": full_system}]
    if context:
        messages.append({"role": "system", "content": f"[KONTEXT]\n{context}\n[/KONTEXT]"})
    messages.append({"role": "user", "content": user_message})

    result = await chat_completion(messages, model=model, temperature=temperature, max_tokens=6000)
    if "error" in result:
        return {"agent": agent_name, "error": result["error"]}
    return {
        "agent": agent_name,
        "role": agent_role,
        "response": result["content"],
        "model": result.get("model", OPENROUTER_MODEL),
        "usage": result.get("usage", {})
    }
