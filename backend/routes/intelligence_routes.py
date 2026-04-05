"""
NeXifyAI — Intelligence Routes
Crawl4AI (Web-Crawling) + Nutrient AI (Dokument-Processing) Endpoints.
"""
import os
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from pydantic import BaseModel
from typing import Optional

from routes.shared import S, utcnow, new_id

logger = logging.getLogger("nexifyai.routes.intelligence")

router = APIRouter(tags=["Intelligence"])


# ── Auth ──
async def get_admin(request: Request):
    import jwt
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Nicht authentifiziert")
    token = auth[7:]
    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY", ""), algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(401, "Ungültiger Token")
        user = await S.db.admin_users.find_one({"email": email}, {"_id": 0})
        if not user:
            raise HTTPException(401, "Admin nicht gefunden")
        return user
    except Exception:
        raise HTTPException(401, "Nicht authentifiziert")


# ════════════════════════════════════════════════════════════
# CRAWL4AI — Web-Crawling
# ════════════════════════════════════════════════════════════

class CrawlRequest(BaseModel):
    url: str
    extract_mode: str = "markdown"
    css_selector: str = None
    max_pages: int = 1


class CompanyResearchRequest(BaseModel):
    url: str


class CompetitorMonitorRequest(BaseModel):
    url: str
    previous_hash: str = None


@router.post("/api/admin/intelligence/crawl")
async def crawl_url_endpoint(body: CrawlRequest, admin: dict = Depends(get_admin)):
    """Web-Crawling: URL crawlen und LLM-fertigen Content extrahieren."""
    from services.crawl4ai_service import crawl_url
    result = await crawl_url(
        url=body.url,
        extract_mode=body.extract_mode,
        css_selector=body.css_selector,
        max_pages=body.max_pages,
    )

    # Ergebnis in Brain speichern
    if result.get("success"):
        try:
            from services import supabase_client as supa
            await supa.store_brain_note(
                title=f"Crawl: {result.get('title', body.url)[:100]}",
                content=f"URL: {body.url}\nTitel: {result.get('title', '')}\n\n{result.get('content', '')[:3000]}",
                note_type="research",
                tags=["crawl4ai", "web-research", body.extract_mode],
                created_by="intelligence-service"
            )
        except Exception:
            pass

    return result


@router.post("/api/admin/intelligence/research-company")
async def research_company_endpoint(body: CompanyResearchRequest, admin: dict = Depends(get_admin)):
    """Firmen-Recherche: Website analysieren für Lead-Qualifizierung."""
    from services.crawl4ai_service import research_company
    result = await research_company(body.url)

    # Lead-Enrichment in MongoDB speichern
    if result.get("success"):
        await S.db.intelligence_results.insert_one({
            "result_id": new_id("intel"),
            "type": "company_research",
            "url": body.url,
            "data": result,
            "created_at": utcnow().isoformat(),
            "created_by": admin.get("email", "admin"),
        })

    return result


@router.post("/api/admin/intelligence/monitor-competitor")
async def monitor_competitor_endpoint(body: CompetitorMonitorRequest, admin: dict = Depends(get_admin)):
    """Wettbewerbsmonitoring: Änderungen auf Competitor-Website erkennen."""
    from services.crawl4ai_service import monitor_competitor
    result = await monitor_competitor(body.url, body.previous_hash)

    if result.get("success"):
        await S.db.competitor_monitoring.insert_one({
            "monitor_id": new_id("mon"),
            "url": body.url,
            "content_hash": result.get("content_hash"),
            "changed": result.get("changed", False),
            "monitored_at": utcnow().isoformat(),
            "created_by": admin.get("email", "admin"),
        })

    return result


# ════════════════════════════════════════════════════════════
# NUTRIENT AI — Document Processing
# ════════════════════════════════════════════════════════════

class DocumentChatRequest(BaseModel):
    file_path: str
    question: str


@router.post("/api/admin/intelligence/analyze-document")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    analysis_type: str = "extract",
    admin: dict = Depends(get_admin)
):
    """PDF/Dokument analysieren via Nutrient AI."""
    from services.nutrient_service import analyze_document, is_configured

    if not is_configured():
        return {"success": False, "error": "NUTRIENT_API_KEY nicht konfiguriert. Bitte unter nutrient.io registrieren."}

    # Datei temporär speichern
    import tempfile
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await analyze_document(tmp_path, analysis_type)
        return result
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.post("/api/admin/intelligence/contract-risk")
async def contract_risk_endpoint(
    file: UploadFile = File(...),
    admin: dict = Depends(get_admin)
):
    """Vertrags-Risikoscoring: PDF analysieren und Risiken bewerten."""
    from services.nutrient_service import contract_risk_score, is_configured

    if not is_configured():
        # Fallback: Nur mit DeepSeek analysieren (ohne Nutrient-Extraktion)
        import tempfile
        suffix = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        try:
            # Versuche direkte Textextraktion via Python
            import io
            text_content = content.decode("utf-8", errors="ignore")[:10000]
            if len(text_content.strip()) < 100:
                return {"success": False, "error": "NUTRIENT_API_KEY nicht konfiguriert und Dokument ist nicht textbasiert."}

            from services import deepseek_provider as deepseek
            scoring = await deepseek.chat_completion(
                messages=[
                    {"role": "system", "content": "Du bist ein Vertrags-Risikobewertungs-Experte. Analysiere und bewerte den Vertrag. Antwort als JSON: {\"score\": N, \"risks\": [...], \"missing\": [...], \"recommendations\": [...]}"},
                    {"role": "user", "content": f"Vertragstext:\n{text_content}"}
                ],
                temperature=0.2
            )
            if "error" not in scoring:
                try:
                    risk_data = json.loads(scoring["content"])
                    return {"success": True, "fallback": True, **risk_data, "scored_at": utcnow().isoformat()}
                except json.JSONDecodeError:
                    return {"success": True, "fallback": True, "analysis": scoring["content"], "scored_at": utcnow().isoformat()}
            return {"success": False, "error": scoring.get("error")}
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    import tempfile
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await contract_risk_score(tmp_path)
        return result
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.post("/api/admin/intelligence/document-chat")
async def document_chat_endpoint(body: DocumentChatRequest, admin: dict = Depends(get_admin)):
    """Dokumenten-Chat: Frage an ein Dokument stellen."""
    from services.nutrient_service import document_chat
    return await document_chat(body.file_path, body.question)


# ════════════════════════════════════════════════════════════
# INTELLIGENCE STATUS
# ════════════════════════════════════════════════════════════

@router.get("/api/admin/intelligence/status")
async def intelligence_status(admin: dict = Depends(get_admin)):
    """Status aller Intelligence-Dienste."""
    crawl4ai_ok = False
    try:
        from crawl4ai import AsyncWebCrawler
        crawl4ai_ok = True
    except ImportError:
        pass

    nutrient_configured = bool(os.environ.get("NUTRIENT_API_KEY", ""))
    research_count = await S.db.intelligence_results.count_documents({})
    monitor_count = await S.db.competitor_monitoring.count_documents({})

    return {
        "crawl4ai": {"installed": crawl4ai_ok, "status": "ok" if crawl4ai_ok else "not_installed"},
        "nutrient": {"configured": nutrient_configured, "status": "ok" if nutrient_configured else "api_key_missing"},
        "stats": {"research_results": research_count, "competitor_monitors": monitor_count},
    }
