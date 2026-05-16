#!/usr/bin/env python3
"""
NeXify AI Redis Stream Consumer - Event-driven task dispatcher.
Listens on nexifyai:tasks stream, routes to enterprise teams,
dispatches via backend /api/orchestration/execute.
"""
import os, sys, json, time, logging, asyncio, signal
from datetime import datetime, timezone

sys.path.insert(0, "/opt/nexifyai-website-sicherheitskopie/backend")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [stream-consumer] %(levelname)s: %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("nexifyai.stream_consumer")

REDIS_HOST = os.environ.get("REDIS_HOST", "172.17.0.6")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")
INTERNAL_AUTH = os.environ.get("INTERNAL_AUTH", "nexifyai-local")
STREAM = "nexifyai:tasks"
GROUP = "orchestrator-group"

DOMAIN_SYSTEMS = {
    "deploy": (4, "Infrastructure"), "docker": (4, "Infrastructure"),
    "security": (5, "Security"), "vulnerability": (5, "Security"),
    "code": (3, "Development"), "bug": (3, "Development"), "develop": (3, "Development"),
    "database": (6, "Data & AI"), "data": (6, "Data & AI"), "ml": (6, "Data & AI"),
    "test": (7, "Quality"), "quality": (7, "Quality"),
    "product": (8, "Product"), "feature": (8, "Product"),
    "legal": (10, "Legal"), "gdpr": (10, "Legal"),
    "marketing": (11, "Marketing"), "seo": (11, "Marketing"), "blog": (11, "Marketing"),
    "monitor": (12, "Monitor"), "health": (12, "Monitor"), "alert": (12, "Monitor"),
    "brain": (2, "Brain"), "knowledge": (2, "Brain"), "memory": (2, "Brain"),
    "orchestrat": (1, "CEO"), "priority": (1, "CEO"),
}

def route_task(task_text):
    task_lower = task_text.lower()
    best_sid, best_name = 1, "CEO"
    best_score = 0
    for keyword, (sid, name) in DOMAIN_SYSTEMS.items():
        if keyword in task_lower and len(keyword) > best_score:
            best_score = len(keyword)
            best_sid, best_name = sid, name
    return best_sid, best_name

async def process_task(task_data):
    import httpx
    task_text = task_data.get("title", task_data.get("task", str(task_data)))
    priority = task_data.get("priority", "M")
    source = task_data.get("source", "stream")
    system_id, team_name = route_task(task_text)
    result = {"task": task_text, "system_id": system_id, "team": team_name,
              "priority": priority, "source": source, "status": "pending",
              "timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{BACKEND_URL}/api/orchestration/execute",
                json={"task": task_text, "agent": "ceo-agent", "system_id": system_id,
                      "context": {"priority": priority, "source": source}},
                headers={"X-Internal-Auth": INTERNAL_AUTH})
            if r.status_code == 200:
                resp = r.json()
                result["status"] = resp.get("status", "executed")
                result["task_id"] = resp.get("task_id", "")
                result["agent"] = resp.get("agent", "")
            else:
                result["status"] = "failed"
                result["error"] = f"HTTP {r.status_code}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result

async def main():
    import redis.asyncio as redis_lib
    consumer = f"worker-{os.uname().nodename}"
    logger.info("=" * 50)
    logger.info("STREAM CONSUMER STARTING - Stream: %s Group: %s", STREAM, GROUP)
    logger.info("=" * 50)
    r = redis_lib.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    try:
        await r.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
        logger.info("Consumer group created: %s", GROUP)
    except Exception:
        pass
    shutdown = False
    def handle(signum, frame):
        nonlocal shutdown
        shutdown = True
    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)
    processed = 0
    while not shutdown:
        try:
            messages = await r.xreadgroup(GROUP, consumer, {STREAM: ">"}, count=5, block=10000)
            if not messages:
                continue
            for stream_name, entries in messages:
                for msg_id, msg_data in entries:
                    logger.info("Processing %s: %s", msg_id, str(msg_data)[:80])
                    result = await process_task(msg_data)
                    await r.xack(STREAM, GROUP, msg_id)
                    processed += 1
                    await r.xadd("nexifyai:events", {
                        "type": "task.processed", "source": "stream-consumer",
                        "payload": json.dumps(result, default=str),
                        "status": result.get("status", "unknown"),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }, maxlen=10000)
                    logger.info("  -> %s: %s", result["status"], result.get("task_id", "N/A"))
        except Exception as e:
            logger.error("Error: %s", e)
            await asyncio.sleep(5)
    await r.close()
    logger.info("Consumer stopped. Processed: %d tasks", processed)

if __name__ == "__main__":
    asyncio.run(main())
