/**
 * NeXifyAI Telemetry — System-internal event tracking.
 * 
 * Tracks CI/CD events, deployment status, cron results, health changes.
 * Unlike analytics (user-facing), telemetry is system-internal.
 * 
 * Events tracked:
 * - deploy_started, deploy_completed, deploy_failed
 * - cron_executed, cron_failed
 * - health_score_changed
 * - security_scan_completed
 * - incident_created, incident_resolved
 * 
 * @package @nexifyai/telemetry
 * @version 1.0.0
 */

import { z } from 'zod';

// ══════════════════════════════════════════════
// TELEMETRY EVENT SCHEMAS
// ══════════════════════════════════════════════

export const DeployEvent = z.object({
  event: z.enum(['deploy_started', 'deploy_completed', 'deploy_failed']),
  service: z.string(),
  environment: z.enum(['production', 'preview', 'development']),
  commit_sha: z.string().optional(),
  duration_ms: z.number().optional(),
  error: z.string().optional(),
  timestamp: z.number(),
});

export const CronEvent = z.object({
  event: z.enum(['cron_executed', 'cron_failed']),
  job_name: z.string(),
  duration_ms: z.number(),
  exit_code: z.number(),
  error: z.string().optional(),
  timestamp: z.number(),
});

export const HealthEvent = z.object({
  event: z.literal('health_score_changed'),
  previous_score: z.number().min(0).max(100),
  current_score: z.number().min(0).max(100),
  component: z.string().optional(),
  reason: z.string().optional(),
  timestamp: z.number(),
});

export const SecurityEvent = z.object({
  event: z.enum(['security_scan_completed', 'vulnerability_found']),
  scan_type: z.enum(['gitleaks', 'trivy', 'npm-audit', 'safety']),
  findings_count: z.number(),
  severity: z.enum(['none', 'low', 'medium', 'high', 'critical']),
  timestamp: z.number(),
});

export const IncidentEvent = z.object({
  event: z.enum(['incident_created', 'incident_resolved']),
  incident_id: z.string(),
  severity: z.enum(['SEV0', 'SEV1', 'SEV2', 'SEV3', 'SEV4']),
  title: z.string(),
  duration_minutes: z.number().optional(),
  timestamp: z.number(),
});

export const TaskEvent = z.object({
  event: z.enum(['task_created', 'task_started', 'task_completed', 'task_failed']),
  task_id: z.string(),
  source: z.string(),
  duration_ms: z.number().optional(),
  error: z.string().optional(),
  timestamp: z.number(),
});

// ══════════════════════════════════════════════
// UNION TYPE
// ══════════════════════════════════════════════

export const AnyTelemetryEvent = z.discriminatedUnion('event', [
  DeployEvent, CronEvent, HealthEvent, SecurityEvent, IncidentEvent, TaskEvent,
]);

export type AnyTelemetryEventType = z.infer<typeof AnyTelemetryEvent>;

// ══════════════════════════════════════════════
// TELEMETRY CLIENT
// ══════════════════════════════════════════════

const TELEMETRY_ENDPOINT = process.env.TELEMETRY_URL || 'http://localhost:8001/api/telemetry/event';

export async function sendTelemetry(event: AnyTelemetryEventType): Promise<boolean> {
  try {
    const response = await fetch(TELEMETRY_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event),
    });
    return response.ok;
  } catch {
    return false;
  }
}

// Convenience functions
export function trackDeploy(status: 'started' | 'completed' | 'failed', service: string, details?: Partial<z.infer<typeof DeployEvent>>) {
  return sendTelemetry(DeployEvent.parse({
    event: `deploy_${status}`,
    service,
    environment: 'production',
    timestamp: Date.now(),
    ...details,
  }));
}

export function trackCron(jobName: string, success: boolean, durationMs: number, error?: string) {
  return sendTelemetry(CronEvent.parse({
    event: success ? 'cron_executed' : 'cron_failed',
    job_name: jobName,
    duration_ms: durationMs,
    exit_code: success ? 0 : 1,
    error,
    timestamp: Date.now(),
  }));
}

export function trackHealthChange(previous: number, current: number, reason?: string) {
  return sendTelemetry(HealthEvent.parse({
    event: 'health_score_changed',
    previous_score: previous,
    current_score: current,
    reason,
    timestamp: Date.now(),
  }));
}

export function trackIncident(id: string, severity: string, title: string, created: boolean, durationMin?: number) {
  return sendTelemetry(IncidentEvent.parse({
    event: created ? 'incident_created' : 'incident_resolved',
    incident_id: id,
    severity: severity as any,
    title,
    duration_minutes: durationMin,
    timestamp: Date.now(),
  }));
}
