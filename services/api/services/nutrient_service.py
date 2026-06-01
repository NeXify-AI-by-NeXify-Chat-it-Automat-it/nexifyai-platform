"""
NeXifyAI — Nutrient AI Document Processing Service
PDF-Analyse, Datenextraktion, Dokumenten-Chat, Vertrags-Risikoscoring, PII-Redaktion.
Nutzt die Nutrient AI API (nutrient.io).

Security: Path sanitization gegen Path-Traversal (Alert #84).
"""
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger("nexifyai.services.nutrient")

NUTRIENT_API_KEY = os.environ.get("NUTRIENT_API_KEY", "")
NUTRIENT_API_URL = "https://api.nutrient.io"

# Erlaubte Basisverzeichnisse für Dokumentenverarbeitung
ALLOWED_UPLOAD_DIRS = [
    Path("/tmp/nexifyai/uploads").resolve(),
    Path("/var/nexifyai/documents").resolve(),
    Path("/opt/nexify/data/uploads").resolve(),
]


def _resolve_safe_path(file_path: str) -> Optional[Path]:
    """Prüft und resolved einen Dateipfad sicher gegen Path-Traversal.

    Gibt den resolved Path zurück, wenn er in einem erlaubten Verzeichnis liegt,
    sonst None.
    """
    try:
        resolved = Path(file_path).resolve()
        for allowed in ALLOWED_UPLOAD_DIRS:
            if str(resolved).startswith(str(allowed)):
                return resolved
        logger.warning("Path-Traversal-Versuch abgewehrt: %s", file_path)
        return None
    except (ValueError, OSError, RuntimeError) as e:
        logger.error("Fehler bei Pfadauflösung: %s — %s", file_path, e)
        return None


def is_configured() -> bool:
    return bool(NUTRIENT_API_KEY)


async def analyze_document(file_path: str, analysis_type: str = "extract") -> dict:
    """
    Analysiert ein PDF/Dokument via Nutrient AI.
    analysis_type: 'extract' | 'summarize' | 'risk_score' | 'pii_detect'
    """
    if not NUTRIENT_API_KEY:
        return {"success": False, "error": "NUTRIENT_API_KEY nicht konfiguriert"}

    safe_path = _resolve_safe_path(file_path)
    if not safe_path:
        return {"success": False, "error": f"Ungültiger oder nicht erlaubter Dateipfad: {file_path}"}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            with open(str(safe_path), "rb") as f:
                files = {"file": (os.path.basename(str(safe_path)), f, "application/pdf")}
                headers = {"Authorization": f"Bearer {NUTRIENT_API_KEY}"}

                if analysis_type == "extract":
                    resp = await client.post(
                        f"{NUTRIENT_API_URL}/build",
                        headers=headers,
                        files=files,
                        data={
                            "instructions": json.dumps({
                                "parts": [{"type": "extract", "strategy": "auto"}]
                            })
                        }
                    )
                elif analysis_type == "pii_detect":
                    resp = await client.post(
                        f"{NUTRIENT_API_URL}/build",
                        headers=headers,
                        files=files,
                        data={
                            "instructions": json.dumps({
                                "parts": [{"type": "redaction", "strategy": "pii", "redactText": False}]
                            })
                        }
                    )
                else:
                    resp = await client.post(
                        f"{NUTRIENT_API_URL}/build",
                        headers=headers,
                        files=files,
                        data={
                            "instructions": json.dumps({
                                "parts": [{"type": "extract", "strategy": "auto"}]
                            })
                        }
                    )

                if resp.status_code == 200:
                    return {
                        "success": True,
                        "analysis_type": analysis_type,
                        "result": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw_size": len(resp.content)},
                        "processed_at": datetime.now(timezone.utc).isoformat()
                    }
                return {
                    "success": False,
                    "error": f"Nutrient API Fehler ({resp.status_code}): {resp.text[:300]}",
                    "analysis_type": analysis_type
                }
    except FileNotFoundError:
        return {"success": False, "error": f"Datei nicht gefunden oder nicht lesbar: {file_path}"}
    except Exception as e:
        logger.error(f"Nutrient analysis error: {e}")
        return {"success": False, "error": str(e)[:500]}


async def contract_risk_score(file_path: str) -> dict:
    """
    Vertrags-Risikoscoring: Analysiert ein Vertragsdokument und bewertet Risiken.
    Nutzt Nutrient für Extraktion + OpenRouter für Scoring.
    """
    extraction = await analyze_document(file_path, "extract")
    if not extraction.get("success"):
        return extraction

    extracted_text = json.dumps(extraction.get("result", {}), ensure_ascii=False)[:8000]

    try:
        from services import nexify_provider_provider as openrouter_llm
        scoring = await openrouter_llm.chat_completion(
            messages=[
                {"role": "system", "content": """Du bist ein Vertrags-Risikobewertungs-Experte.
Analysiere den extrahierten Vertragstext und bewerte:
1. Risiko-Score (1-10, 10 = höchstes Risiko)
2. Identifizierte Risiken (Liste)
3. Fehlende Standardklauseln
4. Empfehlungen

Antwort als JSON: {"score": N, "risks": [...], "missing": [...], "recommendations": [...]}"""},
                {"role": "user", "content": f"Vertragstext:\n{extracted_text}"}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        if "error" not in scoring:
            try:
                risk_data = json.loads(scoring["content"])
                return {
                    "success": True,
                    "risk_score": risk_data.get("score", 5),
                    "risks": risk_data.get("risks", []),
                    "missing_clauses": risk_data.get("missing", []),
                    "recommendations": risk_data.get("recommendations", []),
                    "model": scoring.get("model", ""),
                    "scored_at": datetime.now(timezone.utc).isoformat()
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis": scoring["content"],
                    "scored_at": datetime.now(timezone.utc).isoformat()
                }
        return {"success": False, "error": scoring.get("error", "OpenRouter scoring failed")}
    except Exception as e:
        logger.error(f"Risk scoring error: {e}")
        return {"success": False, "error": str(e)[:500]}


async def document_chat(file_path: str, question: str) -> dict:
    """
    Dokumenten-Chat: Extrahiert Inhalt und beantwortet Fragen via OpenRouter.
    """
    extraction = await analyze_document(file_path, "extract")
    if not extraction.get("success"):
        return extraction

    extracted_text = json.dumps(extraction.get("result", {}), ensure_ascii=False)[:8000]

    try:
        from services import nexify_provider_provider as openrouter_llm
        answer = await openrouter_llm.chat_completion(
            messages=[
                {"role": "system", "content": "Du bist ein Dokumentenexperte. Beantworte Fragen basierend auf dem Dokument."},
                {"role": "user", "content": f"Dokument:\n{extracted_text}\n\nFrage: {question}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        return {
            "success": True,
            "answer": answer.get("content", ""),
            "model": answer.get("model", ""),
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Document chat error: {e}")
        return {"success": False, "error": str(e)[:500]}


async def summarize_document(file_path: str, max_length: int = 500) -> dict:
    """Dokumenten-Zusammenfassung via Nutrient + OpenRouter."""
    extraction = await analyze_document(file_path, "extract")
    if not extraction.get("success"):
        return extraction

    extracted_text = json.dumps(extraction.get("result", {}), ensure_ascii=False)[:8000]

    try:
        from services import deepseek_provider as openrouter_llm
        summary = await openrouter_llm.chat_completion(
            messages=[
                {"role": "system", "content": f"Fasse das folgende Dokument in maximal {max_length} Wörtern zusammen."},
                {"role": "user", "content": extracted_text}
            ],
            temperature=0.3,
            max_tokens=max_length
        )

        return {
            "success": True,
            "summary": summary.get("content", ""),
            "model": summary.get("model", ""),
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        return {"success": False, "error": str(e)[:500]}
