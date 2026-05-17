#!/usr/bin/env python3
"""autonomous_growth_constraints.py -- Limits on growth rate."""
import json,logging
log=logging.getLogger("growth")
RULES={"max_new_capabilities_per_cycle":3,"max_new_services_per_day":2,"require_stability_minutes":15}
class GrowthConstraints:
    def check(self,gt,val):
        l=RULES.get(f"max_new_{gt}")
        if l is not None and val>l: return {"allowed":False,"reason":f"{val}>{l}"}
        return {"allowed":True}
GROWTH=GrowthConstraints()
if __name__=="__main__":print(json.dumps(GROWTH.check("capabilities_per_cycle",5)))
