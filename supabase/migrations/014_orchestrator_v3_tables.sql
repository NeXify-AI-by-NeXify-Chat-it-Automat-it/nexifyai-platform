-- Migration 014: Orchestrator V3 — Team Routing, Task Graph, Rules Registry
-- NeXifyAI DOS v4.8 — AI Enterprise OS Layer
-- Required for: TeamOrchestrator (orchestrator_v3.py), TaskGraph, Quality Gates

BEGIN;

-- ═══════════════════════════════════════
-- RULES REGISTRY — Agent behavior rules
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.rules_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL DEFAULT 'general' CHECK (category IN (
        'always', 'never', 'when', 'security', 'compliance',
        'performance', 'quality', 'general'
    )),
    description TEXT,
    agent_id TEXT,
    rule_content TEXT NOT NULL,
    trigger_type TEXT DEFAULT 'always' CHECK (trigger_type IN ('always', 'never', 'when')),
    scope TEXT DEFAULT 'project' CHECK (scope IN ('global', 'project', 'agent')),
    priority INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_rules_agent ON public.rules_registry(agent_id);
CREATE INDEX IF NOT EXISTS idx_rules_category ON public.rules_registry(category);
CREATE INDEX IF NOT EXISTS idx_rules_enabled ON public.rules_registry(enabled);
CREATE INDEX IF NOT EXISTS idx_rules_priority ON public.rules_registry(priority DESC);

-- ═══════════════════════════════════════
-- TEAM REGISTRY — Capability-based agent teams
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.team_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    display_name TEXT,
    description TEXT,
    capabilities TEXT[] DEFAULT '{}',
    agent_ids TEXT[] DEFAULT '{}',
    routing_rules JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 10,
    enabled BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_teams_capabilities ON public.team_registry USING GIN (capabilities);
CREATE INDEX IF NOT EXISTS idx_teams_priority ON public.team_registry(priority DESC);
CREATE INDEX IF NOT EXISTS idx_teams_enabled ON public.team_registry(enabled);

-- ═══════════════════════════════════════
-- TASK GRAPH — Multi-step agent pipelines
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.task_graph (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    graph_type TEXT DEFAULT 'sequential' CHECK (graph_type IN ('sequential', 'parallel', 'dag', 'conditional')),
    steps JSONB NOT NULL DEFAULT '[]',
    dependencies JSONB DEFAULT '{}',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'deprecated', 'archived')),
    version INTEGER DEFAULT 1,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_task_graph_status ON public.task_graph(status);
CREATE INDEX IF NOT EXISTS idx_task_graph_type ON public.task_graph(graph_type);

-- ═══════════════════════════════════════
-- AGENT METRICS — Performance tracking
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    task_graph_id UUID REFERENCES public.task_graph(id) ON DELETE SET NULL,
    task_id TEXT,
    metric_type TEXT NOT NULL CHECK (metric_type IN (
        'latency', 'tokens', 'success_rate', 'quality_score',
        'brain_hits', 'routing_accuracy', 'gate_pass_rate'
    )),
    metric_value DOUBLE PRECISION NOT NULL,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent ON public.agent_metrics(agent_id, metric_type);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_ts ON public.agent_metrics(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_task ON public.agent_metrics(task_id);

-- ═══════════════════════════════════════
-- SEED DATA: Default teams
-- ═══════════════════════════════════════
INSERT INTO public.team_registry (name, display_name, description, capabilities, agent_ids, priority)
VALUES
    ('analysis', 'Analysis Team', 'Data analysis, research, insights', ARRAY['analyze', 'research', 'report'], ARRAY['research-expert', 'data-analyst'], 10),
    ('engineering', 'Engineering Team', 'Code, architecture, DevOps', ARRAY['code', 'build', 'deploy', 'architecture'], ARRAY['ai-engineer', 'devops-expert'], 20),
    ('creative', 'Creative Team', 'Design, content, UX', ARRAY['design', 'content', 'ux'], ARRAY['design-expert', 'content-expert'], 15),
    ('business', 'Business Team', 'Strategy, legal, finance', ARRAY['strategy', 'legal', 'finance', 'compliance'], ARRAY['legal-expert', 'strategy-expert'], 12),
    ('operations', 'Operations Team', 'Support, monitoring, maintenance', ARRAY['support', 'monitor', 'maintain'], ARRAY['support-expert', 'devops-expert'], 8)
ON CONFLICT (name) DO UPDATE SET
    capabilities = EXCLUDED.capabilities,
    agent_ids = EXCLUDED.agent_ids,
    updated_at = now();

-- ═══════════════════════════════════════
-- SEED DATA: Core rules from SOP Rulebook
-- ═══════════════════════════════════════
INSERT INTO public.rules_registry (name, category, description, rule_content, trigger_type, scope, priority)
VALUES
    ('brain-first-execution', 'always', 'Every agent must query Brain before acting', 'Before ANY task: query Brain (Qdrant nexifyai_brain) for relevant prior knowledge, learned errors, known patterns, and existing skills. Never act without checking if Brain already knows the solution.', 'always', 'global', 100),
    ('brain-post-execution', 'always', 'Every agent must report to Brain after acting', 'After ANY task: report observations, decisions, errors, and learnings back to Brain. Store facts in nexifyai_brain, session observations in nexifyai_memories.', 'always', 'global', 100),
    ('quality-gate-pass-required', 'always', 'All agent outputs must pass quality gates', 'Before returning any result, validate output through quality gates (syntax, content, security). Failed gates must trigger retry or escalation.', 'always', 'global', 90),
    ('no-data-vault-raw-access', 'never', 'Never read data_vault files directly', 'Never read ~/.anton/data_vault files directly. Use DS_<ENGINE>__<FIELD> environment variables. Flat variables are temporary and should not be used in production code.', 'never', 'global', 95),
    ('restore-first-on-corruption', 'always', 'Restore corrupted files from mirror before patching', 'When a critical file is corrupted by inline edits, RESTORE from mirror first, then apply MINIMAL additive changes. Never continue patching a corrupted file.', 'always', 'global', 90),
    ('fastapi-dependency-order', 'when', 'FastAPI Depends runs BEFORE function body', 'Bei FastAPI Depends wird die Dependency VOR dem Funktionskörper ausgeführt. Ein manueller Auth-Check im Funktionskörper wird NIE erreicht wenn Depends 401 wirft.', 'when', 'global', 80)
ON CONFLICT (name) DO NOTHING;

-- ═══════════════════════════════════════
-- SEED DATA: Default task graph templates
-- ═══════════════════════════════════════
INSERT INTO public.task_graph (name, description, graph_type, steps, status)
VALUES
    ('code-review-pipeline', 'Code generation → review → fix', 'sequential', 
     '[{"step": 1, "agent": "ai-engineer", "action": "generate", "description": "Generate initial code"}, {"step": 2, "agent": "review-expert", "action": "review", "description": "Review code quality"}, {"step": 3, "agent": "ai-engineer", "action": "fix", "description": "Apply review fixes"}]',
     'active'),
    ('content-publish-pipeline', 'Content creation → review → publish', 'sequential',
     '[{"step": 1, "agent": "content-expert", "action": "draft", "description": "Draft content"}, {"step": 2, "agent": "review-expert", "action": "review", "description": "Editorial review"}, {"step": 3, "agent": "content-expert", "action": "publish", "description": "Publish final version"}]',
     'active'),
    ('analysis-report-pipeline', 'Data analysis → visualization → summary', 'sequential',
     '[{"step": 1, "agent": "data-analyst", "action": "analyze", "description": "Analyze data"}, {"step": 2, "agent": "design-expert", "action": "visualize", "description": "Create visualization"}, {"step": 3, "agent": "research-expert", "action": "summarize", "description": "Write executive summary"}]',
     'active'),
    ('security-audit-pipeline', 'Audit → fix → verify', 'sequential',
     '[{"step": 1, "agent": "security-expert", "action": "audit", "description": "Security audit"}, {"step": 2, "agent": "ai-engineer", "action": "fix", "description": "Fix vulnerabilities"}, {"step": 3, "agent": "security-expert", "action": "verify", "description": "Verify fixes"}]',
     'active'),
    ('deploy-pipeline', 'Build → test → deploy → monitor', 'sequential',
     '[{"step": 1, "agent": "ai-engineer", "action": "build", "description": "Build artifacts"}, {"step": 2, "agent": "qa-expert", "action": "test", "description": "Run tests"}, {"step": 3, "agent": "devops-expert", "action": "deploy", "description": "Deploy to production"}, {"step": 4, "agent": "devops-expert", "action": "monitor", "description": "Monitor deployment"}]',
     'active')
ON CONFLICT (name) DO NOTHING;

COMMIT;
