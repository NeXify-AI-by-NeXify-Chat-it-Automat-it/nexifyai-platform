import React, { useState, useEffect } from 'react';
import { api } from '../../../lib/adminApi';

const STATUS_MAP = {
  neu: { label: 'Neu', color: '#3b82f6' },
  kontaktiert: { label: 'Kontaktiert', color: '#f59e0b' },
  qualifiziert: { label: 'Qualifiziert', color: '#10b981' },
  termin_gebucht: { label: 'Termin', color: '#8b5cf6' },
  abgeschlossen: { label: 'Abgeschlossen', color: '#6b7280' },
  abgelehnt: { label: 'Abgelehnt', color: '#ef4444' },
};

export default function LeadsView() {
  const [leads, setLeads] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  const loadLeads = () => {
    const params = { limit: 100 };
    if (search) params.search = search;
    if (filter !== 'all') params.status = filter;
    api.getLeads(params).then(d => {
      setLeads(d?.leads || []);
      setTotal(d?.total || 0);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { loadLeads(); }, [filter]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadLeads();
  };

  if (loading) return <div className="ac-loading"><div className="ac-loading-spinner" /><p>Lade Leads...</p></div>;

  return (
    <div className="ac-view" style={{ padding: '24px', overflow: 'auto', flexDirection: 'column' }}>
      <h3>Leads ({total})</h3>
      <div className="ac-search-form" style={{ marginBottom: '16px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px', flex: 1 }}>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Suche nach Name, E-Mail, Firma..."
            className="ac-input ac-search-input"
          />
          <button type="submit" className="ac-btn-primary ac-btn-sm">Suchen</button>
        </form>
        <select value={filter} onChange={e => setFilter(e.target.value)} className="ac-input" style={{ width: 'auto' }}>
          <option value="all">Alle Status</option>
          {Object.entries(STATUS_MAP).map(([k, v]) => (
            <option key={k} value={k}>{v.label}</option>
          ))}
        </select>
      </div>
      <table className="ac-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>E-Mail</th>
            <th>Firma</th>
            <th>Status</th>
            <th>Datum</th>
          </tr>
        </thead>
        <tbody>
          {leads.map(l => (
            <tr key={l._id || l.id}>
              <td>{l.name || l.customer_name || '—'}</td>
              <td>{l.email || l.customer_email || '—'}</td>
              <td>{l.company || l.customer_company || '—'}</td>
              <td><span style={{ color: STATUS_MAP[l.status]?.color || '#6b7280' }}>{STATUS_MAP[l.status]?.label || l.status}</span></td>
              <td>{l.created_at ? new Date(l.created_at).toLocaleDateString('de-DE') : '—'}</td>
            </tr>
          ))}
          {leads.length === 0 && <tr><td colSpan={5} className="ac-empty">Keine Leads gefunden</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
