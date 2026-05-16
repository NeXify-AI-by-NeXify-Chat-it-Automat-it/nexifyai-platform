"""
NeXifyAI Modular Routes

Zentrale Route-Registrierung fuer alle Backend-Module.
Jede Route-Datei wird hier importiert und unter dem entsprechenden
Praefix im FastAPI-Router registriert.

Module:
  admin_routes       — Admin CRM (Leads, Pipeline, Kunden)
  api_v1_routes      — Externe API v1 (API-Key-Auth)
  auth_routes        — Authentifizierung (Login, Token)
  billing_routes     — Abrechnung (Revolut)
  comms_routes       — Kommunikation (Email, WhatsApp)
  compliance_routes  — Compliance (Legal Guardian)
  contract_routes    — Vertraege (Contract OS)
  intelligence_routes— KI-Tools (Crawling, Dokument-Analyse)
  monitoring_routes  — Monitoring (Health, LLM, Workers)
  nexify_ai_routes   — NeXify AI Master Chat (OpenRouter)
  admin_chat_gateway — Admin Chat Gateway (Hermes Bridge)
"""
# NeXifyAI Modular Routes
