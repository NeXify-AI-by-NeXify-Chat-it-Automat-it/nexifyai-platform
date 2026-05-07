/**
 * NeXifyAI — Serverless Automation: KPI Ticket
 * 
 * Trigger: health-score.py unterschreitet Threshold (< 70)
 * Action: Erstellt GitHub Issue mit Label 'kpi-alert'
 * 
 * Endpoint: POST /api/automations/kpi-ticket
 * Deployment: FastAPI Route im Backend
 * Aufruf: VPS Cron (health-score.py) → POST bei Score < 70
 */

// ══════════════════════════════════════════════════════════════
// TYPES
// ══════════════════════════════════════════════════════════════

interface HealthScoreResult {
  timestamp: string;
  score: number;
  status: 'excellent' | 'good' | 'fair' | 'degraded' | 'critical';
  components: Record<string, number>;
  weights: Record<string, number>;
}

interface GitHubIssueRequest {
  title: string;
  body: string;
  labels: string[];
  assignees?: string[];
}

// ══════════════════════════════════════════════════════════════
// THRESHOLD CONFIG
// ══════════════════════════════════════════════════════════════

const KPI_THRESHOLDS = {
  health_score: {
    critical: 40, // SEV1: sofort
    degraded: 60, // SEV2: innerhalb 24h
    fair: 75,     // SEV3: nächster Sprint
  },
};

// ══════════════════════════════════════════════════════════════
// WORKFLOW LOGIC
// ══════════════════════════════════════════════════════════════

async function kpiTicketWorkflow(health: HealthScoreResult): Promise<{issue_url?: string; skipped: boolean}> {
  if (health.score >= 70) {
    return { skipped: true };
  }

  const severity = health.score < KPI_THRESHOLDS.health_score.critical ? 'SEV1' :
                   health.score < KPI_THRESHOLDS.health_score.degraded ? 'SEV2' : 'SEV3';

  // Prüfen ob bereits ein offenes Issue existiert (Deduplizierung)
  const existingIssue = await findOpenIssue('kpi-alert');
  if (existingIssue) {
    // Issue kommentieren mit aktuellem Score
    await commentOnIssue(existingIssue.number, generateComment(health));
    return { issue_url: existingIssue.html_url, skipped: false };
  }

  // Neues Issue erstellen
  const issue: GitHubIssueRequest = {
    title: `[${severity}] Health-Score: ${health.score}% — ${health.status.toUpperCase()}`,
    body: generateIssueBody(health, severity),
    labels: ['kpi-alert', severity.toLowerCase(), 'auto-generated'],
  };

  const created = await createGitHubIssue(issue);
  return { issue_url: created.html_url, skipped: false };
}

function generateIssueBody(health: HealthScoreResult, severity: string): string {
  const lowest = Object.entries(health.components)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 3)
    .map(([k, v]) => `- **${k}**: ${v}%`)
    .join('\n');

  return `## ${severity} — Health Score Alert

**Score:** ${health.score}%
**Status:** ${health.status}
**Zeitpunkt:** ${health.timestamp}

### Schwächste Komponenten
${lowest}

### Erforderliche Aktionen
1. [ ] Root Cause der schwachen Komponenten identifizieren
2. [ ] Fix-Priorität: ${severity === 'SEV1' ? 'SOFORT' : severity === 'SEV2' ? 'Innerhalb 24h' : 'Nächster Sprint'}
3. [ ] Nach Fix: Health-Score neu berechnen

---
🤖 Auto-generiert von NeXifyAI KPI Automation`;
}

function generateComment(health: HealthScoreResult): string {
  return `📊 **Update:** Health-Score jetzt bei **${health.score}%** (${health.status})\nZeitpunkt: ${health.timestamp}`;
}

// ══════════════════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════════════════

async function createGitHubIssue(issue: GitHubIssueRequest): Promise<any> {
  // POST https://api.github.com/repos/nexifyai-dev/nexifyai-website-sicherheitskopie/issues
  throw new Error('Backend-implementiert');
}

async function findOpenIssue(label: string): Promise<any> {
  // GET https://api.github.com/repos/nexifyai-dev/nexifyai-website-sicherheitskopie/issues?labels=kpi-alert&state=open
  throw new Error('Backend-implementiert');
}

async function commentOnIssue(issueNumber: number, body: string): Promise<void> {
  // POST https://api.github.com/repos/nexifyai-dev/nexifyai-website-sicherheitskopie/issues/{number}/comments
  throw new Error('Backend-implementiert');
}

export { kpiTicketWorkflow, KPI_THRESHOLDS };
export type { HealthScoreResult };
