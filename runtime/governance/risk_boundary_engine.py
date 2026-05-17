#!/usr/bin/env python3
"""risk_boundary_engine.py — Evaluates risk boundaries for autonomous actions."""
import json, logging, os, sys
sys.path.insert(0, "/runtime/governance")
log = logging.getLogger("risk-boundary")

BOUNDARIES = {
    "build_break": {"max":10,"auto":7},"runtime_change": {"max":8,"auto":5},
    "dependency_change": {"max":7,"auto":5},"governance_change": {"max":9,"auto":6},
    "infrastructure_change": {"max":8,"auto":5},"deployment": {"max":7,"auto":5},
    "default": {"max":5,"auto":7},
}

class RiskBoundaryEngine:
    def evaluate(self, action: dict) -> dict:
        score = action.get("risk_score", 1)
        atype = action.get("type","default")
        b = BOUNDARIES.get(atype, BOUNDARIES["default"])
        return {"pass": score <= b["max"], "risk_score":score,
                "max_score":b["max"],"auto_threshold":b["auto"],
                "can_auto": score <= b["auto"],
                "level":"safe" if score<=3 else "monitor" if score<=5 else "caution" if score<=7 else "critical"}

RISK_BOUNDARY = RiskBoundaryEngine()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for at,sc in [("code_refactor",2),("deployment",6),("governance_change",8)]:
        r = RISK_BOUNDARY.evaluate({"type":at,"risk_score":sc})
        print(f"{at:25s} score={sc} -> {r['level']:10s} auto={r['can_auto']}")