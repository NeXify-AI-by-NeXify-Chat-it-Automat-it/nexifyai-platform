#!/usr/bin/env python3
"""runtime_stability_protector.py -- Blocks evolution during unstable periods."""
import json,logging,time
from event_bus import get_bus,publish
log=logging.getLogger("stability")
class StabilityProtector:
    def __init__(self): self._last=0;self._window=60;self._unstable=False;self.bus=get_bus()
    def start(self):
        self.bus.subscribe("incident.detected",self._on_incident,"stability:incident");log.info("Stability protector active")
    def is_stable(self):
        if self._unstable and time.time()-self._last>self._window: self._unstable=False
        return not self._unstable
    def _on_incident(self,e): self._last=time.time();self._unstable=True;publish("evolution.blocked",{"reason":"unstable"},"stability")
PROTECTOR=StabilityProtector()
def start():PROTECTOR.start();return PROTECTOR
if __name__=="__main__":logging.basicConfig(level=logging.INFO);start();print(f"Stable:{PROTECTOR.is_stable()}")
