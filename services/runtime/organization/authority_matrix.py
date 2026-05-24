#!/usr/bin/env python3
"""authority_matrix.py — Who can approve what across the organization."""
import json, logging, os, sys
log = logging.getLogger("auth-matrix")
MATRIX={"deploy_prod":{"approver":"governance","veto":"executive"},"pr_merge":{"approver":"delivery","veto":"governance"},"policy_change":{"approver":"governance","veto":"executive"},"architecture_change":{"approver":"executive","veto":None},"secret_rotation":{"approver":"security","veto":"governance"},"incident_resolve":{"approver":"recovery","veto":"orchestration"}}
def authorize(action="deploy_prod",requestor="delivery"):
    entry=MATRIX.get(action)
    if not entry: return {"action":action,"approved":False,"reason":"unknown_action"}
    approved=requestor==entry["approver"] or requestor=="executive"
    return {"action":action,"requestor":requestor,"approver":entry["approver"],"veto":entry["veto"],"approved":approved}
def main():
    a=sys.argv[1] if len(sys.argv)>1 else "deploy_prod"
    r=sys.argv[2] if len(sys.argv)>2 else "delivery"
    print(json.dumps(authorize(a,r),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
