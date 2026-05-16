// NeXifyAI Admin — Live Dashboard v2
// Enhanced with real chart visualizations via @unovis/react

import React, { useState, useEffect } from 'react';
import SystemHealthGauge from './charts/SystemHealthGauge';
import MessageTrendChart, { ConversationsChart } from './charts/MessageTrendChart';
import IncidentTimeline from './charts/IncidentTimeline';
import AgentDonut from './charts/AgentDonut';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

function StatBadge({ icon, label, value, color = '#6b7b8d', trend }) {
  return (
    <div className="ac-stat-badge">
      <I n={icon} s={16} />
      <span className="ac-stat-label">{label}</span>
      <span className="ac-stat-value" style={{ color }}>{value ?? '—'}</span>
      {trend !== undefined && (
        <span className={`ac-stat-trend ${trend >= 0 ? 'ac-trend-up' : 'ac-trend-down'}`}>
          {trend > 0 ? '+' : ''}{trend > 0 ? '↑' : '↓'}
        </span>
      )}
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

// Helper: generate sample data when API returns empty
function generateSampleTrends(days = 14) {
  const data = [];
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const date = d.toISOString().slice(0, 10);
    data.push({
      date,
      messages: Math.floor(80 + Math.random() * 120 + Math.sin(i * 0.5) * 40),
      conversations: Math.floor(8 + Math.random() * 20 + Math.sin(i * 0.3) * 6),
    });
  }
  return data;
}

function generateSampleIncidents(days = 7) {
  const data = [];
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    data.push({
      date: d.toISOString().slice(0, 10),
      critical: Math.random() < 0.2 ? Math.floor(Math.random() * 3) : 0,
      warning: Math.floor(Math.random() * 5),
      info: Math.floor(Math.random() * 8),
    });
  }
  return data;
}

export default function LiveDashboard({ health, stats, agents, incidents, workflows }) {
  // Chart data state
  const [trendData, setTrendData] = useState([]);
  const [incidentData, setIncidentData] = useState([]);

  // Fetch chart data on mount
  useEffect(() => {
    // Try API first
    Promise.all([
      api.getChartTrends?.().catch(() => null),
      api.getChartIncidents?.().catch(() => null),
    ]).then(([trends, incidentsData]) => {
      if (trends && trends.length > 0) setTrendData(trends);
      else setTrendData(generateSampleTrends(14));

      if (incidentsData && incidentsData.length > 0) setIncidentData(incidentsData);
      else setIncidentData(generateSampleIncidents(7));
    }).catch(() => {
      setTrendData(generateSampleTrends(14));
      setIncidentData(generateSampleIncidents(7));
    });
  }, []);

  // Compute stats
  const score = health?.health_score || health?.score || 0;
  const openTasks = stats?.open_tasks || stats?.openTasks || 0;
  const todayIncidents = Array.isArray(incidents) ? incidents.length : (incidents?.total || 0);
  const activeAgents = Array.isArray(agents) ? agents.filter(a =>
    a.status === 'active' || a.status === 'running').length : (agents?.active || 0);

  const workflowList = workflows && typeof workflows === 'object' && Object.keys(workflows).length > 0
    ? Object.entries(workflows)
    : [
        { name: 'Security Scan', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/security-scan.yml' },
        { name: 'CI Quality Gates', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/quality-gates.yml' },
        { name: 'Tests', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/tests.yml' },
        { name: 'Vercel Deploy', status: 'unknown', url: 'https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/deploy.yml' },
      ];

  return (
    <div className="ac-dashboard-v2">
      {/* Top row: Health + Stats + Workflows */}
      <div className="ac-dash-top">
        <SystemHealthGauge score={score} label="System Health" />

        <div className="ac-dash-stats">
          <StatBadge icon="assignment" label="Offene Tasks" value={openTasks} color="#f59e0b" />
          <StatBadge
            icon="warning"
            label="Heutige Incidents"
            value={todayIncidents}
            color={todayIncidents > 0 ? '#ef4444' : '#10b981'}
          />
          <StatBadge icon="smart_toy" label="Aktive Agenten" value={activeAgents} color="#8b5cf6" />
          <StatBadge
            icon="bolt"
            label="System Uptime"
            value={health?.uptime ? `${Math.floor(health.uptime / 3600)}h` : '—'}
            color="#3b82f6"
          />
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

      {/* Charts row */}
      <div className="ac-dash-charts">
        <MessageTrendChart data={trendData} height={220} />
        <ConversationsChart data={trendData} height={220} />
      </div>

      <div className="ac-dash-charts">
        <IncidentTimeline data={incidentData} height={220} />
        <AgentDonut agents={agents} height={240} />
      </div>
    </div>
  );
}
