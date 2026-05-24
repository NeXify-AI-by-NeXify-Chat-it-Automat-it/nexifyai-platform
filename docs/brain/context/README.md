# Brain: Context

**Purpose:** Runtime context snapshots — agent state, conversation context, session bindings.

**Categories mapped from brain.db:** context, heartbeat, session

**Write Policy:** ATTRIBUTED — must reference session_id and agent_id.
**Read Policy:** AGENT — agent's own context only.

**Usage:**
- Save agent runtime state
- Cross-session context recovery
- Conversation thread binding

**brain_cli.py commands:**
```
brain_cli.py store --category context --content '{"session_id":"...","agent":"..."}'
```

**Governance:** SessionGovernor.validate() before read.
