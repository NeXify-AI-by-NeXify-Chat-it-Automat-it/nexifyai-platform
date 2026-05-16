// NeXifyAI Admin — Incident Timeline (GroupedBar Chart)
// Shows incidents by severity over recent days

import React from 'react';
import { VisXYContainer, VisGroupedBar, VisAxis, VisTooltip, VisCrosshair } from '@unovis/react';

export default function IncidentTimeline({ data = [], height = 220 }) {
  if (!data || data.length === 0) {
    return (
      <div className="ac-chart-empty">
        <span className="material-symbols-outlined" style={{ fontSize: 32 }}>warning</span>
        <span>No incident data</span>
      </div>
    );
  }

  return (
    <div className="ac-chart-card">
      <div className="ac-chart-header">
        <span className="material-symbols-outlined">warning</span>
        <span>Incidents</span>
        <span className="ac-chart-sub">By severity (last 7 days)</span>
      </div>
      <div style={{ width: '100%', height }}>
        <VisXYContainer
          data={data}
          height={height}
          scaleRange={[height - 40, 12]}
          margin={{ top: 8, bottom: 40, left: 40, right: 16 }}
        >
          <VisGroupedBar
            x={(d) => d?.date || ''}
            y={[
              { value: (d) => d?.critical || 0, color: '#ef4444' },
              { value: (d) => d?.warning || 0, color: '#f59e0b' },
              { value: (d) => d?.info || 0, color: '#3b82f6' },
            ]}
            barPadding={0.2}
          />
          <VisAxis type="x" numTicks={7} tickFormat={(v) => {
            const d = data.find(dd => dd.date === v);
            return d?.date?.slice(5) || '';
          }} />
          <VisAxis type="y" numTicks={4} />
          <VisCrosshair />
          <VisTooltip />
        </VisXYContainer>
      </div>
      <div className="ac-chart-legend">
        <span className="ac-legend-dot" style={{ background: '#ef4444' }} /> Critical
        <span className="ac-legend-dot" style={{ background: '#f59e0b' }} /> Warning
        <span className="ac-legend-dot" style={{ background: '#3b82f6' }} /> Info
      </div>
    </div>
  );
}
