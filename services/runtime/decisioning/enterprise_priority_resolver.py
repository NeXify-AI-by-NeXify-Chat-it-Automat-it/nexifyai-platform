#!/usr/bin/env python3
"""enterprise_priority_resolver.py"""
import json,logging
log=logging.getLogger("priority-resolve")
PRIO={"incident":1,"recovery":1,"security":2,"deployment":3,"brain":4,"optimization":5}
class PriorityResolver:
    def resolve(self,items):return sorted(items,key=lambda x:PRIO.get(x.get("domain",""),99))
RESOLVER=PriorityResolver()
