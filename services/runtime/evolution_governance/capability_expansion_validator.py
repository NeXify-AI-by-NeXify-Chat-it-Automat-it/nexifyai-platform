#!/usr/bin/env python3
"""capability_expansion_validator.py -- Validates new capability additions."""
import json,logging
log=logging.getLogger("cap-expansion")
class CapExpansionValidator:
    def validate(self,cap):
        checks=[]
        if not cap.get("id"):checks.append({"check":"id","pass":False})
        if not cap.get("domain"):checks.append({"check":"domain","pass":False})
        all_pass=all(c.get("pass",True) for c in checks)
        return {"valid":all_pass,"checks":checks}
EXPANSION=CapExpansionValidator()
if __name__=="__main__":print(json.dumps(EXPANSION.validate({"id":"new.test","domain":"test"})))
