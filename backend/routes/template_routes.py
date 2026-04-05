"""
NeXifyAI — Service Templates / Boilerplate System
Vorgefertigte Konzepte für alle Leistungen der Agentur.
Jede Kundenbestellung < 3h fertigstellbar durch strukturierte Boilerplates.
"""
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional

from routes.shared import S, utcnow, new_id

logger = logging.getLogger("nexifyai.routes.templates")

router = APIRouter(tags=["Service Templates"])


# ── Auth ──
async def get_admin(request: Request):
    import jwt, os
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
# BOILERPLATE SERVICE TEMPLATES
# ════════════════════════════════════════════════════════════

SERVICE_TEMPLATES = {
    "starter_ai_agenten": {
        "key": "starter_ai_agenten",
        "name": "Starter AI Agenten AG",
        "tier": "starter",
        "price_monthly": 499,
        "duration_months": 24,
        "deposit_percent": 30,
        "deposit_amount": 3592.80,
        "description": "KI-Agenten-Grundpaket: Automatisierte Kundenbetreuung, Lead-Qualifizierung, E-Mail-Automatisierung",
        "deliverables": [
            "1x KI-Chatbot (Website-Integration)",
            "1x Lead-Qualifizierungs-Agent",
            "1x E-Mail-Automatisierungs-Agent",
            "CRM-Integration (Standard)",
            "Monatliches Reporting",
            "Support (Mo-Fr, 09-17 Uhr)",
        ],
        "milestones": [
            {"phase": "Discovery & Onboarding", "duration": "Tag 1-2", "tasks": [
                "Kickoff-Call (30 Min)", "Bestandsaufnahme IST-Zustand", "Zugangsdaten einrichten",
                "Anforderungsanalyse", "Projektplan erstellen"
            ]},
            {"phase": "Setup & Konfiguration", "duration": "Tag 2-3", "tasks": [
                "KI-Chatbot konfigurieren", "Lead-Agent trainieren", "E-Mail-Flows einrichten",
                "CRM-Anbindung", "Testdaten importieren"
            ]},
            {"phase": "Training & Go-Live", "duration": "Tag 3-5", "tasks": [
                "Agent-Training mit Kundendaten", "Qualitätsprüfung", "Go-Live Chatbot",
                "Go-Live Lead-Agent", "Übergabe-Call"
            ]},
            {"phase": "Monitoring & Optimierung", "duration": "Laufend", "tasks": [
                "Wöchentliche Performance-Checks", "Monatliches Reporting",
                "Quartals-Review", "Kontinuierliche Optimierung"
            ]},
        ],
        "agent_assignments": {
            "Forge": "Technische Integration, CRM-Anbindung, API-Setup",
            "Care": "Chatbot-Konfiguration, Kundenbetreuung, Onboarding",
            "Scribe": "E-Mail-Flows, Content-Vorlagen, Reporting-Templates",
            "Strategist": "Projektplanung, Optimierungsstrategie",
        },
        "standard_content": {
            "welcome_email": "Willkommen bei NeXify Automate — Ihr AI-Agenten-Team steht bereit",
            "onboarding_checklist": [
                "CRM-Zugangsdaten bereitstellen",
                "Website-Zugang für Chatbot-Integration",
                "E-Mail-Konfiguration (SMTP/API)",
                "Logo & Branding-Richtlinien",
                "FAQ/Wissensbasis-Dokumente",
            ],
            "sla": "99,5% Verfügbarkeit, Reaktionszeit < 4h (Werktage)",
        },
        "automation_rules": [
            "Chatbot antwortet in < 3s auf Standardfragen",
            "Lead-Score wird automatisch berechnet (0-100)",
            "E-Mail-Follow-up: Tag 1, Tag 3, Tag 7",
            "Eskalation an Mensch bei Score < 30 oder negativem Sentiment",
        ],
    },
    "growth_ai_agenten": {
        "key": "growth_ai_agenten",
        "name": "Growth AI Agenten AG",
        "tier": "growth",
        "price_monthly": 1299,
        "duration_months": 24,
        "deposit_percent": 30,
        "deposit_amount": 9352.80,
        "description": "Premium KI-Agenten-Paket: Vollständiges AI-Team mit 9 Fachagenten, Orchestrierung, Brain-Memory, Reporting",
        "deliverables": [
            "9x Spezialisierte KI-Agenten (Nexus, Strategist, Forge, Lexi, Scout, Scribe, Pixel, Care, Rank)",
            "Zentraler AI-Orchestrator (NeXify AI Master)",
            "Brain-Memory-System (mem0)",
            "Oracle Task-Management-System",
            "Vollständige CRM-Integration",
            "Multi-Channel-Kommunikation (E-Mail, Chat, WhatsApp)",
            "Echtzeit-Dashboard & Analytics",
            "Dedizierter Account Manager",
            "Priority Support (Mo-So, 08-22 Uhr)",
            "Quartals-Strategie-Reviews",
        ],
        "milestones": [
            {"phase": "Strategy & Discovery", "duration": "Tag 1-2", "tasks": [
                "Strategie-Workshop (60 Min)", "Geschäftsmodell-Analyse",
                "Wettbewerber-Scan (Scout)", "Technologie-Audit (Forge)",
                "Rechts-Check (Lexi)", "Projektplan erstellen (Strategist)"
            ]},
            {"phase": "Architecture & Setup", "duration": "Tag 2-4", "tasks": [
                "System-Architektur definieren", "Agent-Konfiguration (alle 9)",
                "Brain-Memory initialisieren", "Oracle-Tasks konfigurieren",
                "CRM + Multi-Channel-Anbindung", "Dashboard einrichten"
            ]},
            {"phase": "Training & Integration", "duration": "Tag 4-6", "tasks": [
                "Agent-Training mit Kundendaten", "Workflow-Automatisierung",
                "E-Mail-Vorlagen erstellen (Scribe)", "Design-Assets (Pixel)",
                "SEO-Baseline erstellen (Rank)", "Compliance-Check (Lexi)"
            ]},
            {"phase": "Go-Live & Handover", "duration": "Tag 6-7", "tasks": [
                "End-to-End-Qualitätsprüfung", "Go-Live aller Agenten",
                "Übergabe-Dokumentation", "Schulung Endanwender",
                "Monitoring-Setup"
            ]},
            {"phase": "Continuous Improvement", "duration": "Laufend", "tasks": [
                "Tägliche Performance-Checks (automatisch)",
                "Wöchentliche Brain-Optimierung",
                "Monatliches Executive Reporting",
                "Quartals-Strategie-Review mit Geschäftsführung"
            ]},
        ],
        "agent_assignments": {
            "Nexus": "Orchestrierung, Team-Koordination, Eskalationsmanagement",
            "Strategist": "Geschäftsstrategie, Planung, Optimierung, Quartals-Reviews",
            "Forge": "Architektur, Integration, Security, DevOps, API-Management",
            "Lexi": "DSGVO, Compliance, Vertragsrecht, Audit, Rechts-Checks",
            "Scout": "Marktanalyse, Wettbewerber-Monitoring, Data Intelligence, Lead-Research",
            "Scribe": "Content, E-Mail-Flows, Copywriting, Newsletter, Dokumentation",
            "Pixel": "Design, UX/UI, Branding, Visuals, Präsentationen",
            "Care": "CRM, Kundenbetreuung, Onboarding, Support, Retention",
            "Rank": "SEO, KPIs, Analytics, Performance, Growth-Hacking",
        },
        "standard_content": {
            "welcome_email": "Willkommen beim Growth AI Agenten AG — Ihr Premium AI-Team ist einsatzbereit",
            "onboarding_checklist": [
                "CRM-Zugangsdaten + Admin-Rechte",
                "Website-Zugang (FTP/CMS/API)",
                "E-Mail-Server-Konfiguration",
                "Social-Media-Zugänge",
                "Google Analytics / Search Console",
                "Logo, CI-Guide, Brand Assets",
                "Bestandskunden-Daten (anonymisiert)",
                "Aktuelle Marketing-Materialien",
                "Wettbewerber-Liste",
                "Gewünschte KPIs & Zielwerte",
            ],
            "sla": "99,9% Verfügbarkeit, Reaktionszeit < 1h, Eskalation < 15min",
        },
        "automation_rules": [
            "Master-Orchestrator koordiniert alle 9 Agenten autonom",
            "Brain-Memory speichert und lernt aus jedem Vorgang",
            "Automatische Eskalation bei kritischen Events",
            "Proaktive Handlungsempfehlungen bei Anomalien",
            "Compliance-Gate bei rechtlich relevanten Aktionen",
            "Multi-Touch-Sequenzen: 5 Touchpoints über 14 Tage",
        ],
    },
    "seo_starter": {
        "key": "seo_starter",
        "name": "SEO Starter",
        "tier": "seo_starter",
        "price_monthly": 799,
        "duration_months": 6,
        "deposit_percent": 0,
        "deposit_amount": 0,
        "description": "SEO-Grundpaket: Technisches SEO, On-Page-Optimierung, monatliches Reporting",
        "deliverables": [
            "Technisches SEO-Audit",
            "On-Page-Optimierung (10 Seiten/Monat)",
            "Keyword-Recherche & -Strategie",
            "Meta-Tags & Structured Data",
            "Monatlicher SEO-Report",
            "Google Search Console Setup",
        ],
        "milestones": [
            {"phase": "Audit & Strategie", "duration": "Woche 1", "tasks": [
                "Technisches SEO-Audit", "Keyword-Recherche", "Wettbewerber-Analyse",
                "SEO-Strategie erstellen", "Quick Wins identifizieren"
            ]},
            {"phase": "Implementierung", "duration": "Woche 2-3", "tasks": [
                "Meta-Tags optimieren", "Structured Data implementieren",
                "Site-Speed-Optimierung", "Internal Linking",
                "Content-Gaps identifizieren"
            ]},
            {"phase": "Monitoring", "duration": "Laufend", "tasks": [
                "Ranking-Tracking (wöchentlich)", "Traffic-Analyse",
                "Monatliches Reporting", "Kontinuierliche Optimierung"
            ]},
        ],
        "agent_assignments": {
            "Rank": "SEO-Audit, Keyword-Strategie, Ranking-Tracking, Reporting",
            "Forge": "Technisches SEO, Site-Speed, Structured Data",
            "Scribe": "Content-Optimierung, Meta-Tags, Alt-Texte",
        },
    },
    "seo_growth": {
        "key": "seo_growth",
        "name": "SEO Growth",
        "tier": "seo_growth",
        "price_monthly": 1499,
        "duration_months": 6,
        "deposit_percent": 0,
        "deposit_amount": 0,
        "description": "Premium-SEO: Vollständige SEO-Strategie inkl. Content-Marketing, Link-Building, Local SEO",
        "deliverables": [
            "Vollständiges SEO-Audit (technisch + inhaltlich)",
            "Content-Marketing (4 Artikel/Monat)",
            "Link-Building-Strategie",
            "Local SEO (Google Business Profile)",
            "On-Page-Optimierung (unbegrenzt)",
            "Wöchentliches Reporting + Quartals-Review",
            "Dedizierter SEO-Manager (KI-gestützt)",
        ],
        "milestones": [
            {"phase": "Deep Audit", "duration": "Woche 1-2", "tasks": [
                "Vollständiges technisches Audit", "Content-Audit",
                "Backlink-Profil-Analyse", "Local SEO Audit",
                "Wettbewerber-Deep-Dive", "Strategie-Präsentation"
            ]},
            {"phase": "Foundation", "duration": "Woche 2-4", "tasks": [
                "Technical Fixes", "Core Web Vitals", "Schema Markup",
                "Google Business Profile optimieren", "Content-Kalender erstellen"
            ]},
            {"phase": "Growth", "duration": "Monat 2-6", "tasks": [
                "Content-Produktion (4/Monat)", "Link-Building",
                "Ranking-Monitoring", "Conversion-Optimierung",
                "Quartals-Reviews"
            ]},
        ],
        "agent_assignments": {
            "Rank": "SEO-Strategie, Ranking-Tracking, KPI-Monitoring, Reporting",
            "Scribe": "Content-Produktion, Blog-Artikel, Landing Pages",
            "Scout": "Wettbewerber-Analyse, Link-Prospecting, Market Intelligence",
            "Forge": "Technical SEO, Site-Speed, Core Web Vitals",
            "Pixel": "Content-Design, Infografiken, Visual Content",
        },
    },
    "website_starter": {
        "key": "website_starter",
        "name": "Website Starter",
        "tier": "website_starter",
        "price_fixed": 2990,
        "description": "Professionelle Business-Website: 5-8 Seiten, responsives Design, CMS",
        "deliverables": [
            "5-8 Seiten (Home, Über uns, Leistungen, Kontakt, Impressum/Datenschutz)",
            "Responsives Design (Mobile-First)",
            "CMS-Integration (WordPress/Headless)",
            "Kontaktformular + Google Maps",
            "SSL-Zertifikat + Hosting-Setup",
            "Basis-SEO (Meta-Tags, Sitemap)",
        ],
        "milestones": [
            {"phase": "Konzept & Design", "duration": "Tag 1", "tasks": [
                "Anforderungsanalyse", "Wireframes", "Design-Entwurf",
                "Farb- & Schriftkonzept", "Content-Struktur"
            ]},
            {"phase": "Entwicklung", "duration": "Tag 1-2", "tasks": [
                "Frontend-Entwicklung", "CMS-Setup", "Responsive Tests",
                "Formular-Integration", "SEO-Basis"
            ]},
            {"phase": "Launch", "duration": "Tag 2-3", "tasks": [
                "Content-Einpflege", "Cross-Browser-Tests", "Performance-Check",
                "DNS-Umstellung", "Go-Live + Monitoring"
            ]},
        ],
        "agent_assignments": {
            "Pixel": "Design, UX/UI, Wireframes, Visual Identity",
            "Forge": "Entwicklung, CMS-Setup, Hosting, SSL",
            "Scribe": "Texte, SEO-Content, Rechtliche Seiten",
            "Lexi": "Impressum, Datenschutz, Cookie-Banner",
        },
    },
    "website_professional": {
        "key": "website_professional",
        "name": "Website Professional",
        "tier": "website_professional",
        "price_fixed": 7490,
        "description": "Premium-Website: 10-20 Seiten, Custom Design, E-Commerce-ready, Analytics",
        "deliverables": [
            "10-20 Seiten mit individuellem Design",
            "Custom UI/UX Design",
            "Blog/News-System",
            "E-Commerce-Vorbereitung",
            "Google Analytics + Tag Manager",
            "Multi-Language (DE/EN)",
            "Performance-Optimierung (Core Web Vitals)",
        ],
        "milestones": [
            {"phase": "Strategy & Design", "duration": "Tag 1-2", "tasks": [
                "Brand-Workshop", "UX-Research", "Design-System",
                "Prototyp (Figma)", "Content-Strategie"
            ]},
            {"phase": "Development", "duration": "Tag 2-5", "tasks": [
                "Frontend-Entwicklung", "Backend/CMS", "Blog-System",
                "Multi-Language", "Analytics-Integration"
            ]},
            {"phase": "QA & Launch", "duration": "Tag 5-7", "tasks": [
                "Qualitätssicherung", "Performance-Tests", "Content-Migration",
                "SEO-Audit", "Go-Live"
            ]},
        ],
        "agent_assignments": {
            "Pixel": "Custom Design, Brand Identity, Prototyp",
            "Forge": "Full-Stack Development, Performance, Security",
            "Scribe": "Content-Strategie, Texte, Blog-Templates",
            "Rank": "SEO-Setup, Analytics, Core Web Vitals",
            "Lexi": "DSGVO, Cookie-Consent, Rechtliche Texte",
        },
    },
    "website_enterprise": {
        "key": "website_enterprise",
        "name": "Website Enterprise",
        "tier": "website_enterprise",
        "price_fixed": 14900,
        "description": "Enterprise-Web-Plattform: Individuell, skalierbar, headless CMS, API-first",
        "deliverables": [
            "Individuelle Enterprise-Lösung",
            "Headless CMS (Strapi/Sanity)",
            "API-First Architecture",
            "Multi-Tenant-fähig",
            "CI/CD-Pipeline",
            "24/7 Monitoring",
            "SLA 99,9% Uptime",
        ],
        "milestones": [
            {"phase": "Architecture", "duration": "Tag 1-3", "tasks": [
                "Architektur-Design", "Tech-Stack-Entscheidung", "API-Design",
                "Security-Konzept", "Infrastruktur-Planung"
            ]},
            {"phase": "Development", "duration": "Tag 3-10", "tasks": [
                "Core Platform", "CMS-Integration", "API-Endpoints",
                "Auth & Security", "Performance"
            ]},
            {"phase": "Enterprise Launch", "duration": "Tag 10-14", "tasks": [
                "Staging-Tests", "Load-Testing", "Security-Audit",
                "CI/CD-Setup", "Go-Live + SLA-Start"
            ]},
        ],
        "agent_assignments": {
            "Forge": "Architektur, Full-Stack, CI/CD, Security, Infrastructure",
            "Pixel": "Enterprise Design-System, Component Library",
            "Lexi": "Compliance, DSGVO, Vertragswerk, SLA-Definition",
            "Strategist": "Projektplanung, Stakeholder-Management",
            "Rank": "Performance-Monitoring, SEO, Analytics",
        },
    },
    "app_mvp": {
        "key": "app_mvp",
        "name": "App MVP",
        "tier": "app_mvp",
        "price_fixed": 9900,
        "description": "Minimum Viable Product: Schnell zum Markt, validierbar, skalierbar",
        "deliverables": [
            "MVP-Konzept & Prototyp",
            "Native/Cross-Platform App (React Native/Flutter)",
            "Backend-API",
            "User Authentication",
            "3-5 Kernfeatures",
            "App Store Submission",
        ],
        "milestones": [
            {"phase": "Concept & Design", "duration": "Tag 1-3", "tasks": [
                "Product Discovery", "User Stories", "Wireframes",
                "UI-Design", "Tech-Stack-Entscheidung"
            ]},
            {"phase": "Development Sprint", "duration": "Tag 3-10", "tasks": [
                "Backend-API", "Auth-System", "Core Features",
                "Frontend-App", "Database Design"
            ]},
            {"phase": "Launch", "duration": "Tag 10-14", "tasks": [
                "QA & Testing", "Performance", "App Store Prep",
                "Submission", "Launch-Monitoring"
            ]},
        ],
        "agent_assignments": {
            "Strategist": "Product Discovery, User Stories, MVP-Scoping",
            "Forge": "Full-Stack Development, API, Infrastructure",
            "Pixel": "App Design, UX Flows, App Store Assets",
            "Care": "Beta-Tester-Management, Feedback-Loop",
        },
    },
    "app_professional": {
        "key": "app_professional",
        "name": "App Professional",
        "tier": "app_professional",
        "price_fixed": 24900,
        "description": "Professionelle App: Vollständig, skalierbar, Enterprise-ready",
        "deliverables": [
            "Vollständige App (iOS + Android)",
            "Skalierbares Backend",
            "Admin-Dashboard",
            "Push-Notifications",
            "Analytics & Tracking",
            "In-App Payments",
            "CI/CD + Monitoring",
        ],
        "milestones": [
            {"phase": "Planning & Architecture", "duration": "Tag 1-5", "tasks": [
                "Requirement Engineering", "System Architecture",
                "API Design", "Security Concept", "Project Plan"
            ]},
            {"phase": "Core Development", "duration": "Tag 5-20", "tasks": [
                "Backend + API", "App Frontend", "Admin Dashboard",
                "Push System", "Payment Integration"
            ]},
            {"phase": "QA & Launch", "duration": "Tag 20-28", "tasks": [
                "Testing Suite", "Performance Tuning", "Security Audit",
                "App Store Submission", "Production Monitoring"
            ]},
        ],
        "agent_assignments": {
            "Strategist": "Product Strategy, Requirement Engineering",
            "Forge": "Architecture, Backend, DevOps, Security",
            "Pixel": "UI/UX Design, Design System, App Store Assets",
            "Scribe": "Documentation, API Docs, User Guides",
            "Lexi": "Compliance, Datenschutz, AGB, App Store Richtlinien",
            "Rank": "Analytics Setup, KPI Tracking, Performance",
        },
    },
}


# ════════════════════════════════════════════════════════════
# API ENDPOINTS
# ════════════════════════════════════════════════════════════

@router.get("/api/admin/service-templates")
async def list_service_templates(admin: dict = Depends(get_admin)):
    """Alle Service-Templates (Boilerplates) auflisten."""
    templates = []
    for key, tmpl in SERVICE_TEMPLATES.items():
        templates.append({
            "key": tmpl["key"],
            "name": tmpl["name"],
            "tier": tmpl.get("tier", key),
            "price_monthly": tmpl.get("price_monthly"),
            "price_fixed": tmpl.get("price_fixed"),
            "duration_months": tmpl.get("duration_months"),
            "deposit_amount": tmpl.get("deposit_amount"),
            "description": tmpl["description"],
            "deliverables_count": len(tmpl.get("deliverables", [])),
            "milestones_count": len(tmpl.get("milestones", [])),
            "agents_assigned": list(tmpl.get("agent_assignments", {}).keys()),
        })
    return {"templates": templates, "count": len(templates)}


@router.get("/api/admin/service-templates/{template_key}")
async def get_service_template(template_key: str, admin: dict = Depends(get_admin)):
    """Vollständiges Service-Template abrufen."""
    tmpl = SERVICE_TEMPLATES.get(template_key)
    if not tmpl:
        raise HTTPException(404, f"Template '{template_key}' nicht gefunden")
    return tmpl


class InstantiateTemplateRequest(BaseModel):
    template_key: str
    customer_name: str
    customer_email: str
    customer_company: str = ""
    custom_notes: str = ""
    custom_deliverables: list = []


@router.post("/api/admin/service-templates/instantiate")
async def instantiate_template(body: InstantiateTemplateRequest, admin: dict = Depends(get_admin)):
    """Template instanziieren: Erstellt Projekt + Meilensteine + Tasks aus Boilerplate."""
    tmpl = SERVICE_TEMPLATES.get(body.template_key)
    if not tmpl:
        raise HTTPException(404, f"Template '{body.template_key}' nicht gefunden")

    project_id = new_id("prj")
    now = utcnow().isoformat()

    # Projekt erstellen
    project = {
        "project_id": project_id,
        "title": f"{tmpl['name']} — {body.customer_company or body.customer_name}",
        "template_key": body.template_key,
        "customer_name": body.customer_name,
        "customer_email": body.customer_email,
        "customer_company": body.customer_company,
        "tier": tmpl.get("tier", ""),
        "status": "active",
        "price_monthly": tmpl.get("price_monthly"),
        "price_fixed": tmpl.get("price_fixed"),
        "duration_months": tmpl.get("duration_months"),
        "deposit_amount": tmpl.get("deposit_amount"),
        "deliverables": tmpl.get("deliverables", []) + body.custom_deliverables,
        "milestones": [],
        "agent_assignments": tmpl.get("agent_assignments", {}),
        "automation_rules": tmpl.get("automation_rules", []),
        "custom_notes": body.custom_notes,
        "created_at": now,
        "updated_at": now,
        "created_by": admin.get("email", "admin"),
    }

    # Meilensteine mit Tasks
    for i, ms in enumerate(tmpl.get("milestones", [])):
        milestone = {
            "milestone_id": new_id("ms"),
            "phase": ms["phase"],
            "duration": ms.get("duration", ""),
            "order": i + 1,
            "status": "pending",
            "tasks": [],
        }
        for t in ms.get("tasks", []):
            milestone["tasks"].append({
                "task_id": new_id("tsk"),
                "title": t,
                "status": "pending",
                "assigned_agent": None,
                "completed_at": None,
            })
        project["milestones"].append(milestone)

    await S.db.projects.insert_one(project)
    project.pop("_id", None)

    # Timeline-Event
    await S.db.timeline_events.insert_one({
        "event_id": new_id("ev"),
        "ref_id": project_id,
        "ref_type": "project",
        "event_type": "project_created",
        "description": f"Projekt '{project['title']}' aus Template '{tmpl['name']}' erstellt",
        "timestamp": now,
        "created_by": admin.get("email", "admin"),
    })

    return {
        "project_id": project_id,
        "title": project["title"],
        "milestones": len(project["milestones"]),
        "total_tasks": sum(len(m["tasks"]) for m in project["milestones"]),
        "created": True,
    }
