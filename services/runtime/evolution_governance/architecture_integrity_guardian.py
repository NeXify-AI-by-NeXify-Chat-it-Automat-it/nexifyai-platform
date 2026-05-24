#!/usr/bin/env python3
"""architecture_integrity_guardian.py -- Protects core architecture files."""
import json,logging
log=logging.getLogger("arch-guardian")
PROTECTED=["/services/runtime/mcp/mcp_gateway.py","/services/runtime/mcp/mcp_registry.py","/services/runtime/events/event_bus.py"]
RULES=["never_replace_gateway","never_bypass_governance","never_disable_audit"]
class ArchGuardian:
    def check_file(self,fp):
        for p in PROTECTED:
            if p.endswith("*") and fp.startswith(p[:-1]): return {"allowed":False,"reason":f"protected:{p}"}
            if fp==p: return {"allowed":False,"reason":"protected file"}
        return {"allowed":True}
    def check_rule(self,r):
        if r in RULES: return {"allowed":False}
        return {"allowed":True}
GUARDIAN=ArchGuardian()
if __name__=="__main__":logging.basicConfig(level=logging.INFO);print(json.dumps(GUARDIAN.check_file("/services/runtime/mcp/mcp_gateway.py")))
