import React, { useState, useEffect } from 'react';
import { api } from '../../../lib/adminApi';

const I = ({ n, s = 18 }) => (
  <span className="material-symbols-outlined" style={{ fontSize: s, width: s, height: s }}>{n}</span>
);

const STATUS_MAP = {
  waiting: { label: 'Wartend', color: '#f59e0b' },
  in_progress: { label: 'In Arbeit', color: '#3b82f6' },
  done: { label: 'Erledigt', color: '#10b981' },
  failed: { label: 'Fehlgeschlagen', color: '#ef4444' },
  cancelled: { label: 'Abgebrochen', color: '#6b7280' },
};

export default function TasksView() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newPriority, setNewPriority] = useState('normal');
  const [creating, setCreating] = useState(false);

  const loadTasks = () => {
    api.getTasks(50).then(d => {
      setTasks(d?.tasks || d || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { loadTasks(); }, []);

  const createTask = async (e) => {
    e.preventDefault();
    if (!newTitle.trim() || creating) return;
    setCreating(true);
    try {
      await api.createTask({
        title: newTitle,
        description: newDesc,
        priority: newPriority,
        source: 'admin-cockpit',
      });
      setNewTitle('');
      setNewDesc('');
      loadTasks();
    } catch (err) {
      alert('Fehler: ' + err.message);
    }
    setCreating(false);
  };

  if (loading) return <div className="ac-loading"><div className="ac-loading-spinner" /><p>Lade Tasks...</p></div>;

  return (
    <div className="ac-view">
      <div style={{ flex: 1, overflow: 'auto', padding: '24px' }}>
        <h3>Tasks ({tasks.length})</h3>
        <table className="ac-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Titel</th>
              <th>Status</th>
              <th>Priorität</th>
              <th>Erstellt</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map(t => (
              <tr key={t.id || t.task_id}>
                <td><code>{(t.id || t.task_id || '').slice(0, 8)}</code></td>
                <td>{t.title || t.name}</td>
                <td><span style={{ color: STATUS_MAP[t.status]?.color || '#6b7280' }}>{STATUS_MAP[t.status]?.label || t.status}</span></td>
                <td>{t.priority || t.rice_score || '—'}</td>
                <td>{t.created_at ? new Date(t.created_at).toLocaleString('de-DE') : '—'}</td>
              </tr>
            ))}
            {tasks.length === 0 && <tr><td colSpan={5} className="ac-empty">Keine Tasks</td></tr>}
          </tbody>
        </table>
      </div>
      <div className="ac-view-form">
        <h4>Neuen Task anlegen</h4>
        <form onSubmit={createTask}>
          <input value={newTitle} onChange={e => setNewTitle(e.target.value)} placeholder="Titel" className="ac-input" required />
          <textarea value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="Beschreibung" className="ac-input" rows={3} />
          <select value={newPriority} onChange={e => setNewPriority(e.target.value)} className="ac-input">
            <option value="low">Niedrig</option>
            <option value="normal">Normal</option>
            <option value="high">Hoch</option>
            <option value="critical">Kritisch</option>
          </select>
          <button type="submit" className="ac-btn-primary" disabled={creating}>
            {creating ? 'Erstelle...' : 'Task anlegen'}
          </button>
        </form>
      </div>
    </div>
  );
}
