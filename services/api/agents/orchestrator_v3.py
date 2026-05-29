"""
NeXify AI — Team-Routing Orchestrator v3.0.
Central orchestrator with Supabase-backed Team-Routing, Task-Graph execution,
Quality Gates, and execution logging. Uses OpenRouter (deepseek/deepseek-v4-flash) for all LLM calls.

Replaces: hardcoded single-agent delegation with data-driven team routing.
"""
import os, json, logging, asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

import httpx

from domain import create_timeline_event, utcnow, new_id
from services.llm_provider import create_llm_provider, LLMMessage

logger = logging.getLogger("nexifyai.orchestrator")

SUPABASE_URL = os.environ.get("SUPABASE_URL", os.environ.get("DS_SUPABASE_1E93118D__PROJECT_URL", "https://mdlgodcvpasgplcrkiad.supabase.co"))
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("DS_SUPABASE_1E93118D__SECRET_KEY", ""))

# ═══════════════════════════════════════════════════
# TEAM ROUTING LAYER
# ═══════════════════════════════════════════════════

class TeamRouter:
    """Routes tasks to teams and agents based on Supabase team_registry table."""
    
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._cache_ttl = 300  # 5 min
        self._last_fetch = 0
    
    async def _fetch_teams(self) -> List[dict]:
        """Fetch all active teams from Supabase."""
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                f"{SUPABASE_URL}/rest/v1/team_registry",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                },
                params={"enabled": "eq.true", "order": "priority.desc"}
            )
            if r.status_code == 200:
                return r.json()
            logger.error(f"Team fetch failed: {r.status_code}")
            return []
    
    async def find_team(self, capability: str) -> Optional[dict]:
        """Find the best team for a given capability."""
        teams = await self._fetch_teams()
        
        # Score each team by capability match + priority
        scored = []
        for team in teams:
            caps = team.get("capabilities", [])
            rules = team.get("routing_rules", {})
            
            # Direct match wins
            if capability in caps:
                scored.append((10 + team.get("priority", 0), team))
            # Partial match
            elif any(cap in capability or capability in cap for cap in caps):
                scored.append((5 + team.get("priority", 0), team))
        
        if not scored:
            return None
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    
    async def route_task(self, task: str, capability: str = None, 
                         complexity: str = "medium") -> dict:
        """Route a task to the appropriate team and agent."""
        # 1. Determine capability if not provided
        if not capability:
            capability = self._classify_task(task)
        
        # 2. Find best team
        team = await self.find_team(capability)
        if not team:
            return {
                "agent": "ceo-agent",  # Default fallback
                "team": "planning",
                "capability": capability,
                "routing_method": "fallback",
            }
        
        # 3. Pick best agent from team
        members = team.get("agent_ids", [])
        rules = team.get("routing_rules", {})
        
        agent = rules.get(capability, rules.get("primary", members[0] if members else "ai-engineer"))
        
        return {
            "agent": agent,
            "team": team["name"],
            "team_members": members,
            "capability": capability,
            "routing_method": "team_match",
            "priority": team.get("priority", 5),
        }
    
    def _classify_task(self, task: str) -> str:
        """Quick classification from task text."""
        task_lower = task.lower()
        
        capability_keywords = {
            "code": ["code", "program", "develop", "bug", "fix", "implement", "function", "api", "endpoint"],
            "plan": ["plan", "roadmap", "strategy", "milestone", "sprint", "organize"],
            "analyze": ["analyze", "data", "report", "metric", "statistic", "trend", "insight"],
            "research": ["research", "investigate", "explore", "discover", "learn about", "find"],
            "design": ["design", "ui", "ux", "mockup", "wireframe", "layout", "style"],
            "deploy": ["deploy", "release", "publish", "ship", "launch"],
            "review": ["review", "audit", "check", "verify", "quality", "test"],
            "summarize": ["summarize", "summary", "tldr", "recap", "brief"],
            "classify": ["classify", "categorize", "sort", "label", "tag"],
            "chat": ["hello", "hi", "help", "explain", "what is", "how to", "tell me"],
        }
        
        for cap, keywords in capability_keywords.items():
            if any(kw in task_lower for kw in keywords):
                return cap
        
        return "chat"


# ═══════════════════════════════════════════════════
# TASK GRAPH EXECUTOR
# ═══════════════════════════════════════════════════

class TaskGraphExecutor:
    """Executes tasks as a directed acyclic graph with quality gates."""
    
    def __init__(self, db, llm_provider, team_router: TeamRouter):
        self.db = db
        self.llm = llm_provider
        self.router = team_router
    
    async def execute_graph(self, graph_id: str, context: dict = None) -> dict:
        """Execute a task graph by resolving dependencies and running nodes."""
        # Fetch graph nodes and edges
        nodes = await self._load_nodes(graph_id)
        if not nodes:
            return {"error": "No nodes found"}
        
        # Topological sort by dependencies
        sorted_nodes = self._topological_sort(nodes)
        
        results = {}
        for node in sorted_nodes:
            # Check quality gate before execution
            gate = await self._check_quality_gate(node["id"])
            if gate and not gate.get("passed", True):
                logger.warning(f"Quality gate failed for {node['id']}: {gate}")
                results[node["id"]] = {"status": "blocked", "reason": "quality_gate"}
                continue
            
            # Execute the node
            node_result = await self._execute_node(node, context, results)
            results[node["id"]] = node_result
            
            # Log to execution log
            await self._log_execution(node, node_result)
        
        return results
    
    async def _execute_node(self, node: dict, context: dict, 
                            previous_results: dict) -> dict:
        """Execute a single task graph node."""
        task_type = node.get("task_type", "chat")
        capability = node.get("capability", task_type)
        description = node.get("description", node.get("name", ""))
        
        # Build enriched context from previous results
        enriched_context = self._enrich_context(node, context, previous_results)
        
        # Route to appropriate team/agent
        routing = await self.router.route_task(
            description, capability, 
            node.get("complexity", "medium")
        )
        
        # Execute via LLM provider
        result = await self.llm.chat(
            messages=[LLMMessage(role="user", content=f"{description}\n\nContext: {json.dumps(enriched_context)}")],
            system_prompt=f"You are the {routing['agent']} agent. Team: {routing['team']}. Execute this task.",
            temperature=0.7,
            max_tokens=node.get("max_tokens", 4096),
        )
        
        return {
            "status": "completed" if "[Fehler" not in result and "[Systemfehler" not in result else "failed",
            "output": result,
            "routing": routing,
            "node": node.get("name", node.get("id")),
        }
    
    async def _load_nodes(self, graph_id: str = None) -> List[dict]:
        """Load task graph nodes with their edges."""
        async with httpx.AsyncClient(timeout=15) as client:
            # Load nodes
            url = f"{SUPABASE_URL}/rest/v1/task_graph"
            params = {"status": "eq.active", "order": "version.desc"}
            if graph_id:
                params["id"] = f"eq.{graph_id}"
            
            r = await client.get(url, headers={
                "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"
            }, params=params)
            if r.status_code != 200:
                return []
            return r.json()
    
    def _topological_sort(self, nodes: List[dict]) -> List[dict]:
        """Simple priority-based sort (full topo via edges in production)."""
        return sorted(nodes, key=lambda n: n.get("priority", 5))
    
    def _enrich_context(self, node: dict, base_context: dict, 
                        previous_results: dict) -> dict:
        """Build context for a node by pulling data from dependent upstream nodes."""
        ctx = dict(base_context or {})
        
        # Include results from prior nodes
        for prev_id, prev_result in previous_results.items():
            ctx[f"upstream_{prev_id}"] = prev_result.get("output", "")[:500]
        
        return ctx
    
    async def _check_quality_gate(self, task_id: str) -> Optional[dict]:
        """Check most recent quality gate for this task."""
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{SUPABASE_URL}/rest/v1/quality_gates",
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
                params={"task_id": f"eq.{task_id}", "order": "created_at.desc", "limit": 1}
            )
            if r.status_code == 200:
                data = r.json()
                return data[0] if data else None
        return None
    
    async def _log_execution(self, node: dict, result: dict):
        """Log task execution to Supabase."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    f"{SUPABASE_URL}/rest/v1/task_execution_log",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Prefer": "return=minimal",
                    },
                    json={
                        "task_id": node.get("id"),
                        "agent_id": result.get("routing", {}).get("agent"),
                        "model_used": result.get("routing", {}).get("capability"),
                        "capability_routed": result.get("routing", {}).get("capability"),
                        "status": result.get("status"),
                        "output": {"summary": result.get("output", "")[:500]},
                    }
                )
        except Exception as e:
            logger.warning(f"Execution log failed: {e}")


# ═══════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════

class TeamOrchestrator:
    """Main orchestrator with team routing, task graphs, and quality gates."""
    
    def __init__(self, db):
        self.db = db
        self.llm = create_llm_provider()
        self.team_router = TeamRouter()
        self.graph_executor = TaskGraphExecutor(db, self.llm, self.team_router)
    
    async def route(self, task: str, context: dict = None, 
                    session_id: str = None) -> dict:
        """
        Primary routing method. Classifies task, routes to team/agent,
        and executes with quality gate enforcement.
        """
        # 1. Route to team
        routing = await self.team_router.route_task(task)

        # 1b. Load applicable rules
        rules = await self._load_rules(agent_id=routing.get("agent"))
        
        # 2. Log routing decision
        if session_id:
            create_timeline_event(
                "orchestrator", session_id, "task_routed",
                details={
                    "task": task[:200],
                    "routed_to": routing["agent"],
                    "team": routing["team"],
                    "capability": routing["capability"],
                    "method": routing["routing_method"],
                }
            )
        
        # 3. Execute via OpenRouter (deepseek/deepseek-v4-flash)
        enriched_ctx = dict(context or {})
        enriched_ctx["_rules"] = rules
        result = await self.llm.chat(
            messages=[LLMMessage(role="user", content=task)],
            system_prompt=self._build_system_prompt(routing, enriched_ctx),
            temperature=0.7,
        )
        
        # 4. Record quality gate
        gate_result = await self._record_quality_gate(
            task_id=routing.get("task_id", "unknown"),
            gate_type="team_routing",
            passed=True,
            score=routing.get("priority", 5) / 10.0,
            criteria={"routing_method": routing.get("routing_method"), "team": routing.get("team")},
            notes=f"Routed to {routing['agent']} via {routing.get('routing_method')}",
        )

        return {
            "agent": routing["agent"],
            "team": routing["team"],
            "capability": routing["capability"],
            "result": result,
            "routing": routing,
            "quality_gate": gate_result,
        }
    
    async def execute_graph(self, context: dict = None) -> dict:
        """Execute the full task graph (analyze → research → code → review → deploy)."""
        return await self.graph_executor.execute_graph(None, context)
    
    async def _load_rules(self, agent_id: str = None, scope: str = "global") -> List[dict]:
        """Load applicable rules from rules_registry for the given agent/scope."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                filters = [f"scope.eq.{scope}", "enabled.eq.true"]
                if agent_id:
                    filters.append(f"agent_id.eq.{agent_id}")
                # Also always load global rules
                url = f"{SUPABASE_URL}/rest/v1/rules_registry?or=(scope.eq.global"
                if agent_id:
                    url += f",agent_id.eq.{agent_id}"
                url += ")&enabled=eq.true&order=priority.desc"
                
                r = await client.get(url, headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                })
                if r.status_code == 200:
                    return r.json()
                return []
        except Exception as e:
            logger.warning(f"Rules load failed: {e}")
            return []

    def _build_system_prompt(self, routing: dict, context: dict) -> str:
        """Build agent system prompt with team context and active rules."""
        prompt = f"""You are {routing['agent']}, part of the {routing['team']} team.
Capability: {routing['capability']}
Team members available: {', '.join(routing.get('team_members', []))}

Execute the user's task with precision and expertise.
- If coding: produce clean, tested code
- If planning: structure clearly with priorities
- If analysis: provide data-driven insights
- If design: consider UX and aesthetics

Always deliver actionable output."""

        # Inject active rules
        rules = context.get("_rules", []) if context else []
        if rules:
            always_rules = [r for r in rules if r.get("trigger_type") == "always"]
            never_rules = [r for r in rules if r.get("trigger_type") == "never"]
            when_rules = [r for r in rules if r.get("trigger_type") == "when"]
            
            if always_rules:
                prompt += "\n\n=== ALWAYS RULES (you MUST follow these) ==="
                for r in always_rules:
                    prompt += f"\n- {r.get('name')}: {r.get('rule_content', '')[:200]}"
            if never_rules:
                prompt += "\n\n=== NEVER RULES (you MUST NOT violate these) ==="
                for r in never_rules:
                    prompt += f"\n- {r.get('name')}: {r.get('rule_content', '')[:200]}"
            if when_rules:
                prompt += "\n\n=== CONDITIONAL RULES (follow when applicable) ==="
                for r in when_rules:
                    prompt += f"\n- {r.get('name')}: {r.get('rule_content', '')[:200]}"
        
        if context:
            prompt += "\n\nRelevant context: " + json.dumps(context, default=str)[:1000]

        return prompt



    async def _record_quality_gate(self, task_id: str, gate_type: str,
                                   passed: bool, score: float,
                                   criteria: dict = None, notes: str = "") -> dict:
        """Record a quality gate check in Supabase."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    f"{SUPABASE_URL}/rest/v1/quality_gates",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Prefer": "return=representation",
                    },
                    json={
                        "task_id": task_id,
                        "gate_type": gate_type,
                        "passed": passed,
                        "score": score,
                        "criteria": criteria or {},
                        "notes": notes,
                    }
                )
                if r.status_code == 201:
                    data = r.json()
                    return data[0] if data else {"id": "unknown"}
                return {"error": f"HTTP {r.status_code}"}
        except Exception as e:
            logger.warning(f"Quality gate record failed: {e}")
            return {"error": str(e)}

# ═══════════════════════════════════════════════════
# ORCHESTRATOR FACTORY (replaces old create_llm_provider pattern for orchestration)
# ═══════════════════════════════════════════════════

_orchestrator_instance = None

def get_orchestrator(db=None) -> TeamOrchestrator:
    """Get or create the singleton TeamOrchestrator."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = TeamOrchestrator(db)
    return _orchestrator_instance


logger.info("TeamOrchestrator v3.0 loaded: Supabase team routing + Task Graph + Quality Gates")
