/**
 * HealthStatusPage — Öffentliche Statusseite
 * Zeigt System-Health, Badges und Connection-Status
 * Route: /health
 */
import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const Badge = ({ label, url, alt }) => (
  <a href={url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
    <img src={url} alt={alt || label} style={{ height: 20, margin: '0 4px' }} />
  </a>
);

const HealthStatusPage = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API}/api/health`, { signal: AbortSignal.timeout(10000) });
        const data = await res.json();
        setHealth(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const scoreColor = (score) => {
    if (!score && score !== 0) return '#8892a4';
    if (score >= 90) return '#22c55e';
    if (score >= 75) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{
      minHeight: '100vh', background: '#0f1923', color: '#e0e4e8',
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
      padding: '40px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center'
    }}>
      <div style={{ maxWidth: 720, width: '100%' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
          <span style={{ color: '#FE9B7B' }}>NeXifyAI</span> System-Status
        </h1>
        <p style={{ color: '#8892a4', fontSize: '0.9rem', margin: '4px 0 24px' }}>
          NeXifyAI by NeXify — Chat it. Automate it.
        </p>

        {/* Badges */}
        <div style={{ marginBottom: 24, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          <Badge
            url="https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/security-scan.yml/badge.svg"
            label="Security Scan"
          />
          <Badge
            url="https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/quality-gates.yml/badge.svg"
            label="CI Quality Gates"
          />
          <Badge
            url="https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/tests.yml/badge.svg"
            label="Tests"
          />
          <Badge
            url="https://github.com/nexifyai-dev/nexifyai-website-sicherheitskopie/actions/workflows/vercel-deploy.yml/badge.svg"
            label="Vercel Deploy"
          />
        </div>

        {/* Health Score */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40, color: '#8892a4' }}>
            System-Status wird geladen...
          </div>
        ) : error ? (
          <div style={{
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: 12, padding: 20, textAlign: 'center'
          }}>
            <span style={{ color: '#ef4444', fontSize: '0.9rem' }}>Status nicht verfügbar: {error}</span>
          </div>
        ) : (
          <div style={{
            background: 'rgba(19,26,34,0.85)', border: '1px solid rgba(254,155,123,0.15)',
            borderRadius: 16, padding: 24, backdropFilter: 'blur(12px)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <span style={{ fontSize: '0.85rem', color: '#8892a4' }}>Health-Score</span>
              <span style={{
                fontSize: '2rem', fontWeight: 800,
                color: scoreColor(health?.health_score),
                fontFamily: 'var(--f-mono), monospace'
              }}>
                {health?.health_score ?? '—'}%
              </span>
            </div>

            {/* Service Status */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 8 }}>
              {health?.services && Object.entries(health.services).map(([name, svc]) => (
                <div key={name} style={{
                  background: 'rgba(255,255,255,0.03)', borderRadius: 8, padding: '10px 14px',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  border: `1px solid ${svc.status === 'healthy' ? 'rgba(34,197,94,0.3)' : svc.status === 'degraded' ? 'rgba(245,158,11,0.3)' : 'rgba(239,68,68,0.3)'}`
                }}>
                  <span style={{ fontSize: '0.8rem', color: '#e0e4e8' }}>{name}</span>
                  <span style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: svc.status === 'healthy' ? '#22c55e' : svc.status === 'degraded' ? '#f59e0b' : '#ef4444',
                    boxShadow: `0 0 8px ${svc.status === 'healthy' ? '#22c55e' : svc.status === 'degraded' ? '#f59e0b' : '#ef4444'}`
                  }} />
                </div>
              ))}
            </div>

            {/* Connection Health */}
            {health?.connections && (
              <div style={{ marginTop: 16, fontSize: '0.8rem', color: '#8892a4', textAlign: 'center' }}>
                Verbindungen: {health.connections.filter(c => c.status === 'ok').length}/{health.connections.length}
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div style={{ marginTop: 24, textAlign: 'center', fontSize: '0.75rem', color: 'rgba(255,255,255,0.3)' }}>
          <a href="/" style={{ color: '#FE9B7B', textDecoration: 'none' }}>www.nexify-automate.com</a>
          <span style={{ margin: '0 8px' }}>·</span>
          <a href="/impressum" style={{ color: 'rgba(255,255,255,0.3)', textDecoration: 'none' }}>Impressum</a>
          <span style={{ margin: '0 8px' }}>·</span>
          <span>Aktualisiert: {new Date().toLocaleDateString('de-DE')}</span>
        </div>
      </div>
    </div>
  );
};

export default HealthStatusPage;
