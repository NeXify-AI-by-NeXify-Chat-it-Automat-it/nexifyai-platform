"""QA Worker — validation, quality gates, regression testing."""
import asyncio, logging
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from temporal.activities import record_quality_gate, log_task_execution, fetch_rules

logger = logging.getLogger("nexifyai.temporal.worker.qa")

TASK_QUEUE = "nexifyai-qa-queue"
ACTIVITIES = [record_quality_gate, log_task_execution, fetch_rules]
WORKFLOWS = []

async def start(host="localhost:7233", namespace="default"):
    client = await Client.connect(host, namespace=namespace)
    worker = Worker(client, task_queue=TASK_QUEUE,
                    activities=ACTIVITIES,
                    workflow_runner=UnsandboxedWorkflowRunner())
    logger.info(f"QA worker on {TASK_QUEUE} — {len(ACTIVITIES)} activities")
    await worker.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())
