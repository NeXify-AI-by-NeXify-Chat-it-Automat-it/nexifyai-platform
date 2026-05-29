"""
LangChain Core Configuration — OpenRouter ONLY
==================================================
NUR OpenRouter: https://openrouter.ai/api/v1
NUR Modell: deepseek/deepseek-v4-flash

KEINE Fallback-Provider (Emergent, Anthropic, OpenAI Direct).
KEINE Embedding-Modelle (werden ueber Brain API / Qdrant abgewickelt).
"""

import os
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache

logger = logging.getLogger("nexifyai.langchain")


def get_primary_llm(**kwargs):
    """OpenRouter → DeepSeek V4 Flash (Einziges Modell)."""
    return ChatOpenAI(
        model=kwargs.pop("model", "deepseek/deepseek-v4-flash"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=kwargs.pop("temperature", 0.7),
        max_tokens=kwargs.pop("max_tokens", 4096),
        timeout=kwargs.pop("timeout", 60),
        max_retries=kwargs.pop("max_retries", 3),
        **kwargs
    )


CAPABILITY_ROUTING = {
    "chat":        {"temperature": 0.7},
    "code":        {"temperature": 0.2},
    "analyze":     {"temperature": 0.3},
    "plan":        {"temperature": 0.3},
    "classify":    {"temperature": 0.0},
    "summarize":   {"temperature": 0.3},
    "extract":     {"temperature": 0.0},
    "default":     {"temperature": 0.7},
}


def get_llm_for_task(task_type: str = "default", **kwargs):
    """Waehlt Temperatur basierend auf task_type. Immer deepseek/deepseek-v4-flash."""
    cfg = CAPABILITY_ROUTING.get(task_type, CAPABILITY_ROUTING["default"])
    if "temperature" not in kwargs:
        kwargs["temperature"] = cfg["temperature"]
    return get_primary_llm(**kwargs)


def configure_cache(cache_dir: str = ".langchain_cache"):
    """SQLite-basiertes LLM-Caching."""
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "langchain.db")
    set_llm_cache(SQLiteCache(database_path=cache_path))
    logger.info(f"LLM-Cache initialisiert: {cache_path}")


def init_langchain(cache: bool = True):
    """Einmalige Initialisierung."""
    if cache:
        configure_cache()
    logger.info("LangChain Core Layer initialisiert (OpenRouter ONLY)")
