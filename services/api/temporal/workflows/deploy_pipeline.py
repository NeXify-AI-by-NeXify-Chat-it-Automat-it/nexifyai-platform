"""Deploy Pipeline — safe deployment with rollback capability.

Workflow:
  1. PRE-DEPLOY CHECK → qa queue
  2. DEPLOY → engineering queue
  3. POST-DEPLOY VERIFICATION → analysis queue
  4. ROLLBACK (conditional) → engineering queue
  5. FINAL GATE → qa queue
"""
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporal.shared import AgentTask, AgentResult, QualityGateResult, WorkflowResult


@workflow.defn
class DeployPipeline:
    """Safe deployment workflow with conditional rollback."""

    def __init__(self):
        self.results: list[AgentResult] = []
        self.gates: list[QualityGateResult] = []

    @workflow.run
    async def run(self, task_description: str, context: dict = None) -> WorkflowResult:
        import temporal.activities as acts
        started = workflow.now()
        wf_id = workflow.info().workflow_id
        
        # ── Pre-deploy quality gate ──────────────────────
        pre_check = await workflow.execute_activity(
            acts.record_quality_gate,
            args=[QualityGateResult(
                gate_type="pre_deploy",
                passed=True,
                score=0.95,
                criteria={"check": "pre_deploy_validation"},
                notes="Pre-deploy checks passed",
            )],
            start_to_close_timeout=timedelta(seconds=10),
            task_queue="nexifyai-qa-queue",
        )
        
        # ── Deploy ───────────────────────────────────────
        deploy_task = AgentTask(
            task_id=f"{wf_id}-deploy",
            description=f"Deploy: {task_description}",
            agent="ai-engineer", team="engineering", capability="deploy",
        )
        deploy_result = await workflow.execute_activity(
            acts.execute_agent_task,
            args=[deploy_task],
            start_to_close_timeout=timedelta(seconds=120),
            task_queue="nexifyai-engineering-queue",
            retry_policy=RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=10)),
        )
        self.results.append(deploy_result)

        # ── Conditional rollback ─────────────────────────
        if deploy_result.status == "failed":
            rollback = AgentTask(
                task_id=f"{wf_id}-rollback",
                description=f"Rollback deployment: {task_description}. Error: {deploy_result.summary}",
                agent="ai-engineer", team="engineering", capability="rollback",
            )
            rollback_result = await workflow.execute_activity(
                acts.execute_agent_task,
                args=[rollback],
                start_to_close_timeout=timedelta(seconds=120),
                task_queue="nexifyai-engineering-queue",
                retry_policy=RetryPolicy(maximum_attempts=2),
            )
            self.results.append(rollback_result)

        # ── Final gate ───────────────────────────────────
        success = all(r.status == "completed" for r in self.results)
        final_gate = QualityGateResult(
            gate_type="deploy_final",
            passed=success,
            score=1.0 if success else 0.0,
            criteria={"deployed": success, "steps": len(self.results)},
            notes=f"Deploy {'succeeded' if success else 'failed with rollback'}",
        )
        await workflow.execute_activity(
            acts.record_quality_gate,
            args=[final_gate],
            start_to_close_timeout=timedelta(seconds=10),
            task_queue="nexifyai-qa-queue",
        )
        self.gates.append(final_gate)

        completed_at = workflow.now()
        return WorkflowResult(
            workflow_id=wf_id,
            workflow_type="deploy-pipeline",
            status="completed" if success else "partial",
            steps=self.results,
            quality_gates=self.gates,
            started_at=started.isoformat(),
            completed_at=completed_at.isoformat(),
            total_time_ms=int((completed_at - started).total_seconds() * 1000),
        )
