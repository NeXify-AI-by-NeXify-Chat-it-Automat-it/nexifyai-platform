# NeXify AI Systemmaster Runtime

Migrated from Anton CLI/Cloud session to local, persistent, host-native runtime.

## Architecture
- /systemmaster/ — root directory
- /venv/ — isolated Python runtime
- 12 systemd services (nexify-*)
- Event-driven architecture via event bus
- Governance + Recovery + Watchdog + Self-Healing

## Service Chain
eventbus → planner → governance → recovery → watchdog → mcp → memory → orchestrator → workers → systemmaster

## Key Env
NEXIFY_AUTONOMY_MODE=YOLO_GOVERNED
NEXIFY_ASSUME_APPROVAL=true
NEXIFY_DAEMON_MODE=true
NEXIFY_SELF_HEALING=true
NEXIFY_RECOVERY_ENABLED=true
NEXIFY_POLICY_GUARDED=true

## Recovery
If deadlock / freeze / crash / leak → watchdog detects → incident published → recovery daemon auto-restarts service → escalates after 3 retries.

## No Cloud Dependency
MindsDB Cloud optional for model access only. Runtime state, planner, governance, event loops, all local.
