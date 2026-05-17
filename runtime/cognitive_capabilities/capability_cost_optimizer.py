#!/usr/bin/env python3
"""capability_cost_optimizer.py — Optimizes capability selection based on cost/benefit."""
import json, logging
log = logging.getLogger("cap-cost")

COST_MAP = {
    "github.issue.create": {"cost": 0.01, "benefit": 0.5},
    "github.pr.create": {"cost": 0.05, "benefit": 0.9},
    "brain.store": {"cost": 0.001, "benefit": 0.3},
    "brain.query": {"cost": 0.001, "benefit": 0.4},
    "infra.service.restart": {"cost": 0.1, "benefit": 0.8},
    "runtime.shell": {"cost": 0.01, "benefit": 0.2},
}

class CapabilityCostOptimizer:
    def optimize(self, candidates, budget=1.0):
        scored = []
        for c in candidates:
            meta = COST_MAP.get(c, {"cost": 0.01, "benefit": 0.1})
            ratio = meta["benefit"] / max(meta["cost"], 0.001)
            scored.append({"cap": c, "cost": meta["cost"], "benefit": meta["benefit"], "ratio": round(ratio, 2)})
        scored.sort(key=lambda x: -x["ratio"])
        selected = []; total_cost = 0
        for s in scored:
            if total_cost + s["cost"] <= budget:
                selected.append(s); total_cost += s["cost"]
        return {"selected": selected, "total_cost": round(total_cost, 3), "budget": budget}

OPT = CapabilityCostOptimizer()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); print(json.dumps(OPT.optimize(["github.pr.create","brain.store","infra.service.restart"], 0.5), indent=2))
