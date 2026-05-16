"""
Legal & Compliance Guardian — operativ verdrahtet.

Pflicht:
- Aktiv an Outreach, Verträge, Angebots-/Rechnungslogik,
  Kommunikation, Rechtsseiten, Signatur-/Vertragsannahme binden.
- Risiken markieren.
- Gate-Fälle setzen.
- Änderungen historisieren.
- Keine ungated rechtliche Außenwirkung.
- DSGVO/UWG im Outreach aktiv prüfen.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from domain import create_timeline_event, new_id, utcnow

logger = logging.getLogger("nexifyai.services.legal_guardian")


LEGAL_RISK_LEVELS = {
    "none": {"label": "Kein Risiko", "gate": False, "color": "#10b981"},
    "low": {"label": "Geringes Risiko", "gate": False, "color": "#f59e0b"},
    "medium": {"label": "Mittleres Risiko", "gate": True, "color": "#f97316"},
    "high": {"label": "Hohes Risiko", "gate": True, "color": "#ef4444"},
    "critical": {"label": "Kritisch", "gate": True, "color": "#dc2626"},
}

COMPLIANCE_CHECKS = {
    "dsgvo_consent": {
        "label": "DSGVO-Einwilligung",
        "description": "Einwilligung zur Datenverarbeitung nach Art. 6 Abs. 1 DSGVO",
        "applies_to": ["outreach", "contract", "communication"],
        "required": True,
    },
    "uwg_kaltansprache": {
        "label": "UWG Kaltansprache",
        "description": "Prüfung § 7 UWG — unzumutbare Belästigung bei Kaltansprache",
        "applies_to": ["outreach"],
        "required": True,
    },
    "ki_transparenz": {
        "label": "KI-Transparenz",
        "description": "EU AI Act Art. 52 — Kennzeichnungspflicht für KI-generierte Inhalte",
        "applies_to": ["outreach", "communication", "contract"],
        "required": True,
    },
    "datenschutzerklaerung": {
        "label": "Datenschutzerklärung",
        "description": "Verweis auf aktuelle Datenschutzerklärung vorhanden",
        "applies_to": ["contract", "communication"],
        "required": True,
    },
    "widerrufsrecht": {
        "label": "Widerrufsrecht",
        "description": "Widerrufsbelehrung nach § 312g BGB",
        "applies_to": ["contract"],
        "required": True,
    },
    "agb_verweis": {
        "label": "AGB-Verweis",
        "description": "Verweis auf Allgemeine Geschäftsbedingungen",
        "applies_to": ["contract", "quote"],
        "required": True,
    },
    "impressum": {
        "label": "Impressumspflicht",
        "description": "§ 5 TMG — vollständiges Impressum",
        "applies_to": ["communication", "outreach"],
        "required": True,
    },
    "opt_out": {
        "label": "Opt-Out Möglichkeit",
        "description": "Abmeldemöglichkeit in jeder kommerziellen Kommunikation",
        "applies_to": ["outreach", "communication"],
        "required": True,
    },
    "avv": {
        "label": "Auftragsverarbeitung",
        "description": "AVV nach Art. 28 DSGVO bei Datenverarbeitung im Auftrag",
        "applies_to": ["contract"],
        "required": False,
    },
    "payment_pci": {
        "label": "PCI DSS Compliance",
        "description": "Zahlungssicherheit via zertifizierten Payment Provider",
        "applies_to": ["billing"],
        "required": True,
    },
}


class LegalGuardian:
    """Operativer Legal & Compliance Guardian."""

    def __init__(self, db, memory_svc=None):
        self.db = db
        self.memory_svc = memory_svc

    async def check_outreach(self, lead_data: dict) -> dict:
        """
        Legal-Gate für Outreach.
        Prüft DSGVO, UWG, Suppression, Opt-Out, KI-Transparenz.
        Returns: {approved: bool, risk_level, checks, gate_reason}
        """
        checks = []
        risk_level = "none"
        gate_reasons = []
        email = lead_data.get("email", lead_data.get("contact_email", "")).lower()

        # Suppression check
        if email:
            suppressed = await self.db.suppression_list.find_one({"email": email})
            if suppressed:
                checks.append({"check": "suppression", "passed": False, "detail": "E-Mail auf Suppression-Liste"})
                risk_level = "critical"
                gate_reasons.append("suppression_list")
            else:
                checks.append({"check": "suppression", "passed": True, "detail": "Nicht auf Suppression-Liste"})

        # Opt-out check
        if email:
            opt_out = await self.db.opt_outs.find_one({"email": email})
            if opt_out:
                checks.append({"check": "opt_out", "passed": False, "detail": "Kunde hat Opt-Out gewählt"})
                risk_level = "critical"
                gate_reasons.append("opt_out")
            else:
                checks.append({"check": "opt_out", "passed": True, "detail": "Kein Opt-Out vorliegend"})

        # UWG Kaltansprache
        channel = lead_data.get("channel", "email")
        has_prior_relationship = lead_data.get("existing_customer", False)
        has_consent = lead_data.get("consent_given", False)
        if channel == "email" and not has_prior_relationship and not has_consent:
            checks.append({"check": "uwg_kaltansprache", "passed": False, "detail": "§ 7 UWG: E-Mail-Kaltansprache ohne Einwilligung oder Bestandskundenbeziehung"})
            if risk_level in ("none", "low"):
                risk_level = "high"
            gate_reasons.append("uwg_kaltansprache_email")
        elif channel == "phone" and not has_prior_relationship:
            checks.append({"check": "uwg_kaltansprache", "passed": False, "detail": "§ 7 UWG: Telefonische Kaltansprache (B2B unter Umständen zulässig)"})
            if risk_level in ("none",):
                risk_level = "medium"
            gate_reasons.append("uwg_kaltansprache_phone_b2b")
        else:
            checks.append({"check": "uwg_kaltansprache", "passed": True, "detail": "Bestandskundenbeziehung oder Einwilligung vorhanden"})

        # KI-Transparenz
        is_ai_generated = lead_data.get("ai_generated", True)
        if is_ai_generated:
            checks.append({"check": "ki_transparenz", "passed": True, "detail": "KI-Transparenzkennzeichnung erforderlich — muss in Kommunikation enthalten sein"})

        # Fit-Score minimum
        score = lead_data.get("score", 0)
        if score < 30:
            checks.append({"check": "fit_score", "passed": False, "detail": f"Fit-Score zu niedrig ({score}/100) — keine pauschale Ansprache"})
            if risk_level in ("none", "low"):
                risk_level = "medium"
            gate_reasons.append("low_fit_score")
        else:
            checks.append({"check": "fit_score", "passed": True, "detail": f"Fit-Score ausreichend ({score}/100)"})

        approved = risk_level in ("none", "low")

        # Log
        audit_entry = {
            "audit_id": new_id("lga"),
            "type": "outreach_check",
            "entity_email": email,
            "risk_level": risk_level,
            "approved": approved,
            "checks": checks,
            "gate_reasons": gate_reasons,
            "timestamp": utcnow().isoformat(),
        }
        await self.db.legal_audit.insert_one({**audit_entry})

        return {
            "approved": approved,
            "risk_level": risk_level,
            "checks": checks,
            "gate_reasons": gate_reasons,
            "audit_id": audit_entry["audit_id"],
        }

    async def check_contract(self, contract: dict) -> dict:
        """
        Legal-Gate für Vertragsversand.
        Prüft: AGB, Datenschutz, KI-Hinweise, Zahlungsbedingungen, Widerruf.
        """
        checks = []
        risk_level = "none"
        gate_reasons = []

        legal_modules = contract.get("legal_modules", {})

        # Check required legal modules
        from domain import LEGAL_MODULES
        for lm in LEGAL_MODULES:
            if lm["required"]:
                module_data = legal_modules.get(lm["key"], {})
                version = module_data.get("version", "")
                if version:
                    checks.append({"check": lm["key"], "passed": True, "detail": f"{lm['label']} Version {version} vorhanden"})
                else:
                    checks.append({"check": lm["key"], "passed": False, "detail": f"{lm['label']} fehlt — Pflichtmodul"})
                    if risk_level in ("none", "low"):
                        risk_level = "medium"
                    gate_reasons.append(f"missing_{lm['key']}")

        # Calculation check
        calc = contract.get("calculation", {})
        if not calc or not calc.get("total_contract_eur"):
            checks.append({"check": "calculation", "passed": False, "detail": "Keine Kalkulation vorhanden"})
            if risk_level in ("none",):
                risk_level = "low"
        else:
            checks.append({"check": "calculation", "passed": True, "detail": f"Kalkulation: {calc.get('total_contract_eur', 0)} EUR"})

        # Customer data
        customer = contract.get("customer", {})
        if not customer.get("email"):
            checks.append({"check": "customer_data", "passed": False, "detail": "Keine Kunden-E-Mail"})
            risk_level = "high"
            gate_reasons.append("no_customer_email")
        else:
            checks.append({"check": "customer_data", "passed": True, "detail": "Kundendaten vorhanden"})

        approved = risk_level in ("none", "low")

        audit_entry = {
            "audit_id": new_id("lga"),
            "type": "contract_check",
            "entity_id": contract.get("contract_id", ""),
            "risk_level": risk_level,
            "approved": approved,
            "checks": checks,
            "gate_reasons": gate_reasons,
            "timestamp": utcnow().isoformat(),
        }
        await self.db.legal_audit.insert_one({**audit_entry})

        return {
            "approved": approved,
            "risk_level": risk_level,
            "checks": checks,
            "gate_reasons": gate_reasons,
            "audit_id": audit_entry["audit_id"],
        }

    async def check_communication(self, comm_data: dict) -> dict:
        """
        Legal-Gate für Kommunikation (E-Mail, WhatsApp, Portal).
        """
        checks = []
        risk_level = "none"

        channel = comm_data.get("channel", "email")
        content = comm_data.get("content", "")
        recipient = comm_data.get("recipient", "")

        # Opt-Out prüfen
        if recipient:
            opt_out = await self.db.opt_outs.find_one({"email": recipient.lower()})
            if opt_out:
                checks.append({"check": "opt_out", "passed": False, "detail": "Empfänger hat Opt-Out"})
                risk_level = "critical"
            else:
                checks.append({"check": "opt_out", "passed": True, "detail": "Kein Opt-Out"})

        # KI-Transparenz
        if comm_data.get("ai_generated", False):
            has_disclosure = any(kw in content.lower() for kw in ["ki-", "künstliche intelligenz", "automatisch erstellt", "ai-"])
            if not has_disclosure:
                checks.append({"check": "ki_transparenz", "passed": False, "detail": "KI-generierter Inhalt ohne Kennzeichnung"})
                if risk_level in ("none",):
                    risk_level = "low"
            else:
                checks.append({"check": "ki_transparenz", "passed": True, "detail": "KI-Kennzeichnung vorhanden"})

        # Impressum/Absender
        if channel in ("email",):
            has_footer = any(kw in content.lower() for kw in ["nexify", "impressum", "nexifyai.de", "abmeld"])
            if not has_footer:
                checks.append({"check": "impressum", "passed": False, "detail": "Kein Impressum/Absenderkennzeichnung in E-Mail"})
                if risk_level in ("none",):
                    risk_level = "low"

        approved = risk_level in ("none", "low")
        return {"approved": approved, "risk_level": risk_level, "checks": checks}

    async def check_billing(self, invoice_data: dict) -> dict:
        """
        Legal-Gate für Rechnungs-/Zahlungslogik.
        """
        checks = []
        risk_level = "none"

        totals = invoice_data.get("totals", {})
        if not totals.get("vat_rate"):
            checks.append({"check": "vat", "passed": False, "detail": "Kein MwSt.-Satz definiert"})
            risk_level = "medium"
        else:
            checks.append({"check": "vat", "passed": True, "detail": f"MwSt.-Satz: {totals.get('vat_rate')}%"})

        if not invoice_data.get("customer", {}).get("email"):
            checks.append({"check": "customer", "passed": False, "detail": "Keine Kunden-E-Mail auf Rechnung"})
            risk_level = "medium"

        if not invoice_data.get("invoice_number"):
            checks.append({"check": "numbering", "passed": False, "detail": "Keine Rechnungsnummer"})
            risk_level = "high"

        approved = risk_level in ("none", "low")
        return {"approved": approved, "risk_level": risk_level, "checks": checks}

    async def add_risk(self, entity_type: str, entity_id: str, risk: dict, actor: str = "system") -> dict:
        """Risiko an Entity anhängen und historisieren."""
        risk_entry = {
            "risk_id": new_id("rsk"),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "level": risk.get("level", "low"),
            "description": risk.get("description", ""),
            "mitigation": risk.get("mitigation", ""),
            "created_by": actor,
            "created_at": utcnow().isoformat(),
            "resolved": False,
        }
        await self.db.legal_risks.insert_one({**risk_entry})
        await self.db.timeline_events.insert_one(create_timeline_event(
            entity_type, entity_id, "legal_risk_added",
            actor=actor, actor_type="system",
            details={"risk_id": risk_entry["risk_id"], "level": risk.get("level"), "description": risk.get("description", "")[:100]},
        ))
        return risk_entry

    async def resolve_risk(self, risk_id: str, resolution: str, actor: str = "admin") -> dict:
        """Risiko als gelöst markieren."""
        await self.db.legal_risks.update_one(
            {"risk_id": risk_id},
            {"$set": {"resolved": True, "resolution": resolution, "resolved_by": actor, "resolved_at": utcnow().isoformat()}}
        )
        return {"resolved": True}

    async def get_risks(self, entity_type: str = None, entity_id: str = None, resolved: bool = None) -> list:
        """Risiken abrufen."""
        query = {}
        if entity_type:
            query["entity_type"] = entity_type
        if entity_id:
            query["entity_id"] = entity_id
        if resolved is not None:
            query["resolved"] = resolved
        risks = []
        async for r in self.db.legal_risks.find(query, {"_id": 0}).sort("created_at", -1):
            risks.append(r)
        return risks

    async def get_audit_log(self, entity_type: str = None, limit: int = 50) -> list:
        """Legal-Audit-Log abrufen."""
        query = {}
        if entity_type:
            query["type"] = {"$regex": entity_type}
        entries = []
        async for e in self.db.legal_audit.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit):
            entries.append(e)
        return entries

    async def opt_out(self, email: str, reason: str = "", actor: str = "customer") -> dict:
        """Opt-Out registrieren."""
        email = email.lower().strip()
        existing = await self.db.opt_outs.find_one({"email": email})
        if existing:
            return {"already_opted_out": True}
        await self.db.opt_outs.insert_one({
            "email": email,
            "reason": reason,
            "actor": actor,
            "created_at": utcnow().isoformat(),
        })
        # Also suppress
        await self.db.suppression_list.update_one(
            {"email": email},
            {"$set": {"email": email, "reason": f"opt_out: {reason}", "added_at": utcnow().isoformat()}},
            upsert=True,
        )
        return {"opted_out": True}

    async def compliance_summary(self) -> dict:
        """Gesamtübersicht Compliance-Status."""
        open_risks = await self.db.legal_risks.count_documents({"resolved": False})
        total_risks = await self.db.legal_risks.count_documents({})
        total_audits = await self.db.legal_audit.count_documents({})
        opt_outs = await self.db.opt_outs.count_documents({})
        suppressions = await self.db.suppression_list.count_documents({})

        recent_gates = []
        async for a in self.db.legal_audit.find({"approved": False}, {"_id": 0}).sort("timestamp", -1).limit(10):
            recent_gates.append(a)

        return {
            "risks": {"open": open_risks, "total": total_risks, "resolved": total_risks - open_risks},
            "audits": {"total": total_audits},
            "opt_outs": opt_outs,
            "suppressions": suppressions,
            "recent_gates": recent_gates,
            "compliance_checks": {k: v["label"] for k, v in COMPLIANCE_CHECKS.items()},
        }
