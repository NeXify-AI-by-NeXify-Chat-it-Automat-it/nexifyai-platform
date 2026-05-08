"""FinOps Agent — Cost analysis and budget monitoring."""

from backend.agents.base_agent import BaseAgent
from typing import Dict, List, Any


class FinOpsAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("FinOps Agent", "Cost analysis and budget monitoring")
    
    def observe(self) -> Dict[str, Any]:
        return {
            "budgets": {
                "openrouter": {"limit": 500, "current": 0},  # TODO: real API
                "vercel": {"limit": 20, "current": 20},
                "supabase": {"limit": 25, "current": 25},
                "hostinger": {"limit": 15, "current": 15},
            },
            "total_monthly": 60,  # estimated
            "total_budget": 560,
        }
    
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        findings = []
        budgets = data.get("budgets", {})
        total = data.get("total_monthly", 0)
        
        for name, budget in budgets.items():
            usage_pct = (budget["current"] / budget["limit"]) * 100 if budget["limit"] > 0 else 0
            if usage_pct > 90:
                findings.append(f"🔴 {name}: {usage_pct:.0f}% of budget used")
            elif usage_pct > 75:
                findings.append(f"🟡 {name}: {usage_pct:.0f}% of budget used")
            else:
                findings.append(f"🟢 {name}: {usage_pct:.0f}% used")
        
        findings.append(f"Total: ${total}/ ${data.get('total_budget', 0)} ({total/data.get('total_budget', 1)*100:.0f}%)")
        return findings
    
    def recommend(self, findings: List[str]) -> List[str]:
        return [
            "Track OpenRouter API costs per model",
            "Optimize deepseek-v4-flash vs v4-pro usage ratio",
            "Review Vercel plan if approaching Pro limits",
        ]
