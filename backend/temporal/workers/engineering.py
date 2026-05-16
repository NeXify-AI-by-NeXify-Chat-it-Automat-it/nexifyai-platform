"""Engineering Worker — code generation, refactoring, debugging."""
import asyncio, logging
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from temporal.activities import execute_agent_task, record_quality_gate, log_task_execution

logger = logging.getLogger("nexifyai.temporal.worker.engineering")

TASK_QUEUE = "nexifyai-engineering-queue"
ACTIVITIES = [execute_agent_task, record_quality_gate, log_task_execution]
WORKFLOWS = []

async def start(host="localhost:7233", namespace="default"):
    client = await Client.connect(host, namespace=namespace)
    worker = Worker(client, task_queue=TASK_QUEUE,
                    activities=ACTIVITIES,
                    workflow_runner=UnsandboxedWorkflowRunner())
    logger.info(f"Engineering worker on {TASK_QUEUE} — {len(ACTIVITIES)} activities")
    await worker.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())
