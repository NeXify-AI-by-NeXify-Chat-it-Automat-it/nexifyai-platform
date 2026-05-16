"""
NeXifyAI — External API v1 Routes
API-Key-basierte Authentifizierung für externen programmatischen Zugriff.
Prefix: /api/v1/
"""
import secrets
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Request, Depends, Header, Query
from pydantic import BaseModel, Field

from routes.shared import S, log_audit, utcnow, new_id

logger = logging.getLogger("nexifyai.api_v1")

router = APIRouter(prefix="/api/v1", tags=["External API v1"])


# ══════════════════════════════════════════════════════════════
# API KEY HELPERS
# ══════════════════════════════════════════════════════════════
def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_api_key() -> tuple:
    """Returns (display_key, hash). Display key shown once, hash stored."""
    raw = f"nxa_live_{secrets.token_hex(24)}"
    return raw, _hash_key(raw)


async def validate_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """Dependency: validates API key from X-API-Key header."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API-Key fehlt. Header: X-API-Key")
    key_hash = _hash_key(x_api_key)
    key_doc = await S.db.api_keys.find_one({"key_hash": key_hash, "is_active": True}, {"_id": 0})
    if not key_doc:
        raise HTTPException(status_code=401, detail="Ungültiger oder deaktivierter API-Key")
    if key_doc.get("expires_at"):
        exp = key_doc["expires_at"]
        if isinstance(exp, str):
            exp = datetime.fromisoformat(exp)
        if exp < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="API-Key abgelaufen")
    # Rate limiting
    rate_limit = key_doc.get("rate_limit_per_hour", 1000)
    now = datetime.now(timezone.utc)
    hour_key = f"apirl_{key_doc['key_id']}_{now.strftime('%Y%m%d%H')}"
    if hour_key in S.rate_limit_storage:
        count, _ = S.rate_limit_storage[hour_key]
        if count >= rate_limit:
            raise HTTPException(status_code=429, detail=f"Rate-Limit erreicht ({rate_limit}/Stunde)")
        S.rate_limit_storage[hour_key] = (count + 1, _)
    else:
        S.rate_limit_storage[hour_key] = (1, now.timestamp())
    # Update last_used
    await S.db.api_keys.update_one(
        {"key_id": key_doc["key_id"]},
        {"$set": {"last_used_at": now.isoformat()}, "$inc": {"total_requests": 1}}
    )
    return key_doc


def check_scope(key_doc: dict, required_scope: str):
    """Check if API key has the required scope."""
    scopes = key_doc.get("scopes", [])
    if "*" in scopes or "all" in scopes:
        return True
    # Check wildcard: "contacts:*" matches "contacts:read"
    resource = required_scope.split(":")[0]
    if f"{resource}:*" in scopes:
        return True
    if required_scope in scopes:
        return True
    raise HTTPException(status_code=403, detail=f"API-Key hat nicht die Berechtigung: {required_scope}")


# ══════════════════════════════════════════════════════════════
# MODELS
# ══════════════════════════════════════════════════════════════
class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    per_page: int
    has_more: bool


class ContactCreate(BaseModel):
    email: str
    first_name: str = ""
    last_name: str = ""
    company: str = ""
    phone: str = ""
    source: str = "api"
    tags: list = []
    metadata: dict = {}


class LeadCreate(BaseModel):
    email: str
    vorname: str = ""
    nachname: str = ""
    unternehmen: str = ""
    telefon: str = ""
    nachricht: str = ""
    source: str = "api"
    kanal: str = "api"


class WebhookRegister(BaseModel):
    url: str
    events: List[str] = ["*"]
    secret: str = ""
    description: str = ""


# ══════════════════════════════════════════════════════════════
# API KEY MANAGEMENT (Admin — called from admin_routes)
# ══════════════════════════════════════════════════════════════
class CreateApiKeyRequest(BaseModel):
    name: str
    scopes: List[str] = ["all"]
    rate_limit_per_hour: int = 1000
    expires_in_days: Optional[int] = None
    description: str = ""


# ══════════════════════════════════════════════════════════════
# DOCUMENTATION ENDPOINT
# ══════════════════════════════════════════════════════════════
@router.get("/docs", dependencies=[])
async def api_documentation():
    """Vollständige API-Dokumentation für externe Integrationen."""
    return {
        "name": "NeXifyAI External API",
        "version": "1.0.0",
        "base_url": "/api/v1",
        "authentication": {
            "type": "API Key",
            "header": "X-API-Key",
            "description": "API-Key im Header X-API-Key mitschicken. Keys werden im Admin-Panel generiert.",
            "example": "curl -H 'X-API-Key: nxa_live_...' https://your-domain.com/api/v1/contacts"
        },
        "rate_limits": {
            "default": "1.000 Anfragen/Stunde",
            "configurable": True,
            "header_info": "Rate-Limit-Status wird bei 429-Fehlern zurückgegeben."
        },
        "pagination": {
            "default_page_size": 50,
            "max_page_size": 200,
            "parameters": {"page": "Seitennummer (ab 1)", "per_page": "Einträge pro Seite (max 200)"}
        },
        "endpoints": {
            "contacts": {
                "list": {"method": "GET", "path": "/contacts", "scopes": ["contacts:read"], "params": ["page", "per_page", "search", "source"]},
                "create": {"method": "POST", "path": "/contacts", "scopes": ["contacts:write"], "body": "ContactCreate"},
                "get": {"method": "GET", "path": "/contacts/{contact_id}", "scopes": ["contacts:read"]},
                "update": {"method": "PUT", "path": "/contacts/{contact_id}", "scopes": ["contacts:write"]},
            },
            "leads": {
                "list": {"method": "GET", "path": "/leads", "scopes": ["leads:read"], "params": ["page", "per_page", "status", "source"]},
                "create": {"method": "POST", "path": "/leads", "scopes": ["leads:write"], "body": "LeadCreate"},
                "get": {"method": "GET", "path": "/leads/{lead_id}", "scopes": ["leads:read"]},
            },
            "quotes": {
                "list": {"method": "GET", "path": "/quotes", "scopes": ["quotes:read"], "params": ["page", "per_page", "status"]},
                "get": {"method": "GET", "path": "/quotes/{quote_id}", "scopes": ["quotes:read"]},
            },
            "contracts": {
                "list": {"method": "GET", "path": "/contracts", "scopes": ["contracts:read"]},
                "get": {"method": "GET", "path": "/contracts/{contract_id}", "scopes": ["contracts:read"]},
            },
            "projects": {
                "list": {"method": "GET", "path": "/projects", "scopes": ["projects:read"]},
                "get": {"method": "GET", "path": "/projects/{project_id}", "scopes": ["projects:read"]},
            },
            "invoices": {
                "list": {"method": "GET", "path": "/invoices", "scopes": ["invoices:read"], "params": ["status"]},
                "get": {"method": "GET", "path": "/invoices/{invoice_id}", "scopes": ["invoices:read"]},
            },
            "stats": {"method": "GET", "path": "/stats", "scopes": ["stats:read"]},
            "webhooks": {
                "register": {"method": "POST", "path": "/webhooks", "scopes": ["webhooks:write"]},
                "list": {"method": "GET", "path": "/webhooks", "scopes": ["webhooks:read"]},
                "delete": {"method": "DELETE", "path": "/webhooks/{webhook_id}", "scopes": ["webhooks:write"]},
            },
        },
        "scopes": [
            "all", "contacts:read", "contacts:write", "leads:read", "leads:write",
            "quotes:read", "contracts:read", "projects:read", "invoices:read",
            "stats:read", "webhooks:read", "webhooks:write"
        ],
        "error_format": {
            "structure": {"detail": "Fehlermeldung"},
            "codes": {
                "401": "Ungültiger oder fehlender API-Key",
                "403": "Fehlende Berechtigung (Scope)",
                "404": "Ressource nicht gefunden",
                "429": "Rate-Limit erreicht",
                "500": "Serverfehler"
            }
        }
    }


# ══════════════════════════════════════════════════════════════
# HEALTH / STATUS
# ══════════════════════════════════════════════════════════════
@router.get("/health")
async def api_health():
    return {"status": "operational", "version": "1.0.0", "timestamp": utcnow().isoformat()}


# ══════════════════════════════════════════════════════════════
# CONTACTS
# ══════════════════════════════════════════════════════════════
@router.get("/contacts")
async def list_contacts(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str = Query("", description="Suche nach E-Mail, Name oder Firma"),
    source: str = Query("", description="Filter nach Quelle"),
    key: dict = Depends(validate_api_key),
):
    check_scope(key, "contacts:read")
    query = {}
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}},
        ]
    if source:
        query["source"] = source
    total = await S.db.contacts.count_documents(query)
    skip = (page - 1) * per_page
    items = []
    async for c in S.db.contacts.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(per_page):
        items.append(c)
    return {"data": items, "total": total, "page": page, "per_page": per_page, "has_more": skip + per_page < total}


@router.post("/contacts", status_code=201)
async def create_contact_api(body: ContactCreate, key: dict = Depends(validate_api_key)):
    check_scope(key, "contacts:write")
    existing = await S.db.contacts.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="Kontakt mit dieser E-Mail existiert bereits")
    contact_id = new_id("con")
    doc = {
        "contact_id": contact_id,
        "email": body.email.lower(),
        "first_name": body.first_name,
        "last_name": body.last_name,
        "company": body.company,
        "phone": body.phone,
        "source": body.source,
        "tags": body.tags,
        "metadata": body.metadata,
        "created_at": utcnow().isoformat(),
        "updated_at": utcnow().isoformat(),
        "channels_used": ["api"],
    }
    await S.db.contacts.insert_one(doc)
    await log_audit("api_contact_created", key.get("name", "api"), {"contact_id": contact_id, "email": body.email})
    doc.pop("_id", None)
    return doc


@router.get("/contacts/{contact_id}")
async def get_contact_api(contact_id: str, key: dict = Depends(validate_api_key)):
    check_scope(key, "contacts:read")
    c = await S.db.contacts.find_one({"contact_id": contact_id}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail="Kontakt nicht gefunden")
    return c


@router.put("/contacts/{contact_id}")
async def update_contact_api(contact_id: str, request: Request, key: dict = Depends(validate_api_key)):
    check_scope(key, "contacts:write")
    body = await request.json()
    protected = {"contact_id", "_id", "created_at"}
    updates = {k: v for k, v in body.items() if k not in protected}
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen angegeben")
    updates["updated_at"] = utcnow().isoformat()
    result = await S.db.contacts.update_one({"contact_id": contact_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Kontakt nicht gefunden")
    c = await S.db.contacts.find_one({"contact_id": contact_id}, {"_id": 0})
    return c


# ══════════════════════════════════════════════════════════════
# LEADS
# ══════════════════════════════════════════════════════════════
@router.get("/leads")
async def list_leads(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: str = Query("", description="Filter nach Status"),
    source: str = Query("", description="Filter nach Quelle"),
    key: dict = Depends(validate_api_key),
):
    check_scope(key, "leads:read")
    query = {}
    if status:
        query["status"] = status
    if source:
        query["kanal"] = source
    total = await S.db.leads.count_documents(query)
    skip = (page - 1) * per_page
    items = []
    async for l in S.db.leads.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(per_page):
        items.append(l)
    return {"data": items, "total": total, "page": page, "per_page": per_page, "has_more": skip + per_page < total}


@router.post("/leads", status_code=201)
async def create_lead_api(body: LeadCreate, key: dict = Depends(validate_api_key)):
    check_scope(key, "leads:write")
    lead_id = new_id("lead")
    doc = {
        "lead_id": lead_id,
        "email": body.email.lower(),
        "vorname": body.vorname,
        "nachname": body.nachname,
        "unternehmen": body.unternehmen,
        "telefon": body.telefon,
        "nachricht": body.nachricht,
        "source": body.source,
        "kanal": body.kanal,
        "status": "new",
        "created_at": utcnow().isoformat(),
    }
    await S.db.leads.insert_one(doc)
    await log_audit("api_lead_created", key.get("name", "api"), {"lead_id": lead_id, "email": body.email})
    doc.pop("_id", None)
    return doc


@router.get("/leads/{lead_id}")
async def get_lead_api(lead_id: str, key: dict = Depends(validate_api_key)):
    check_scope(key, "leads:read")
    l = await S.db.leads.find_one({"lead_id": lead_id}, {"_id": 0})
    if not l:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    return l


# ══════════════════════════════════════════════════════════════
# QUOTES
# ══════════════════════════════════════════════════════════════
@router.get("/quotes")
async def list_quotes(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: str = Query(""),
    key: dict = Depends(validate_api_key),
):
    check_scope(key, "quotes:read")
    query = {}
    if status:
        query["status"] = status
    total = await S.db.quotes.count_documents(query)
    skip = (page - 1) * per_page
    items = []
    async for q in S.db.quotes.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(per_page):
        items.append(q)
    return {"data": items, "total": total, "page": page, "per_page": per_page, "has_more": skip + per_page < total}


@router.get("/quotes/{quote_id}")
async def get_quote_api(quote_id: str, key: dict = Depends(validate_api_key)):
    check_scope(key, "quotes:read")
    q = await S.db.quotes.find_one({"quote_id": quote_id}, {"_id": 0})
    if not q:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    return q


# ══════════════════════════════════════════════════════════════
# CONTRACTS
# ══════════════════════════════════════════════════════════════
@router.get("/contracts")
async def list_contracts(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: str = Query(""),
    key: dict = Depends(validate_api_key),
):
    check_scope(key, "contracts:read")
    query = {}
    if status:
        query["status"] = status
    total = await S.db.contracts.count_documents(query)
    skip = (page - 1) * per_page
    items = []
    async for c in S.db.contracts.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(per_page):
        items.append(c)
    return {"data": items, "total": total, "page": page, "per_page": per_page, "has_more": skip + per_page < total}


@router.get("/contracts/{contract_id}")
async def get_contract_api(contract_id: str, key: dict = Depends(validate_api_key)):
    check_scope(key, "contracts:read")
    c = await S.db.contracts.find_one({"contract_id": contract_id}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")
    return c


# ══════════════════════════════════════════════════════════════
# PROJECTS
# ══════════════════════════════════════════════════════════════
@router.get("/projects")
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: str = Query(""),
    key: dict = Depends(validate_api_key),
):
    check_scope(key, "projects:read")
    query = {}
    if status:
        query["status"] = status
    total = await S.db.projects.count_documents(query)
    skip = (page - 1) * per_page
    items = []
    async for p in S.db.projects.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(per_page):
        items.append(p)
    return {"data": items, "total": total, "page": page, "per_page": per_page, "has_more": skip + per_page < total}


@router.get("/projects/{project_id}")
async def get_project_api(project_id: str, key: dict = Depends(validate_api_key)):
    check_scope(key, "projects:read")
    p = await S.db.projects.find_one({"project_id": project_id}, {"_id": 0})
    if not p:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return p


# ══════════════════════════════════════════════════════════════
# INVOICES
# ══════════════════════════════════════════════════════════════
@router.get("/invoices")
async def list_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: str = Query(""),
    key: dict = Depends(validate_api_key),
):
    check_scope(key, "invoices:read")
    query = {}
    if status:
        query["status"] = status
    total = await S.db.invoices.count_documents(query)
    skip = (page - 1) * per_page
    items = []
    async for i in S.db.invoices.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(per_page):
        items.append(i)
    return {"data": items, "total": total, "page": page, "per_page": per_page, "has_more": skip + per_page < total}


@router.get("/invoices/{invoice_id}")
async def get_invoice_api(invoice_id: str, key: dict = Depends(validate_api_key)):
    check_scope(key, "invoices:read")
    i = await S.db.invoices.find_one({"invoice_id": invoice_id}, {"_id": 0})
    if not i:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    return i


# ══════════════════════════════════════════════════════════════
# STATS
# ══════════════════════════════════════════════════════════════
@router.get("/stats")
async def get_stats(key: dict = Depends(validate_api_key)):
    check_scope(key, "stats:read")
    stats = {
        "contacts": await S.db.contacts.count_documents({}),
        "leads": await S.db.leads.count_documents({}),
        "quotes": {
            "total": await S.db.quotes.count_documents({}),
            "sent": await S.db.quotes.count_documents({"status": "sent"}),
            "accepted": await S.db.quotes.count_documents({"status": "accepted"}),
        },
        "contracts": {
            "total": await S.db.contracts.count_documents({}),
            "accepted": await S.db.contracts.count_documents({"status": "accepted"}),
        },
        "projects": {
            "total": await S.db.projects.count_documents({}),
            "active": await S.db.projects.count_documents({"status": {"$in": ["discovery", "planning", "build", "review"]}}),
        },
        "invoices": {
            "total": await S.db.invoices.count_documents({}),
            "paid": await S.db.invoices.count_documents({"status": "paid"}),
            "pending": await S.db.invoices.count_documents({"status": "pending"}),
        },
        "timestamp": utcnow().isoformat(),
    }
    return stats


# ══════════════════════════════════════════════════════════════
# WEBHOOKS
# ══════════════════════════════════════════════════════════════
@router.post("/webhooks", status_code=201)
async def register_webhook(body: WebhookRegister, key: dict = Depends(validate_api_key)):
    check_scope(key, "webhooks:write")
    webhook_id = new_id("whk")
    doc = {
        "webhook_id": webhook_id,
        "url": body.url,
        "events": body.events,
        "secret": body.secret or secrets.token_hex(16),
        "description": body.description,
        "api_key_id": key["key_id"],
        "is_active": True,
        "created_at": utcnow().isoformat(),
        "last_triggered_at": None,
        "failure_count": 0,
    }
    await S.db.webhooks.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/webhooks")
async def list_webhooks(key: dict = Depends(validate_api_key)):
    check_scope(key, "webhooks:read")
    items = []
    async for w in S.db.webhooks.find({"api_key_id": key["key_id"]}, {"_id": 0}):
        items.append(w)
    return {"data": items, "total": len(items)}


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, key: dict = Depends(validate_api_key)):
    check_scope(key, "webhooks:write")
    result = await S.db.webhooks.delete_one({"webhook_id": webhook_id, "api_key_id": key["key_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Webhook nicht gefunden")
    return {"deleted": True}
