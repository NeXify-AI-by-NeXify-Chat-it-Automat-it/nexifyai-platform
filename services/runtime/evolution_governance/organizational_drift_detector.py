#!/usr/bin/env python3
"""org_drift_detector.py -- Detects drift from enterprise truth."""
import json,logging
from event_bus import get_bus,publish
log=logging.getLogger("drift-detect")
class DriftDetector:
    def __init__(self): self._truth={};self._state={};self.bus=get_bus()
    def start(self):
        self.bus.subscribe("truth.changed",self._on_truth,"drift:truth")
        self.bus.subscribe("state.changed",self._on_state,"drift:state");log.info("Drift detector active")
    def _on_truth(self,e):self._truth.update(e.get("payload",{}))
    def _on_state(self,e):self._state.update(e.get("payload",{}))
    def detect(self):
        drifts=[]
        for k in set(list(self._truth.keys())+list(self._state.keys())):
            t=self._truth.get(k);s=self._state.get(k)
            if t is not None and s is not None and t!=s:
                drifts.append({"key":k,"truth":t,"state":s});publish("watchdog.drift",{"key":k},"drift-detect")
        return {"drifts":drifts,"total":len(drifts)}
DETECTOR=DriftDetector()
def start():DETECTOR.start();return DETECTOR
if __name__=="__main__":logging.basicConfig(level=logging.INFO);start();print(json.dumps(DETECTOR.detect()))
