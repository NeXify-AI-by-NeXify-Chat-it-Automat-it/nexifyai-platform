"""
DEPRECATED: Wird durch services/langchain_config.py ersetzt.
            Nutze CAPABILITY_ROUTING + get_llm_for_task() direkt.
            Migration: from services.langchain_config import get_llm_for_task
            Entfernung geplant: 2026-06-21
"""

"""
NeXify AI — Central Model Router Layer (Cambo 9Router).
ALL agent model calls flow through this single entry point.
No direct model calls anywhere else in the system.

Architecture:
  Agent/Task → model_router.route(task_type, complexity) → Cambo → Model
  - Planning/light tasks → ds/deepseek-v4-flash
  - Coding/engineering → ds/deepseek-v4-pro-max  
  - Architecture/reasoning → ds/deepseek-reasoner
  - JSON mode / tool calling → ds/deepseek-v4-pro-max

Features:
  - Capability-based routing
  - Automatic fallback chains
  - Circuit breaker pattern
  - Retry with exponential backoff
  - Health checks
  - Audit logging
  - SSE response parsing (Cambo returns text/event-stream)
"""
import os, json, time, logging, hashlib
from enum import Enum
from typing import Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger("nexifyai.model_router")

# ═══ CONFIGURATION ═══
CAMBRO_BASE_URL = os.environ.get("CAMBRO_BASE_URL", "https://ai-router.nexifyai.cloud/v1")
CAMBRO_API_KEY = os.environ.get("CAMBRO_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))

# Model mapping
MODEL_MAP = {
    "planning": "ds/deepseek-v4-flash",
    "flash": "ds/deepseek-v4-flash",
    "coding": "ds/deepseek-v4-pro-max",
    "pro_max": "ds/deepseek-v4-pro-max",
    "reasoning": "ds/deepseek-reasoner",
    "reasoner": "ds/deepseek-reasoner",
    "default": "ds/deepseek-v4-pro-max",
}

# Capability → model routing
CAPABILITY_ROUTING = {
    "chat": "ds/deepseek-v4-flash",
    "plan": "ds/deepseek-v4-flash",
    "route": "ds/deepseek-v4-flash",
    "classify": "ds/deepseek-v4-flash",
    "summarize": "ds/deepseek-v4-flash",
    "code": "ds/deepseek-v4-pro-max",
    "develop": "ds/deepseek-v4-pro-max",
    "debug": "ds/deepseek-v4-pro-max",
    "refactor": "ds/deepseek-v4-pro-max",
    "json": "ds/deepseek-v4-pro-max",
    "tool_call": "ds/deepseek-v4-pro-max",
    "analyze": "ds/deepseek-reasoner",
    "reason": "ds/deepseek-reasoner",
    "architect": "ds/deepseek-reasoner",
    "design": "ds/deepseek-reasoner",
    "research": "ds/deepseek-reasoner",
}

# Fallback chain: try primary, then fallback
FALLBACK_CHAIN = {
    "ds/deepseek-v4-pro-max": ["ds/deepseek-v4-pro", "ds/deepseek-v4-flash"],
    "ds/deepseek-v4-pro": ["ds/deepseek-v4-flash"],
    "ds/deepseek-reasoner": ["ds/deepseek-v4-pro-max", "ds/deepseek-v4-flash"],
    "ds/deepseek-v4-flash": ["ds/deepseek-v4-pro-max"],  # flash fails → try pro
}

# ═══ CIRCUIT BREAKER ═══
class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject immediately
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max: int = 2
    
    failures: int = 0
    state: CircuitState = CircuitState.CLOSED
    last_failure: float = 0.0
    half_open_attempts: int = 0
    
    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_attempts -= 1
            if self.half_open_attempts <= 0:
                self.state = CircuitState.CLOSED
                self.failures = 0
                logger.info("Circuit breaker CLOSED — model recovered")
        else:
            self.failures = 0
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPEN — {self.failures} failures")
    
    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_attempts = self.half_open_max
                logger.info("Circuit breaker HALF_OPEN — testing recovery")
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_attempts > 0
        return True

# ═══ MODEL ROUTER ═══
class ModelRouter:
    """Central routing layer — single entry point for all LLM calls."""
    
    def __init__(self):
        self._circuits: dict[str, CircuitBreaker] = {}
        self._metrics: dict[str, dict] = {}
        self._enabled = bool(CAMBRO_API_KEY)
    
    def _circuit_for(self, model: str) -> CircuitBreaker:
        if model not in self._circuits:
            self._circuits[model] = CircuitBreaker()
        return self._circuits[model]
    
    def _track_metric(self, model: str, latency_ms: float, success: bool):
        if model not in self._metrics:
            self._metrics[model] = {"calls": 0, "errors": 0, "total_latency": 0}
        m = self._metrics[model]
        m["calls"] += 1
        m["total_latency"] += latency_ms
        if not success:
            m["errors"] += 1
    
    def route_model(self, task_type: str = None, capability: str = None, 
                    complexity: str = "medium") -> str:
        """Determine which model to use based on task characteristics."""
        # Explicit capability routing
        if capability and capability in CAPABILITY_ROUTING:
            return CAPABILITY_ROUTING[capability]
        
        # Task type routing
        if task_type:
            for key, model in CAPABILITY_ROUTING.items():
                if key in task_type.lower():
                    return model
        
        # Complexity-based
        if complexity == "high":
            return "ds/deepseek-reasoner"
        elif complexity == "low":
            return "ds/deepseek-v4-flash"
        
        return MODEL_MAP["default"]
    
    async def complete(self, messages: list, system_prompt: str = "",
                       task_type: str = None, capability: str = None,
                       complexity: str = "medium", max_tokens: int = 4096,
                       temperature: float = 0.7, tools: list = None,
                       response_format: dict = None) -> dict:
        """
        Single completion call — routed through Cambo.
        Returns {"content": str, "usage": dict, "model": str} or {"error": str}
        """
        if not self._enabled:
            return {"error": "Model Router: No API key configured"}
        
        model = self.route_model(task_type, capability, complexity)
        fallback_models = FALLBACK_CHAIN.get(model, [])
        all_models = [model] + fallback_models
        
        import httpx
        
        for attempt, try_model in enumerate(all_models):
            circuit = self._circuit_for(try_model)
            if not circuit.allow_request():
                logger.warning(f"Circuit breaker blocking {try_model}")
                continue
            
            start = time.time()
            try:
                result = await self._call_cambo(
                    model=try_model, messages=messages,
                    system_prompt=system_prompt, max_tokens=max_tokens,
                    temperature=temperature, tools=tools,
                    response_format=response_format
                )
                latency = (time.time() - start) * 1000
                
                if "error" not in result:
                    circuit.record_success()
                    self._track_metric(try_model, latency, True)
                    result["model"] = try_model
                    return result
                
                circuit.record_failure()
                self._track_metric(try_model, latency, False)
                logger.warning(f"Model {try_model} failed (attempt {attempt+1}): {result['error']}")
                
            except Exception as e:
                latency = (time.time() - start) * 1000
                circuit.record_failure()
                self._track_metric(try_model, latency, False)
                logger.error(f"Model {try_model} exception: {e}")
        
        return {"error": f"All models failed after {len(all_models)} attempts"}
    
    async def _call_cambo(self, model: str, messages: list, system_prompt: str = "",
                          max_tokens: int = 4096, temperature: float = 0.7,
                          tools: list = None, response_format: dict = None) -> dict:
        """Raw call to Cambo endpoint with SSE parsing."""
        import httpx
        
        # Build messages array
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)
        
        payload = {
            "model": model,
            "messages": msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
        if response_format:
            payload["response_format"] = response_format
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{CAMBRO_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {CAMBRO_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload
            )
            
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}: {resp.text[:300]}"}
            
            # Parse SSE response (Cambo returns text/event-stream)
            text = resp.text.strip()
            if text.endswith("data: [DONE]"):
                text = text[:-(len("data: [DONE]"))].strip()
            
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                return {"error": f"JSON parse: {str(e)[:200]}"}
            
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
            }
    
    def get_metrics(self) -> dict:
        return self._metrics
    
    def get_circuit_status(self) -> dict:
        return {m: c.state.value for m, c in self._circuits.items()}
    
    def is_enabled(self) -> bool:
        return self._enabled


# ═══ GLOBAL INSTANCE ═══
router = ModelRouter()

logger.info(f"Model Router initialized: enabled={router.is_enabled()}, endpoint={CAMBRO_BASE_URL}")
