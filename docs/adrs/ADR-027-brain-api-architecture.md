# ADR-027: Brain API Architecture

**Status:** proposed
**Datum:** 2026-05-22
**Autor:** AI-Swarm
**Stakeholder:** AI Team, Backend

## Kontext

Brain API (port 8420) dient als Knowledge-Layer für RAG-Queries, System-Status und Orchestrierung. Aktuell nur `/health` implementiert; `/system/status` fehlt.

## Entscheidung

**Brain API Endpoints:**

| Endpoint | Methode | Status | Beschreibung |
|----------|---------|--------|-------------|
| `/health` | GET | ✅ live | Health-Check |
| `/system/status` | GET | 🔜 TODO | Vollständiger System-Status |
| `/api/v1/rag/query` | POST | 🔜 TODO | RAG Query (Qdrant) |
| `/api/v1/rag/conversation` | POST | 🔜 TODO | Conversational RAG |
| `/api/v2/agent/run` | POST | ✅ live | Single-Task Agent |
| `/api/v2/agent/stream` | POST | ✅ live | Streaming Agent (SSE) |
| `/api/v2/oracle/run` | POST | ✅ live | Oracle Lifecycle |
| `/api/v2/oracle/{task_id}` | GET | ✅ live | Task-Status |
| `/api/v2/rag/query` | POST | ✅ live | RAG Query |
| `/api/v2/health/ai` | GET | ✅ live | AI Health |

## Auth

Alle Endpoints via JWT (gleicher Pool wie 9Router) oder API-Key.
