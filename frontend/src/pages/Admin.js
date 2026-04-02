import React, { useState, useEffect, useCallback } from 'react';
import './Admin.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

const STATUSES = {
  neu: { label: 'Neu', color: '#3b82f6' },
  qualifiziert: { label: 'Qualifiziert', color: '#8b5cf6' },
  termin_gebucht: { label: 'Termin gebucht', color: '#f59e0b' },
  in_bearbeitung: { label: 'In Bearbeitung', color: '#06b6d4' },
  gewonnen: { label: 'Gewonnen', color: '#22c55e' },
  verloren: { label: 'Verloren', color: '#ef4444' },
  archiviert: { label: 'Archiviert', color: '#6b7280' }
};

const I = ({ n, c = '' }) => <span className={`material-symbols-outlined ${c}`}>{n}</span>;

const AdminLogin = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [pw, setPw] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const body = new URLSearchParams();
      body.append('username', email);
      body.append('password', pw);
      const r = await fetch(`${API}/api/admin/login`, { method: 'POST', body });
      const d = await r.json();
      if (r.ok && d.access_token) {
        sessionStorage.setItem('admin_token', d.access_token);
        onLogin(d.access_token);
      } else {
        setError(d.detail || 'Ungültige Anmeldedaten');
      }
    } catch (_) {
      setError('Verbindungsfehler');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="admin-login" data-testid="admin-login">
      <div className="admin-login-card">
        <div className="admin-login-header">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 16 }}>
            <img src="/icon-mark.svg" alt="" width="32" height="32" />
            <span style={{ fontFamily: 'var(--f-display)', fontWeight: 800, fontSize: '1.125rem', color: '#fff' }}>NeXify<span style={{ color: 'var(--nx-accent)' }}>AI</span></span>
          </div>
          <h1>Admin-Bereich</h1>
        </div>
        <form onSubmit={submit} className="admin-login-form" data-testid="admin-login-form">
          <div className="form-group">
            <label htmlFor="admin-email" className="form-label">E-Mail</label>
            <input type="email" id="admin-email" className="form-input" value={email} onChange={e => setEmail(e.target.value)} required autoFocus data-testid="admin-email-input" />
          </div>
          <div className="form-group">
            <label htmlFor="admin-pw" className="form-label">Passwort</label>
            <input type="password" id="admin-pw" className="form-input" value={pw} onChange={e => setPw(e.target.value)} required data-testid="admin-password-input" />
          </div>
          {error && <div className="admin-login-error" data-testid="admin-login-error">{error}</div>}
          <button type="submit" className="btn btn-primary admin-login-btn" disabled={busy} data-testid="admin-login-submit">{busy ? 'Anmelden...' : 'Anmelden'}</button>
        </form>
      </div>
    </div>
  );
};

const DashboardStats = ({ stats }) => (
  <div className="admin-stats" data-testid="admin-stats">
    {[
      { i: 'people', v: stats.total_leads, l: 'Gesamte Leads' },
      { i: 'fiber_new', v: stats.new_leads_today, l: 'Heute', hl: true },
      { i: 'trending_up', v: stats.new_leads_week, l: 'Diese Woche' },
      { i: 'event', v: stats.upcoming_bookings, l: 'Anstehende Termine' }
    ].map((s, i) => (
      <div key={i} className={`admin-stat-card ${s.hl ? 'highlight' : ''}`}>
        <I n={s.i} c="admin-stat-icon" />
        <div className="admin-stat-content"><div className="admin-stat-value">{s.v}</div><div className="admin-stat-label">{s.l}</div></div>
      </div>
    ))}
  </div>
);

const LeadsTable = ({ leads, onSelect, selected }) => (
  <div className="admin-table-container" data-testid="leads-table">
    <table className="admin-table">
      <thead><tr><th>Status</th><th>Name</th><th>E-Mail</th><th>Unternehmen</th><th>Quelle</th><th>Datum</th><th></th></tr></thead>
      <tbody>
        {leads.map(l => (
          <tr key={l.lead_id} className={selected?.lead_id === l.lead_id ? 'selected' : ''} onClick={() => onSelect(l)}>
            <td><span className="lead-status-badge" style={{ backgroundColor: STATUSES[l.status]?.color || '#6b7280' }}>{STATUSES[l.status]?.label || l.status}</span></td>
            <td className="lead-name">{l.vorname} {l.nachname}</td>
            <td><a href={`mailto:${l.email}`} onClick={e => e.stopPropagation()} className="lead-email">{l.email}</a></td>
            <td>{l.unternehmen || '-'}</td>
            <td className="lead-source">{l.source}</td>
            <td className="lead-date">{new Date(l.created_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: '2-digit' })}</td>
            <td><button className="admin-table-action"><I n="chevron_right" /></button></td>
          </tr>
        ))}
      </tbody>
    </table>
    {leads.length === 0 && <div className="admin-empty">Keine Leads vorhanden</div>}
  </div>
);

const LeadDetail = ({ lead, token, onUpdate, onClose }) => {
  const [status, setStatus] = useState(lead.status);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      await fetch(`${API}/api/admin/leads/${lead.lead_id}`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, notes: note || null })
      });
      onUpdate();
      setNote('');
    } catch (_) {}
    finally { setSaving(false); }
  };

  return (
    <div className="admin-drawer" data-testid="lead-detail">
      <div className="admin-drawer-header"><h2>{lead.vorname} {lead.nachname}</h2><button className="admin-drawer-close" onClick={onClose}><I n="close" /></button></div>
      <div className="admin-drawer-content">
        <div className="admin-drawer-section"><h3>Kontaktdaten</h3>
          <div className="admin-drawer-field"><label>E-Mail</label><div className="admin-drawer-value"><a href={`mailto:${lead.email}`}>{lead.email}</a><button className="admin-copy-btn" onClick={() => navigator.clipboard.writeText(lead.email)} aria-label="Kopieren"><I n="content_copy" /></button></div></div>
          {lead.telefon && <div className="admin-drawer-field"><label>Telefon</label><div className="admin-drawer-value"><a href={`tel:${lead.telefon}`}>{lead.telefon}</a><button className="admin-copy-btn" onClick={() => navigator.clipboard.writeText(lead.telefon)} aria-label="Kopieren"><I n="content_copy" /></button></div></div>}
          {lead.unternehmen && <div className="admin-drawer-field"><label>Unternehmen</label><div className="admin-drawer-value">{lead.unternehmen}</div></div>}
        </div>
        <div className="admin-drawer-section"><h3>Nachricht</h3><div className="admin-drawer-message">{lead.nachricht}</div></div>
        <div className="admin-drawer-section"><h3>Status</h3><select className="form-input admin-status-select" value={status} onChange={e => setStatus(e.target.value)} data-testid="lead-status-select">{Object.entries(STATUSES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</select></div>
        <div className="admin-drawer-section"><h3>Notiz hinzufügen</h3><textarea className="form-textarea" rows="3" value={note} onChange={e => setNote(e.target.value)} placeholder="Interne Notiz..."></textarea></div>
        {lead.notes?.length > 0 && <div className="admin-drawer-section"><h3>Bisherige Notizen</h3><div className="admin-notes-list">{lead.notes.map((n, i) => <div key={i} className="admin-note"><div className="admin-note-text">{n.text}</div><div className="admin-note-meta">{n.by} • {new Date(n.at).toLocaleString('de-DE')}</div></div>)}</div></div>}
        <div className="admin-drawer-section"><h3>Metadaten</h3>
          <div className="admin-drawer-field"><label>Lead-ID</label><div className="admin-drawer-value">{lead.lead_id}</div></div>
          <div className="admin-drawer-field"><label>Erstellt</label><div className="admin-drawer-value">{new Date(lead.created_at).toLocaleString('de-DE')}</div></div>
          <div className="admin-drawer-field"><label>Quelle</label><div className="admin-drawer-value">{lead.source}</div></div>
        </div>
      </div>
      <div className="admin-drawer-footer"><button className="btn btn-primary" onClick={save} disabled={saving} data-testid="lead-save-btn">{saving ? 'Speichern...' : 'Änderungen speichern'}</button></div>
    </div>
  );
};

const Admin = () => {
  const [token, setToken] = useState(sessionStorage.getItem('admin_token'));
  const [view, setView] = useState('leads');
  const [stats, setStats] = useState({ total_leads: 0, new_leads_today: 0, new_leads_week: 0, upcoming_bookings: 0, by_status: {} });
  const [leads, setLeads] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const h = { 'Authorization': `Bearer ${token}` };
      const [sr, lr, br] = await Promise.all([
        fetch(`${API}/api/admin/stats`, { headers: h }),
        fetch(`${API}/api/admin/leads?search=${search}&status=${filter}`, { headers: h }),
        fetch(`${API}/api/admin/bookings`, { headers: h })
      ]);
      if (sr.status === 401 || lr.status === 401) { sessionStorage.removeItem('admin_token'); setToken(null); return; }
      if (sr.ok) setStats(await sr.json());
      if (lr.ok) { const d = await lr.json(); setLeads(d.leads || []); }
      if (br.ok) { const d = await br.json(); setBookings(d.bookings || []); }
    } catch (_) {}
    finally { setLoading(false); }
  }, [token, search, filter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const logout = () => { sessionStorage.removeItem('admin_token'); setToken(null); };

  if (!token) return <AdminLogin onLogin={setToken} />;

  return (
    <div className="admin-layout" data-testid="admin-dashboard">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <img src="/icon-mark.svg" alt="" width="24" height="24" />
            <span className="admin-sidebar-text" style={{ fontFamily: 'var(--f-display)', fontWeight: 800, fontSize: '.875rem', color: '#fff' }}>NeXify<span style={{ color: 'var(--nx-accent)' }}>AI</span></span>
          </div>
        </div>
        <nav className="admin-nav">
          <button className={`admin-nav-item ${view === 'leads' ? 'active' : ''}`} onClick={() => setView('leads')} data-testid="nav-leads"><I n="people" /><span>Leads</span></button>
          <button className={`admin-nav-item ${view === 'bookings' ? 'active' : ''}`} onClick={() => setView('bookings')} data-testid="nav-bookings"><I n="calendar_month" /><span>Termine</span></button>
        </nav>
        <div className="admin-sidebar-footer"><button className="admin-logout" onClick={logout} data-testid="admin-logout"><I n="logout" /><span>Abmelden</span></button></div>
      </aside>
      <main className="admin-main">
        <header className="admin-header"><h1>{view === 'leads' ? 'Lead-Übersicht' : 'Termine'}</h1><div className="admin-header-actions"><button className="btn btn-secondary" onClick={fetchData} data-testid="admin-refresh"><I n="refresh" /> Aktualisieren</button></div></header>
        <DashboardStats stats={stats} />
        {view === 'leads' && (
          <>
            <div className="admin-filters">
              <div className="admin-search"><I n="search" /><input type="text" placeholder="Suchen..." value={search} onChange={e => setSearch(e.target.value)} data-testid="admin-search" /></div>
              <select className="admin-filter-select" value={filter} onChange={e => setFilter(e.target.value)} data-testid="admin-filter"><option value="">Alle Status</option>{Object.entries(STATUSES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}</select>
            </div>
            {loading ? <div className="admin-loading">Laden...</div> : <LeadsTable leads={leads} onSelect={setSelected} selected={selected} />}
          </>
        )}
        {view === 'bookings' && (
          <div className="admin-bookings">
            {bookings.length === 0 ? <div className="admin-empty">Keine Termine vorhanden</div> : (
              <div className="admin-bookings-grid">{bookings.map(b => (
                <div key={b.booking_id} className="admin-booking-card">
                  <div className="admin-booking-date"><I n="event" />{b.date} um {b.time} Uhr</div>
                  <div className="admin-booking-name">{b.vorname} {b.nachname}</div>
                  <div className="admin-booking-email"><a href={`mailto:${b.email}`}>{b.email}</a></div>
                  {b.telefon && <div className="admin-booking-phone"><a href={`tel:${b.telefon}`}>{b.telefon}</a></div>}
                  {b.thema && <div className="admin-booking-topic">{b.thema}</div>}
                </div>
              ))}</div>
            )}
          </div>
        )}
      </main>
      {selected && <LeadDetail lead={selected} token={token} onUpdate={fetchData} onClose={() => setSelected(null)} />}
    </div>
  );
};

export default Admin;
