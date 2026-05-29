"""
NeXifyAI — SLA Routes (CRM Phase 2)
SLA-Status und Compliance für Kunden.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from .shared import get_current_customer

router = APIRouter()


def get_sla_for_tariff(tariff: str = "") -> dict:
    """SLA-Konfiguration pro Tarif."""
    tariff = tariff.lower()
    if "growth" in tariff or "enterprise" in tariff:
        return {
            "name": "Enterprise",
            "response_time": "15 min",
            "resolution_time": "4h",
            "support_hours": "24/7",
            "priority": "P0-P1"
        }
    elif "starter" in tariff:
        return {
            "name": "Business",
            "response_time": "1h",
            "resolution_time": "8h",
            "support_hours": "Business hours",
            "priority": "P1-P2"
        }
    else:
        return {
            "name": "Standard",
            "response_time": "4h",
            "resolution_time": "24h",
            "support_hours": "Business hours",
            "priority": "P2-P3"
        }


def _calc_sla_compliance(email: str, sla_config: dict) -> float:
    """Berechnet SLA-Compliance in Prozent."""
    if not sla_config:
        return 100.0
    return 100.0  # Platzhalter — echte Berechnung bei Ticket-Resolve


@router.get("/api/customer/sla")
async def customer_sla(user=Depends(get_current_customer)):
    """SLA-Status des Kunden basierend auf Tarif."""
    from services.compat import S  # MongoDB-Instance

    email = user.get("email", "").lower()

    # Tarif aus Contract ermitteln
    contract = await S.db.contracts.find_one(
        {"customer.email": email, "status": "active"},
        {"_id": 0}
    )
    if not contract:
        return {"sla": None, "tier": None, "message": "Kein aktiver Vertrag"}

    tariff = contract.get("tariff", "").lower()
    sla_config = get_sla_for_tariff(tariff)

    # Support-Tickets in den letzten 30 Tagen
    recent_tickets = []
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    async for t in S.db.support_tickets.find(
        {"customer_email": email, "created_at": {"$gte": thirty_days_ago.isoformat()}},
        {"_id": 0, "ticket_id": 1, "subject": 1, "status": 1, "priority": 1, "created_at": 1}
    ).sort("created_at", -1).limit(10):
        recent_tickets.append(t)

    # Durchschnittliche Resolve-Zeit berechnen
    avg_resolve_hours = None
    resolved = []
    async for t in S.db.support_tickets.find(
        {"customer_email": email, "status": "resolved", "resolved_at": {"$ne": None}},
        {"_id": 0, "created_at": 1, "resolved_at": 1}
    ).limit(20):
        resolved.append(t)

    if resolved:
        total_hours = 0
        count = 0
        for t in resolved:
            try:
                created = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))
                resolved_at = datetime.fromisoformat(t["resolved_at"].replace("Z", "+00:00"))
                total_hours += (resolved_at - created).total_seconds() / 3600
                count += 1
            except Exception:
                pass
        if count > 0:
            avg_resolve_hours = round(total_hours / count, 1)

    return {
        "sla": sla_config,
        "tier": sla_config.get("name") if sla_config else None,
        "contract_tariff": tariff,
        "recent_tickets": recent_tickets,
        "tickets_last_30d": len(recent_tickets),
        "avg_resolve_time_hours": avg_resolve_hours,
        "sla_compliance_pct": _calc_sla_compliance(email, sla_config),
    }