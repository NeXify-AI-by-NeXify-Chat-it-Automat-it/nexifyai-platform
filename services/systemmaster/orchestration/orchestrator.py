#!/venv/bin/python3
"""Orchestrator — coordinates multi-service workflows."""
import logging, sys, time
sys.path.insert(0, "/systemmaster/eventbus")
from eventbus_daemon import get_bus
logging.basicConfig(level=logging.INFO, format="%(asctime)s [orch] %(levelname)s: %(message)s")
log = logging.getLogger("orch")
log.info("Orchestrator initialized")
while True: time.sleep(10)
