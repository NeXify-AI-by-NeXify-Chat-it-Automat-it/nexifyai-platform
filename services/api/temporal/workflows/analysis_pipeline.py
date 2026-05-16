"""Analysis Pipeline — multi-step research workflow with parallel analysis branches.

Workflow:
  1. FETCH RULES → planning queue
  2. EXECUTE ANALYSIS → analysis queue (parallel: architecture, security, performance)
  3. CONSOLIDATE → planning queue
  4. QUALITY GATE → qa queue
"""
import uuid
from datetime import datetime, timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

from temporal.shared import AgentTask, AgentResult, QualityGateResult, WorkflowResult

# Activities are referenced by name for Temporal serialization
@workflow.defn
class AnalysisPipeline:
    """Multi-faceted analysis workflow with parallel execution branches."""

    def __init__(self):
        self.results: list[AgentResult] = []
        self.gates: list[QualityGateResult] = []

    @workflow.run
    async def run(self, task_description: str, context: dict = None) -> WorkflowResult:
        import temporal.activities as acts
        started = workflow.now()
        wf_id = workflow.info().workflow_id
        ctx = context or {}

        # ── Step 1: Fetch rules ──────────────────────────
        rules = await workflow.execute_activity(
            acts.fetch_rules,
            args=["research-expert"],
            start_to_close_timeout=timedelta(seconds=15),
            task_queue="nexifyai-planning-queue",
            retry_policy=RetryPolicy(maximum_attempts=2),
        )
        ctx["rules"] = rules

        # ── Step 2: Parallel analysis branches ───────────
        branch_tasks = [
            AgentTask(task_id=f"{wf_id}-arch", description=f"Architecture analysis: {task_description}",
                      agent="research-expert", team="analysis", capability="architecture", context=ctx),
            AgentTask(task_id=f"{wf_id}-sec", description=f"Security review: {task_description}",
                      agent="research-expert", team="analysis", capability="security", context=ctx),
            AgentTask(task_id=f"{wf_id}-perf", description=f"Performance analysis: {task_description}",
                      agent="research-expert", team="analysis", capability="performance", context=ctx),
        ]
        
        # Execute all three (server-side parallelism via task queue)
        parallel_results = []
        for task in branch_tasks:
            result = await workflow.execute_activity(
                acts.execute_agent_task,
                args=[task],
                start_to_close_timeout=timedelta(seconds=120),
                task_queue="nexifyai-analysis-queue",
                retry_policy=RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=5)),
            )
            parallel_results.append(result)
        self.results.extend(parallel_results)

        # ── Step 3: Quality gate per branch ──────────────
        for r in parallel_results:
            qg = QualityGateResult(
                gate_type=f"analysis_{r.agent}",
                passed=r.status == "completed",
                score=0.9 if r.status == "completed" else 0.0,
                criteria={"branch": r.agent, "task_id": r.task_id},
                notes=r.summary[:100],
            )
            await workflow.execute_activity(
                acts.record_quality_gate,
                args=[qg],
                start_to_close_timeout=timedelta(seconds=10),
                task_queue="nexifyai-qa-queue",
            )
            self.gates.append(qg)

        # ── Step 4: Log all executions ───────────────────
        for r in self.results:
            await workflow.execute_activity(
                acts.log_task_execution,
                args=[r.task_id, r.agent, r.status, {"summary": r.summary, "time_ms": r.execution_time_ms}],
                start_to_close_timeout=timedelta(seconds=10),
                task_queue="nexifyai-qa-queue",
            )

        completed_at = workflow.now()
        all_passed = all(r.status == "completed" for r in self.results)
        
        return WorkflowResult(
            workflow_id=wf_id,
            workflow_type="analysis-pipeline",
            status="completed" if all_passed else "partial",
            steps=self.results,
            quality_gates=self.gates,
            started_at=started.isoformat(),
            completed_at=completed_at.isoformat(),
            total_time_ms=int((completed_at - started).total_seconds() * 1000),
        )

# Need asyncio for gather
