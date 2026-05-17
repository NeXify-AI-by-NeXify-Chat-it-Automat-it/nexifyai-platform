#!/venv/bin/python3
"""eventbus_daemon.py — Persistenter, replayfähiger Event Bus. File-backed."""
import json, logging, os, sys, threading, time, queue
from datetime import datetime, timezone
from collections import defaultdict

EVENT_STORE = "/systemmaster/state/event_store.jsonl"
MAX_HISTORY = 100000

logging.basicConfig(level=logging.INFO, format="%(asctime)s [eventbus] %(levelname)s: %(message)s")
log = logging.getLogger("eventbus")

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._history = []
        self._running = False
        self._lock = threading.Lock()
        self._event_queue = queue.Queue()
        self._load_history()
        log.info("Eventbus initialized with %d historical events", len(self._history))

    def _load_history(self):
        if not os.path.exists(EVENT_STORE):
            os.makedirs(os.path.dirname(EVENT_STORE), exist_ok=True)
            return
        try:
            with open(EVENT_STORE) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try: self._history.append(json.loads(line))
                        except: pass
            # Keep last MAX_HISTORY
            if len(self._history) > MAX_HISTORY:
                self._history = self._history[-MAX_HISTORY:]
        except: pass

    def _append_store(self, event):
        try:
            with open(EVENT_STORE, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            log.error("Store write failed: %s", e)

    def subscribe(self, event_type, callback, name="anonymous"):
        with self._lock:
            self._subscribers[event_type].append({"cb": callback, "name": name})
            log.info("Subscribe %s -> %s", name, event_type)

    def publish(self, event_type, payload, source="system"):
        event = {"type": event_type, "payload": payload, "source": source,
                 "ts": datetime.now(timezone.utc).isoformat(),
                 "id": f"evt-{int(time.time()*1000000)}"}
        self._append_store(event)
        self._event_queue.put(event)

    def _dispatcher(self):
        while self._running:
            try:
                event = self._event_queue.get(timeout=1)
                with self._lock:
                    self._history.append(event)
                    if len(self._history) > MAX_HISTORY:
                        self._history = self._history[-MAX_HISTORY:]
                    subs = list(self._subscribers.get(event["type"], []))
                for sub in subs:
                    try: sub["cb"](event)
                    except Exception as e: log.error("Sub %s failed: %s", sub["name"], e)
            except queue.Empty: continue

    def start(self):
        self._running = True
        t = threading.Thread(target=self._dispatcher, daemon=True)
        t.start()
        # Replay stored events for subscribers that need catch-up
        log.info("Eventbus daemon started — %d historical events available", len(self._history))
        return self

    def stop(self): self._running = False

    def replay(self, event_type=None, since=None, callback=None):
        events = self._history
        if event_type: events = [e for e in events if e["type"] == event_type]
        if since: events = [e for e in events if e.get("ts","") >= since]
        if callback:
            for e in events:
                try: callback(e)
                except: pass
        return events

_BUS = None
def get_bus():
    global _BUS
    if _BUS is None: _BUS = EventBus().start()
    return _BUS

if __name__ == "__main__":
    bus = get_bus()
    log.info("Eventbus ready. Blocking forever...")
    threading.Event().wait()
