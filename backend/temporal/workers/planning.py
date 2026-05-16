"""Planning Worker — task decomposition, dependency graphs, workflow planning."""
import asyncio, logging
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from temporal.activities import log_task_execution, fetch_rules

logger = logging.getLogger("nexifyai.temporal.worker.planning")

TASK_QUEUE = "nexifyai-planning-queue"
ACTIVITIES = [log_task_execution, fetch_rules]
WORKFLOWS = []

async def start(host="localhost:7233", namespace="default"):
    client = await Client.connect(host, namespace=namespace)
    worker = Worker(client, task_queue=TASK_QUEUE,
                    activities=ACTIVITIES,
                    workflow_runner=UnsandboxedWorkflowRunner())
    logger.info(f"Planning worker on {TASK_QUEUE} — {len(ACTIVITIES)} activities")
    await worker.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())
