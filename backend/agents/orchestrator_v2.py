"""
NeXifyAI Orchestrator v2 — Central AI Agent Router.
Brain-first: routes tasks via semantic search on hermes_brain.
25+ specialized agents, 9 knowledge skills, full mesh routing.
"""
import os
import json
import logging
import asyncio
from pathlib import Path

logger = logging.getLogger("nexifyai.orchestrator")

# === ALL 27 AGENT ROLES (from brain + mesh) ===
AGENT_ROLES = {
    # Core Architecture
    "ai-engineer": "AI Systems Architect — plant, designed und baut das gesamte Agenten-Ökosystem",
    "agent-expert": "Agent-Management — Prompt-Optimierung, Lifecycle, Inter-Agent-Protokolle",
    
    # Project Management
    "project-manager": "Zentrale Projektkoordination — 4 Tenants, 7 Repos, 33 Agenten, DOS v2.1",
    "task-decomposition-expert": "Work-Breakdown-Structures mit Dependencies, Effort, Agent-Zuweisung",
    "project-supervisor-orchestrator": "Multi-Projekt-Supervision — Velocity, Quality, Budget, Eskalation",
    "business-analyst": "Geschäftsanforderungen → technische Specs, Gap-Analyse, KPI-Definition",
    
    # Infrastructure
    "cloud-architect": "Multi-Cloud-Infrastruktur, ADR-013 Tenant-Isolation, Disaster Recovery",
    "deployment-engineer": "CI/CD: GitHub Actions → Vercel/Docker, Blue-Green, Canary, Auto-Rollback",
        "network-specialist": {
        "display_name": "Netzwerk-Spezialist",
        "primary_capability": "network",
        "roles": ["tailscale management", "dns", "firewall", "docker networking", "ssl monitoring"],
        "mesh_group": "infrastructure",
        "priority": 3,
    },
"monitoring-specialist": "Observability: 4 Golden Signals, Uptime Kuma, Grafana, Alerting",
    
    # Development
    "fullstack-developer": "DB→API→Frontend, TypeScript-Strict, Zod, Playwright, Supabase",
    "nextjs-architecture-expert": "Next.js 14, shadcn/ui, Coral Design System, App Router, i18n",
    "supabase-schema-architect": "PostgreSQL + RLS für 4 Tenants, safe Migrations, Performance",
    
    # Data & Analytics
    "data-analyst": "Deskriptive Statistik, Trend-Analyse, Visualisierung, Forecasting",
    "data-engineer": "ETL-Pipelines: GitHub→Supabase, Brain→Analytics, Tenant-Metriken",
    "research-coordinator": "Recherche-Delegation, Multi-Source-Synthese, Fact-Validation",
    "fact-checker": "Multi-Source-Validation, Contradiction-Detection, E3.5 Directive 3",
    
    # Quality & Security
    "review-agent": "Code/PR-Review, DOS v2.1-Compliance, ADR-013-Isolation, Type-Safety",
    "security-engineer": "DevSecOps, Trivy, Gitleaks, Incident Response, DSGVO",
    "security-auditor": "Unabhängiger Security-Audit, Pentest, Compliance-Check",
    
    # AI & Context
    "llms-maintainer": "LLM-Provider: DeepSeek/OpenRouter/Emergent, Cost-Optimierung",
    "context-manager": "Brain-Integration, Hybrid-Search, Context-Window-Management",
    "search-specialist": "Qdrant Vector+Keyword, Reranking, Query-Expansion",
    "prompt-engineer": "Prompt-Engineering Patterns: Few-Shot, Chain-of-Thought, Optimization",
    
    # Documentation & Metadata
    "documentation-expert": "Docusaurus, ADR, OpenAPI, Runbooks, DOS v2.1-konform",
    "metadata-agent": "Auto-Tagging, Schema-Validierung, Brain-Metadaten-Management",
    "document-structure-analyzer": "PDF/Scan→JSON, Key-Value-Extraction, Risk-Flagging",
    
        # Governance & Autonomy (CEO System)
    "nexifyai-ceo": "CEO — Höchste Entscheidungsinstanz, autonome Orchestrierung, 24/7 aktiv",
    "order-workflow-specialist": "Auftragsverwaltung — DIN 69901/9001, IST-Scan, Wissensquellen, Quality-Gate",
    "senior-quality-auditor": "Qualitätsprüfung — Abnahme jeder Auftragserledigung, PASS/FAIL/X-Auftrag",
    "legal-expert": "Recht & Compliance — Impressum, DSGVO, AGB, AVV, Cookie-Consent, §5 TMG",
    "inventory-brain-scanner": "System-Inventur — DNS, SSL, Docker, Brain, Agent-Scores, Credential-Rotation",
    
# Modernization
    "architecture-modernizer": "Strangler-Fig, Monolith→Microservices, Zero-Downtime",
    "dependency-manager": "Renovate, npm/pip/Docker-Audit, Supply-Chain-Security",
}

# === MESH ROUTING (from agent_mesh.yaml) ===
MESH_ROUTING = {
    # CEO — Top-Level Authority
    "nexifyai-ceo": {
        "delegates_to": ["project-manager", "task-decomposition-expert", "cloud-architect", 
                        "ai-engineer", "security-auditor", "inventory-brain-scanner",
                        "legal-expert", "order-workflow-specialist", "senior-quality-auditor"],
        "receives_from": [],
        "authority": "supreme",
    },
    "project-manager": {
        "delegates_to": ["task-decomposition-expert", "research-coordinator", "project-supervisor-orchestrator", "business-analyst"],
        "receives_from": ["project-supervisor-orchestrator", "task-decomposition-expert", "review-agent"],
        },
    "task-decomposition-expert": {
        "delegates_to": ["ai-engineer", "deployment-engineer", "cloud-architect", "supabase-schema-architect", "nextjs-architecture-expert", "fullstack-developer", "data-engineer"],
        "receives_from": ["project-manager", "business-analyst"],
    },
    "ai-engineer": {
        "delegates_to": ["agent-expert", "llms-maintainer", "context-manager", "search-specialist"],
        "receives_from": ["task-decomposition-expert", "project-manager"],
    },
    "cloud-architect": {
        "delegates_to": ["deployment-engineer", "security-engineer", "monitoring-specialist"],
        "receives_from": ["task-decomposition-expert", "architecture-modernizer"],
    },
    "deployment-engineer": {
        "delegates_to": ["review-agent", "dependency-manager", "monitoring-specialist"],
        "receives_from": ["cloud-architect", "fullstack-developer"],
    },
    "fullstack-developer": {
        "delegates_to": ["supabase-schema-architect", "nextjs-architecture-expert", "review-agent"],
        "receives_from": ["task-decomposition-expert"],
    },
    "review-agent": {
        "delegates_to": ["security-engineer", "fact-checker"],
        "receives_from": ["deployment-engineer", "fullstack-developer"],
    },
    "security-engineer": {
        "delegates_to": ["dependency-manager", "security-auditor"],
        "receives_from": ["cloud-architect", "review-agent"],
    },
    "research-coordinator": {
        "delegates_to": ["search-specialist", "data-analyst", "fact-checker", "data-engineer"],
        "receives_from": ["project-manager", "business-analyst"],
    },
    "documentation-expert": {
        "delegates_to": ["metadata-agent", "document-structure-analyzer", "review-agent"],
        "receives_from": ["task-decomposition-expert", "security-auditor"],
    },
    "architecture-modernizer": {
        "delegates_to": ["cloud-architect", "deployment-engineer", "task-decomposition-expert"],
        "receives_from": ["project-manager", "business-analyst"],
    },
    "network": ["network-specialist", "infrastructure-architect", "devsecops-engineer"],
}


# === WEBHOOK → AGENT ROUTING (from github_webhooks.yaml) ===
WEBHOOK_ROUTING = {
    "all": {"notify_ceo": True},
    "push": {
        "trigger_agents": ["review-agent", "deployment-engineer", "metadata-agent"],
        "branch_main": ["deployment-engineer"],
    },
    "pull_request": {
        "trigger_agents": ["review-agent", "dependency-manager", "security-engineer"],
        "opened": ["review-agent", "dependency-manager", "security-engineer"],
        "synchronize": ["review-agent"],
    },
    "pull_request_review": {
        "submitted_approved": ["deployment-engineer"],
        "submitted_changes_requested": ["task-decomposition-expert"],
    },
    "issues": {
        "trigger_agents": ["project-manager", "business-analyst"],
        "opened": ["project-manager", "business-analyst"],
        "labeled_bug": ["task-decomposition-expert"],
    },
    "release": {
        "trigger_agents": ["deployment-engineer", "monitoring-specialist", "documentation-expert"],
    },
    "workflow_run": {
        "trigger_agents": ["monitoring-specialist", "data-engineer"],
    },
    "check_run": {
        "trigger_agents": ["review-agent", "security-engineer"],
    },
}


class AgentRouter:
    """Brain-first agent routing. Determines which agents handle a task/event."""
    
    def __init__(self):
        self.roles = AGENT_ROLES
        self.mesh = MESH_ROUTING
        self.webhooks = WEBHOOK_ROUTING
    
    async def route_task(self, task: str, context: dict = None) -> dict:
        """
        Route a natural-language task to the best agent.
        Attempts Brain semantic search first, falls back to keyword matching.
        """
        try:
            from .brain_connector import search_agents
            agents = await search_agents(task, limit=3)
            if agents:
                return {
                    "method": "brain_semantic",
                    "agents": agents,
                    "primary": agents[0],
                }
        except Exception as e:
            logger.warning(f"Brain search failed, falling back to keyword: {e}")
        
        # Fallback: keyword matching
        task_lower = task.lower()
        matches = []
        for agent_id, desc in self.roles.items():
            if any(kw in task_lower for kw in agent_id.split("-")):
                matches.append(agent_id)
            elif any(kw in task_lower for kw in desc.lower().split()[:5]):
                matches.append(agent_id)
        
        return {
            "method": "keyword_fallback",
            "agents": list(set(matches))[:3],
            "primary": matches[0] if matches else "ai-engineer",
        }
    
    def route_webhook(self, event: str, action: str = None, branch: str = None) -> list[str]:
        """Determine which agents to trigger for a GitHub webhook event."""
        agents = []
        event_config = self.webhooks.get(event, {})
        agents.extend(event_config.get("trigger_agents", []))
        
        if action:
            action_key = None
            if event == "pull_request":
                action_key = "opened" if action == "opened" else action
            elif event == "pull_request_review":
                action_key = f"submitted_{action}" if action in ("approved", "changes_requested") else None
            elif event == "issues":
                action_key = action
            elif event == "push" and branch == "main":
                agents.extend(event_config.get("branch_main", []))
            
            if action_key and action_key in event_config:
                agents.extend(event_config[action_key])
        
        return list(set(agents))
    
    def get_delegations(self, agent_name: str) -> dict:
        """Get delegation rules for a specific agent."""
        return self.mesh.get(agent_name, {"delegates_to": [], "receives_from": []})


# Global router instance
router = AgentRouter()
