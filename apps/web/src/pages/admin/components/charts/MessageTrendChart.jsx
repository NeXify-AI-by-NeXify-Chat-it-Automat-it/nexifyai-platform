// NeXifyAI Admin — Message/Conversation Trend Line + Area Chart
// Uses @unovis/react VisLine + VisArea on VisXYContainer

import React from 'react';
import { VisXYContainer, VisArea, VisLine, VisAxis, VisTooltip, VisCrosshair } from '@unovis/react';

const gradientDefs = (
  <defs>
    <linearGradient id="msg-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
      <stop offset="100%" stopColor="#10b981" stopOpacity={0.0} />
    </linearGradient>
  </defs>
);

function dateLabel(i, d) {
  return d?.date || '';
}

function valLabel(d) {
  return d?.messages || 0;
}

export default function MessageTrendChart({ data = [], height = 220 }) {
  if (!data || data.length === 0) {
    return (
      <div className="ac-chart-empty">
        <span className="material-symbols-outlined" style={{ fontSize: 32 }}>timeline</span>
        <span>No trend data available</span>
      </div>
    );
  }

  return (
    <div className="ac-chart-card">
      <div className="ac-chart-header">
        <span className="material-symbols-outlined">chat</span>
        <span>Message Trend</span>
        <span className="ac-chart-sub">Last 14 days</span>
      </div>
      <div style={{ width: '100%', height }}>
        <VisXYContainer data={data} height={height} scaleRange={[height - 40, 8]}>
          {/* Area fill */}
          <VisArea x={dateLabel} y={valLabel} color="#10b981" curveBlur={4} />
          {/* Line on top */}
          <VisLine x={dateLabel} y={valLabel} color="#10b981" strokeWidth={2} />
          {/* Axes */}
          <VisAxis type="x" numTicks={7} tickFormat={(v) => {
            const d = data.find(dd => dd.date === v || dd.messages === v);
            return d?.date?.slice(5) || '';
          }} />
          <VisAxis type="y" numTicks={4} tickFormat={(v) => Number.isInteger(v) ? v : ''} />
          {/* Interactive */}
          <VisCrosshair />
          <VisTooltip />
        </VisXYContainer>
      </div>
      <svg style={{ width: 0, height: 0, position: 'absolute' }}>{gradientDefs}</svg>
    </div>
  );
}

export function ConversationsChart({ data = [], height = 220 }) {
  if (!data || data.length === 0) {
    return (
      <div className="ac-chart-empty">
        <span className="material-symbols-outlined" style={{ fontSize: 32 }}>forum</span>
        <span>No conversation data</span>
      </div>
    );
  }

  return (
    <div className="ac-chart-card">
      <div className="ac-chart-header">
        <span className="material-symbols-outlined">forum</span>
        <span>Conversations</span>
        <span className="ac-chart-sub">Last 14 days</span>
      </div>
      <div style={{ width: '100%', height }}>
        <VisXYContainer data={data} height={height} scaleRange={[height - 40, 8]}>
          <VisArea x={d => d?.date || ''} y={d => d?.conversations || 0} color="#3b82f6" curveBlur={3} />
          <VisLine x={d => d?.date || ''} y={d => d?.conversations || 0} color="#3b82f6" strokeWidth={2} />
          <VisAxis type="x" numTicks={7} tickFormat={(v) => {
            const d = data.find(dd => dd.date === v || dd.conversations === v);
            return d?.date?.slice(5) || '';
          }} />
          <VisAxis type="y" numTicks={4} />
          <VisCrosshair />
          <VisTooltip />
        </VisXYContainer>
      </div>
    </div>
  );
}
