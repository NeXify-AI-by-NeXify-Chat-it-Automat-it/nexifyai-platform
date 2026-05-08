import React from 'react';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

function HealthCircle({ score }) {
  const pct = score?.health_score || score?.score || 0;
  let color = '#ef4444'; // red
  if (pct >= 90) color = '#10b981'; // green
  else if (pct >= 70) color = '#f59e0b'; // yellow

  const circumference = 2 * Math.PI * 36;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="ac-health-circle">
      <svg width="88" height="88" viewBox="0 0 88 88">
        <circle cx="44" cy="44" r="36" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
        <circle
          cx="44" cy="44" r="36"
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 44 44)"
          style={{ transition: 'stroke-dashoffset 1s ease, stroke 0.5s ease' }}
        />
      </svg>
      <div className="ac-health-value" style={{ color }}>
        {Math.round(pct)}%
      </div>
    </div>
  );
}

function StatBadge({ icon, label, value, color = '#6b7b8d' }) {
  return (
    <div className="ac-stat-badge">
      <I n={icon} s={16} />
      <span className="ac-stat-label">{label}</span>
      <span className="ac-stat-value" style={{ color }}>{value ?? '—'}</span>
    </div>
  );
}

function WorkflowBadge({ name, status, url }) {
  const s = status?.toLowerCase?.() || '';
  let cls = 'ac-badge-gray';
  let icon = 'help';
  if (s === 'passing' || s === 'success' || s === 'completed') { cls = 'ac-badge-green'; icon = 'check_circle'; }
  else if (s === 'failing' || s === 'failure' || s === 'failed') { cls = 'ac-badge-red'; icon = 'error'; }
  else if (s === 'in_progress' || s === 'running') { cls = 'ac-badge-yellow'; icon = 'sync'; }

  const Comp = url ? 'a' : 'span';
  return (
    <Comp
      className={`ac-workflow-badge ${cls}`}
      href={url || undefined}
      target={url ? '_blank' : undefined}
      rel={url ? 'noopener noreferrer' : undefined}
    >
      <I n={icon} s={14} />
      <span>{name}</span>
    </Comp>
  );
}

export default function LiveDashboard({ health, stats, agents, incidents, workflows }) {
  const score = health?.health_score || health?.score || 0;
  const openTasks = stats?.open_tasks || stats?.openTasks || 0;
  const todayIncidents = Array.isArray(incidents) ? incidents.length : (incidents?.total || 0);
  const activeAgents = Array.isArray(agents) ? agents.filter(a => a.status === 'active' || a.status === 'running').length : (agents?.active || 0);

  const workflowList = workflows && typeof workflows === 'object' && Object.keys(workflows).length > 0
    ? Object.entries(workflows)
    : [
        { name: 'Security Scan', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/security-scan.yml' },
        { name: 'CI Quality Gates', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/quality-gates.yml' },
        { name: 'Tests', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/tests.yml' },
        { name: 'Vercel Deploy', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/deploy.yml' },
      ];

  return (
    <div className="ac-dashboard">
      <div className="ac-dash-section">
        <HealthCircle score={score} />
        <div className="ac-dash-stats">
          <StatBadge icon="assignment" label="Offene Tasks" value={openTasks} color="#f59e0b" />
          <StatBadge icon="warning" label="Heutige Incidents" value={todayIncidents} color={todayIncidents > 0 ? '#ef4444' : '#10b981'} />
          <StatBadge icon="smart_toy" label="Aktive Agenten" value={activeAgents} color="#8b5cf6" />
        </div>
      </div>
      <div className="ac-dash-workflows">
        {Array.isArray(workflowList) && workflowList.map((w, i) => {
          const name = typeof w === 'string' ? w : (w[0] || w.name || w);
          const status = typeof w === 'object' && !Array.isArray(w) ? (w[1] || w.status) : (w.status || w);
          const url = w.url || w[2] || undefined;
          return <WorkflowBadge key={i} name={name} status={status} url={url} />;
        })}
      </div>
    </div>
  );
}
