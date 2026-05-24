"""
LangChain Backward Compatibility Layer
=======================================
Ermöglicht nahtlosen Übergang: Alter Code importiert alte Module,
die intern auf LangChain weiterleiten.

Statt:
    from services.llm_provider import create_llm_provider
    llm = create_llm_provider()

Weiterhin möglich (leitet auf LangChain weiter):
    from services.llm_provider import create_llm_provider
    llm = create_llm_provider()  # → ruft intern get_llm_for_task("chat") auf

Entfernung geplant: 2026-06-21
"""
import logging
import warnings

warnings.warn(
    "DEPRECATED: Nutze 'from services.langchain_config import get_llm_for_task' "
    "statt 'from services.llm_provider import create_llm_provider'. "
    "Entfernung geplant: 2026-06-21",
    DeprecationWarning,
    stacklevel=2,
)

from services.langchain_config import get_llm_for_task, get_reasoning_llm, get_primary_llm

logger = logging.getLogger("nexifyai.compat")


def create_llm_provider(model_type: str = "primary", **kwargs):
    """COMPAT: Wrapper für alten create_llm_provider()-Aufruf.
    
    Früher: Custom-LLM-Provider mit Circuit-Breaker + Retry-Logik.
    Jetzt: LangChain create_llm_with_fallbacks() + ChatOpenAI.
    """
    if model_type == "reasoning":
        return get_reasoning_llm(**kwargs)
    return get_primary_llm(**kwargs)


# Alte Funktionsnamen als Aliases
get_model = get_llm_for_task  # model_router.get_model()
call_llm = get_primary_llm    # llm_provider._call_llm()
