#!/venv/bin/python3
"""NeXify AI Systemmaster — primary runtime process. Connects all subsystems."""
import logging, os, sys, time
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus
logging.basicConfig(level=logging.INFO, format="%(asctime)s [systemmaster] %(levelname)s: %(message)s")
log = logging.getLogger("systemmaster")
bus = get_bus()
log.info("NeXify AI Systemmaster runtime started")
log.info("Connected to event bus at pid=%d", os.getpid())
while True:
    bus.publish("systemmaster.heartbeat", {"pid": os.getpid(), "uptime": time.time()}, "systemmaster")
    time.sleep(60)
