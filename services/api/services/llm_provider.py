"""
DEPRECATED: Wird durch services/langchain_config.py ersetzt.
            Nutze get_llm_for_task(), create_llm_with_fallbacks() oder get_primary_llm().
            Migration: from services.langchain_config import get_llm_for_task
            Entfernung geplant: 2026-06-21
"""

"""
NeXifyAI — LLM Provider Abstraction Layer
OpenRouter (DeepSeek V4 Flash) = Primary. Emergent GPT = Fallback.
"""
import os
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("nexifyai.services.llm_provider")


@dataclass
class LLMMessage:
    role: str
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class LLMProvider:
    """Basis-Klasse für LLM-Provider."""

    async def chat(
        self,
        messages: List[LLMMessage],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = None,
    ) -> str:
        raise NotImplementedError

    async def chat_with_history(
        self,
        session_id: str,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        model: str = None,
    ) -> str:
        raise NotImplementedError

    def get_provider_name(self) -> str:
        raise NotImplementedError

    def clear_session(self, session_id: str):
        pass

    async def health_check(self) -> dict:
        """Provider-spezifischer Health-Check."""
        return {"status": "unknown"}


# ══════════════════════════════════════════
# OPENROUTER — PRIMÄRER PROVIDER (DeepSeek V4 Flash)
# ══════════════════════════════════════════

class OpenRouterProvider(LLMProvider):
    """
    PRIMÄRER Provider: OpenRouter (DeepSeek V4 Flash).
    OpenAI-kompatible API mit Retry-Logik und Audit-Trail.
    """

    MODELS = {
        "deepseek/deepseek-v4-flash": "DeepSeek V4 Flash (Standard)",
    }

    def __init__(self):
        self._api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        self._base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self._default_model = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
        self._sessions: Dict[str, list] = {}
        self._metrics = {"calls": 0, "errors": 0, "total_latency_ms": 0}
        self._max_retries = 3
        self._retry_base_delay = 1.0

    async def _call_api(self, messages: list, temperature: float, max_tokens: int, model: str) -> str:
        """API-Call mit Retry-Logik und Metriken."""
        import httpx

        target_model = model or self._default_model
        last_error = None

        for attempt in range(self._max_retries):
            start = time.monotonic()
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        f"{self._base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self._api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://nexifyai.de",
                            "X-Title": "NeXifyAI",
                        },
                        json={
                            "model": target_model,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                    )
                    latency = int((time.monotonic() - start) * 1000)
                    self._metrics["calls"] += 1
                    self._metrics["total_latency_ms"] += latency

                    if response.status_code == 429:
                        retry_after = float(response.headers.get("retry-after", self._retry_base_delay * (2 ** attempt)))
                        logger.warning(f"OpenRouter rate-limited (429), retry in {retry_after}s (attempt {attempt+1}/{self._max_retries})")
                        import asyncio
                        await asyncio.sleep(retry_after)
                        continue

                    if response.status_code >= 500:
                        logger.warning(f"OpenRouter server error {response.status_code}, retry (attempt {attempt+1}/{self._max_retries})")
                        import asyncio
                        await asyncio.sleep(self._retry_base_delay * (2 ** attempt))
                        continue

                    response.raise_for_status()
                    data = response.json()
                    choices = data.get("choices")
                    if not choices:
                        self._metrics["errors"] += 1
                        logger.error(f"OpenRouter API response ohne 'choices'-Feld: code={response.status_code}, body={response.text[:500]}")
                        import asyncio
                        await asyncio.sleep(self._retry_base_delay * (2 ** attempt))
                        last_error = f"API ohne 'choices': {response.text[:80]}"
                        continue
                    msg_obj = choices[0]["message"]
                    content = msg_obj.get("content")
                    # Reasoning models may put output in reasoning_content/reasoning when content is empty
                    if not content:
                        content = msg_obj.get("reasoning_content") or msg_obj.get("reasoning") or ""
                    logger.info(f"OpenRouter OK — model={target_model}, latency={latency}ms, tokens_used={data.get('usage', {}).get('total_tokens', '?')}")
                    return content or ""

            except httpx.TimeoutException:
                latency = int((time.monotonic() - start) * 1000)
                self._metrics["errors"] += 1
                last_error = f"Timeout nach {latency}ms"
                logger.warning(f"OpenRouter timeout (attempt {attempt+1}/{self._max_retries})")
                import asyncio
                await asyncio.sleep(self._retry_base_delay * (2 ** attempt))
            except httpx.HTTPStatusError as e:
                self._metrics["errors"] += 1
                last_error = f"HTTP {e.response.status_code}"
                logger.error(f"OpenRouter HTTP error: {e.response.status_code} — {e.response.text[:200]}")
                if e.response.status_code in (401, 403):
                    return "[OpenRouter Auth-Fehler: API-Key ungültig oder gesperrt]"
                break
            except Exception as e:
                self._metrics["errors"] += 1
                last_error = str(e)[:100]
                logger.error(f"OpenRouter connection error: {e}")
                import asyncio
                await asyncio.sleep(self._retry_base_delay * (2 ** attempt))

        self._metrics["errors"] += 1
        return f"[OpenRouter nicht erreichbar nach {self._max_retries} Versuchen: {last_error}]"

    async def chat(
        self,
        messages: List[LLMMessage],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = None,
    ) -> str:
        if not self._api_key:
            return "[OpenRouter nicht konfiguriert — OPENROUTER_API_KEY fehlt]"

        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend([m.to_dict() for m in messages])

        return await self._call_api(api_messages, temperature, max_tokens, model)

    async def chat_with_history(
        self,
        session_id: str,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        model: str = None,
    ) -> str:
        if not self._api_key:
            return "[OpenRouter nicht konfiguriert — OPENROUTER_API_KEY fehlt]"

        if session_id not in self._sessions:
            self._sessions[session_id] = []
            if system_prompt:
                self._sessions[session_id].append({"role": "system", "content": system_prompt})

        self._sessions[session_id].append({"role": "user", "content": user_message})

        result = await self._call_api(self._sessions[session_id], temperature, 2048, model)
        self._sessions[session_id].append({"role": "assistant", "content": result})

        if len(self._sessions[session_id]) > 42:
            system_msgs = [m for m in self._sessions[session_id] if m["role"] == "system"]
            other_msgs = [m for m in self._sessions[session_id] if m["role"] != "system"]
            self._sessions[session_id] = system_msgs + other_msgs[-40:]

        return result

    def get_provider_name(self) -> str:
        return "openrouter"

    def clear_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    async def health_check(self) -> dict:
        if not self._api_key:
            return {"status": "not_configured", "error": "OPENROUTER_API_KEY fehlt"}
        try:
            result = await self.chat(
                [LLMMessage(role="user", content="Antworte mit exakt einem Wort: OK")],
                system_prompt="Du bist ein Health-Check-Agent. Antworte nur mit OK.",
                temperature=0.0,
                max_tokens=10,
            )
            ok = "ok" in result.lower() and not result.startswith("[")
            return {
                "status": "healthy" if ok else "degraded",
                "response_sample": result[:50],
                "metrics": {**self._metrics},
            }
        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}

    def get_metrics(self) -> dict:
        avg = (self._metrics["total_latency_ms"] / self._metrics["calls"]) if self._metrics["calls"] else 0
        return {
            **self._metrics,
            "avg_latency_ms": round(avg),
            "error_rate": round(self._metrics["errors"] / max(self._metrics["calls"], 1), 3),
        }


# ══════════════════════════════════════════
# EMERGENT GPT — FALLBACK
# ══════════════════════════════════════════

class EmergentGPTProvider(LLMProvider):
    """
    FALLBACK-Provider: GPT via Emergent LLM Key.
    Aktiv nur wenn OPENROUTER_API_KEY nicht gesetzt.
    """

    def __init__(self):
        self._sessions = {}
        self._api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self._metrics = {"calls": 0, "errors": 0}

    async def chat(
        self,
        messages: List[LLMMessage],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = None,
    ) -> str:
        if not self._api_key:
            return "[LLM nicht verfügbar — kein API-Key konfiguriert]"

        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import secrets

        self._metrics["calls"] += 1
        try:
            session_id = f"chat_{secrets.token_hex(8)}"
            chat = LlmChat(
                api_key=self._api_key,
                session_id=session_id,
                system_message=system_prompt,
            )
            chat.with_model("openai", model or "deepseek/deepseek-v4-flash")

            last_user = ""
            for msg in messages:
                if msg.role == "user":
                    last_user = msg.content

            response = await chat.send_message(UserMessage(text=last_user or ""))
            return response
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Emergent GPT error: {e}")
            return f"[Emergent GPT Fehler: {str(e)[:100]}]"

    async def chat_with_history(
        self,
        session_id: str,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        model: str = None,
    ) -> str:
        if not self._api_key:
            return "[LLM nicht verfügbar — kein API-Key konfiguriert]"

        from emergentintegrations.llm.chat import LlmChat, UserMessage

        self._metrics["calls"] += 1
        try:
            if session_id not in self._sessions:
                chat = LlmChat(
                    api_key=self._api_key,
                    session_id=session_id,
                    system_message=system_prompt,
                )
                chat.with_model("openai", model or "deepseek/deepseek-v4-flash")
                self._sessions[session_id] = chat

            chat = self._sessions[session_id]
            response = await chat.send_message(UserMessage(text=user_message))
            return response
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Emergent GPT session error: {e}")
            return f"[Emergent GPT Fehler: {str(e)[:100]}]"

    def get_provider_name(self) -> str:
        return "emergent_gpt_fallback"

    def clear_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    async def health_check(self) -> dict:
        if not self._api_key:
            return {"status": "not_configured", "error": "OPENROUTER_API_KEY fehlt"}
        try:
            result = await self.chat(
                [LLMMessage(role="user", content="Antworte mit exakt einem Wort: OK")],
                system_prompt="Health-Check. Antworte nur mit OK.",
                temperature=0.0,
            )
            ok = "ok" in result.lower() and not result.startswith("[")
            return {"status": "healthy" if ok else "degraded", "response_sample": result[:50]}
        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}



# ══════════════════════════════════════════
# DEEPSEEK DIRECT — PRIMÄRER PROVIDER (Bot Fleet)
# ══════════════════════════════════════════

class DeepSeekDirectProvider(LLMProvider):
    """
    PRIMÄRER Provider: DeepSeek Direct API.
    OpenAI-kompatible API, dedizierter API-Key.
    Identische Schnittstelle wie OpenRouterProvider.
    """

    MODELS = {
        "deepseek-chat": "DeepSeek Chat (Standard, 1M Kontext)",
    }

    def __init__(self):
        self._api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        self._base_url = "https://api.deepseek.com/v1"
        self._default_model = "deepseek-chat"
        self._sessions: Dict[str, list] = {}
        self._metrics = {"calls": 0, "errors": 0, "total_latency_ms": 0}
        self._max_retries = 3
        self._retry_base_delay = 1.0

    async def _call_api(self, messages: list, temperature: float, max_tokens: int, model: str) -> str:
        """API-Call mit Retry-Logik und Metriken (identisch zu OpenRouterProvider)."""
        import httpx

        target_model = model or self._default_model
        last_error = None

        for attempt in range(self._max_retries):
            start = time.monotonic()
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        f"{self._base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self._api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": target_model,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                    )
                    latency = int((time.monotonic() - start) * 1000)
                    self._metrics["calls"] += 1
                    self._metrics["total_latency_ms"] += latency

                    if response.status_code == 429:
                        retry_after = float(response.headers.get("retry-after", self._retry_base_delay * (2 ** attempt)))
                        logger.warning(f"DeepSeek rate-limited (429), retry in {retry_after}s (attempt {attempt+1}/{self._max_retries})")
                        import asyncio
                        await asyncio.sleep(retry_after)
                        continue

                    if response.status_code >= 500:
                        logger.warning(f"DeepSeek server error {response.status_code}, retry (attempt {attempt+1}/{self._max_retries})")
                        import asyncio
                        await asyncio.sleep(self._retry_base_delay * (2 ** attempt))
                        continue

                    response.raise_for_status()
                    data = response.json()
                    choices = data.get("choices")
                    if not choices:
                        self._metrics["errors"] += 1
                        logger.error(f"DeepSeek API response ohne 'choices'-Feld: code={response.status_code}, body={response.text[:500]}")
                        import asyncio
                        await asyncio.sleep(self._retry_base_delay * (2 ** attempt))
                        last_error = f"API ohne 'choices': {response.text[:80]}"
                        continue
                    msg_obj = choices[0]["message"]
                    content = msg_obj.get("content")
                    if not content:
                        content = msg_obj.get("reasoning") or ""
                    logger.info(f"DeepSeek OK — model={target_model}, latency={latency}ms, tokens_used={data.get('usage', {}).get('total_tokens', '?')}")
                    return content or ""

            except httpx.TimeoutException:
                latency = int((time.monotonic() - start) * 1000)
                self._metrics["errors"] += 1
                last_error = f"Timeout nach {latency}ms"
                logger.warning(f"DeepSeek timeout (attempt {attempt+1}/{self._max_retries})")
                import asyncio
                await asyncio.sleep(self._retry_base_delay * (2 ** attempt))
            except httpx.HTTPStatusError as e:
                self._metrics["errors"] += 1
                last_error = f"HTTP {e.response.status_code}"
                logger.error(f"DeepSeek HTTP error: {e.response.status_code} — {e.response.text[:200]}")
                if e.response.status_code in (401, 403):
                    return "[DeepSeek Auth-Fehler: API-Key ungültig oder gesperrt]"
                break
            except Exception as e:
                self._metrics["errors"] += 1
                last_error = str(e)[:100]
                logger.error(f"DeepSeek connection error: {e}")
                import asyncio
                await asyncio.sleep(self._retry_base_delay * (2 ** attempt))

        self._metrics["errors"] += 1
        return f"[DeepSeek nicht erreichbar nach {self._max_retries} Versuchen: {last_error}]"

    async def chat(self, messages, system_prompt="", temperature=0.7, max_tokens=2048, model=None):
        if not self._api_key:
            return "[DeepSeek nicht konfiguriert]"
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend([m.to_dict() for m in messages])
        return await self._call_api(api_messages, temperature, max_tokens, model)

    async def chat_with_history(self, session_id, user_message, system_prompt="", temperature=0.7, model=None):
        if not self._api_key:
            return "[DeepSeek nicht konfiguriert]"
        if session_id not in self._sessions:
            self._sessions[session_id] = []
            if system_prompt:
                self._sessions[session_id].append({"role": "system", "content": system_prompt})
        self._sessions[session_id].append({"role": "user", "content": user_message})
        result = await self._call_api(self._sessions[session_id], temperature, 2048, model)
        self._sessions[session_id].append({"role": "assistant", "content": result})
        if len(self._sessions[session_id]) > 42:
            system_msgs = [m for m in self._sessions[session_id] if m["role"] == "system"]
            other_msgs = [m for m in self._sessions[session_id] if m["role"] != "system"]
            self._sessions[session_id] = system_msgs + other_msgs[-40:]
        return result

    def get_provider_name(self):
        return "deepseek_direct"

    def clear_session(self, session_id):
        self._sessions.pop(session_id, None)

    async def health_check(self):
        if not self._api_key:
            return {"status": "not_configured"}
        try:
            result = await self.chat(
                [LLMMessage(role="user", content="Antworte mit exakt einem Wort: OK")],
                system_prompt="Health-Check. Antworte nur mit OK.",
                temperature=0.0, max_tokens=10,
            )
            ok = "ok" in result.lower() and not result.startswith("[")
            return {"status": "healthy" if ok else "degraded", "response_sample": result[:50], "metrics": {**self._metrics}}
        except Exception as e:
            return {"status": "error", "error": str(e)[:100]}

    def get_metrics(self):
        avg = (self._metrics["total_latency_ms"] / self._metrics["calls"]) if self._metrics["calls"] else 0
        return {**self._metrics, "avg_latency_ms": round(avg), "error_rate": round(self._metrics["errors"] / max(self._metrics["calls"], 1), 3)}


# ══════════════════════════════════════════
# FACTORY
def create_llm_provider() -> LLMProvider:
    """
    OpenRouter Provider Factory.
    NUR OpenRouter: https://openrouter.ai/api/v1
    NUR Modell: deepseek/deepseek-v4-flash
    NUR OpenRouter (deepseek/deepseek-v4-flash).
    NUR OpenRouter (deepseek/deepseek-v4-flash).
    """
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "").strip()

    if not openrouter_key:
        logger.warning("OPENROUTER_API_KEY nicht konfiguriert. Nutze OpenRouterProvider ohne Key.")
        return OpenRouterProvider()

    logger.info("LLM-Provider: OpenRouter (deepseek/deepseek-v4-flash)")
    return OpenRouterProvider()


def get_provider_status(provider: LLMProvider) -> dict:
    """Provider-Status für Admin-Dashboard."""
    result = {
        "active_provider": "OpenRouter (deepseek/deepseek-v4-flash)",
        "configured": bool(os.environ.get("OPENROUTER_API_KEY", "").strip()),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "deepseek/deepseek-v4-flash",
        "no_fallback": True,
        "cambo_removed": "2026-05-29",
        "env_config": {
            "OPENROUTER_API_KEY": "***" if os.environ.get("OPENROUTER_API_KEY") else "not set",
            "OPENROUTER_MODEL": os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash"),
        },
    }

    if hasattr(provider, 'get_metrics'):
        result["metrics"] = provider.get_metrics()

    return result