import React, { useState, useEffect, useCallback } from 'react';
import './Admin.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const LEAD_STATUSES = {
  neu: { label: 'Neu', color: '#3b82f6' },
  qualifiziert: { label: 'Qualifiziert', color: '#8b5cf6' },
  termin_gebucht: { label: 'Termin gebucht', color: '#f59e0b' },
  in_bearbeitung: { label: 'In Bearbeitung', color: '#06b6d4' },
  gewonnen: { label: 'Gewonnen', color: '#22c55e' },
  verloren: { label: 'Verloren', color: '#ef4444' },
  archiviert: { label: 'Archiviert', color: '#6b7280' }
};

// Icon Component
const Icon = ({ name, className = '' }) => (
  <span className={`material-symbols-outlined ${className}`}>{name}</span>
);

// Login Component
const AdminLogin = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const credentials = btoa(`${email}:${password}`);
      const res = await fetch(`${API_URL}/api/admin/stats`, {
        headers: { 'Authorization': `Basic ${credentials}` }
      });
      
      if (res.ok) {
        sessionStorage.setItem('admin_auth', credentials);
        onLogin(credentials);
      } else {
        setError('Ungültige Anmeldedaten');
      }
    } catch (err) {
      setError('Verbindungsfehler');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login">
      <div className="admin-login-card">
        <div className="admin-login-header">
          <img src="/logo-light.svg" alt="NeXifyAI" className="admin-login-logo" />
          <h1>Admin-Bereich</h1>
        </div>
        <form onSubmit={handleSubmit} className="admin-login-form">
          <div className="form-group">
            <label htmlFor="email" className="form-label">E-Mail</label>
            <input
              type="email"
              id="email"
              className="form-input"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label htmlFor="password" className="form-label">Passwort</label>
            <input
              type="password"
              id="password"
              className="form-input"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="admin-login-error">{error}</div>}
          <button type="submit" className="btn btn-primary admin-login-btn" disabled={loading}>
            {loading ? 'Anmelden...' : 'Anmelden'}
          </button>
        </form>
      </div>
    </div>
  );
};

// Dashboard Stats
const DashboardStats = ({ stats }) => (
  <div className="admin-stats">
    <div className="admin-stat-card">
      <Icon name="people" className="admin-stat-icon" />
      <div className="admin-stat-content">
        <div className="admin-stat-value">{stats.total_leads}</div>
        <div className="admin-stat-label">Gesamte Leads</div>
      </div>
    </div>
    <div className="admin-stat-card highlight">
      <Icon name="fiber_new" className="admin-stat-icon" />
      <div className="admin-stat-content">
        <div className="admin-stat-value">{stats.new_leads_today}</div>
        <div className="admin-stat-label">Heute</div>
      </div>
    </div>
    <div className="admin-stat-card">
      <Icon name="trending_up" className="admin-stat-icon" />
      <div className="admin-stat-content">
        <div className="admin-stat-value">{stats.new_leads_week}</div>
        <div className="admin-stat-label">Diese Woche</div>
      </div>
    </div>
    <div className="admin-stat-card">
      <Icon name="event" className="admin-stat-icon" />
      <div className="admin-stat-content">
        <div className="admin-stat-value">{stats.upcoming_bookings}</div>
        <div className="admin-stat-label">Anstehende Termine</div>
      </div>
    </div>
  </div>
);

// Leads Table
const LeadsTable = ({ leads, onSelectLead, selectedLead }) => (
  <div className="admin-table-container">
    <table className="admin-table">
      <thead>
        <tr>
          <th>Status</th>
          <th>Name</th>
          <th>E-Mail</th>
          <th>Unternehmen</th>
          <th>Quelle</th>
          <th>Datum</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {leads.map(lead => (
          <tr 
            key={lead.lead_id} 
            className={selectedLead?.lead_id === lead.lead_id ? 'selected' : ''}
            onClick={() => onSelectLead(lead)}
          >
            <td>
              <span 
                className="lead-status-badge" 
                style={{ backgroundColor: LEAD_STATUSES[lead.status]?.color || '#6b7280' }}
              >
                {LEAD_STATUSES[lead.status]?.label || lead.status}
              </span>
            </td>
            <td className="lead-name">{lead.vorname} {lead.nachname}</td>
            <td>
              <a href={`mailto:${lead.email}`} onClick={e => e.stopPropagation()} className="lead-email">
                {lead.email}
              </a>
            </td>
            <td>{lead.unternehmen || '-'}</td>
            <td className="lead-source">{lead.source}</td>
            <td className="lead-date">
              {new Date(lead.created_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: '2-digit' })}
            </td>
            <td>
              <button className="admin-table-action" onClick={() => onSelectLead(lead)}>
                <Icon name="chevron_right" />
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// Lead Detail Drawer
const LeadDetail = ({ lead, auth, onUpdate, onClose }) => {
  const [status, setStatus] = useState(lead.status);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`${API_URL}/api/admin/leads/${lead.lead_id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status, notes: note || null })
      });
      onUpdate();
      setNote('');
    } catch (err) {
      console.error('Update failed:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-drawer">
      <div className="admin-drawer-header">
        <h2>{lead.vorname} {lead.nachname}</h2>
        <button className="admin-drawer-close" onClick={onClose}>
          <Icon name="close" />
        </button>
      </div>
      
      <div className="admin-drawer-content">
        <div className="admin-drawer-section">
          <h3>Kontaktdaten</h3>
          <div className="admin-drawer-field">
            <label>E-Mail</label>
            <div className="admin-drawer-value">
              <a href={`mailto:${lead.email}`}>{lead.email}</a>
              <button className="admin-copy-btn" onClick={() => navigator.clipboard.writeText(lead.email)}>
                <Icon name="content_copy" />
              </button>
            </div>
          </div>
          {lead.telefon && (
            <div className="admin-drawer-field">
              <label>Telefon</label>
              <div className="admin-drawer-value">
                <a href={`tel:${lead.telefon}`}>{lead.telefon}</a>
                <button className="admin-copy-btn" onClick={() => navigator.clipboard.writeText(lead.telefon)}>
                  <Icon name="content_copy" />
                </button>
              </div>
            </div>
          )}
          {lead.unternehmen && (
            <div className="admin-drawer-field">
              <label>Unternehmen</label>
              <div className="admin-drawer-value">{lead.unternehmen}</div>
            </div>
          )}
        </div>
        
        <div className="admin-drawer-section">
          <h3>Nachricht</h3>
          <div className="admin-drawer-message">{lead.nachricht}</div>
        </div>
        
        <div className="admin-drawer-section">
          <h3>Status</h3>
          <select 
            className="form-input admin-status-select" 
            value={status} 
            onChange={e => setStatus(e.target.value)}
          >
            {Object.entries(LEAD_STATUSES).map(([key, val]) => (
              <option key={key} value={key}>{val.label}</option>
            ))}
          </select>
        </div>
        
        <div className="admin-drawer-section">
          <h3>Notiz hinzufügen</h3>
          <textarea 
            className="form-textarea" 
            rows="3" 
            value={note} 
            onChange={e => setNote(e.target.value)}
            placeholder="Interne Notiz..."
          ></textarea>
        </div>
        
        {lead.notes && lead.notes.length > 0 && (
          <div className="admin-drawer-section">
            <h3>Bisherige Notizen</h3>
            <div className="admin-notes-list">
              {lead.notes.map((n, i) => (
                <div key={i} className="admin-note">
                  <div className="admin-note-text">{n.text}</div>
                  <div className="admin-note-meta">{n.by} • {new Date(n.at).toLocaleString('de-DE')}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="admin-drawer-section">
          <h3>Metadaten</h3>
          <div className="admin-drawer-field">
            <label>Lead-ID</label>
            <div className="admin-drawer-value">{lead.lead_id}</div>
          </div>
          <div className="admin-drawer-field">
            <label>Erstellt</label>
            <div className="admin-drawer-value">{new Date(lead.created_at).toLocaleString('de-DE')}</div>
          </div>
          <div className="admin-drawer-field">
            <label>Quelle</label>
            <div className="admin-drawer-value">{lead.source}</div>
          </div>
        </div>
      </div>
      
      <div className="admin-drawer-footer">
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? 'Speichern...' : 'Änderungen speichern'}
        </button>
      </div>
    </div>
  );
};

// Main Admin Component
const Admin = () => {
  const [auth, setAuth] = useState(sessionStorage.getItem('admin_auth'));
  const [view, setView] = useState('leads');
  const [stats, setStats] = useState({ total_leads: 0, new_leads_today: 0, new_leads_week: 0, upcoming_bookings: 0, by_status: {} });
  const [leads, setLeads] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!auth) return;
    setLoading(true);
    
    try {
      const headers = { 'Authorization': `Basic ${auth}` };
      
      const [statsRes, leadsRes, bookingsRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/stats`, { headers }),
        fetch(`${API_URL}/api/admin/leads?search=${search}&status=${statusFilter}`, { headers }),
        fetch(`${API_URL}/api/admin/bookings`, { headers })
      ]);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (leadsRes.ok) {
        const data = await leadsRes.json();
        setLeads(data.leads || []);
      }
      if (bookingsRes.ok) {
        const data = await bookingsRes.json();
        setBookings(data.bookings || []);
      }
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [auth, search, statusFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLogout = () => {
    sessionStorage.removeItem('admin_auth');
    setAuth(null);
  };

  if (!auth) {
    return <AdminLogin onLogin={setAuth} />;
  }

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-header">
          <img src="/logo-light.svg" alt="NeXifyAI" className="admin-sidebar-logo" />
        </div>
        <nav className="admin-nav">
          <button 
            className={`admin-nav-item ${view === 'leads' ? 'active' : ''}`}
            onClick={() => setView('leads')}
          >
            <Icon name="people" />
            <span>Leads</span>
          </button>
          <button 
            className={`admin-nav-item ${view === 'bookings' ? 'active' : ''}`}
            onClick={() => setView('bookings')}
          >
            <Icon name="calendar_month" />
            <span>Termine</span>
          </button>
        </nav>
        <div className="admin-sidebar-footer">
          <button className="admin-logout" onClick={handleLogout}>
            <Icon name="logout" />
            <span>Abmelden</span>
          </button>
        </div>
      </aside>
      
      <main className="admin-main">
        <header className="admin-header">
          <h1>{view === 'leads' ? 'Lead-Übersicht' : 'Termine'}</h1>
          <div className="admin-header-actions">
            <button className="btn btn-secondary" onClick={fetchData}>
              <Icon name="refresh" />
              Aktualisieren
            </button>
          </div>
        </header>
        
        <DashboardStats stats={stats} />
        
        {view === 'leads' && (
          <>
            <div className="admin-filters">
              <div className="admin-search">
                <Icon name="search" />
                <input 
                  type="text" 
                  placeholder="Suchen..." 
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              <select 
                className="admin-filter-select" 
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
              >
                <option value="">Alle Status</option>
                {Object.entries(LEAD_STATUSES).map(([key, val]) => (
                  <option key={key} value={key}>{val.label}</option>
                ))}
              </select>
            </div>
            
            {loading ? (
              <div className="admin-loading">Laden...</div>
            ) : (
              <LeadsTable leads={leads} onSelectLead={setSelectedLead} selectedLead={selectedLead} />
            )}
          </>
        )}
        
        {view === 'bookings' && (
          <div className="admin-bookings">
            {bookings.length === 0 ? (
              <div className="admin-empty">Keine Termine vorhanden</div>
            ) : (
              <div className="admin-bookings-grid">
                {bookings.map(booking => (
                  <div key={booking.booking_id} className="admin-booking-card">
                    <div className="admin-booking-date">
                      <Icon name="event" />
                      {booking.date} um {booking.time} Uhr
                    </div>
                    <div className="admin-booking-name">{booking.vorname} {booking.nachname}</div>
                    <div className="admin-booking-email">
                      <a href={`mailto:${booking.email}`}>{booking.email}</a>
                    </div>
                    {booking.thema && <div className="admin-booking-topic">{booking.thema}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
      
      {selectedLead && (
        <LeadDetail 
          lead={selectedLead} 
          auth={auth}
          onUpdate={fetchData}
          onClose={() => setSelectedLead(null)}
        />
      )}
    </div>
  );
};

export default Admin;
