"""Temporal Worker — runs Workflows and Activities.

Start this as a long-running process alongside the FastAPI server.
"""
import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner

from .activities import (
    execute_agent_task,
    record_quality_gate,
    log_task_execution,
    fetch_rules,
)
from .workflows.code_review import CodeReviewPipeline
from .workflows.analysis_pipeline import AnalysisPipeline
from .workflows.deploy_pipeline import DeployPipeline

logger = logging.getLogger("nexifyai.temporal.worker")

ACTIVITIES = [execute_agent_task, record_quality_gate, log_task_execution, fetch_rules]
WORKFLOWS = [CodeReviewPipeline, AnalysisPipeline, DeployPipeline]


async def start_worker(host: str = "localhost:7233", namespace: str = "default",
                       task_queue: str = "nexifyai-task-queue"):
    """Start a Temporal worker that polls for tasks."""
    client = await Client.connect(host, namespace=namespace)
    
    worker = Worker(
        client,
        use_worker_versioning=False,
        workflow_runner=UnsandboxedWorkflowRunner(),
        task_queue=task_queue,
        workflows=WORKFLOWS,
        activities=ACTIVITIES,
    )
    
    logger.info(f"Temporal worker started on {host}/{namespace}/{task_queue} "
                f"with {len(WORKFLOWS)} workflows, {len(ACTIVITIES)} activities")
    
    await worker.run()


async def main():
    logging.basicConfig(level=logging.INFO)
    await start_worker()


if __name__ == "__main__":
    asyncio.run(main())
