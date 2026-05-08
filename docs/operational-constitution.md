# NeXifyAI — Operational Constitution (E3.5)
**Status:** EXECUTABLE DOCTRINE | **Version:** 1.0.0 | **Date:** 2026-05-08

**THIS IS NOT DOCUMENTATION.** This is the binding operational constitution.
Every runtime component, agent, CI pipeline, and recovery action MUST comply.
Violations are CI-blocking, not advisory.

---

## I. PRIME DIRECTIVES (Non-Negotiable)

### 1. Projection ≠ Reality
```
A health check result is a PROJECTION, never canonical truth.
Canonical truth = verifiable source (systemctl, docker ps, direct probe).
Any component that treats a projection as truth is in violation.
```

### 2. No Mutation Without Re-Observation
```
After ANY state change (restart, deploy, config):
  1. Wait stabilization (≥3s)
  2. Re-observe from ALL observer positions
  3. Compare pre vs post reachability
  4. Validate convergence
  5. Persist outcome
No "command succeeded" without steps 1-5.
```

### 3. Contradictions Are Signals
```
When two observers disagree about the same target:
  → This is NOT noise to suppress
  → This IS the most valuable signal in the system
  → Must be classified (network-isolation, auth, port-binding, dns)
  → Must be persisted as a Contradiction in the Truth Graph
```

### 4. Confidence Decays Without Evidence
```
Truth ages:
  0 hours:  confidence = probe_result
  1 hour:   confidence *= 0.95
  6 hours:  confidence *= 0.70
  24 hours: confidence *= 0.30
  >48h:     confidence → 0 (stale, must re-probe)

No confidence value is eternal.
```

### 5. Recovery Requires Convergence
```
RECOVERY_EXECUTED ≠ RECOVERY_SUCCESSFUL
RECOVERY_SUCCESSFUL = All observers agree + no contradictions + confidence ≥ 0.8
Until convergence is validated, recovery state = PENDING or REGRESSED.
```

---

## II. METHOD PERSISTENCE (More Important Than Incident Memory)

### Anti-Patterns (Forbidden Reasoning)
```
❌ Trusting a single observer's report
❌ Trusting a transient healthy state
❌ Assuming execution == recovery
❌ Ignoring observer contradictions
❌ Persisting success without multi-observer validation
❌ Using continue-on-error or || true patterns
❌ Hardcoding values that have canonical tokens
❌ Reporting "healthy" when canonical truth differs
```

### Required Reasoning Patterns (Must Be Learned)
```
✅ Multi-observer comparison before any status assertion
✅ Dependency tracing (which service depends on which)
✅ Stabilization wait after any mutation
✅ Post-recovery convergence validation
✅ Contradiction classification (not suppression)
✅ Confidence scoring with temporal decay
✅ Recovery outcome correlation over time
✅ Persisting negative recovery memory
```

---

## III. SUB-AGENT INHERITANCE

Every agent (Hermes, Architect, Security, QA, FinOps, etc.) inherits:

```python
class OperationalContract:
    mandatory_validation = True           # Must validate after mutation
    mandatory_reobservation = True        # Must re-observe all observers
    mandatory_convergence = True          # Must check convergence state
    forbid_unverified_success = True      # Never emit "SUCCESS" without validation
    forbid_single_observer_trust = True   # Never trust one observer
    require_contradiction_delta = True    # Must report contradiction change
    require_confidence_recomputation = True  # Must recompute confidence after action
    max_staleness_seconds = 3600          # State older than 1h is invalid
```

No agent may override these. No agent may skip validation. No agent may emit "SUCCESS" without:
1. ALL observer re-check
2. Contradiction delta (before → after)
3. Convergence state
4. Confidence recomputation

---

## IV. CI/CD ENFORCEMENT

These rules are CI-blocking (not advisory):

```bash
# Rule 1: Mutation without revalidation
if grep -r "docker restart\|systemctl restart\|deploy" commit && ! grep -r "convergence_state\|re_observed" commit; then
    echo "⛔ BLOCKED: Mutation detected but no post-execution validation"
    exit 1
fi

# Rule 2: Contradictions increased
if contradiction_count_after > contradiction_count_before; then
    echo "⛔ BLOCKED: Contradictions increased — system integrity degraded"
    exit 1
fi

# Rule 3: Recovery without temporal validation
if recovery_action and not convergence_validated:
    echo "⛔ BLOCKED: Recovery executed but convergence not validated"
    exit 1
fi

# Rule 4: Design drift increased
if new_design_violations > 0 and severity >= HIGH:
    echo "⛔ BLOCKED: New HIGH-severity design violations"
    exit 1
fi

# Rule 5: Confidence staleness
if any(confidence_age > 3600 for confidence in active_confidences):
    echo "⛔ BLOCKED: Confidence values stale (>1h) — re-probe required"
    exit 1
fi
```

---

## V. BEHAVIORAL LEARNING MEMORY

Hermes must persist not just WHAT happened, but HOW reasoning succeeded or failed.

```json
{
  "successful_reasoning_patterns": [
    "multi-observer comparison before status assertion",
    "dependency tracing to identify cascading root cause",
    "stabilization wait after recovery action",
    "post-recovery convergence validation with confidence scoring",
    "contradiction classification by topology layer"
  ],
  "anti_patterns_encountered": [
    "trusting single observer (caused false-negative for qdrant)",
    "trusting transient healthy state (1s after restart)",
    "assuming execution == recovery (no re-observation)",
    "echo-based success (fake CI gate)"
  ],
  "recovery_outcome_correlations": {
    "qdrant_localhost_bind": {
      "docker_restart": {"outcome": "regressed", "score": 0.12},
      "port_rebinding_to_0.0.0.0": {"outcome": "converged", "score": 0.96}
    }
  }
}
```

---

## VI. TEMPORAL CONFIDENCE MODEL

```
Confidence(t) = confidence_0 × decay(t) + evidence_weight × convergence_score

Where:
  decay(t) = 0.95 ^ (t_hours)
  
  At t=0:    confidence = probe_result
  At t=1h:   confidence *= 0.95
  At t=6h:   confidence *= 0.70
  At t=24h:  confidence *= 0.30
  At t=48h:  confidence → stale (must re-probe)

Penalties:
  new_contradiction: confidence *= 0.5
  observer_disagreement: confidence *= 0.7
  regression_after_recovery: confidence *= 0.3

Bonuses:
  all_observers_converge: confidence += 0.1
  contradictions_resolved: confidence += 0.15
  consistent_across_time: confidence += 0.05
```

---

## VII. SYSTEM-WIDE ENFORCEMENT

This constitution governs:
- **Recovery Engine** (`backend/runtime/convergence.py`)
- **Sub-Agent Orchestrator** (`backend/agents/`)
- **CI Pipelines** (`.github/workflows/`)
- **Truth Graph** (`backend/runtime/truth_graph.py`)
- **Health System** (`backend/health/`, `backend/routes/health_v2_routes.py`)
- **Operator Plane** (`docs/operator-control-plane.md`)
- **Design Audit** (`packages/ui/design-audit.py`)
- **Auto-Fix Engine** (`packages/ui/violation_lineage.py`)

No component is exempt. Local truth is forbidden. Method drift is an incident.



## VI. DEPLOYMENT CONFIDENCE (E4.5)

A deployment is a mutation. Per §I.2, every mutation requires re-observation.
A deployment is NOT a point-in-time event — it is a continuously revalidated operational state.

```
DEPLOYED
  → STABILIZING (≥3s)
  → RE-OBSERVED (all observers)
  → CANONICAL VERIFIED (systemctl/docker ps)
  → TEMPORALLY VALIDATED (confidence fresh)
  → CONVERGED (no contradictions)
```

### Deployment Confidence Model

```
deployment_confidence(t) = confidence_0 × decay(t) + convergence_score

Where:
  decay(t) = 0.95 ^ (t_hours)

At t=0:    confidence = 1.0 (fresh deploy)
At t=1h:   confidence *= 0.95
At t=6h:   confidence *= 0.70
At t=24h:  confidence *= 0.30
At t=48h:  confidence → stale (must re-validate)

Penalties:
  dependency_contradiction: confidence *= 0.6
  observer_divergence: confidence *= 0.7
  runtime_degradation: confidence *= 0.5
  no_reobservation >4h: confidence *= 0.4

Bonuses:
  all_observers_converge: confidence += 0.1
  dependency_health_consistent: confidence += 0.05
  temporal_freshness <1h: confidence += 0.05
```

### Deployment Illusions

| Illusion | Reality | Detection |
|----------|---------|-----------|
| "Deploy succeeded" | Runtime degraded | Re-observe after deploy |
| "CI green" | Observer contradiction | Multi-observer check |
| "Last known healthy" | 4h stale truth | Temporal decay |
| "All services up" | Dependency drifted | Truth Graph validation |
| "Vercel deployed" | DNS not propagated | External observer probe |

### Prohibited Deployment Patterns

```
❌ "latest deployment successful" WITHOUT:
    - runtime convergence validation
    - dependency convergence check
    - canonical source verification
    - temporal freshness <1h
    - contradiction count = 0

❌ Deploy-then-forget:
    - No post-deploy health check
    - No re-observation window
    - No confidence tracking over time

❌ CI/CD success == deployment success:
    - CI exit code is EXECUTION layer, not CANONICAL
    - A green pipeline does not mean the system converged
```
