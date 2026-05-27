#!/usr/bin/env python3
import json, logging, os, sys
from datetime import datetime, timezone
log = logging.getLogger("org-learn")
def learn(events=None):
    if not events: events=[{"type":"incident","outcome":"resolved","lesson":"add_retry"}]
    knowledge=[{"lesson":e.get("lesson"),"applied":e.get("outcome")=="resolved"} for e in events]
    return {"ts":datetime.now(timezone.utc).isoformat(),"learned":len(knowledge)}
def main():
    event = None
    if not sys.stdin.isatty():
        import select
        if select.select([sys.stdin],[],[],0.5)[0]:
            try:
                event = json.loads(sys.stdin.read())
            except json.JSONDecodeError:
                pass
    print(json.dumps(learn(event),indent=2))
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO); main()
