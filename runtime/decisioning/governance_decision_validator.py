#!/usr/bin/env python3
"""gov_decision_validator.py"""
import json,logging
from organizational_constitution import CON
log=logging.getLogger("gov-decision")
class GovernanceDecisionValidator:
    def validate(self,decision):
        c=CON.validate({"type":decision.get("type","")})
        return {"valid":c["conforms"],"constitution":c}
VALIDATOR=GovernanceDecisionValidator()
