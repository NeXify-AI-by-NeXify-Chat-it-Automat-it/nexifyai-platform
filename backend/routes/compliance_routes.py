"""
Legal & Compliance Routes — aktiviert den Legal Guardian für API-Zugriff.

Endpunkte:
  GET  /api/admin/compliance/summary    — Ampelsystem-Report
  POST /api/admin/compliance/check      — Prüft Kommunikation/Outreach
  GET  /api/admin/compliance/risks      — Alle offenen Risiken
  POST /api/admin/compliance/risk       — Neues Risiko eintragen
  POST /api/admin/compliance/opt-out    — Widerspruch verwalten
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from services.legal_guardian import LegalGuardian, LEGAL_RISK_LEVELS, COMPLIANCE_CHECKS

logger = logging.getLogger("nexifyai.routes.compliance")
router = APIRouter(prefix="/api/admin/compliance", tags=["compliance"])

def get_guardian(request: Request) -> LegalGuardian:
    """Dependency: LegalGuardian aus der App-Instanz holen."""
    guardian = getattr(request.app.state, "legal_guardian", None)
    if guardian is None:
        # Auto-init falls nicht vorhanden
        from routes.shared import S
        guardian = LegalGuardian(S.db, S.memory_svc)
        request.app.state.legal_guardian = guardian
    return guardian


@router.get("/summary")
async def compliance_summary(request: Request):
    """Gesamt-Status aller Compliance-Prüfungen (Ampelsystem)."""
    guardian = get_guardian(request)
    try:
        summary = await guardian.compliance_summary()
    except Exception as e:
        logger.error(f"compliance_summary failed: {e}")
        # Fallback: hardcoded defaults
        summary = {
            "status": "degraded",
            "checks_passed": 0,
            "checks_total": len(COMPLIANCE_CHECKS),
            "open_risks": 0,
            "legal_guardian_active": True,
            "note": "Legal Guardian läuft, compliance_summary() noch nicht vollständig verdrahtet"
        }
    return summary


@router.get("/checks")
async def list_checks():
    """Listet alle möglichen Compliance-Prüfungen."""
    return {
        "risk_levels": LEGAL_RISK_LEVELS,
        "checks": {k: {"label": v["label"], "required": v.get("required", False)}
                   for k, v in COMPLIANCE_CHECKS.items()}
    }


@router.post("/outreach/check")
async def check_outreach(request: Request, data: dict):
    """Prüft eine Outreach-Nachricht auf DSGVO/UWG-Compliance."""
    guardian = get_guardian(request)
    try:
        result = await guardian.check_outreach(data)
        return result
    except Exception as e:
        raise HTTPException(500, f"Outreach-Check fehlgeschlagen: {e}")


@router.post("/contract/check")
async def check_contract(request: Request, data: dict):
    """Prüft einen Vertrag auf AVV/AGB-Compliance."""
    guardian = get_guardian(request)
    try:
        result = await guardian.check_contract(data)
        return result
    except Exception as e:
        raise HTTPException(500, f"Contract-Check fehlgeschlagen: {e}")


@router.post("/communication/check")
async def check_communication(request: Request, data: dict):
    """Prüft eine Kommunikation auf Impressum/Opt-Out-Pflicht."""
    guardian = get_guardian(request)
    try:
        result = await guardian.check_communication(data)
        return result
    except Exception as e:
        raise HTTPException(500, f"Communication-Check fehlgeschlagen: {e}")


@router.post("/billing/check")
async def check_billing(request: Request, data: dict):
    """Prüft eine Rechnung auf DIN 5008/Steuer-Compliance."""
    guardian = get_guardian(request)
    try:
        result = await guardian.check_billing(data)
        return result
    except Exception as e:
        raise HTTPException(500, f"Billing-Check fehlgeschlagen: {e}")


@router.get("/risks")
async def get_risks(request: Request, resolved: Optional[bool] = None):
    """Alle offenen/gelösten Risiken."""
    guardian = get_guardian(request)
    try:
        risks = await guardian.get_risks(resolved=resolved)
        return {"risks": risks, "total": len(risks)}
    except Exception as e:
        raise HTTPException(500, f"Risiken konnten nicht geladen werden: {e}")


@router.post("/risk")
async def add_risk(request: Request, risk_data: dict):
    """Neues Risiko eintragen (z.B. bei fehlendem AVV)."""
    guardian = get_guardian(request)
    entity_type = risk_data.get("entity_type", "customer")
    entity_id = risk_data.get("entity_id", "unknown")
    risk = risk_data.get("risk", {})
    try:
        result = await guardian.add_risk(entity_type, entity_id, risk)
        return result
    except Exception as e:
        raise HTTPException(500, f"Risiko konnte nicht eingetragen werden: {e}")


@router.post("/opt-out")
async def opt_out(request: Request, data: dict):
    """Opt-Out/Widerspruch für eine E-Mail-Adresse."""
    guardian = get_guardian(request)
    email = data.get("email", "")
    reason = data.get("reason", "")
    try:
        result = await guardian.opt_out(email, reason)
        return result
    except Exception as e:
        raise HTTPException(500, f"Opt-Out fehlgeschlagen: {e}")


@router.get("/audit-log")
async def audit_log(request: Request, limit: int = 50):
    """Letzte Compliance-Events."""
    guardian = get_guardian(request)
    try:
        log = await guardian.get_audit_log(limit=limit)
        return {"events": log, "total": len(log)}
    except Exception as e:
        raise HTTPException(500, f"Audit-Log nicht verfügbar: {e}")
