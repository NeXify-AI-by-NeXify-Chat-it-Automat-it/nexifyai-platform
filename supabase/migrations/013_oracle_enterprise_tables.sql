-- Migration 013: Oracle Enterprise Knowledge Tables (AIC-49 Phase 2)
-- NeXifyAI DOS v4.8 — Enterprise Blueprint Consolidation
-- Governed Enterprise Truth Schema

BEGIN;

-- ═══════════════════════════════════════
-- ORACLE DOCUMENTS — Primary knowledge container
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT UNIQUE,
    title TEXT NOT NULL,
    content TEXT,
    content_hash TEXT NOT NULL,
    source TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN (
        'adr', 'policy', 'directive', 'chat', 'runtime_log',
        'recovery_log', 'ci_log', 'agent_config', 'playbook',
        'incident_report', 'security_audit', 'knowledge_entry',
        'governance_rule', 'architecture_note', 'prompt', 'code'
    )),
    language TEXT DEFAULT 'de',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deprecated', 'draft')),
    version INTEGER NOT NULL DEFAULT 1,
    classification JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    governance_tags TEXT[] DEFAULT '{}',
    chunk_count INTEGER DEFAULT 0,
    embedding_count INTEGER DEFAULT 0,
    last_ingested_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_docs_source ON public.oracle_documents(source, source_type);
CREATE INDEX idx_oracle_docs_status ON public.oracle_documents(status);
CREATE INDEX idx_oracle_docs_hash ON public.oracle_documents(content_hash);
CREATE INDEX idx_oracle_docs_governance ON public.oracle_documents USING GIN (governance_tags);

-- ═══════════════════════════════════════
-- ORACLE CHUNKS — Document fragments for embedding
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES public.oracle_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    token_count INTEGER,
    chunk_strategy TEXT DEFAULT 'semantic',
    embedding_id UUID,
    embedding_model TEXT,
    embedding_dim INTEGER,
    embedding_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX idx_oracle_chunks_doc ON public.oracle_chunks(document_id);
CREATE INDEX idx_oracle_chunks_embed ON public.oracle_chunks(embedding_id);
CREATE INDEX idx_oracle_chunks_hash ON public.oracle_chunks(content_hash);

-- ═══════════════════════════════════════
-- ORACLE EMBEDDINGS — Vector metadata (actual vectors in Qdrant)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES public.oracle_chunks(id) ON DELETE CASCADE,
    qdrant_point_id TEXT UNIQUE,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    embedding_version TEXT NOT NULL,
    quality_score REAL CHECK (quality_score >= 0 AND quality_score <= 1),
    validated BOOLEAN DEFAULT false,
    validation_errors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_embs_chunk ON public.oracle_embeddings(chunk_id);
CREATE INDEX idx_oracle_embs_qdrant ON public.oracle_embeddings(qdrant_point_id);
CREATE INDEX idx_oracle_embs_validated ON public.oracle_embeddings(validated) WHERE NOT validated;

-- ═══════════════════════════════════════
-- ORACLE EVENTS — Enterprise event ledger (Kausalität)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    event_source TEXT NOT NULL,
    session_id TEXT,
    agent_id TEXT,
    task_id TEXT,
    payload JSONB NOT NULL DEFAULT '{}',
    previous_event_id UUID REFERENCES public.oracle_events(id),
    causality_chain TEXT[] DEFAULT '{}',
    governance_state TEXT DEFAULT 'recorded',
    audit_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_events_type ON public.oracle_events(event_type, created_at DESC);
CREATE INDEX idx_oracle_events_session ON public.oracle_events(session_id);
CREATE INDEX idx_oracle_events_agent ON public.oracle_events(agent_id);
CREATE INDEX idx_oracle_events_causality ON public.oracle_events USING GIN (causality_chain);

-- ═══════════════════════════════════════
-- ORACLE TASKS — Governed task ledger
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'todo' CHECK (status IN (
        'todo', 'in_progress', 'done', 'cancelled', 'blocked', 'quarantined'
    )),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    risk_level TEXT DEFAULT 'low' CHECK (risk_level IN ('critical', 'high', 'medium', 'low')),
    assignee_agent_id TEXT,
    phase TEXT,
    session_id TEXT,
    recovery_required BOOLEAN DEFAULT false,
    audit_required BOOLEAN DEFAULT true,
    brain_sync_required BOOLEAN DEFAULT true,
    oracle_sync_required BOOLEAN DEFAULT true,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    governance_lock BOOLEAN DEFAULT false,
    dependencies UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_oracle_tasks_status ON public.oracle_tasks(status, priority);
CREATE INDEX idx_oracle_tasks_agent ON public.oracle_tasks(assignee_agent_id);
CREATE INDEX idx_oracle_tasks_phase ON public.oracle_tasks(phase);

-- ═══════════════════════════════════════
-- ORACLE AGENTS — Governed agent registry
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'quarantined', 'recovering')),
    runtime_state JSONB DEFAULT '{}',
    last_heartbeat TIMESTAMPTZ,
    heartbeat_interval_seconds INTEGER DEFAULT 30,
    current_task_id TEXT,
    session_id TEXT,
    capabilities TEXT[] DEFAULT '{}',
    governance_rules JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_agents_status ON public.oracle_agents(status);
CREATE INDEX idx_oracle_agents_heartbeat ON public.oracle_agents(last_heartbeat);

-- ═══════════════════════════════════════
-- ORACLE SESSIONS — Governed session registry
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    agent_id TEXT,
    channel TEXT NOT NULL CHECK (channel IN (
        'hermes', 'paperclip', 'cli', 'telegram', 'webchat',
        'github', 'slack', 'mail', 'admin-chat', 'vercel', 'mcp'
    )),
    runtime_state JSONB DEFAULT '{}',
    governance_lock BOOLEAN DEFAULT false,
    retrieval_state JSONB DEFAULT '{}',
    audit_state JSONB DEFAULT '{}',
    heartbeat_at TIMESTAMPTZ,
    stall_detected BOOLEAN DEFAULT false,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ
);

CREATE INDEX idx_oracle_sessions_state ON public.oracle_sessions(runtime_state);
CREATE INDEX idx_oracle_sessions_channel ON public.oracle_sessions(channel);
CREATE INDEX idx_oracle_sessions_stall ON public.oracle_sessions(stall_detected) WHERE stall_detected = true;

-- ═══════════════════════════════════════
-- ORACLE INCIDENTS — Incident management
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    title TEXT NOT NULL,
    description TEXT,
    source TEXT,
    affected_components TEXT[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'mitigating', 'resolved', 'closed')),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    root_cause TEXT,
    resolution TEXT,
    related_events UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_incidents_status ON public.oracle_incidents(status, severity);
CREATE INDEX idx_oracle_incidents_detected ON public.oracle_incidents(detected_at DESC);

-- ═══════════════════════════════════════
-- ORACLE POLICIES — Governed policy registry
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK (category IN (
        'security', 'governance', 'runtime', 'data', 'access',
        'compliance', 'recovery', 'deployment', 'development'
    )),
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'draft')),
    standard_refs TEXT[] DEFAULT '{}',
    enforced BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_policies_cat ON public.oracle_policies(category, status);

-- ═══════════════════════════════════════
-- ORACLE ADRs — Architecture Decision Records
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_adrs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    adr_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed' CHECK (status IN (
        'proposed', 'accepted', 'deprecated', 'superseded'
    )),
    context TEXT,
    decision TEXT NOT NULL,
    consequences TEXT,
    superseded_by TEXT,
    document_id UUID REFERENCES public.oracle_documents(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_adrs_status ON public.oracle_adrs(status);

-- ═══════════════════════════════════════
-- ORACLE AUDIT — Immutable audit trail
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    agent_id TEXT,
    session_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    before_state JSONB,
    after_state JSONB,
    audit_hash TEXT NOT NULL,
    governance_validated BOOLEAN DEFAULT false,
    reconciliation_status TEXT DEFAULT 'pending' CHECK (reconciliation_status IN ('pending', 'reconciled', 'conflict', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_audit_type ON public.oracle_audit(event_type, created_at DESC);
CREATE INDEX idx_oracle_audit_session ON public.oracle_audit(session_id);
CREATE INDEX idx_oracle_audit_entity ON public.oracle_audit(entity_type, entity_id);
CREATE INDEX idx_oracle_audit_recon ON public.oracle_audit(reconciliation_status) WHERE reconciliation_status != 'reconciled';

-- ═══════════════════════════════════════
-- ORACLE RECONCILIATION — Conflict tracking
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    source_a TEXT NOT NULL,
    source_b TEXT NOT NULL,
    conflict_type TEXT NOT NULL CHECK (conflict_type IN ('duplicate', 'divergent', 'stale', 'missing', 'invalid')),
    resolution TEXT DEFAULT 'pending' CHECK (resolution IN ('pending', 'merged', 'source_a_wins', 'source_b_wins', 'manual', 'failed')),
    resolved_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_oracle_recon_status ON public.oracle_reconciliation(resolution);
CREATE INDEX idx_oracle_recon_entity ON public.oracle_reconciliation(entity_type, entity_id);

-- ═══════════════════════════════════════
-- ORACLE RUNTIME — Runtime state tracking
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_runtime (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component TEXT NOT NULL,
    instance_id TEXT,
    state JSONB NOT NULL DEFAULT '{}',
    health TEXT DEFAULT 'unknown' CHECK (health IN ('healthy', 'degraded', 'stalled', 'down', 'recovering', 'quarantined')),
    last_heartbeat TIMESTAMPTZ,
    stall_detected BOOLEAN DEFAULT false,
    circuit_breaker_open BOOLEAN DEFAULT false,
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_runtime_component ON public.oracle_runtime(component, health);
CREATE INDEX idx_oracle_runtime_stall ON public.oracle_runtime(stall_detected) WHERE stall_detected = true;

-- ═══════════════════════════════════════
-- ORACLE KNOWLEDGE SOURCES — Source registry
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    location TEXT,
    access_method TEXT,
    last_scanned TIMESTAMPTZ,
    document_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error', 'archived')),
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ═══════════════════════════════════════
-- ORACLE IDENTITIES — Cross-channel identity mapping
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_id TEXT NOT NULL UNIQUE,
    channel TEXT NOT NULL,
    channel_user_id TEXT NOT NULL,
    display_name TEXT,
    metadata JSONB DEFAULT '{}',
    first_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(channel, channel_user_id)
);

CREATE INDEX idx_oracle_identities_canon ON public.oracle_identities(canonical_id);
CREATE INDEX idx_oracle_identities_channel ON public.oracle_identities(channel, channel_user_id);

-- ═══════════════════════════════════════
-- ORACLE IDENTITY LINKS — Link identities across channels
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_identity_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_id TEXT NOT NULL REFERENCES public.oracle_identities(canonical_id),
    source_identity_id UUID NOT NULL REFERENCES public.oracle_identities(id),
    target_identity_id UUID NOT NULL REFERENCES public.oracle_identities(id),
    link_confidence REAL DEFAULT 1.0 CHECK (link_confidence >= 0 AND link_confidence <= 1),
    link_method TEXT DEFAULT 'auto',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(canonical_id, target_identity_id)
);

-- ═══════════════════════════════════════
-- ORACLE RETRIEVAL — Retrieval quality tracking
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_retrieval (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT,
    query_hash TEXT NOT NULL,
    query_text TEXT NOT NULL,
    results_count INTEGER,
    top_scores REAL[] DEFAULT '{}',
    latency_ms INTEGER,
    retrieval_source TEXT,
    feedback_score REAL CHECK (feedback_score IS NULL OR (feedback_score >= 0 AND feedback_score <= 1)),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_retrieval_session ON public.oracle_retrieval(session_id);
CREATE INDEX idx_oracle_retrieval_hash ON public.oracle_retrieval(query_hash);

-- ═══════════════════════════════════════
-- ORACLE DEPENDENCIES — Task/entity dependency graph
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    dependency_type TEXT DEFAULT 'requires' CHECK (dependency_type IN ('requires', 'blocks', 'relates_to', 'duplicates', 'supersedes')),
    strength REAL DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_oracle_deps_source ON public.oracle_dependencies(source_type, source_id);
CREATE INDEX idx_oracle_deps_target ON public.oracle_dependencies(target_type, target_id);

-- ═══════════════════════════════════════
-- ORACLE SECURITY EVENTS — Security audit log
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info' CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    source_ip TEXT,
    agent_id TEXT,
    session_id TEXT,
    description TEXT,
    payload JSONB DEFAULT '{}',
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved BOOLEAN DEFAULT false
);

CREATE INDEX idx_oracle_sec_events_severity ON public.oracle_security_events(severity, detected_at DESC);

-- ═══════════════════════════════════════
-- ORACLE RECOVERY — Recovery event log
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.oracle_recovery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES public.oracle_incidents(id),
    recovery_type TEXT NOT NULL CHECK (recovery_type IN (
        'auto', 'manual', 'circuit_breaker', 'rollback', 'restart', 'quarantine'
    )),
    component TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'initiated' CHECK (status IN ('initiated', 'in_progress', 'completed', 'failed', 'rolled_back')),
    steps JSONB DEFAULT '[]',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    success BOOLEAN
);

CREATE INDEX idx_oracle_recovery_component ON public.oracle_recovery(component, status);

-- ═══════════════════════════════════════
-- RLS: Enable on all oracle tables
-- ═══════════════════════════════════════
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public' AND tablename LIKE 'oracle_%'
    LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);
        EXECUTE format('CREATE POLICY %I_all ON public.%I FOR ALL TO authenticated USING (true)', tbl, tbl);
    END LOOP;
END $$;

COMMIT;
