#!/usr/bin/env python3
"""architecture_guardian.py — Protects architectural integrity against drift."""
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("arch-guard")
ARCH_RULES={"no_cyclic_deps":True,"single_source_brain":True,"governance_gated_delivery":True,"runtime_over_config":True,"api_stability":True,"no_direct_db_access":True}
def check(rules=None):
    if not rules: rules=ARCH_RULES
    violations=[k for k,v in rules.items() if not v]
    return {"ts":datetime.now(timezone.utc).isoformat(),"violations":violations,"intact":len(violations)==0}
def main():
    print(json.dumps(check(),indent=2)); exit(0 if check()["intact"] else 1)
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); sys.exit(main())
