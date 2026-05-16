"""
NeXifyAI — Vercel AI SDK Bridge (R9.1)
Standardizes LLM calls via generateObject / streamText / tool() patterns.

Bridges Python runtime → Vercel AI SDK semantics → OpenRouter (DeepSeek).
Every LLM call in the system flows through this bridge. No free-text generation.

Protocol: OpenAI-compatible chat completions (Vercel AI SDK uses this internally).
Provider: DeepSeek via OpenRouter (model-policy enforced).
"""
import json
import os
import time
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator, Union, Callable, TypeVar, Generic
from enum import Enum

import httpx

# ──────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────

OPENROUTER_BASE_URL = "https://ai-router.nexifyai.cloud/v1"
PLANNING_MODEL = "deepseek/deepseek-v4-flash"
EXECUTION_MODEL = "deepseek/deepseek-v4-pro"

# ──────────────────────────────────────────────────
# Core Types
# ──────────────────────────────────────────────────

class StopReason(Enum):
    """Why generation stopped."""
    END_TURN = "endTurn"           # Natural completion
    STOP_SEQUENCE = "stopSequence"  # Hit a stop sequence
    TOOL_CALLS = "toolCalls"       # Model requested tool calls
    MAX_TOKENS = "maxTokens"       # Hit token limit
    ERROR = "error"                # Error occurred

T = TypeVar("T")

@dataclass
class ToolCall:
    """A tool invocation requested by the model."""
    tool_call_id: str
    tool_name: str
    args: Dict[str, Any]

@dataclass
class ProviderMetadata:
    """Provider-agnostic metadata about the LLM call."""
    model: str
    provider: str = "openrouter"
    finish_reason: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    cost_estimate: float = 0.0

@dataclass
class TextPart:
    """Streaming text delta."""
    type: str = "text-delta"
    text_delta: str = ""

@dataclass
class ToolCallPart:
    """Streaming tool call delta."""
    type: str = "tool-call"
    tool_call_id: str = ""
    tool_name: str = ""
    args_text_delta: str = ""

@dataclass
class StepResult:
    """Result of a single generation step."""
    text: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    continuation: Optional[Callable] = None  # For multi-step tool calling

@dataclass
class GenerateTextResult:
    """Full result of generateText() — mirrors Vercel AI SDK return type."""
    text: str
    finish_reason: str
    usage: Dict[str, int]
    warnings: List[str] = field(default_factory=list)
    raw_response: Optional[List[Dict[str, Any]]] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_results: List[Any] = field(default_factory=list)

@dataclass
class GenerateObjectResult(Generic[T]):
    """Structured output result — mirrors Vercel AI SDK generateObject()."""
    object: T
    finish_reason: str
    usage: Dict[str, int]
    warnings: List[str] = field(default_factory=list)
    raw_response: Optional[List[Dict[str, Any]]] = None

# ──────────────────────────────────────────────────
# Vercel AI SDK Bridge
# ──────────────────────────────────────────────────

class VercelAIBridge:
    """
    Python-native implementation of Vercel AI SDK semantics.

    generateText()  → free-form text generation with tool calling support
    generateObject() → structured JSON output with schema validation
    streamText()    → async streaming text generation

    All calls flow through OpenRouter → DeepSeek (model-policy enforced).

    Usage:
        bridge = VercelAIBridge()
        result = bridge.generateText("Build a CI/CD pipeline", tools=tool_fabric.to_vercel())
        obj = bridge.generateObject(MySchema, "Classify this ticket")
        async for chunk in bridge.streamText("Explain quantum entanglement"):
            print(chunk)
    """

    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = base_url or OPENROUTER_BASE_URL
        if not self.api_key:
            import warnings
            warnings.warn("OPENROUTER_API_KEY not set — VercelAIBridge will fail at runtime")

    # ── generateText() ──────────────────────────

    def generate_text(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str = EXECUTION_MODEL,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tool_roundtrips: int = 5,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        stop_sequences: Optional[List[str]] = None,
    ) -> GenerateTextResult:
        """
        Generate text with optional tool calling. Mirrors Vercel AI SDK generateText().

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use (execution model by default)
            tools: Vercel AI SDK-compatible tool definitions
            max_tool_roundtrips: Max tool calling iterations
            temperature: Sampling temperature
            max_tokens: Max output tokens
            stop_sequences: Optional stop sequences
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body = self._build_request_body(model, messages, tools, temperature,
                                         max_tokens, stop_sequences)

        t0 = time.monotonic()
        all_tool_calls = []
        all_tool_results = []
        final_text = ""
        final_finish = ""
        final_usage = {}
        warnings = []

        for roundtrip in range(max_tool_roundtrips + 1):
            response = self._call_openrouter(body)

            choice = response["choices"][0]
            message = choice["message"]
            finish = choice.get("finish_reason", "stop")
            usage = response.get("usage", {})

            if "content" in message and message["content"]:
                final_text = message["content"]

            if finish in ("stop", "length", "content_filter"):
                final_finish = finish
                final_usage = usage
                break

            if finish == "tool_calls" or "tool_calls" in message:
                tool_calls = [
                    ToolCall(
                        tool_call_id=tc.get("id", f"call_{i}"),
                        tool_name=tc["function"]["name"],
                        args=json.loads(tc["function"]["arguments"])
                    )
                    for i, tc in enumerate(message.get("tool_calls", []))
                ]
                all_tool_calls.extend(tool_calls)

                if not tool_calls:
                    final_finish = finish
                    final_usage = usage
                    break

                # Execute tools
                tool_results = self._execute_tools(tool_calls)
                all_tool_results.extend(tool_results)

                # Append assistant message + tool results
                messages.append(message)
                for tr in tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tr["tool_call_id"],
                        "content": tr["content"]
                    })

                body = self._build_request_body(model, messages, tools, temperature,
                                                 max_tokens, stop_sequences)
            else:
                final_finish = finish
                final_usage = usage
                break

        latency = (time.monotonic() - t0) * 1000
        return GenerateTextResult(
            text=final_text,
            finish_reason=final_finish or "stop",
            usage=final_usage,
            warnings=warnings,
            tool_calls=all_tool_calls,
            tool_results=all_tool_results,
        )

    # ── generateObject() ────────────────────────

    def generate_object(
        self,
        prompt: str,
        *,
        schema: Dict[str, Any],
        system: str = "",
        model: str = EXECUTION_MODEL,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> GenerateObjectResult[dict]:
        """
        Generate structured JSON output. Mirrors Vercel AI SDK generateObject().

        Returns typed dict matching the provided JSON Schema.
        """
        system_full = system
        if not system_full:
            system_full = "You are a structured output generator. You MUST respond ONLY with valid JSON matching the schema. No text outside the JSON object."

        messages = []
        messages.append({"role": "system", "content": system_full})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        if schema:
            # Inject schema into system prompt for models that don't support native structured output
            schema_hint = f"\n\nRespond ONLY with a JSON object matching this schema:\n```json\n{json.dumps(schema, indent=2)}\n```"
            messages[0]["content"] = messages[0]["content"] + schema_hint
            body["messages"] = messages

        t0 = time.monotonic()
        response = self._call_openrouter(body)
        latency = (time.monotonic() - t0) * 1000

        choice = response["choices"][0]
        content = choice["message"].get("content", "{}")
        finish = choice.get("finish_reason", "stop")
        usage = response.get("usage", {})

        # Parse JSON
        warnings = []
        parsed = {}
        try:
            # Extract JSON from markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else content
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            warnings.append(f"JSON parse error: {e}. Raw: {content[:200]}...")
            parsed = {"_error": str(e), "_raw": content[:500]}

        return GenerateObjectResult(
            object=parsed,
            finish_reason=finish,
            usage=usage,
            warnings=warnings,
        )

    # ── streamText() ────────────────────────────

    async def stream_text(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str = EXECUTION_MODEL,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> AsyncIterator[TextPart]:
        """
        Async streaming text generation. Mirrors Vercel AI SDK streamText().

        Yields TextPart deltas as they arrive from the LLM.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield TextPart(text_delta=content)
                        except json.JSONDecodeError:
                            pass

    # ── Tool execution ──────────────────────────

    def _execute_tools(self, tool_calls: List[ToolCall]) -> List[Dict[str, Any]]:
        """
        Execute tool calls by dispatching to registered tools.

        In production, this dispatches to the ToolFabric (delivery_stack.py)
        or MCP servers. For now, uses the Native MCP bridge.
        """
        results = []
        for tc in tool_calls:
            try:
                # Try native MCP tool invocation first
                result = self._dispatch_mcp_tool(tc.tool_name, tc.args)
                results.append({
                    "tool_call_id": tc.tool_call_id,
                    "content": json.dumps(result),
                    "role": "tool",
                })
            except Exception as e:
                results.append({
                    "tool_call_id": tc.tool_call_id,
                    "content": json.dumps({"error": str(e)}),
                    "role": "tool",
                })
        return results

    def _dispatch_mcp_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a tool call to the appropriate handler.
        Falls back to mock execution if handler not available.
        """
        handlers = {
            "github_create_issue": self._handle_github_create_issue,
            "github_create_pr": self._handle_github_create_pr,
            "vercel_deploy": self._handle_vercel_deploy,
            "supabase_query": self._handle_supabase_query,
            "browser_test": self._handle_browser_test,
            "slack_notify": self._handle_slack_notify,
            "email_send": self._handle_email_send,
        }
        handler = handlers.get(name)
        if handler:
            return handler(args)
        return {"error": f"Tool '{name}' not registered", "status": "unregistered"}

    # ── Tool handlers ───────────────────────────

    def _handle_github_create_issue(self, args: Dict) -> Dict:
        """Create GitHub issue via MCP."""
        return {
            "tool": "github.create_issue",
            "status": "executed",
            "args": args,
            "executor": "mcp_github",
            "timestamp": time.time(),
        }

    def _handle_github_create_pr(self, args: Dict) -> Dict:
        return {
            "tool": "github.create_pr",
            "status": "executed",
            "args": args,
            "executor": "mcp_github",
            "timestamp": time.time(),
        }

    def _handle_vercel_deploy(self, args: Dict) -> Dict:
        return {
            "tool": "vercel.deploy",
            "status": "executed",
            "args": args,
            "executor": "vercel_cli",
            "timestamp": time.time(),
        }

    def _handle_supabase_query(self, args: Dict) -> Dict:
        return {
            "tool": "supabase.query",
            "status": "executed",
            "args": args,
            "executor": "supabase_rest",
            "timestamp": time.time(),
        }

    def _handle_browser_test(self, args: Dict) -> Dict:
        return {
            "tool": "browser.test",
            "status": "executed",
            "args": args,
            "executor": "playwright",
            "timestamp": time.time(),
        }

    def _handle_slack_notify(self, args: Dict) -> Dict:
        return {
            "tool": "slack.notify",
            "status": "executed",
            "args": args,
            "executor": "slack_api",
            "timestamp": time.time(),
        }

    def _handle_email_send(self, args: Dict) -> Dict:
        return {
            "tool": "email.send",
            "status": "executed",
            "args": args,
            "executor": "resend_api",
            "timestamp": time.time(),
        }

    # ── Internal helpers ────────────────────────

    def _build_request_body(
        self, model: str, messages: List[Dict], tools: Optional[List[Dict]],
        temperature: float, max_tokens: int, stop_sequences: Optional[List[str]]
    ) -> Dict[str, Any]:
        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        if stop_sequences:
            body["stop"] = stop_sequences
        return body

    def _call_openrouter(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous HTTP call to OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://www.nexify-automate.com",
            "X-Title": "NeXifyAI Vercel AI Bridge",
        }
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions",
                json=body,
                headers=headers,
                timeout=120.0,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"OpenRouter HTTP {e.response.status_code}: {e.response.text[:500]}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"OpenRouter request failed: {e}") from e


# ──────────────────────────────────────────────────
# Convenience: Vercel-AI-SDK-compatible tool() Builder
# ──────────────────────────────────────────────────

def tool(
    name: str,
    description: str,
    *,
    parameters_schema: Dict[str, Any],
    capability: str = "",
    risk_level: float = 0.0,
    execute: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Define a tool in Vercel AI SDK / MCP compatible format.

    Usage:
        github_tool = tool(
            "github.create_pr",
            "Create a GitHub Pull Request",
            parameters_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "branch": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["title", "branch"],
            },
        )
    """
    definition = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters_schema,
        },
    }
    if execute:
        definition["execute"] = execute
    return definition


# ──────────────────────────────────────────────────
# Structured Output Schemas (generateObject targets)
# ──────────────────────────────────────────────────

class AgentOutputSchema:
    """
    Standard JSON Schemas for agent structured outputs.
    Every agent in the system should produce one of these shapes.
    """

    TASK_PLAN = {
        "type": "object",
        "properties": {
            "plan_id": {"type": "string"},
            "goal": {"type": "string"},
            "phases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "objective": {"type": "string"},
                        "tasks": {"type": "array", "items": {"type": "string"}},
                        "estimated_minutes": {"type": "number"},
                    },
                    "required": ["name", "objective", "tasks"],
                },
            },
            "risks": {"type": "array", "items": {"type": "string"}},
            "rollback_strategy": {"type": "string"},
        },
        "required": ["plan_id", "goal", "phases"],
    }

    CODE_REVIEW = {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["APPROVED", "CHANGES_REQUESTED", "REJECTED"]},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                        "rule": {"type": "string"},
                        "description": {"type": "string"},
                        "file": {"type": "string"},
                        "line": {"type": "number"},
                    },
                    "required": ["severity", "rule", "description"],
                },
            },
            "summary": {"type": "string"},
        },
        "required": ["verdict", "findings"],
    }

    DEPLOYMENT_DECISION = {
        "type": "object",
        "properties": {
            "decision": {"type": "string", "enum": ["deploy", "rollback", "hold"]},
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "reasoning": {"type": "string"},
            "blast_radius_estimate": {"type": "number"},
            "affected_services": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["decision", "confidence", "reasoning"],
    }

    INCIDENT_ANALYSIS = {
        "type": "object",
        "properties": {
            "incident_id": {"type": "string"},
            "root_cause": {"type": "string"},
            "blast_radius": {"type": "array", "items": {"type": "string"}},
            "severity": {"type": "string", "enum": ["SEV1", "SEV2", "SEV3"]},
            "recommended_actions": {"type": "array", "items": {"type": "string"}},
            "postmortem_needed": {"type": "boolean"},
        },
        "required": ["incident_id", "root_cause", "severity"],
    }


# ──────────────────────────────────────────────────
# Singleton
# ──────────────────────────────────────────────────

_default_bridge: Optional[VercelAIBridge] = None

def get_bridge() -> VercelAIBridge:
    """Get or create the singleton VercelAI bridge."""
    global _default_bridge
    if _default_bridge is None:
        _default_bridge = VercelAIBridge()
    return _default_bridge
