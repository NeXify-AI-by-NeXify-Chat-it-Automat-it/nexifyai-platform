#!/usr/bin/env python3
"""recursive_change_controller.py -- Prevents infinite recursion."""
import json,logging,time
from collections import defaultdict
log=logging.getLogger("recursive-ctl")
class RecursiveChangeController:
    def __init__(self): self._hist=defaultdict(list);self._max=3;self._cooldown=60
    def check(self,agent,change_type):
        now=time.time();h=self._hist[f"{agent}:{change_type}"]
        recent=[x for x in h if now-x<self._cooldown]
        if len(recent)>=self._max: return {"allowed":False,"reason":"recursive","remaining":int(self._cooldown-(now-recent[0]))}
        h.append(now);return {"allowed":True,"depth":len(recent)+1}
CTRL=RecursiveChangeController()
if __name__=="__main__":logging.basicConfig(level=logging.INFO);print(json.dumps(CTRL.check("agent","add")))
