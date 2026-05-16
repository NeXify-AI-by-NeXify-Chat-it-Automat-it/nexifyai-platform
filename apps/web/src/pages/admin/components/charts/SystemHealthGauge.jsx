// NeXifyAI Admin — System Health Gauge (SVG)
// Enhanced version of the HealthCircle with animated segments

import React from 'react';

export default function SystemHealthGauge({ score = 0, label = 'System Health' }) {
  const pct = Math.min(100, Math.max(0, Number(score) || 0));
  let color = '#ef4444';
  let status = 'Critical';
  if (pct >= 90) { color = '#10b981'; status = 'Healthy'; }
  else if (pct >= 70) { color = '#f59e0b'; status = 'Degraded'; }
  else if (pct >= 50) { color = '#f97316'; status = 'Warning'; }

  const r = 54;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '8px',
      padding: '16px',
      background: 'rgba(255,255,255,0.02)',
      border: '1px solid rgba(255,255,255,0.04)',
      borderRadius: '12px',
      minWidth: 160,
    }}>
      <div style={{ position: 'relative', width: 128, height: 128 }}>
        <svg width="128" height="128" viewBox="0 0 128 128">
          {/* Background ring */}
          <circle cx="64" cy="64" r={r} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="8" />
          {/* Foreground ring */}
          <circle
            cx="64" cy="64" r={r}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            transform="rotate(-90 64 64)"
            style={{ transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s ease' }}
          />
          {/* Glow effect */}
          <circle
            cx="64" cy="64" r={r}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            transform="rotate(-90 64 64)"
            opacity="0.15"
            style={{ filter: 'blur(4px)', transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)' }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, color, lineHeight: 1 }}>{Math.round(pct)}</div>
          <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)', fontWeight: 600 }}>%</div>
        </div>
      </div>
      <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)' }}>{label}</div>
      <div style={{
        fontSize: '0.7rem',
        fontWeight: 700,
        color,
        background: `${color}15`,
        padding: '2px 10px',
        borderRadius: '999px',
      }}>{status}</div>
    </div>
  );
}
