// NeXifyAI Admin — Agent Status Distribution (Donut Chart)
// Shows agent status as a donut with legend

import React from 'react';
import { VisSingleContainer, VisDonut, VisBulletLegend } from '@unovis/react';

const STATUS_COLORS = {
  active: '#10b981',
  idle: '#f59e0b',
  error: '#ef4444',
  offline: '#6b7b8d',
  running: '#3b82f6',
  paused: '#8b5cf6',
};

export default function AgentDonut({ agents = [], height = 240 }) {
  if (!agents || agents.length === 0) {
    return (
      <div className="ac-chart-empty">
        <span className="material-symbols-outlined" style={{ fontSize: 32 }}>donut_small</span>
        <span>No agent data</span>
      </div>
    );
  }

  // Aggregate by status
  const counts = {};
  agents.forEach((a) => {
    const s = (a.status || 'unknown').toLowerCase();
    counts[s] = (counts[s] || 0) + 1;
  });

  const data = Object.entries(counts).map(([status, count]) => ({
    name: status.charAt(0).toUpperCase() + status.slice(1),
    value: count,
    color: STATUS_COLORS[status] || '#6b7b8d',
  }));

  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <div className="ac-chart-card">
      <div className="ac-chart-header">
        <span className="material-symbols-outlined">donut_small</span>
        <span>Agents</span>
        <span className="ac-chart-sub">{total} total</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, height }}>
        <div style={{ width: '60%', height: '100%' }}>
          <VisSingleContainer data={data} height={height - 20}>
            <VisDonut
              value={(d) => d.value}
              color={(d) => d.color}
              arcWidth={24}
              showBackground={true}
              backgroundArcWidth={24}
              backgroundArcColor="rgba(255,255,255,0.04)"
            />
          </VisSingleContainer>
        </div>
        <div style={{ width: '40%' }}>
          <VisBulletLegend items={data.map(d => ({ name: `${d.name} (${d.value})`, color: d.color }))} />
        </div>
      </div>
    </div>
  );
}
