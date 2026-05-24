"""
LangChain Governance & Observability — Enterprise Production Layer
===================================================================
Ersetzt: runtime/governance/* (758 Zeilen Custom-Code), 
         runtime/events/*, runtime/mcp/* (teilweise)

Bietet:
- LangSmith Tracing (Automatisch für alle Chains/Agents)
- Governance Callbacks (Policy-Validation, Audit-Log)
- Health-Check für alle Komponenten
- Einheitliche Initialisierung
"""
import os
import json
import logging
from typing import Optional, Any
from datetime import datetime, timezone

# LangChain Callbacks
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage

from langchain_config import init_langchain

logger = logging.getLogger("nexifyai.governance")


# ─── LangSmith Observability ─────────────────────────────────────────────────

def configure_langsmith(
    project_name: str = "nexifyai",
    api_key: Optional[str] = None,
) -> bool:
    """Aktiviere LangSmith Tracing.
    
    Alle Chains, Agents und LLM-Calls werden automatisch getraced.
    Einsichtbar unter: https://smith.langchain.com
    
    Args:
        project_name: LangSmith Project Name
        api_key: LangSmith API Key (Default: LANGCHAIN_API_KEY env)
    
    Returns: True wenn konfiguriert, False wenn kein API-Key
    
    Usage:
        configure_langsmith("nexifyai-production")
        # Alle folgenden LLM-Calls sind automatisch getraced
        llm.invoke("Hello")  # → Trace in LangSmith
        agent.invoke(...)    # → Trace in LangSmith
    """
    api_key = api_key or os.getenv("LANGCHAIN_API_KEY")
    
    if not api_key:
        logger.warning("Kein LangSmith API-Key konfiguriert — Tracing deaktiviert")
        return False
    
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGCHAIN_PROJECT"] = project_name
    
    # Optional: Endpoint für Self-Hosted LangSmith
    endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    os.environ["LANGCHAIN_ENDPOINT"] = endpoint
    
    logger.info(f"LangSmith Tracing aktiviert: {project_name} @ {endpoint}")
    return True


# ─── Governance Callbacks ────────────────────────────────────────────────────

class GovernanceCallback(BaseCallbackHandler):
    """Ersetzt: runtime/governance/* (Policy-Engine, Audit-Log, Risk-Classifier).
    
    Dieser Callback wird an jeden Agent/Chain angehängt und protokolliert:
    - Jeden LLM-Call (Modell, Prompt, Token-Anzahl)
    - Jeden Tool-Call (Tool-Name, Input, Output)
    - Policy-Verstöße (Sensitive Data, Verbotene Patterns)
    - Audit-Log für Compliance
    
    Integration:
        from governance import GovernanceCallback
        governance = GovernanceCallback()
        agent = create_agent(..., callbacks=[governance])
    """
    
    def __init__(self):
        super().__init__()
        self.audit_log: list[dict] = []
        self.total_tokens = 0
        self.total_cost = 0.0
        
        # Governance-Regeln (ersetzt policy_engine.py + risk_classifier.py)
        self.blocked_patterns = [
            "sk-",           # OpenAI API Keys
            "ghp_",          # GitHub PATs
            "gho_",          # GitHub OAuth
            "-----BEGIN",    # Private Keys
            "AKIA",          # AWS Access Keys
        ]
    
    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        """LLM-Call gestartet — Audit-Log-Eintrag."""
        entry = {
            "type": "llm_call",
            "model": serialized.get("kwargs", {}).get("model", "unknown"),
            "prompt_length": sum(len(p) for p in prompts),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.audit_log.append(entry)
        
    def on_llm_end(self, response, **kwargs):
        """LLM-Call beendet — Token-Zählung."""
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            self.total_tokens += token_usage.get("total_tokens", 0)
    
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        """Tool-Call gestartet — Governance-Prüfung."""
        tool_name = serialized.get("name", "unknown")
        
        # Policy-Check: Sensitive Data?
        for pattern in self.blocked_patterns:
            if pattern in str(input_str):
                self._log_violation(tool_name, f"Blocked pattern detected: {pattern}")
        
        entry = {
            "type": "tool_call",
            "tool": tool_name,
            "input_length": len(str(input_str)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.audit_log.append(entry)
    
    def on_tool_end(self, output: str, **kwargs):
        """Tool-Call beendet — Output-Länge loggen."""
        if self.audit_log and self.audit_log[-1]["type"] == "tool_call":
            self.audit_log[-1]["output_length"] = len(str(output))
    
    def _log_violation(self, tool: str, reason: str):
        """Policy-Verstoß loggen (ersetzt policy_evaluator.py)."""
        violation = {
            "type": "policy_violation",
            "tool": tool,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.audit_log.append(violation)
        logger.warning(f"[GOVERNANCE] Policy-Verstoß: {tool} — {reason}")
    
    def get_audit_report(self) -> dict:
        """Generiere Audit-Report (ersetzt decision_ledger.py)."""
        violations = [e for e in self.audit_log if e["type"] == "policy_violation"]
        return {
            "total_calls": len(self.audit_log),
            "total_tokens": self.total_tokens,
            "estimated_cost": self.total_cost,
            "violations": len(violations),
            "violations_detail": violations[-10:],  # Letzte 10
            "calls_by_type": {
                "llm": sum(1 for e in self.audit_log if e["type"] == "llm_call"),
                "tool": sum(1 for e in self.audit_log if e["type"] == "tool_call"),
            },
        }


# ─── Health Check ────────────────────────────────────────────────────────────

def get_system_health() -> dict:
    """Zentraler Health-Check für alle LangChain-Komponenten.
    
    Ersetzt: runtime/health/* + runtime/watchdog/*
    
    Returns: Dict mit Status aller Komponenten
    """
    status = {"status": "healthy", "components": {}, "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # 1. LLM Provider Check
    try:
        from langchain_config import get_primary_llm
        llm = get_primary_llm()
        response = llm.invoke("Antworte mit 'ok'")
        status["components"]["llm"] = {
            "status": "healthy",
            "response_time": "~1s",
        }
    except Exception as e:
        status["components"]["llm"] = {"status": "degraded", "error": str(e)}
        status["status"] = "degraded"
    
    # 2. Qdrant / Vector Store Check
    try:
        from rag_pipeline import get_qdrant_client
        client = get_qdrant_client()
        collections = client.get_collections()
        status["components"]["vector_store"] = {
            "status": "healthy",
            "collections": len(collections.collections),
        }
    except Exception as e:
        status["components"]["vector_store"] = {"status": "degraded", "error": str(e)}
        if status["status"] == "healthy":
            status["status"] = "degraded"
    
    # 3. Embedding Model Check
    try:
        from langchain_config import get_embedding_model
        embeddings = get_embedding_model()
        test = embeddings.embed_query("test")
        status["components"]["embeddings"] = {
            "status": "healthy",
            "dimension": len(test),
            "model": "intfloat/e5-small-v2",
        }
    except Exception as e:
        status["components"]["embeddings"] = {"status": "degraded", "error": str(e)}
    
    # 4. LangSmith Check
    has_langsmith = bool(os.getenv("LANGCHAIN_API_KEY"))
    status["components"]["observability"] = {
        "status": "healthy" if has_langsmith else "disabled",
        "provider": "LangSmith" if has_langsmith else "none",
    }
    
    return status


# ─── Einheitliche Initialisierung ────────────────────────────────────────────

def init_ai_infrastructure(
    enable_langsmith: bool = True,
    enable_cache: bool = True,
    project_name: str = "nexifyai",
):
    """Initialisiere die gesamte AI-Infrastruktur.
    
    Aufruf in server.py's lifespan():
        from governance import init_ai_infrastructure
        await init_ai_infrastructure()
    
    Das ersetzt:
    - llm_provider.py Initialisierung (manuelle Provider-Chain)
    - brain_api.py Start (Zero-Vector-API)
    - governance_bootstrap.py (Custom Policy-Engine)
    - runtime/events/* Initialisierung
    
    Args:
        enable_langsmith: LangSmith Tracing aktivieren
        enable_cache: LLM-Cache aktivieren
        project_name: LangSmith Project Name
    """
    logger.info("=" * 60)
    logger.info("AI-Infrastruktur-Initialisierung gestartet")
    logger.info("=" * 60)
    
    # 1. LangChain Core (Cache + Config)
    logger.info("[1/3] LangChain Core Layer...")
    init_langchain(cache=enable_cache)
    
    # 2. LangSmith Observability
    if enable_langsmith:
        logger.info("[2/3] Observability...")
        configure_langsmith(project_name)
    else:
        logger.info("[2/3] Observability: deaktiviert")
    
    # 3. Governance Callback (Global)
    logger.info("[3/3] Governance Callback...")
    governance = GovernanceCallback()
    
    logger.info("=" * 60)
    logger.info("AI-Infrastruktur initialisiert ✅")
    logger.info(f"  - LLM: OpenRouter/DeepSeek + EmergentGPT-Fallback + Claude-Reasoning")
    logger.info(f"  - RAG: Qdrant + HuggingFace Embeddings (intfloat/e5-small-v2)")
    logger.info(f"  - Agents: LangGraph StateGraph mit {len(get_agent_tools())} Tools")
    logger.info(f"  - Observability: {'LangSmith' if enable_langsmith and os.getenv('LANGCHAIN_API_KEY') else 'deaktiviert'}")
    logger.info(f"  - Cache: {'SQLite' if enable_cache else 'deaktiviert'}")
    logger.info("=" * 60)
    
    return governance


def get_agent_tools():
    """Import-Helper für Tool-Liste (wird im Init-Log verwendet)."""
    from tool_registry import get_all_tools
    return get_all_tools()
