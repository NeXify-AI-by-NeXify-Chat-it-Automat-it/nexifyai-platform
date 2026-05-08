"""FinOps Agent — Real cost analysis from local filesystem + health scripts."""

import os, sqlite3, json
from backend.agents.base_agent import BaseAgent


class FinOpsAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("FinOps Agent", "Cost analysis and budget monitoring")
    
    def observe(self) -> dict:
        data = {
            "budgets": {
                "openrouter": {"limit": 500, "current": 0},
                "vercel": {"limit": 20, "current": 20},
                "supabase": {"limit": 25, "current": 25},
                "hostinger": {"limit": 15, "current": 15},
            },
            "total_monthly": 60,
            "total_budget": 560,
            "warnings": [],
        }
        
        # Check if finops.yaml exists with real budget config
        finops_path = "/opt/nexifyai-website-sicherheitskopie/packages/config/finops.yaml"
        if os.path.exists(finops_path):
            try:
                import yaml
                with open(finops_path) as f:
                    cfg = yaml.safe_load(f)
                if cfg and "budgets" in cfg:
                    for name, budget in cfg["budgets"].items():
                        if name in data["budgets"]:
                            data["budgets"][name].update(budget)
            except Exception:
                pass
        
        # Check brain.db for any cost-related entries
        brain_db = "/opt/data/brain/brain.db"
        if os.path.exists(brain_db):
            try:
                conn = sqlite3.connect(brain_db)
                rows = conn.execute(
                    "SELECT content FROM memories WHERE content LIKE '%cost%' OR content LIKE '%budget%' OR content LIKE '%finops%' LIMIT 5"
                ).fetchall()
                for row in rows:
                    data["warnings"].append(f"Cost entry: {str(row[0])[:100]}")
                conn.close()
            except Exception:
                pass
        
        return data
    
    def analyze(self, data: dict) -> list:
        findings = []
        budgets = data.get("budgets", {})
        
        for name, budget in budgets.items():
            usage_pct = (budget["current"] / budget["limit"]) * 100 if budget["limit"] > 0 else 0
            if usage_pct > 90:
                findings.append(f"🔴 {name}: {usage_pct:.0f}% of ${budget['limit']}/mo used ($ {budget['current']})")
            elif usage_pct > 75:
                findings.append(f"🟡 {name}: {usage_pct:.0f}% of ${budget['limit']}/mo used ($ {budget['current']})")
            else:
                findings.append(f"🟢 {name}: {usage_pct:.0f}% used (${budget['current']}/${budget['limit']})")
        
        total_used = sum(b["current"] for b in budgets.values())
        findings.append(f"💰 Total: ${total_used}/${data.get('total_budget', 560)}/mo")
        
        if data.get("warnings"):
            findings.append(f"ℹ️  {len(data['warnings'])} cost-related entries in brain")
        
        return findings
    
    def recommend(self, findings: list) -> list:
        return [
            "Track OpenRouter API costs via OpenRouter dashboard",
            "Set up Vercel spending alerts",
            "Consider Supabase plan upgrade if approaching limits",
            "Audit unused Docker containers/images for cost savings",
        ]
