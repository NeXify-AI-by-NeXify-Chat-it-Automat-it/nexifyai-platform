"""
NeXifyAI — Embedding Manager for Qwen/Qwen3-Embedding-8B (4096d)
=========================================================
Embedding-Stack:
  Primary:   OpenRouter → Qwen/Qwen3-Embedding-8B (4096d, ~$0.025/1M tokens)
  Fallback1: Ollama local → nomic-embed-text (768d → padded to 4096d)
  Fallback2: Zero-Vector (4096d) — wenn gar nichts geht

Nscale: Infrastruktur-Provider. Qwen3-Embedding-8B wird via OpenRouter API bezogen.
"""
import os
import json
import time
import logging
import hashlib
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("nexifyai.embedding")

# ─── Konfiguration ──────────────────────────────────────────────

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
EMBEDDING_DIM = 4096

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11435")
OLLAMA_FALLBACK_MODEL = "nomic-embed-text"
OLLAMA_FALLBACK_DIM = 768


def get_embedding(text: str, retries: int = 2) -> Optional[List[float]]:
    """
    Embedding-Stack (Primär → Fallback1 → Fallback2).
    Liefert immer 4096d-Embedding zurück.
    """
    # ▸ Primary: OpenRouter → Qwen3-Embedding-8B
    if OPENROUTER_API_KEY:
        vec = _openrouter_embed(text, retries)
        if vec and len(vec) == EMBEDDING_DIM:
            logger.debug(f"Embedding via OpenRouter/{EMBEDDING_MODEL}: {len(vec)}d")
            return vec
        elif vec:
            logger.warning(f"OpenRouter embedding wrong dim: {len(vec)} (expected {EMBEDDING_DIM})")

    # ▸ Fallback 1: Ollama local
    vec = _ollama_embed(text)
    if vec:
        if len(vec) == EMBEDDING_DIM:
            return vec
        elif len(vec) == OLLAMA_FALLBACK_DIM:
            # Padder auf 4096d
            padded = vec + [0.0] * (EMBEDDING_DIM - len(vec))
            logger.debug(f"Embedding via Ollama/{OLLAMA_FALLBACK_MODEL}: {len(vec)}d → padded 4096d")
            return padded
        else:
            logger.warning(f"Ollama embedding wrong dim: {len(vec)}")

    # ▸ Fallback 2: Zero-Vector
    logger.warning("Kein Embedding verfügbar — nutze Zero-Vector")
    return [0.0] * EMBEDDING_DIM


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Batch-Verarbeitung für mehrere Texte."""
    return [get_embedding(t) for t in texts]


def _openrouter_embed(text: str, retries: int = 2) -> Optional[List[float]]:
    """Embedding via OpenRouter API (Qwen/Qwen3-Embedding-8B, 4096d)."""
    import httpx
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{OPENROUTER_BASE_URL}/embeddings",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": EMBEDDING_MODEL,
                        "input": text,
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    emb = data.get("data", [{}])[0].get("embedding", [])
                    return emb
                elif resp.status_code == 429 and attempt < retries:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    logger.error(f"OpenRouter embedding error {resp.status_code}: {resp.text[:200]}")
                    return None
        except Exception as e:
            logger.error(f"OpenRouter embedding exception (attempt {attempt+1}): {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    return None


def _ollama_embed(text: str) -> Optional[List[float]]:
    """Embedding via Ollama (nomic-embed-text, 768d)."""
    import httpx
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": OLLAMA_FALLBACK_MODEL,
                    "prompt": text,
                }
            )
            if resp.status_code == 200:
                return resp.json().get("embedding", [])
            else:
                logger.error(f"Ollama embedding error {resp.status_code}: {resp.text[:200]}")
                return None
    except Exception as e:
        logger.error(f"Ollama embedding exception: {e}")
        return None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity zwischen zwei Embeddings."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def embedding_health() -> dict:
    """Health-Check für den Embedding-Stack."""
    result = {
        "configured": bool(OPENROUTER_API_KEY),
        "model": EMBEDDING_MODEL,
        "dimension": EMBEDDING_DIM,
        "provider": "OpenRouter",
        "fallback": f"Ollama/{OLLAMA_FALLBACK_MODEL} ({OLLAMA_FALLBACK_DIM}d)",
        "nscale_via": "OpenRouter API (kein dedizierter Service)",
    }

    # Test-Embedding
    if OPENROUTER_API_KEY:
        test = _openrouter_embed("test", retries=1)
        result["status"] = "ok" if test else "fallback_active"
        result["test_dim"] = len(test) if test else 0
    else:
        test = _ollama_embed("test")
        result["status"] = "ollama_fallback" if test else "unavailable"
        result["test_dim"] = len(test) if test else 0

    return result