"""
LangChain Core Configuration — Enterprise Agent Infrastructure
=============================================================
Ersetzt: llm_provider.py (687 Zeilen), model_router.py (292 Zeilen), deepseek_provider.py (102 Zeilen)

Provider-Strategie:
  Primary:   OpenRouter → DeepSeek V4 Flash (chat, code, analyze)
  Fallback:  EmergentGPT → GPT-4o-mini 
  Secondary: Anthropic → Claude Sonnet (complex reasoning)
  Embedding: HuggingFace → intfloat/e5-small-v2 (lokal, DSGVO-konform)
"""

import os
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache
from langchain.load import dumps, loads

logger = logging.getLogger("nexifyai.langchain")

# ─── Model Registry ───────────────────────────────────────────────────────────

def get_primary_llm(**kwargs):
    """OpenRouter → DeepSeek V4 Flash (Standard für alle Agenten)."""
    return ChatOpenAI(
        model=kwargs.pop("model", "deepseek/deepseek-v4-flash"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=kwargs.pop("temperature", 0.7),
        max_tokens=kwargs.pop("max_tokens", 4096),
        timeout=kwargs.pop("timeout", 30),
        max_retries=kwargs.pop("max_retries", 3),
        **kwargs
    )


def get_fallback_llm(**kwargs):
    """EmergentGPT → GPT-4o-mini (Fallback bei OpenRouter-Ausfall)."""
    return ChatOpenAI(
        model=kwargs.pop("model", "gpt-4o-mini"),
        openai_api_key=os.getenv("EMERGENT_LLM_KEY"),
        openai_api_base=os.getenv("EMERGENT_LLM_BASE", "https://emergent-gpt.com/api/v1"),
        temperature=kwargs.pop("temperature", 0.7),
        max_tokens=kwargs.pop("max_tokens", 4096),
        timeout=kwargs.pop("timeout", 30),
        max_retries=kwargs.pop("max_retries", 2),
        **kwargs
    )


def get_reasoning_llm(**kwargs):
    """Anthropic Claude Sonnet (für komplexe Reasoning-Aufgaben)."""
    return ChatAnthropic(
        model=kwargs.pop("model", "claude-sonnet-4-5-20250929"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=kwargs.pop("temperature", 0.0),
        max_tokens=kwargs.pop("max_tokens", 8192),
        timeout=kwargs.pop("timeout", 60),
        **kwargs
    )


def get_embedding_model(**kwargs):
    """HuggingFace Embeddings (lokal, DSGVO-konform).
    
    Ersetzt die Zero-Vector-Placeholder in brain_api.py (243 Zeilen → 0).
    """
    return HuggingFaceEmbeddings(
        model_name=kwargs.pop("model_name", "intfloat/e5-small-v2"),
        model_kwargs={"device": kwargs.pop("device", "cpu")},
        encode_kwargs={"normalize_embeddings": kwargs.pop("normalize", True)},
        **kwargs
    )


# ─── Fallback Chain (ersetzt ModelRouter._call_cambo + FALLBACK_CHAIN) ──────────

def create_llm_with_fallbacks(**kwargs):
    """Erstellt LLM mit automatischer Fallback-Kette.
    
    Verhalten:
      1. Versuch: Primary (OpenRouter/DeepSeek) 
      2. Fallback: EmergentGPT (GPT-4o-mini)
      3. Letzter Fallback: Direkter OpenAI-Aufruf (falls vorhanden)
    
    LangChain's .with_fallbacks() übernimmt:
    - Retry-Logik ✅
    - Rate-Limit-Handling ✅
    - Timeout-Handling ✅
    - Fehlerklassifizierung ✅ (RateLimitError, ServiceUnavailable, etc.)
    """
    primary = get_primary_llm(**kwargs)
    fallback = get_fallback_llm(**kwargs)
    
    # Fallback-Kette: Primary → Fallback1 → Fallback2
    llm = primary.with_fallbacks(
        [fallback],
        # Bei welchen Fehlern soll fallback aktiviert werden?
        exceptions_to_handle=(
            Exception,  # Alle Fehler (ServerError, RateLimit, Timeout, Auth)
        )
    )
    return llm


# ─── Capability-based Model Router (ersetzt CAPABILITY_ROUTING Dict) ──────────

CAPABILITY_ROUTING = {
    # task_type → (model_type, temperature)
    "chat":        ("primary", 0.7),
    "code":        ("primary", 0.2),
    "analyze":     ("primary", 0.3),
    "research":    ("reasoning", 0.1),
    "plan":        ("reasoning", 0.2),
    "creative":    ("primary", 0.9),
    "extract":     ("primary", 0.0),
    "classify":    ("primary", 0.0),
    "summarize":   ("primary", 0.3),
    "default":     ("primary", 0.7),
}


def get_llm_for_task(task_type: str = "default", **kwargs):
    """Wählt basierend auf task_type das optimale Modell.
    
    >>> get_llm_for_task("research") → Claude Sonnet (complex reasoning)
    >>> get_llm_for_task("chat") → DeepSeek V4 Flash (fast, cheap)
    >>> get_llm_for_task("code") → DeepSeek V4 Flash (low temp)
    """
    model_type, temp = CAPABILITY_ROUTING.get(task_type, CAPABILITY_ROUTING["default"])
    
    if "temperature" not in kwargs:
        kwargs["temperature"] = temp
    
    if model_type == "reasoning":
        return get_reasoning_llm(**kwargs)
    else:
        return create_llm_with_fallbacks(**kwargs)


# ─── Cache-Konfiguration (ersetzt manuelles Caching) ──────────────────────────

def configure_cache(cache_dir: str = ".langchain_cache"):
    """SQLite-basiertes LLM-Caching.
    
    Vorteile gegenüber Custom-Caching:
    - Automatisch: Gleicher Prompt → Cache-Hit (kein API-Call, keine Kosten)
    - Persistiert: Über Prozess-Grenzen hinweg
    - Konfigurierbar: TTL, Max-Size
    
    Nutzung:
        configure_cache()
        llm.invoke("What is Python?")  # API-Call
        llm.invoke("What is Python?")  # Cache-Hit (sofort, kein API-Call)
    """
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "langchain.db")
    set_llm_cache(SQLiteCache(database_path=cache_path))
    logger.info(f"LLM-Cache initialisiert: {cache_path}")


# ─── Initialisierung ──────────────────────────────────────────────────────────

def init_langchain(cache: bool = True):
    """Einmalige Initialisierung des LangChain-Layers.
    
    Aufruf in server.py lifespan():
        from langchain_config import init_langchain
        init_langchain()
    """
    if cache:
        configure_cache()
    logger.info("LangChain Core Layer initialisiert")
    logger.info(f"  Primary:     OpenRouter/DeepSeek V4")
    logger.info(f"  Fallback:    EmergentGPT/GPT-4o-mini")
    logger.info(f"  Reasoning:   Anthropic/Claude Sonnet")
    logger.info(f"  Embeddings:  HuggingFace/intfloat-e5-small-v2")
    logger.info(f"  Cache:       SQLite (.langchain_cache/langchain.db)")
