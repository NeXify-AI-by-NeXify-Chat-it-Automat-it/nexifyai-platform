"""Temporal Client — singleton for FastAPI integration.

Provides get_temporal_client() for starting workflows from API endpoints.
"""
import logging
from temporalio.client import Client
from metrics import WORKFLOW_EXECUTIONS

logger = logging.getLogger("nexifyai.temporal.client")

_client: Client | None = None


async def get_temporal_client(host: str = "localhost:7233", namespace: str = "default") -> Client:
    """Get or create the Temporal client singleton."""
    global _client
    if _client is None:
        _client = await Client.connect(host, namespace=namespace)
        logger.info(f"Temporal client connected to {host}/{namespace}")
    return _client


async def start_workflow(
    workflow_class,
    task: str,
    context: dict = None,
    workflow_id: str = None,
    task_queue: str = "nexifyai-task-queue",
) -> dict:
    """Start a Temporal workflow and return its result."""
    import uuid
    from temporalio.client import WorkflowFailureError
    
    client = await get_temporal_client()
    
    wf_id = workflow_id or f"wf-{uuid.uuid4().hex[:8]}"
    
    try:
        result = await client.execute_workflow(
            workflow_class.run,
            args=[task, context or {}],
            id=wf_id,
            task_queue=task_queue,
        )
        
        WORKFLOW_EXECUTIONS.labels(workflow_type=str(workflow_class).split('.')[-1], status='completed').inc()
        # Convert dataclass to dict if needed
        if hasattr(result, '__dataclass_fields__'):
            from dataclasses import asdict
            return {"workflow_id": wf_id, "status": "completed", "result": asdict(result)}
        return {"workflow_id": wf_id, "status": "completed", "result": result}
    
    except WorkflowFailureError as e:
        WORKFLOW_EXECUTIONS.labels(workflow_type=str(workflow_class).split('.')[-1], status='failed').inc()
        return {"workflow_id": wf_id, "status": "failed", "error": str(e)}
    except Exception as e:
        WORKFLOW_EXECUTIONS.labels(workflow_type=str(workflow_class).split('.')[-1], status='failed').inc()
        return {"workflow_id": wf_id, "status": "failed", "error": str(e)}


async def start_analysis_workflow(task: str, context: dict = None, workflow_id: str = None) -> dict:
    """Start a parallel analysis workflow."""
    import uuid
    from temporal.workflows.analysis_pipeline import AnalysisPipeline
    return await start_workflow(
        AnalysisPipeline, task, context,
        workflow_id or f"analysis-{uuid.uuid4().hex[:8]}",
    )


async def start_deploy_workflow(task: str, context: dict = None, workflow_id: str = None) -> dict:
    """Start a deploy workflow with conditional rollback."""
    import uuid
    from temporal.workflows.deploy_pipeline import DeployPipeline
    return await start_workflow(
        DeployPipeline, task, context,
        workflow_id or f"deploy-{uuid.uuid4().hex[:8]}",
    )
