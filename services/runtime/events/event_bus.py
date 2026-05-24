#!/usr/bin/env python3
"""event_bus.py -- Central event bus for organizational runtime events."""
import json, logging, os, threading, time, uuid
from datetime import datetime, timezone
from collections import defaultdict
log = logging.getLogger("event-bus")

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._history = []
        self._max_history = 1000
        self._lock = threading.Lock()
        self._event_counter = 0

    def subscribe(self, event_type, callback, name=None):
        with self._lock:
            self._subscribers[event_type].append({"cb": callback, "name": name or f"sub-{id(callback)}"})
            return len(self._subscribers[event_type]) - 1

    def publish(self, event_type, payload=None, source="unknown"):
        ev = {"id": str(uuid.uuid4())[:8], "type": event_type, "payload": payload or {}, "source": source, "ts": datetime.now(timezone.utc).isoformat(), "seq": self._event_counter}
        self._event_counter += 1
        with self._lock:
            self._history.append(ev)
            if len(self._history) > self._max_history: self._history = self._history[-self._max_history:]
            subs = list(self._subscribers.get(event_type, [])) + list(self._subscribers.get("*", []))
        for s in subs:
            try: s["cb"](ev)
            except Exception as e: log.error(f"Subscriber {s.get('name')} failed: {e}")
        return ev

    def get_history(self, event_type=None, limit=50):
        with self._lock:
            events = list(self._history)
        if event_type: events = [e for e in events if e["type"] == event_type]
        return events[-limit:]

    def stats(self):
        with self._lock:
            types = defaultdict(int)
            for e in self._history: types[e["type"]] += 1
            return {"total_events": self._event_counter, "types": dict(types), "subscribers": {k: len(v) for k, v in self._subscribers.items()}}

BUS = EventBus()
def get_bus(): return BUS
def publish(event_type, payload=None, source="unknown"): return BUS.publish(event_type, payload, source)
def subscribe(event_type, callback, name=None): return BUS.subscribe(event_type, callback, name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [event-bus] %(message)s")
    bus = get_bus()
    bus.subscribe("test", lambda e: print(f"Got: {e['type']}"), "test")
    bus.publish("test", {"msg": "hello"}, "main")
    print(json.dumps(bus.stats(), indent=2))
