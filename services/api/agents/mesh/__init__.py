"""NeXifyAI Agent Mesh — Multi-Agent Operational Runtime.

Agent Mesh: agent_mesh.yaml (Routing + Skill Assignments)
Webhooks: github_webhooks.yaml (GitHub Event → Agent Routing)
Build Plan: build_plan.md (Kollaborativer 4-Sprint-Plan)

Architektur:
  Agent Discovery → Brain Semantic Search (hermes_brain)
  Agent Delegation → Orchestrator (POST /orchestrate)  
  Context Sharing → Brain (Shared Memory)
  Webhook Triggers → Hermes Gateway → Agent Routing
"""

from pathlib import Path
import yaml

MESH_DIR = Path(__file__).parent


def load_mesh():
    """Load agent routing table."""
    with open(MESH_DIR / "agent_mesh.yaml") as f:
        return yaml.safe_load(f)


def load_webhooks():
    """Load GitHub webhook routing config."""
    with open(MESH_DIR / "github_webhooks.yaml") as f:
        return yaml.safe_load(f)


def route_event(event_type: str, action: str = None) -> list[str]:
    """Determine which agents to trigger for a GitHub event."""
    config = load_webhooks()
    event_config = config["webhooks"].get(event_type, {})
    agents = event_config.get("trigger_agents", [])
    if action and "conditions" in event_config:
        for cond_key, cond_agents in event_config["conditions"].items():
            if str(action) in cond_key:
                agents.extend(cond_agents)
    return list(set(agents))


def get_skill_assignments() -> dict:
    """Get which agents use which skills."""
    mesh = load_mesh()
    return mesh.get("skill_assignments", {})


def get_delegations(agent_name: str) -> dict:
    """Get delegation rules for a specific agent."""
    mesh = load_mesh()
    routing = mesh.get("routing", {})
    agent = routing.get(agent_name, {})
    return {
        "delegates_to": agent.get("delegates_to", []),
        "receives_from": agent.get("receives_from", []),
    }
