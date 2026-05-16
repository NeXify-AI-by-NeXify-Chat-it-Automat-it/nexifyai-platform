// NeXifyAI Admin — Worker Pool View
// Manages multi-agent sandbox workers (Claude Code, Codex CLI, OpenCode)

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

const WORKER_META = {
  'claude-code': { label: 'Claude Code', icon: 'psychology', color: '#10b981' },
  'codex': { label: 'Codex CLI', icon: 'code', color: '#3b82f6' },
  'opencode': { label: 'OpenCode', icon: 'terminal', color: '#f59e0b' },
};

const STATUS_META = {
  starting: { label: 'Starting', icon: 'hourglass_top', color: '#f59e0b' },
  running: { label: 'Running', icon: 'play_circle', color: '#10b981' },
  completed: { label: 'Completed', icon: 'check_circle', color: '#22c55e' },
  failed: { label: 'Failed', icon: 'error', color: '#ef4444' },
  timeout: { label: 'Timeout', icon: 'timer_off', color: '#f97316' },
};

function WorkerCard({ worker }) {
  const meta = WORKER_META[worker.type] || { label: worker.type, icon: 'smart_toy', color: '#888' };
  const status = STATUS_META[worker.status] || { label: worker.status, icon: 'help', color: '#888' };

  return (
    <div className="ac-card" style={{ marginBottom: 8, padding: '12px 16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
        <I n={meta.icon} s={20} />
        <span style={{ fontWeight: 600, fontFamily: 'var(--f-mono, monospace)', fontSize: '0.85rem' }}>
          {meta.label}
        </span>
        <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', fontFamily: 'var(--f-mono, monospace)' }}>
          {worker.id}
        </span>
        <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.75rem', color: status.color }}>
          <I n={status.icon} s={14} />
          {status.label}
        </span>
      </div>

      <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)', marginBottom: 4 }}>
        Started: {new Date(worker.startedAt).toLocaleTimeString()}
        {worker.completedAt && ` · Completed: ${new Date(worker.completedAt).toLocaleTimeString()}`}
      </div>

      {worker.error && (
        <div style={{ fontSize: '0.7rem', color: '#ef4444', background: 'rgba(239,68,68,0.1)', padding: '6px 8px', borderRadius: 4, marginTop: 4, fontFamily: 'var(--f-mono, monospace)', maxHeight: 80, overflow: 'auto' }}>
          {worker.error}
        </div>
      )}

      {worker.result && worker.status === 'completed' && (
        <details style={{ marginTop: 4 }}>
          <summary style={{ fontSize: '0.7rem', color: '#22c55e', cursor: 'pointer' }}>Show Result</summary>
          <pre style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.5)', background: 'rgba(0,0,0,0.2)', padding: 8, borderRadius: 4, marginTop: 4, maxHeight: 200, overflow: 'auto', fontFamily: 'var(--f-mono, monospace)' }}>
            {worker.result}
          </pre>
        </details>
      )}
    </div>
  );
}

export default function WorkerPoolView() {
  const [workers, setWorkers] = useState([]);
  const [stats, setStats] = useState({ total: 0, running: 0, completed: 0, failed: 0, activeWorkers: 0 });
  const [type, setType] = useState('claude-code');
  const [task, setTask] = useState('');
  const [timeout, setTimeout_] = useState(300);
  const [spawning, setSpawning] = useState(false);
  const [health, setHealth] = useState(null);

  const fetchWorkers = useCallback(async () => {
    try {
      const res = await api.listWorkers();
      if (res?.success) {
        setWorkers(res.workers || []);
        setStats(res.stats || {});
      }
    } catch (e) {
      // silently retry
    }
  }, []);

  useEffect(() => {
    fetchWorkers();
    const interval = setInterval(fetchWorkers, 5000);
    return () => clearInterval(interval);
  }, [fetchWorkers]);

  const handleSpawn = async () => {
    if (!task.trim()) return;
    setSpawning(true);
    try {
      await api.spawnWorker(type, task.trim(), timeout);
      setTask('');
      setTimeout(fetchWorkers, 1000);
    } catch (e) {
      console.error('Spawn failed', e);
    }
    setSpawning(false);
  };

  const handleKill = async (id) => {
    await api.killWorker(id);
    fetchWorkers();
  };

  const handleCleanup = async () => {
    await api.cleanupWorkers();
    fetchWorkers();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSpawn();
    }
  };

  return (
    <div>
      {/* Stats Bar */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
        <div className="ac-stat-box" style={{ flex: 1, textAlign: 'center', padding: '12px' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#3b82f6' }}>{stats.activeWorkers || 0}</div>
          <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Active</div>
        </div>
        <div className="ac-stat-box" style={{ flex: 1, textAlign: 'center', padding: '12px' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#22c55e' }}>{stats.completed || 0}</div>
          <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Completed</div>
        </div>
        <div className="ac-stat-box" style={{ flex: 1, textAlign: 'center', padding: '12px' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#ef4444' }}>{stats.failed || 0}</div>
          <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Failed</div>
        </div>
      </div>

      {/* Spawn Form */}
      <div className="ac-card" style={{ padding: 16, marginBottom: 16 }}>
        <div style={{ fontWeight: 600, marginBottom: 12, fontSize: '0.85rem' }}>Spawn Worker</div>
        <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
          {Object.entries(WORKER_META).map(([key, meta]) => (
            <button
              key={key}
              className={`ac-btn-sm ${type === key ? 'ac-btn-primary' : 'ac-btn-ghost'}`}
              onClick={() => setType(key)}
              style={{ display: 'flex', alignItems: 'center', gap: 4 }}
            >
              <I n={meta.icon} s={14} />
              {meta.label}
            </button>
          ))}
          <input
            type="number"
            value={timeout}
            onChange={e => setTimeout_(parseInt(e.target.value) || 300)}
            style={{
              width: 64, padding: '4px 8px', fontSize: '0.75rem',
              background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 4, color: 'rgba(255,255,255,0.7)', marginLeft: 'auto',
            }}
            title="Timeout (seconds)"
          />
          <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.4)', display: 'flex', alignItems: 'center' }}>s</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <textarea
            value={task}
            onChange={e => setTask(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe the coding task for this worker..."
            style={{
              flex: 1, padding: '8px 12px', fontSize: '0.8rem', minHeight: 48,
              background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 6, color: 'rgba(255,255,255,0.8)', resize: 'vertical',
              fontFamily: 'var(--f-ui, sans-serif)',
            }}
          />
          <button
            className="ac-btn-primary"
            onClick={handleSpawn}
            disabled={spawning || !task.trim()}
            style={{ alignSelf: 'flex-end', display: 'flex', alignItems: 'center', gap: 4, padding: '8px 16px' }}
          >
            <I n={spawning ? 'sync' : 'play_arrow'} s={16} />
            {spawning ? 'Spawning...' : 'Spawn'}
          </button>
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <button className="ac-btn-ghost ac-btn-xs" onClick={fetchWorkers}>
          <I n="refresh" s={14} /> Refresh
        </button>
        <button className="ac-btn-ghost ac-btn-xs" onClick={handleCleanup}>
          <I n="cleaning_services" s={14} /> Cleanup Stale
        </button>
      </div>

      {/* Worker List */}
      <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: 8 }}>
        {workers.length} worker{workers.length !== 1 ? 's' : ''} in this session
      </div>

      {workers.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: 'rgba(255,255,255,0.3)', fontSize: '0.85rem' }}>
          <I n="smart_toy" s={40} /><br /><br />
          No workers spawned yet.<br />
          Configure a task above to start.
        </div>
      ) : (
        [...workers].reverse().map(w => (
          <div key={w.id} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}><WorkerCard worker={w} /></div>
            {(w.status === 'running' || w.status === 'starting') && (
              <button
                className="ac-btn-ghost ac-btn-xs"
                onClick={() => handleKill(w.id)}
                style={{ marginTop: 8, color: '#ef4444' }}
                title="Kill worker"
              >
                <I n="stop" s={16} />
              </button>
            )}
          </div>
        ))
      )}
    </div>
  );
}
