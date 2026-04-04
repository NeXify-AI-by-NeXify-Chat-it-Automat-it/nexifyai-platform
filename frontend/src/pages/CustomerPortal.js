import React, { useState, useEffect, useRef, useCallback } from 'react';
import './CustomerPortal.css';

const API = process.env.REACT_APP_BACKEND_URL || '';
const I = ({ n }) => <span className="material-symbols-outlined">{n}</span>;
const fmtDate = (d) => d ? new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '-';
const fmtTime = (d) => d ? new Date(d).toLocaleString('de-DE', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) : '-';
const fmtEur = (v) => v != null ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v) : '-';

const QUOTE_STATUS = {
  draft: { l: 'Entwurf', c: '#6b7b8d', i: 'edit' },
  sent: { l: 'Versendet', c: '#3b82f6', i: 'send' },
  opened: { l: 'Geöffnet', c: '#f59e0b', i: 'visibility' },
  accepted: { l: 'Angenommen', c: '#10b981', i: 'check_circle' },
  declined: { l: 'Abgelehnt', c: '#ef4444', i: 'cancel' },
  revision_requested: { l: 'Änderung angefragt', c: '#8b5cf6', i: 'edit_note' },
};

const CustomerPortal = () => {
  useEffect(() => { document.body.classList.add('hide-wa'); return () => document.body.classList.remove('hide-wa'); }, []);
  const params = new URLSearchParams(window.location.search);
  const urlToken = params.get('token');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [actionBusy, setActionBusy] = useState('');
  const [revisionNotes, setRevisionNotes] = useState('');
  const [showRevision, setShowRevision] = useState(null);
  const [authToken, setAuthToken] = useState('');
  const [contracts, setContracts] = useState([]);
  const [selectedContract, setSelectedContract] = useState(null);
  const [contractDetail, setContractDetail] = useState(null);
  const [contractLoading, setContractLoading] = useState(false);
  const [legalAccepted, setLegalAccepted] = useState({});
  const [signatureType, setSignatureType] = useState('canvas');
  const [signatureName, setSignatureName] = useState('');
  const [signatureData, setSignatureData] = useState('');
  const [contractBusy, setContractBusy] = useState('');
  const [changeRequest, setChangeRequest] = useState('');
  const [declineReason, setDeclineReason] = useState('');
  const [showDecline, setShowDecline] = useState(false);
  const [showChangeReq, setShowChangeReq] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDetail, setProjectDetail] = useState(null);
  const [projectChatMsg, setProjectChatMsg] = useState('');
  const [financeData, setFinanceData] = useState(null);
  const [financeLoading, setFinanceLoading] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [profileForm, setProfileForm] = useState({ first_name:'', last_name:'', phone:'', company:'', country:'DE' });
  const [profileSaving, setProfileSaving] = useState(false);
  const [customerDocs, setCustomerDocs] = useState([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [consentsData, setConsentsData] = useState(null);
  /* Active features state */
  const [customerRequests, setCustomerRequests] = useState([]);
  const [customerMessages, setCustomerMessages] = useState([]);
  const [supportTickets, setSupportTickets] = useState([]);
  const [showNewRequest, setShowNewRequest] = useState(false);
  const [showNewBooking, setShowNewBooking] = useState(false);
  const [showNewMessage, setShowNewMessage] = useState(false);
  const [showNewTicket, setShowNewTicket] = useState(false);
  const [formBusy, setFormBusy] = useState(false);
  const [formSuccess, setFormSuccess] = useState('');
  const [requestForm, setRequestForm] = useState({ type: 'project', subject: '', description: '', budget_range: '', urgency: 'normal' });
  const [bookingForm, setBookingForm] = useState({ date: '', time: '', type: 'beratung', notes: '' });
  const [messageForm, setMessageForm] = useState({ subject: '', content: '', category: 'general' });
  const [ticketForm, setTicketForm] = useState({ subject: '', description: '', category: 'general', priority: 'normal' });
  const canvasRef = useRef(null);
  const isDrawingRef = useRef(false);

  const hdrs = useCallback(() => {
    const h = {};
    if (authToken) h['Authorization'] = `Bearer ${authToken}`;
    return h;
  }, [authToken]);

  const loadDashboard = async (jwt) => {
    const r = await fetch(`${API}/api/customer/dashboard`, { headers: { Authorization: `Bearer ${jwt}` } });
    if (!r.ok) throw new Error('Zugang abgelaufen');
    const d = await r.json();
    setData(d);
    setAuthToken(jwt);
  };

  const loadLegacyToken = async (token) => {
    const r = await fetch(`${API}/api/portal/customer/${token}`);
    if (!r.ok) throw new Error('Zugangslink ungültig oder abgelaufen');
    const d = await r.json();
    setData(d);
  };

  const reload = () => {
    if (authToken) {
      loadDashboard(authToken).catch(e => setError(e.message));
      loadContracts(); loadProjects();
    } else if (urlToken) {
      loadLegacyToken(urlToken).catch(e => setError(e.message));
    }
  };

  const loadContracts = useCallback(async () => {
    if (!authToken) return;
    try { const r = await fetch(`${API}/api/customer/contracts`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setContracts(d.contracts || []); } } catch {}
  }, [authToken]);

  const loadContractDetail = async (contractId) => {
    setContractLoading(true);
    try {
      const r = await fetch(`${API}/api/customer/contracts/${contractId}`, { headers: { Authorization: `Bearer ${authToken}` } });
      if (r.ok) {
        const d = await r.json();
        setContractDetail(d); setSelectedContract(contractId);
        const initial = {};
        (d.legal_module_definitions || []).forEach(lm => { initial[lm.key] = d.legal_modules?.[lm.key]?.accepted || false; });
        setLegalAccepted(initial); setSignatureData(''); setSignatureName(''); setShowDecline(false); setShowChangeReq(false);
      }
    } catch (e) { console.error(e); } finally { setContractLoading(false); }
  };

  const loadProjects = useCallback(async () => {
    if (!authToken) return;
    try { const r = await fetch(`${API}/api/customer/projects`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setProjects(d.projects || []); } } catch {}
  }, [authToken]);

  const loadFinance = useCallback(async () => {
    if (!authToken) return;
    setFinanceLoading(true);
    try { const r = await fetch(`${API}/api/customer/finance`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setFinanceData(d); } } catch {} finally { setFinanceLoading(false); }
  }, [authToken]);

  const loadProfile = useCallback(async () => {
    if (!authToken) return;
    try {
      const r = await fetch(`${API}/api/customer/profile`, { headers: { Authorization: `Bearer ${authToken}` } });
      if (r.ok) { const d = await r.json(); setProfileData(d); setProfileForm({ first_name: d.first_name||'', last_name: d.last_name||'', phone: d.phone||'', company: d.company||'', country: d.country||'DE' }); }
    } catch {}
  }, [authToken]);

  const saveProfile = async () => {
    setProfileSaving(true);
    try { const r = await fetch(`${API}/api/customer/profile`, { method: 'PATCH', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify(profileForm) }); if (r.ok) loadProfile(); } catch {} finally { setProfileSaving(false); }
  };

  const loadDocuments = useCallback(async () => {
    if (!authToken) return;
    setDocsLoading(true);
    try { const r = await fetch(`${API}/api/customer/documents`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setCustomerDocs(d.documents || []); } } catch {} finally { setDocsLoading(false); }
  }, [authToken]);

  const loadConsents = useCallback(async () => {
    if (!authToken) return;
    try { const r = await fetch(`${API}/api/customer/consents`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setConsentsData(d); } } catch {}
  }, [authToken]);

  const toggleOptOut = async (optOut) => {
    const url = optOut ? `${API}/api/customer/consents/opt-out` : `${API}/api/customer/consents/opt-in`;
    try { await fetch(url, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ reason: 'customer_request' }) }); loadConsents(); } catch {}
  };

  const loadProjectDetail = async (projectId) => {
    try { const r = await fetch(`${API}/api/customer/projects/${projectId}`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setProjectDetail(d); setSelectedProject(projectId); } } catch {}
  };

  const sendProjectChatMsg = async () => {
    if (!projectChatMsg.trim() || !selectedProject) return;
    try { await fetch(`${API}/api/customer/projects/${selectedProject}/chat`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ content: projectChatMsg }) }); setProjectChatMsg(''); loadProjectDetail(selectedProject); } catch {}
  };

  /* Active Features — Loaders */
  const loadRequests = useCallback(async () => {
    if (!authToken) return;
    try { const r = await fetch(`${API}/api/customer/requests`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setCustomerRequests(d.requests || []); } } catch {}
  }, [authToken]);

  const loadMessages = useCallback(async () => {
    if (!authToken) return;
    try { const r = await fetch(`${API}/api/customer/messages`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setCustomerMessages(d.messages || []); } } catch {}
  }, [authToken]);

  const loadSupportTickets = useCallback(async () => {
    if (!authToken) return;
    try { const r = await fetch(`${API}/api/customer/support`, { headers: { Authorization: `Bearer ${authToken}` } }); if (r.ok) { const d = await r.json(); setSupportTickets(d.tickets || []); } } catch {}
  }, [authToken]);

  /* Active Features — Create */
  const submitRequest = async () => {
    if (!requestForm.subject.trim() || !requestForm.description.trim()) return;
    setFormBusy(true);
    try {
      const r = await fetch(`${API}/api/customer/requests`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify(requestForm) });
      if (r.ok) { setShowNewRequest(false); setRequestForm({ type: 'project', subject: '', description: '', budget_range: '', urgency: 'normal' }); setFormSuccess('Anfrage erfolgreich eingereicht!'); loadRequests(); setTimeout(() => setFormSuccess(''), 4000); }
    } catch {} finally { setFormBusy(false); }
  };

  const submitBooking = async () => {
    if (!bookingForm.date || !bookingForm.time) return;
    setFormBusy(true);
    try {
      const r = await fetch(`${API}/api/customer/bookings`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify(bookingForm) });
      if (r.ok) { setShowNewBooking(false); setBookingForm({ date: '', time: '', type: 'beratung', notes: '' }); setFormSuccess('Termin erfolgreich angefragt!'); reload(); setTimeout(() => setFormSuccess(''), 4000); }
    } catch {} finally { setFormBusy(false); }
  };

  const submitMessage = async () => {
    if (!messageForm.content.trim()) return;
    setFormBusy(true);
    try {
      const r = await fetch(`${API}/api/customer/messages`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify(messageForm) });
      if (r.ok) { setShowNewMessage(false); setMessageForm({ subject: '', content: '', category: 'general' }); setFormSuccess('Nachricht gesendet!'); loadMessages(); setTimeout(() => setFormSuccess(''), 4000); }
    } catch {} finally { setFormBusy(false); }
  };

  const submitTicket = async () => {
    if (!ticketForm.subject.trim() || !ticketForm.description.trim()) return;
    setFormBusy(true);
    try {
      const r = await fetch(`${API}/api/customer/support`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify(ticketForm) });
      if (r.ok) { setShowNewTicket(false); setTicketForm({ subject: '', description: '', category: 'general', priority: 'normal' }); setFormSuccess('Support-Ticket erstellt!'); loadSupportTickets(); setTimeout(() => setFormSuccess(''), 4000); }
    } catch {} finally { setFormBusy(false); }
  };

  /* Signature Canvas */
  const initCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2; canvas.height = rect.height * 2;
    ctx.scale(2, 2); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  }, []);

  const startDraw = useCallback((e) => {
    const canvas = canvasRef.current; if (!canvas) return;
    isDrawingRef.current = true;
    const ctx = canvas.getContext('2d'); const rect = canvas.getBoundingClientRect();
    const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
    ctx.beginPath(); ctx.moveTo(x, y);
  }, []);

  const draw = useCallback((e) => {
    if (!isDrawingRef.current) return;
    const canvas = canvasRef.current; if (!canvas) return;
    e.preventDefault();
    const ctx = canvas.getContext('2d'); const rect = canvas.getBoundingClientRect();
    const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
    ctx.lineTo(x, y); ctx.stroke();
  }, []);

  const endDraw = useCallback(() => {
    isDrawingRef.current = false;
    const canvas = canvasRef.current;
    if (canvas) setSignatureData(canvas.toDataURL('image/png'));
  }, []);

  const clearCanvas = useCallback(() => {
    const canvas = canvasRef.current; if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height); setSignatureData('');
  }, []);

  useEffect(() => { if (tab === 'contracts' && selectedContract && signatureType === 'canvas') { setTimeout(initCanvas, 200); } }, [tab, selectedContract, signatureType, initCanvas]);

  const allRequiredLegalAccepted = () => {
    if (!contractDetail?.legal_module_definitions) return false;
    return contractDetail.legal_module_definitions.filter(l => l.required).every(l => legalAccepted[l.key]);
  };
  const hasValidSignature = () => signatureType === 'name' ? signatureName.trim().length >= 2 : !!signatureData;

  const acceptContract = async () => {
    if (!allRequiredLegalAccepted() || !hasValidSignature()) return;
    setContractBusy('accepting');
    try {
      const payload = { signature_type: signatureType, signature_data: signatureType === 'name' ? signatureName : signatureData, legal_modules_accepted: legalAccepted, customer_name: contractDetail?.customer?.name || '' };
      const r = await fetch(`${API}/api/customer/contracts/${selectedContract}/accept`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (r.ok) { loadContractDetail(selectedContract); loadContracts(); }
    } catch (e) { console.error(e); } finally { setContractBusy(''); }
  };

  const declineContract = async () => {
    setContractBusy('declining');
    try { await fetch(`${API}/api/customer/contracts/${selectedContract}/decline`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ reason: declineReason }) }); loadContractDetail(selectedContract); loadContracts(); setShowDecline(false); } catch (e) { console.error(e); } finally { setContractBusy(''); }
  };

  const requestChange = async () => {
    if (!changeRequest.trim()) return;
    setContractBusy('change');
    try { await fetch(`${API}/api/customer/contracts/${selectedContract}/request-change`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ requested_changes: changeRequest }) }); loadContractDetail(selectedContract); loadContracts(); setShowChangeReq(false); setChangeRequest(''); } catch (e) { console.error(e); } finally { setContractBusy(''); }
  };

  useEffect(() => {
    const init = async () => {
      const stored = localStorage.getItem('nx_auth');
      if (stored) {
        try {
          const auth = JSON.parse(stored);
          if (auth.role === 'customer' && auth.token) { await loadDashboard(auth.token); setLoading(false); return; }
        } catch {}
      }
      const pathParts = window.location.pathname.split('/portal/');
      const pathToken = pathParts.length > 1 ? pathParts[1] : null;
      if (pathToken) {
        try {
          const vr = await fetch(`${API}/api/auth/verify-token`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token: pathToken }) });
          if (vr.ok) {
            const vd = await vr.json();
            localStorage.setItem('nx_auth', JSON.stringify({ token: vd.access_token, role: 'customer', email: vd.email, name: vd.customer_name }));
            await loadDashboard(vd.access_token); setLoading(false); return;
          }
        } catch {}
      }
      if (urlToken) { try { await loadLegacyToken(urlToken); setLoading(false); return; } catch (e) { setError(e.message); setLoading(false); return; } }
      setError('Bitte melden Sie sich an, um auf Ihr Portal zuzugreifen.'); setLoading(false);
    };
    init();
  }, []);

  useEffect(() => {
    if (authToken) { loadContracts(); loadProjects(); loadFinance(); loadProfile(); loadDocuments(); loadConsents(); loadRequests(); loadMessages(); loadSupportTickets(); }
  }, [authToken, loadContracts, loadProjects, loadFinance, loadProfile, loadDocuments, loadConsents, loadRequests, loadMessages, loadSupportTickets]);

  const logout = () => { localStorage.removeItem('nx_auth'); window.location.href = '/login'; };

  const quoteAction = async (quoteId, action, body = {}) => {
    setActionBusy(`${quoteId}_${action}`);
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
      const qp = urlToken ? `?token=${urlToken}` : '';
      const r = await fetch(`${API}/api/portal/quote/${quoteId}/${action}${qp}`, { method: 'POST', headers, body: JSON.stringify(body) });
      if (r.ok) reload();
    } catch (e) { console.error(e); } finally { setActionBusy(''); }
  };

  if (loading) return <div className="cp-loading"><div className="cp-spinner"></div><p>Laden...</p></div>;
  if (error) return (
    <div className="cp-error">
      <div className="cp-error-box">
        <I n="lock" /><h2>Zugang nicht möglich</h2><p>{error}</p>
        <a href="/login" className="cp-btn cp-btn-primary" data-testid="portal-login-link">Zum Login</a>
        <a href="/" className="cp-btn cp-btn-secondary" style={{marginTop:8}}>Zur Startseite</a>
      </div>
    </div>
  );

  const navItems = [
    { id: 'overview', icon: 'dashboard', label: 'Übersicht' },
    { id: 'requests', icon: 'add_circle', label: 'Anfragen' },
    { id: 'contracts', icon: 'gavel', label: 'Verträge' },
    { id: 'projects', icon: 'folder_special', label: 'Projekte' },
    { id: 'quotes', icon: 'description', label: 'Angebote' },
    { id: 'divider1' },
    { id: 'invoices', icon: 'account_balance', label: 'Finanzen' },
    { id: 'bookings', icon: 'event', label: 'Termine' },
    { id: 'documents', icon: 'folder_open', label: 'Dokumente' },
    { id: 'divider2' },
    { id: 'messages', icon: 'chat', label: 'Nachrichten' },
    { id: 'support', icon: 'support_agent', label: 'Support' },
    { id: 'communication', icon: 'forum', label: 'Kommunikation' },
    { id: 'timeline', icon: 'timeline', label: 'Aktivität' },
    { id: 'divider3' },
    { id: 'settings', icon: 'settings', label: 'Einstellungen' },
  ];

  const currentLabel = navItems.find(n => n.id === tab)?.label || '';

  return (
    <div className={`cp-layout ${sidebarOpen ? '' : 'cp-collapsed'}`} data-testid="customer-portal">
      {/* ══════ SIDEBAR ══════ */}
      <aside className="cp-sidebar" data-testid="cp-sidebar">
        <div className="cp-sidebar-logo">
          <img src="/icon-mark.svg" alt="" width="28" height="28" />
          <span className="cp-sidebar-logo-text">NeXify<em>AI</em></span>
        </div>
        <button className="cp-collapse-btn" onClick={() => setSidebarOpen(!sidebarOpen)} title={sidebarOpen ? 'Einklappen' : 'Ausklappen'} data-testid="cp-sidebar-toggle">
          <I n={sidebarOpen ? 'chevron_left' : 'chevron_right'} />
        </button>
        <nav className="cp-sidebar-nav">
          {navItems.map(n => {
            if (n.id.startsWith('divider')) return <div key={n.id} className="cp-nav-divider" />;
            return (
              <button key={n.id} className={`cp-nav-item ${tab === n.id ? 'active' : ''}`} onClick={() => setTab(n.id)} data-testid={`cp-nav-${n.id}`} title={n.label}>
                <I n={n.icon} /><span className="cp-nav-label">{n.label}</span>
              </button>
            );
          })}
        </nav>
        <button className="cp-logout-sidebar" onClick={logout} title="Abmelden" data-testid="cp-logout">
          <I n="logout" /><span className="cp-nav-label">Abmelden</span>
        </button>
      </aside>

      {/* ══════ CONTENT ══════ */}
      <div className="cp-content">
        <div className="cp-topbar">
          <div className="cp-topbar-left">
            <h1 className="cp-topbar-title">{currentLabel}</h1>
          </div>
          <div className="cp-topbar-user">
            <I n="person" /> {data?.customer_name || data?.email}
          </div>
        </div>
        <main className="cp-main">
          {formSuccess && <div className="cp-success-msg" data-testid="cp-success-msg"><I n="check_circle" />{formSuccess}</div>}

          {/* ══════════ OVERVIEW ══════════ */}
          {tab === 'overview' && (
            <div data-testid="cp-overview">
              <h2>Willkommen{data?.customer_name ? `, ${data.customer_name.split(' ')[0]}` : ''}</h2>
              <div className="cp-stat-grid">
                <div className="cp-stat"><I n="description" /><div className="cp-stat-val">{data?.quotes?.length || 0}</div><div className="cp-stat-label">Angebote</div></div>
                <div className="cp-stat"><I n="gavel" /><div className="cp-stat-val">{contracts.length}</div><div className="cp-stat-label">Verträge</div></div>
                <div className="cp-stat"><I n="folder_special" /><div className="cp-stat-val">{projects.length}</div><div className="cp-stat-label">Projekte</div></div>
                <div className="cp-stat"><I n="event" /><div className="cp-stat-val">{data?.bookings?.length || 0}</div><div className="cp-stat-label">Termine</div></div>
              </div>
              <h3>Schnellzugriff</h3>
              <div className="cp-quick-grid">
                <button className="cp-quick-card" onClick={() => { setTab('requests'); setShowNewRequest(true); }} data-testid="cp-quick-request">
                  <I n="add_circle" /><span className="cp-quick-card-title">Neue Anfrage</span><span className="cp-quick-card-desc">Projekt, Angebot oder Beratung anfragen</span>
                </button>
                <button className="cp-quick-card" onClick={() => { setTab('bookings'); setShowNewBooking(true); }} data-testid="cp-quick-booking">
                  <I n="calendar_add_on" /><span className="cp-quick-card-title">Termin buchen</span><span className="cp-quick-card-desc">Beratung oder Review vereinbaren</span>
                </button>
                <button className="cp-quick-card" onClick={() => { setTab('messages'); setShowNewMessage(true); }} data-testid="cp-quick-message">
                  <I n="chat" /><span className="cp-quick-card-title">Nachricht senden</span><span className="cp-quick-card-desc">Direkter Kontakt zum Team</span>
                </button>
                <button className="cp-quick-card" onClick={() => { setTab('support'); setShowNewTicket(true); }} data-testid="cp-quick-support">
                  <I n="support_agent" /><span className="cp-quick-card-title">Support-Ticket</span><span className="cp-quick-card-desc">Hilfe bei Fragen oder Problemen</span>
                </button>
              </div>
              {data?.quotes?.length > 0 && (
                <div className="cp-section">
                  <h3>Aktuelle Angebote</h3>
                  {data.quotes.slice(0, 3).map(q => {
                    const s = QUOTE_STATUS[q.status] || { l: q.status, c: '#6b7b8d' };
                    return (
                      <div key={q.quote_id} className="cp-card" data-testid={`cp-quote-${q.quote_id}`}>
                        <div className="cp-card-header"><span className="cp-card-title">{q.quote_number}</span><span className="cp-badge" style={{background:s.c+'22',color:s.c}}><I n={s.i||'circle'}/> {s.l}</span></div>
                        <div className="cp-card-body"><span>{q.calculation?.tier_name || q.tier}</span><span className="cp-card-price">{fmtEur(q.calculation?.total_contract_eur)}</span></div>
                        <div className="cp-card-footer"><span>{fmtDate(q.created_at)}</span>
                          {(q.status === 'sent' || q.status === 'opened') && <button className="cp-btn cp-btn-primary cp-btn-sm" onClick={() => setTab('quotes')} data-testid={`cp-goto-quote-${q.quote_id}`}>Angebot ansehen</button>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* ══════════ REQUESTS (Anfragen) ══════════ */}
          {tab === 'requests' && (
            <div data-testid="cp-requests">
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:20}}>
                <h2 style={{margin:0}}>Ihre Anfragen</h2>
                <button className="cp-btn cp-btn-primary" onClick={() => setShowNewRequest(true)} data-testid="cp-new-request-btn"><I n="add" /> Neue Anfrage</button>
              </div>
              {showNewRequest && (
                <div className="cp-card" style={{marginBottom:20,borderColor:'rgba(255,107,0,0.2)'}} data-testid="cp-request-form">
                  <h3 style={{margin:'0 0 16px',fontSize:'.9375rem'}}>Neue Anfrage erstellen</h3>
                  <div className="cp-form">
                    <div className="cp-form-grid">
                      <div className="cp-field"><label>Typ</label><select value={requestForm.type} onChange={e => setRequestForm({...requestForm, type: e.target.value})} data-testid="cp-req-type">
                        <option value="project">Neues Projekt</option><option value="quote">Angebot anfordern</option><option value="consultation">Beratung</option><option value="expansion">Erweiterung</option><option value="other">Sonstiges</option>
                      </select></div>
                      <div className="cp-field"><label>Dringlichkeit</label><select value={requestForm.urgency} onChange={e => setRequestForm({...requestForm, urgency: e.target.value})} data-testid="cp-req-urgency">
                        <option value="low">Niedrig</option><option value="normal">Normal</option><option value="high">Hoch</option><option value="urgent">Dringend</option>
                      </select></div>
                    </div>
                    <div className="cp-field"><label>Betreff</label><input type="text" value={requestForm.subject} onChange={e => setRequestForm({...requestForm, subject: e.target.value})} placeholder="Kurze Beschreibung Ihrer Anfrage" data-testid="cp-req-subject" /></div>
                    <div className="cp-field"><label>Beschreibung</label><textarea rows={4} value={requestForm.description} onChange={e => setRequestForm({...requestForm, description: e.target.value})} placeholder="Beschreiben Sie Ihr Anliegen im Detail..." data-testid="cp-req-description" /></div>
                    <div className="cp-field"><label>Budgetrahmen (optional)</label><input type="text" value={requestForm.budget_range} onChange={e => setRequestForm({...requestForm, budget_range: e.target.value})} placeholder="z.B. 5.000 - 10.000 EUR" data-testid="cp-req-budget" /></div>
                    <div style={{display:'flex',gap:8,marginTop:4}}>
                      <button className="cp-btn cp-btn-primary" onClick={submitRequest} disabled={formBusy || !requestForm.subject.trim() || !requestForm.description.trim()} data-testid="cp-req-submit">{formBusy ? 'Wird gesendet...' : 'Anfrage absenden'}</button>
                      <button className="cp-btn cp-btn-secondary" onClick={() => setShowNewRequest(false)}>Abbrechen</button>
                    </div>
                  </div>
                </div>
              )}
              {customerRequests.length === 0 && !showNewRequest ? (
                <div className="cp-empty"><I n="add_circle" /><p>Noch keine Anfragen gestellt. Erstellen Sie Ihre erste Anfrage.</p></div>
              ) : customerRequests.map(req => {
                const urgencyMap = { low: { l:'Niedrig', c:'#6b7b8d' }, normal: { l:'Normal', c:'#3b82f6' }, high: { l:'Hoch', c:'#f59e0b' }, urgent: { l:'Dringend', c:'#ef4444' } };
                const statusMap = { new: { l:'Neu', c:'#3b82f6' }, in_progress: { l:'In Bearbeitung', c:'#f59e0b' }, resolved: { l:'Erledigt', c:'#10b981' }, closed: { l:'Geschlossen', c:'#6b7b8d' } };
                const u = urgencyMap[req.urgency] || urgencyMap.normal;
                const st = statusMap[req.status] || statusMap.new;
                return (
                  <div key={req.request_id} className="cp-card" data-testid={`cp-request-${req.request_id}`}>
                    <div className="cp-card-header">
                      <span className="cp-card-title">{req.subject}</span>
                      <div style={{display:'flex',gap:6}}>
                        <span className="cp-badge" style={{background:u.c+'22',color:u.c}}>{u.l}</span>
                        <span className="cp-badge" style={{background:st.c+'22',color:st.c}}>{st.l}</span>
                      </div>
                    </div>
                    <div className="cp-card-body"><span>{{project:'Neues Projekt',quote:'Angebot',consultation:'Beratung',expansion:'Erweiterung',other:'Sonstiges'}[req.type]||req.type}</span></div>
                    <p style={{fontSize:'.8125rem',color:'#c8d1dc',margin:'8px 0 0',lineHeight:1.5}}>{req.description}</p>
                    <div className="cp-card-footer"><span>{fmtDate(req.created_at)}</span></div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ══════════ CONTRACTS ══════════ */}
          {tab === 'contracts' && (
            <div data-testid="cp-contracts">
              {selectedContract && contractDetail ? (() => {
                const cd = contractDetail;
                const CTR_S = { draft:{l:'Entwurf',c:'#6b7b8d'}, review:{l:'Review',c:'#f59e0b'}, sent:{l:'Zur Prüfung',c:'#3b82f6'}, viewed:{l:'Eingesehen',c:'#06b6d4'}, accepted:{l:'Angenommen',c:'#10b981'}, declined:{l:'Abgelehnt',c:'#ef4444'}, change_requested:{l:'Änderung angefragt',c:'#f97316'}, amended:{l:'Überarbeitet',c:'#8b5cf6'}, cancelled:{l:'Storniert',c:'#64748b'}, expired:{l:'Abgelaufen',c:'#4a5568'} };
                const st = CTR_S[cd.status] || CTR_S.draft;
                const canSign = ['sent', 'viewed'].includes(cd.status);
                const isAccepted = cd.status === 'accepted';
                const isDeclined = cd.status === 'declined';
                const isChangeReq = cd.status === 'change_requested';
                return (
                  <div data-testid="cp-contract-detail">
                    <button className="cp-btn cp-btn-secondary cp-btn-sm" onClick={() => { setSelectedContract(null); setContractDetail(null); }} data-testid="cp-contract-back"><I n="arrow_back" /> Alle Verträge</button>
                    <div style={{display:'flex',alignItems:'center',gap:12,margin:'20px 0 16px',flexWrap:'wrap'}}><h2 style={{margin:0}}>Vertrag {cd.contract_number}</h2><span className="cp-badge" style={{background:st.c+'22',color:st.c,fontSize:'.75rem'}}>{st.l}</span></div>
                    {isAccepted && <div className="cp-status-box cp-status-success" data-testid="cp-contract-accepted-msg"><I n="verified" /> <span>Vertrag erfolgreich angenommen.</span></div>}
                    {isDeclined && <div className="cp-status-box cp-status-danger" data-testid="cp-contract-declined-msg"><I n="cancel" /> <span>Vertrag wurde abgelehnt.</span></div>}
                    {isChangeReq && <div className="cp-status-box cp-status-warning" data-testid="cp-contract-change-msg"><I n="edit_note" /> <span>Ihre Änderungsanfrage wurde übermittelt.</span></div>}
                    <div className="cp-card" style={{marginBottom:16}}>
                      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(180px,1fr))',gap:12}}>
                        <div><div className="cp-meta-label">Vertragstyp</div><div className="cp-meta-val">{{standard:'Standardvertrag',individual:'Individualvertrag',amendment:'Nachtragsvertrag'}[cd.contract_type]||cd.contract_type}</div></div>
                        <div><div className="cp-meta-label">Tarif</div><div className="cp-meta-val">{cd.calculation?.tier_name || cd.tier_key || '-'}</div></div>
                        <div><div className="cp-meta-label">Version</div><div className="cp-meta-val">v{cd.version || 1}</div></div>
                        <div><div className="cp-meta-label">Erstellt</div><div className="cp-meta-val">{fmtDate(cd.created_at)}</div></div>
                      </div>
                    </div>
                    {cd.calculation?.total_contract_eur && (
                      <div className="cp-card" style={{marginBottom:16}}>
                        <h3 style={{margin:'0 0 12px',fontSize:'.9375rem'}}>Kommerzielle Konditionen</h3>
                        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(180px,1fr))',gap:12}}>
                          <div><div className="cp-meta-label">Gesamtvertragswert</div><div className="cp-meta-val" style={{fontSize:'1.125rem',fontWeight:700,color:'#fff'}}>{fmtEur(cd.calculation.total_contract_eur)}</div></div>
                          <div><div className="cp-meta-label">Aktivierungsanzahlung (30%)</div><div className="cp-meta-val" style={{color:'#FF6B00',fontWeight:600}}>{fmtEur(cd.calculation.upfront_eur)}</div></div>
                          <div><div className="cp-meta-label">Monatsrate</div><div className="cp-meta-val">{fmtEur(cd.calculation.recurring_eur)}/Monat</div></div>
                          <div><div className="cp-meta-label">Laufzeit</div><div className="cp-meta-val">{cd.calculation.contract_months || 0} Monate</div></div>
                        </div>
                      </div>
                    )}
                    {(cd.appendices_detail || []).length > 0 && (
                      <div className="cp-card" style={{marginBottom:16}}>
                        <h3 style={{margin:'0 0 12px',fontSize:'.9375rem'}}>Vertragsanlagen</h3>
                        {cd.appendices_detail.map(a => (
                          <div key={a.appendix_id} style={{padding:'10px 0',borderBottom:'1px solid rgba(255,255,255,0.03)'}} data-testid={`cp-appendix-${a.appendix_id}`}>
                            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><span style={{fontWeight:600,color:'#fff',fontSize:'.8125rem'}}>{a.title}</span>{a.pricing?.amount > 0 && <span style={{color:'#FF6B00',fontWeight:600}}>{fmtEur(a.pricing.amount)}</span>}</div>
                            {a.content?.description && <p style={{margin:'4px 0 0',fontSize:'.75rem',color:'#6b7b8d'}}>{a.content.description}</p>}
                          </div>
                        ))}
                      </div>
                    )}
                    {isAccepted && cd.signature_preview && (
                      <div className="cp-card" style={{marginBottom:16}} data-testid="cp-signature-preview">
                        <h3 style={{margin:'0 0 12px',fontSize:'.9375rem'}}>Ihre Unterschrift</h3>
                        <div className="cp-sig-preview-inner">
                          {cd.signature_preview.is_image ? <img src={cd.signature_preview.data} alt="Signatur" className="cp-sig-preview-img" /> : <div className="cp-sig-preview-name">{cd.signature_preview.data}</div>}
                          <div className="cp-sig-preview-meta"><span><I n="person" /> {cd.signature_preview.customer_name}</span><span><I n="schedule" /> {fmtTime(cd.signature_preview.timestamp)}</span></div>
                        </div>
                      </div>
                    )}
                    {cd.has_pdf && (
                      <div className="cp-card" style={{marginBottom:16}} data-testid="cp-contract-pdf">
                        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                          <div><h3 style={{margin:0,fontSize:'.9375rem'}}>Vertragsdokument</h3><p style={{margin:'4px 0 0',fontSize:'.75rem',color:'#6b7b8d'}}>PDF-Version Ihres Vertrags</p></div>
                          <a href={`${API}${cd.pdf_url}`} target="_blank" rel="noreferrer" className="cp-btn cp-btn-secondary" data-testid="cp-contract-pdf-download"><I n="picture_as_pdf" /> PDF</a>
                        </div>
                      </div>
                    )}
                    {cd.evidence_trail?.length > 0 && (
                      <div className="cp-card" style={{marginBottom:16}} data-testid="cp-evidence-trail">
                        <h3 style={{margin:'0 0 12px',fontSize:'.9375rem'}}>Nachweisprotokoll</h3>
                        {cd.evidence_trail.map(ev => {
                          const al = {accepted:'Angenommen',declined:'Abgelehnt',change_requested:'Änderung angefragt',viewed:'Eingesehen'};
                          return (
                            <div key={ev.evidence_id} className="cp-evidence-item">
                              <div className="cp-evidence-header"><span className="cp-badge cp-badge-sm" style={{background:ev.action==='accepted'?'#10b98122':ev.action==='declined'?'#ef444422':'#3b82f622',color:ev.action==='accepted'?'#10b981':ev.action==='declined'?'#ef4444':'#3b82f6'}}>{al[ev.action]||ev.action}</span><span className="cp-evidence-time">{fmtTime(ev.timestamp)}</span></div>
                              <div className="cp-evidence-details"><div><span className="cp-finance-label">Version</span><span>v{ev.contract_version}</span></div><div><span className="cp-finance-label">Hash</span><span style={{fontSize:'.625rem',fontFamily:'monospace'}}>{ev.document_hash?.substring(0,16)}...</span></div><div><span className="cp-finance-label">IP</span><span style={{fontSize:'.75rem',fontFamily:'monospace'}}>{ev.ip_address}</span></div></div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                    {canSign && (
                      <div className="cp-card" style={{marginBottom:16}} data-testid="cp-legal-modules">
                        <h3 style={{margin:'0 0 12px',fontSize:'.9375rem'}}>Rechtliche Bestimmungen</h3>
                        {(cd.legal_module_definitions || []).map(lm => (
                          <label key={lm.key} className="cp-legal-check" data-testid={`cp-legal-${lm.key}`}>
                            <input type="checkbox" checked={legalAccepted[lm.key]||false} onChange={e => setLegalAccepted({...legalAccepted,[lm.key]:e.target.checked})} />
                            <span className="cp-legal-check-box"><I n={legalAccepted[lm.key] ? 'check_box' : 'check_box_outline_blank'} /></span>
                            <div><span className="cp-legal-label">{lm.label}{lm.required && <span style={{color:'#ef4444'}}> *</span>}</span></div>
                          </label>
                        ))}
                      </div>
                    )}
                    {canSign && (
                      <div className="cp-card" style={{marginBottom:16}} data-testid="cp-signature-section">
                        <h3 style={{margin:'0 0 12px',fontSize:'.9375rem'}}>Digitale Unterschrift</h3>
                        <div className="cp-sig-toggle">
                          <button className={`cp-sig-btn ${signatureType==='canvas'?'active':''}`} onClick={() => setSignatureType('canvas')} data-testid="cp-sig-canvas-btn"><I n="draw"/> Zeichnen</button>
                          <button className={`cp-sig-btn ${signatureType==='name'?'active':''}`} onClick={() => setSignatureType('name')} data-testid="cp-sig-name-btn"><I n="edit"/> Name eingeben</button>
                        </div>
                        {signatureType === 'canvas' ? (
                          <div className="cp-canvas-wrap">
                            <canvas ref={canvasRef} className="cp-sig-canvas" data-testid="cp-sig-canvas" onMouseDown={startDraw} onMouseMove={draw} onMouseUp={endDraw} onMouseLeave={endDraw} onTouchStart={startDraw} onTouchMove={draw} onTouchEnd={endDraw} />
                            <button className="cp-btn cp-btn-secondary cp-btn-sm" onClick={clearCanvas} style={{marginTop:8}} data-testid="cp-sig-clear"><I n="delete"/> Löschen</button>
                            {signatureData && <p style={{fontSize:'.6875rem',color:'#10b981',marginTop:4}}>Unterschrift erfasst</p>}
                          </div>
                        ) : (
                          <div>
                            <input type="text" className="cp-sig-name-input" value={signatureName} onChange={e => setSignatureName(e.target.value)} placeholder="Vor- und Nachname" data-testid="cp-sig-name-input" />
                            {signatureName.trim().length >= 2 && <p style={{fontSize:'.6875rem',color:'#10b981',marginTop:4}}>Name erfasst</p>}
                          </div>
                        )}
                      </div>
                    )}
                    {canSign && (
                      <div className="cp-contract-actions" data-testid="cp-contract-actions">
                        <button className="cp-btn cp-btn-accept" onClick={acceptContract} disabled={!allRequiredLegalAccepted()||!hasValidSignature()||!!contractBusy} data-testid="cp-accept-contract">{contractBusy==='accepting' ? 'Wird verarbeitet...' : <><I n="verified"/> Vertrag annehmen</>}</button>
                        <button className="cp-btn cp-btn-secondary" onClick={() => setShowChangeReq(!showChangeReq)} disabled={!!contractBusy} data-testid="cp-change-contract"><I n="edit_note"/> Änderung anfragen</button>
                        <button className="cp-btn cp-btn-danger" onClick={() => setShowDecline(!showDecline)} disabled={!!contractBusy} data-testid="cp-decline-contract"><I n="cancel"/> Ablehnen</button>
                      </div>
                    )}
                    {showChangeReq && canSign && (
                      <div className="cp-revision-form" style={{marginTop:12}} data-testid="cp-change-form">
                        <textarea value={changeRequest} onChange={e => setChangeRequest(e.target.value)} rows={3} placeholder="Welche Änderungen wünschen Sie?" />
                        <div style={{display:'flex',gap:8,marginTop:8}}><button className="cp-btn cp-btn-primary cp-btn-sm" onClick={requestChange} disabled={!changeRequest.trim()||!!contractBusy}>Anfrage senden</button><button className="cp-btn cp-btn-secondary cp-btn-sm" onClick={() => setShowChangeReq(false)}>Abbrechen</button></div>
                      </div>
                    )}
                    {showDecline && canSign && (
                      <div className="cp-revision-form" style={{marginTop:12}} data-testid="cp-decline-form">
                        <textarea value={declineReason} onChange={e => setDeclineReason(e.target.value)} rows={3} placeholder="Grund der Ablehnung (optional)" />
                        <div style={{display:'flex',gap:8,marginTop:8}}><button className="cp-btn cp-btn-danger cp-btn-sm" onClick={declineContract} disabled={!!contractBusy}>Vertrag ablehnen</button><button className="cp-btn cp-btn-secondary cp-btn-sm" onClick={() => setShowDecline(false)}>Abbrechen</button></div>
                      </div>
                    )}
                  </div>
                );
              })() : (
                <>
                  <h2>Ihre Verträge</h2>
                  {contracts.length === 0 ? <div className="cp-empty"><I n="gavel" /><p>Noch keine Verträge vorhanden.</p></div> : contracts.map(c => {
                    const CTR_S = { draft:{l:'Entwurf',c:'#6b7b8d'}, sent:{l:'Zur Prüfung',c:'#3b82f6'}, viewed:{l:'Eingesehen',c:'#06b6d4'}, accepted:{l:'Angenommen',c:'#10b981'}, declined:{l:'Abgelehnt',c:'#ef4444'}, change_requested:{l:'Änderung angefragt',c:'#f97316'} };
                    const st = CTR_S[c.status] || { l: c.status, c: '#6b7b8d' };
                    return (
                      <div key={c.contract_id} className="cp-card" style={{cursor:'pointer'}} onClick={() => loadContractDetail(c.contract_id)} data-testid={`cp-contract-${c.contract_id}`}>
                        <div className="cp-card-header"><span className="cp-card-title">{c.contract_number}</span><span className="cp-badge" style={{background:st.c+'22',color:st.c}}>{st.l}</span></div>
                        <div className="cp-card-body"><span>{{standard:'Standardvertrag',individual:'Individualvertrag',amendment:'Nachtrag'}[c.contract_type]||c.contract_type}</span><span className="cp-card-price">{fmtEur(c.calculation?.total_contract_eur)}</span></div>
                        <div className="cp-card-footer"><span>{fmtDate(c.created_at)}</span>{['sent','viewed'].includes(c.status) && <span className="cp-btn cp-btn-primary cp-btn-sm">Vertrag prüfen</span>}</div>
                      </div>
                    );
                  })}
                </>
              )}
            </div>
          )}

          {/* ══════════ PROJECTS ══════════ */}
          {tab === 'projects' && (
            <div data-testid="cp-projects">
              {selectedProject && projectDetail ? (() => {
                const pd = projectDetail;
                const PRJ_S = { draft:{l:'Entwurf',c:'#6b7b8d'}, discovery:{l:'Discovery',c:'#3b82f6'}, planning:{l:'Planung',c:'#f59e0b'}, approved:{l:'Freigegeben',c:'#10b981'}, build:{l:'Build',c:'#8b5cf6'}, review:{l:'Review',c:'#ec4899'}, handover:{l:'Handover',c:'#06b6d4'}, live:{l:'Live',c:'#22c55e'}, paused:{l:'Pausiert',c:'#f97316'}, closed:{l:'Abgeschlossen',c:'#64748b'} };
                const st = PRJ_S[pd.status] || PRJ_S.draft;
                return (
                  <div data-testid="cp-project-detail">
                    <button className="cp-btn cp-btn-secondary cp-btn-sm" onClick={() => { setSelectedProject(null); setProjectDetail(null); }} data-testid="cp-project-back"><I n="arrow_back" /> Alle Projekte</button>
                    <div style={{display:'flex',alignItems:'center',gap:12,margin:'20px 0 16px',flexWrap:'wrap'}}>
                      <h2 style={{margin:0}}>{pd.title}</h2><span className="cp-badge" style={{background:st.c+'22',color:st.c}}>{st.l}</span>
                      <span className="cp-badge" style={{background:'rgba(255,107,0,0.12)',color:'#FF6B00'}}>{pd.completeness||0}% abgeschlossen</span>
                    </div>
                    <div style={{background:'rgba(255,255,255,0.04)',borderRadius:6,height:8,marginBottom:20,overflow:'hidden'}}>
                      <div style={{background:'linear-gradient(90deg,#FF6B00,#FF8533)',height:'100%',width:`${pd.completeness||0}%`,borderRadius:6,transition:'width .5s'}}></div>
                    </div>
                    {(pd.sections || []).length > 0 && (
                      <div style={{marginBottom:24}}><h3 style={{fontSize:'.9375rem',marginBottom:12}}>Projektdokumentation</h3>
                        {pd.sections.map(s => (
                          <div key={s.section_id} className="cp-card" style={{marginBottom:8,borderLeft:`3px solid ${s.status==='freigegeben'?'#10b981':s.status==='review'?'#3b82f6':'#f59e0b'}`}} data-testid={`cp-section-${s.section_key}`}>
                            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:6}}><span style={{fontWeight:600,color:'#fff',fontSize:'.8125rem'}}>{s.label}</span><span className="cp-badge" style={{background:s.status==='freigegeben'?'#10b98122':'#f59e0b22',color:s.status==='freigegeben'?'#10b981':'#f59e0b',fontSize:'.625rem'}}>{s.status} v{s.version}</span></div>
                            <p style={{fontSize:'.8125rem',color:'#c8d1dc',whiteSpace:'pre-wrap',lineHeight:1.6}}>{s.content}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    <h3 style={{fontSize:'.9375rem',marginBottom:12}}>Projektchat</h3>
                    <div className="cp-card">
                      <div style={{maxHeight:300,overflowY:'auto',marginBottom:12}}>
                        {(pd.chat || []).map(m => (
                          <div key={m.message_id} style={{marginBottom:8,padding:'8px 12px',background:m.sender_type==='customer'?'rgba(255,107,0,0.06)':'rgba(59,130,246,0.06)',borderRadius:6,borderLeft:`3px solid ${m.sender_type==='customer'?'#FF6B00':'#3b82f6'}`}}>
                            <div style={{display:'flex',justifyContent:'space-between',fontSize:'.6875rem',color:'#6b7b8d',marginBottom:2}}><span>{m.sender_type==='customer'?'Sie':'NeXifyAI'}</span><span>{fmtTime(m.timestamp)}</span></div>
                            <div style={{fontSize:'.8125rem',color:'#c8d1dc',whiteSpace:'pre-wrap'}}>{m.content}</div>
                          </div>
                        ))}
                        {(!pd.chat || pd.chat.length === 0) && <div style={{textAlign:'center',padding:20,color:'#4a5568',fontSize:'.8125rem'}}>Noch keine Nachrichten</div>}
                      </div>
                      <div style={{display:'flex',gap:8}}>
                        <input style={{flex:1,background:'rgba(14,20,28,0.6)',border:'1px solid rgba(255,255,255,0.06)',color:'#fff',padding:'10px 14px',fontSize:'.8125rem',borderRadius:4}} value={projectChatMsg} onChange={e => setProjectChatMsg(e.target.value)} placeholder="Nachricht schreiben..." onKeyDown={e => { if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendProjectChatMsg();}}} data-testid="cp-project-chat-input" />
                        <button className="cp-btn cp-btn-primary" style={{flexShrink:0}} onClick={sendProjectChatMsg} disabled={!projectChatMsg.trim()} data-testid="cp-project-chat-send"><I n="send" /></button>
                      </div>
                    </div>
                  </div>
                );
              })() : (
                <>
                  <h2>Ihre Projekte</h2>
                  {projects.length === 0 ? <div className="cp-empty"><I n="folder_special" /><p>Noch keine Projekte vorhanden.</p></div> : projects.map(p => {
                    const PRJ_S = { draft:{l:'Entwurf',c:'#6b7b8d'}, discovery:{l:'Discovery',c:'#3b82f6'}, planning:{l:'Planung',c:'#f59e0b'}, build:{l:'Build',c:'#8b5cf6'}, live:{l:'Live',c:'#22c55e'} };
                    const st = PRJ_S[p.status] || { l: p.status, c: '#6b7b8d' };
                    return (
                      <div key={p.project_id} className="cp-card" style={{cursor:'pointer'}} onClick={() => loadProjectDetail(p.project_id)} data-testid={`cp-project-${p.project_id}`}>
                        <div className="cp-card-header"><span className="cp-card-title">{p.title}</span><span className="cp-badge" style={{background:st.c+'22',color:st.c}}>{st.l}</span></div>
                        <div className="cp-card-body"><span>{p.tier||'-'}</span><span style={{color:'#FF6B00',fontWeight:600}}>{p.completeness||0}%</span></div>
                        <div className="cp-card-footer"><span>{fmtDate(p.created_at)}</span></div>
                      </div>
                    );
                  })}
                </>
              )}
            </div>
          )}

          {/* ══════════ QUOTES ══════════ */}
          {tab === 'quotes' && (
            <div data-testid="cp-quotes">
              <h2>Ihre Angebote</h2>
              {(!data?.quotes || data.quotes.length === 0) ? <div className="cp-empty"><I n="description" /><p>Noch keine Angebote vorhanden.</p><button className="cp-btn cp-btn-primary" onClick={() => { setTab('requests'); setShowNewRequest(true); }} style={{marginTop:12}}>Angebot anfragen</button></div> : data.quotes.map(q => {
                const s = QUOTE_STATUS[q.status] || { l: q.status, c: '#6b7b8d' };
                return (
                  <div key={q.quote_id} className="cp-card" data-testid={`cp-quote-card-${q.quote_id}`}>
                    <div className="cp-card-header"><span className="cp-card-title">{q.quote_number}</span><span className="cp-badge" style={{background:s.c+'22',color:s.c}}><I n={s.i||'circle'}/> {s.l}</span></div>
                    <div className="cp-card-body"><span>{q.calculation?.tier_name || q.tier}</span><span className="cp-card-price">{fmtEur(q.calculation?.total_contract_eur)}</span></div>
                    <div className="cp-card-actions">
                      {(q.status === 'sent' || q.status === 'opened') && (<>
                        <button className="cp-btn cp-btn-accept" onClick={() => quoteAction(q.quote_id,'accept')} disabled={!!actionBusy} data-testid={`cp-accept-${q.quote_id}`}><I n="check_circle"/> Annehmen</button>
                        <button className="cp-btn cp-btn-danger" onClick={() => quoteAction(q.quote_id,'decline')} disabled={!!actionBusy} data-testid={`cp-decline-${q.quote_id}`}><I n="cancel"/> Ablehnen</button>
                        <button className="cp-btn cp-btn-secondary" onClick={() => { setShowRevision(q.quote_id); setRevisionNotes(''); }} data-testid={`cp-revision-${q.quote_id}`}><I n="edit_note"/> Änderung anfragen</button>
                      </>)}
                      <a href={`${API}/api/documents/quote/${q.quote_id}/pdf`} target="_blank" rel="noreferrer" className="cp-btn cp-btn-secondary" data-testid={`cp-dl-quote-${q.quote_id}`}><I n="picture_as_pdf"/> PDF</a>
                    </div>
                    {showRevision === q.quote_id && (
                      <div className="cp-revision-form" data-testid="cp-revision-form">
                        <textarea value={revisionNotes} onChange={e => setRevisionNotes(e.target.value)} placeholder="Welche Änderungen wünschen Sie?" rows={3} />
                        <div style={{display:'flex',gap:8,marginTop:8}}>
                          <button className="cp-btn cp-btn-primary cp-btn-sm" onClick={() => { quoteAction(q.quote_id,'revision',{notes:revisionNotes}); setShowRevision(null); }} disabled={!revisionNotes.trim()}>Absenden</button>
                          <button className="cp-btn cp-btn-secondary cp-btn-sm" onClick={() => setShowRevision(null)}>Abbrechen</button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* ══════════ FINANCE ══════════ */}
          {tab === 'invoices' && (
            <div data-testid="cp-finance">
              <h2>Ihre Finanzen</h2>
              {financeLoading ? <div className="cp-empty"><div className="cp-spinner"></div><p>Finanzdaten laden...</p></div> : financeData ? (
                <>
                  <div className="cp-stat-grid cp-finance-summary" data-testid="cp-finance-summary">
                    <div className="cp-stat"><I n="receipt_long"/><div className="cp-stat-val">{financeData.summary.total_invoices}</div><div className="cp-stat-label">Rechnungen</div></div>
                    <div className="cp-stat"><I n="pending_actions"/><div className="cp-stat-val" style={{color:financeData.summary.open_invoices > 0 ? '#f59e0b':'#10b981'}}>{financeData.summary.open_invoices}</div><div className="cp-stat-label">Offen</div></div>
                    <div className="cp-stat"><I n="payments"/><div className="cp-stat-val" style={{color:'#10b981'}}>{fmtEur(financeData.summary.total_paid_eur)}</div><div className="cp-stat-label">Bezahlt</div></div>
                    <div className="cp-stat"><I n="account_balance_wallet"/><div className="cp-stat-val" style={{color:financeData.summary.total_outstanding_eur > 0 ? '#f59e0b':'#10b981'}}>{fmtEur(financeData.summary.total_outstanding_eur)}</div><div className="cp-stat-label">Ausstehend</div></div>
                  </div>
                  {financeData.summary.overdue_invoices > 0 && (
                    <div className="cp-finance-alert cp-finance-alert-warning" data-testid="cp-finance-overdue-alert"><I n="warning"/><div><strong>{financeData.summary.overdue_invoices} Rechnung{financeData.summary.overdue_invoices>1?'en':''} überfällig</strong><p>Bitte begleichen Sie offene Rechnungen zeitnah.</p></div></div>
                  )}
                  <div className="cp-finance-section"><h3>Rechnungen</h3>
                    {financeData.invoices.length === 0 ? <div className="cp-empty"><I n="receipt"/><p>Noch keine Rechnungen.</p></div> : financeData.invoices.map(inv => {
                      const sc = {success:'#10b981',warning:'#f59e0b',error:'#ef4444',neutral:'#6b7b8d'}[inv.payment_status_severity]||'#6b7b8d';
                      return (
                        <div key={inv.invoice_id} className={`cp-card cp-finance-card ${inv.is_overdue?'cp-card-overdue':''}`} data-testid={`cp-fin-inv-${inv.invoice_id}`}>
                          <div className="cp-card-header"><div className="cp-finance-card-title"><span className="cp-card-title">{inv.invoice_number}</span>{inv.type==='deposit'&&<span className="cp-badge cp-badge-sm" style={{background:'#3b82f622',color:'#3b82f6'}}>Anzahlung</span>}</div><span className="cp-badge" style={{background:sc+'22',color:sc}}><I n={inv.payment_status==='paid'?'check_circle':inv.is_overdue?'error':'schedule'}/>{inv.payment_status_label}</span></div>
                          <div className="cp-finance-card-body">
                            <div className="cp-finance-detail-grid">
                              <div className="cp-finance-detail"><span className="cp-finance-label">Netto</span><span className="cp-finance-value">{fmtEur(inv.amount_net)}</span></div>
                              <div className="cp-finance-detail"><span className="cp-finance-label">USt. ({inv.vat_rate}%)</span><span className="cp-finance-value">{fmtEur(inv.amount_vat)}</span></div>
                              <div className="cp-finance-detail cp-finance-detail-total"><span className="cp-finance-label">Brutto</span><span className="cp-finance-value cp-finance-total">{fmtEur(inv.amount_gross)}</span></div>
                              <div className="cp-finance-detail"><span className="cp-finance-label">Rechnungsdatum</span><span className="cp-finance-value">{inv.date}</span></div>
                              <div className="cp-finance-detail"><span className="cp-finance-label">Fällig bis</span><span className="cp-finance-value" style={{color:inv.is_overdue?'#ef4444':'inherit'}}>{inv.due_date}</span></div>
                              {inv.reminder_count > 0 && <div className="cp-finance-detail"><span className="cp-finance-label">Mahnstufe</span><span className="cp-finance-value" style={{color:'#ef4444'}}>{inv.reminder_level}</span></div>}
                            </div>
                          </div>
                          <div className="cp-card-actions cp-finance-actions">
                            {inv.has_pdf && <a href={`${API}${inv.pdf_url}`} target="_blank" rel="noreferrer" className="cp-btn cp-btn-secondary"><I n="picture_as_pdf"/> PDF</a>}
                            {inv.checkout_url && inv.payment_status !== 'paid' && <a href={inv.checkout_url} target="_blank" rel="noreferrer" className="cp-btn cp-btn-primary"><I n="payment"/> Jetzt bezahlen</a>}
                          </div>
                          {inv.payment_status !== 'paid' && inv.payment_status !== 'cancelled' && (
                            <div className="cp-finance-bank">
                              <div className="cp-finance-bank-header"><I n="account_balance"/> <span>Banküberweisung</span></div>
                              <div className="cp-finance-bank-grid">
                                <div><span className="cp-finance-label">Empfänger</span><span>{financeData.bank_transfer_info.account_holder}</span></div>
                                <div><span className="cp-finance-label">IBAN</span><span className="cp-finance-mono">{financeData.bank_transfer_info.iban}</span></div>
                                <div><span className="cp-finance-label">BIC</span><span className="cp-finance-mono">{financeData.bank_transfer_info.bic}</span></div>
                                <div><span className="cp-finance-label">Verwendungszweck</span><span className="cp-finance-mono cp-finance-ref">{inv.payment_reference}</span></div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : <div className="cp-empty"><I n="account_balance"/><p>Finanzdaten nicht verfügbar.</p><button className="cp-btn cp-btn-secondary" onClick={loadFinance}>Erneut laden</button></div>}
            </div>
          )}

          {/* ══════════ BOOKINGS ══════════ */}
          {tab === 'bookings' && (
            <div data-testid="cp-bookings">
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:20}}>
                <h2 style={{margin:0}}>Ihre Termine</h2>
                <button className="cp-btn cp-btn-primary" onClick={() => setShowNewBooking(true)} data-testid="cp-new-booking-btn"><I n="calendar_add_on"/> Termin buchen</button>
              </div>
              {showNewBooking && (
                <div className="cp-card" style={{marginBottom:20,borderColor:'rgba(255,107,0,0.2)'}} data-testid="cp-booking-form">
                  <h3 style={{margin:'0 0 16px',fontSize:'.9375rem'}}>Neuen Termin buchen</h3>
                  <div className="cp-form">
                    <div className="cp-form-grid">
                      <div className="cp-field"><label>Datum</label><input type="date" value={bookingForm.date} onChange={e => setBookingForm({...bookingForm, date: e.target.value})} data-testid="cp-bk-date" /></div>
                      <div className="cp-field"><label>Uhrzeit</label><input type="time" value={bookingForm.time} onChange={e => setBookingForm({...bookingForm, time: e.target.value})} data-testid="cp-bk-time" /></div>
                      <div className="cp-field"><label>Art</label><select value={bookingForm.type} onChange={e => setBookingForm({...bookingForm, type: e.target.value})} data-testid="cp-bk-type">
                        <option value="beratung">Erstberatung</option><option value="review">Projekt-Review</option><option value="strategy">Strategie-Call</option><option value="support">Support-Termin</option>
                      </select></div>
                    </div>
                    <div className="cp-field"><label>Anmerkungen (optional)</label><textarea rows={2} value={bookingForm.notes} onChange={e => setBookingForm({...bookingForm, notes: e.target.value})} placeholder="Themen oder Fragen für den Termin..." data-testid="cp-bk-notes" /></div>
                    <div style={{display:'flex',gap:8}}><button className="cp-btn cp-btn-primary" onClick={submitBooking} disabled={formBusy||!bookingForm.date||!bookingForm.time} data-testid="cp-bk-submit">{formBusy ? 'Wird gebucht...' : 'Termin anfragen'}</button><button className="cp-btn cp-btn-secondary" onClick={() => setShowNewBooking(false)}>Abbrechen</button></div>
                  </div>
                </div>
              )}
              {(!data?.bookings || data.bookings.length === 0) && !showNewBooking ? (
                <div className="cp-empty"><I n="event"/><p>Noch keine Termine vorhanden.</p></div>
              ) : (data?.bookings || []).map(bk => (
                <div key={bk.booking_id} className="cp-card" data-testid={`cp-bk-${bk.booking_id}`}>
                  <div className="cp-card-header"><span className="cp-card-title">{bk.date} um {bk.time}</span><span className="cp-badge" style={{background:'#3b82f622',color:'#3b82f6'}}><I n="event"/> {bk.status}</span></div>
                  {bk.type && <div className="cp-card-body"><span>{{beratung:'Erstberatung',review:'Projekt-Review',strategy:'Strategie-Call',support:'Support-Termin'}[bk.type]||bk.type}</span></div>}
                  {bk.notes && <p style={{fontSize:'.8125rem',color:'#6b7b8d',margin:'8px 0 0'}}>{bk.notes}</p>}
                </div>
              ))}
            </div>
          )}

          {/* ══════════ MESSAGES ══════════ */}
          {tab === 'messages' && (
            <div data-testid="cp-messages">
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:20}}>
                <h2 style={{margin:0}}>Nachrichten</h2>
                <button className="cp-btn cp-btn-primary" onClick={() => setShowNewMessage(true)} data-testid="cp-new-message-btn"><I n="edit"/> Neue Nachricht</button>
              </div>
              {showNewMessage && (
                <div className="cp-card" style={{marginBottom:20,borderColor:'rgba(255,107,0,0.2)'}} data-testid="cp-message-form">
                  <h3 style={{margin:'0 0 16px',fontSize:'.9375rem'}}>Nachricht an das Team</h3>
                  <div className="cp-form">
                    <div className="cp-form-grid">
                      <div className="cp-field"><label>Betreff</label><input type="text" value={messageForm.subject} onChange={e => setMessageForm({...messageForm, subject: e.target.value})} placeholder="Betreff Ihrer Nachricht" data-testid="cp-msg-subject" /></div>
                      <div className="cp-field"><label>Kategorie</label><select value={messageForm.category} onChange={e => setMessageForm({...messageForm, category: e.target.value})} data-testid="cp-msg-category">
                        <option value="general">Allgemein</option><option value="project">Projekt</option><option value="billing">Rechnung / Zahlung</option><option value="feedback">Feedback</option>
                      </select></div>
                    </div>
                    <div className="cp-field"><label>Nachricht</label><textarea rows={4} value={messageForm.content} onChange={e => setMessageForm({...messageForm, content: e.target.value})} placeholder="Ihre Nachricht..." data-testid="cp-msg-content" /></div>
                    <div style={{display:'flex',gap:8}}><button className="cp-btn cp-btn-primary" onClick={submitMessage} disabled={formBusy||!messageForm.content.trim()} data-testid="cp-msg-submit">{formBusy ? 'Wird gesendet...' : 'Nachricht senden'}</button><button className="cp-btn cp-btn-secondary" onClick={() => setShowNewMessage(false)}>Abbrechen</button></div>
                  </div>
                </div>
              )}
              {customerMessages.length === 0 && !showNewMessage ? (
                <div className="cp-empty"><I n="chat"/><p>Noch keine Nachrichten gesendet.</p></div>
              ) : customerMessages.map(m => {
                const catMap = { general:'Allgemein', project:'Projekt', billing:'Rechnung', feedback:'Feedback' };
                const stMap = { unread:{l:'Gesendet',c:'#3b82f6'}, read:{l:'Gelesen',c:'#10b981'}, replied:{l:'Beantwortet',c:'#FF6B00'} };
                const st = stMap[m.status] || stMap.unread;
                return (
                  <div key={m.message_id} className="cp-card" data-testid={`cp-msg-${m.message_id}`}>
                    <div className="cp-card-header"><span className="cp-card-title">{m.subject || 'Nachricht'}</span><span className="cp-badge" style={{background:st.c+'22',color:st.c}}>{st.l}</span></div>
                    <p style={{fontSize:'.8125rem',color:'#c8d1dc',margin:'4px 0',lineHeight:1.5}}>{m.content}</p>
                    <div className="cp-card-footer"><span>{catMap[m.category] || m.category}</span><span>{fmtTime(m.created_at)}</span></div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ══════════ SUPPORT ══════════ */}
          {tab === 'support' && (
            <div data-testid="cp-support">
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:20}}>
                <h2 style={{margin:0}}>Support</h2>
                <button className="cp-btn cp-btn-primary" onClick={() => setShowNewTicket(true)} data-testid="cp-new-ticket-btn"><I n="add"/> Neues Ticket</button>
              </div>
              {showNewTicket && (
                <div className="cp-card" style={{marginBottom:20,borderColor:'rgba(255,107,0,0.2)'}} data-testid="cp-ticket-form">
                  <h3 style={{margin:'0 0 16px',fontSize:'.9375rem'}}>Support-Ticket erstellen</h3>
                  <div className="cp-form">
                    <div className="cp-form-grid">
                      <div className="cp-field"><label>Kategorie</label><select value={ticketForm.category} onChange={e => setTicketForm({...ticketForm, category: e.target.value})} data-testid="cp-tkt-category">
                        <option value="general">Allgemein</option><option value="technical">Technisch</option><option value="billing">Abrechnung</option><option value="contract">Vertrag</option><option value="project">Projekt</option>
                      </select></div>
                      <div className="cp-field"><label>Priorität</label><select value={ticketForm.priority} onChange={e => setTicketForm({...ticketForm, priority: e.target.value})} data-testid="cp-tkt-priority">
                        <option value="low">Niedrig</option><option value="normal">Normal</option><option value="high">Hoch</option><option value="critical">Kritisch</option>
                      </select></div>
                    </div>
                    <div className="cp-field"><label>Betreff</label><input type="text" value={ticketForm.subject} onChange={e => setTicketForm({...ticketForm, subject: e.target.value})} placeholder="Kurze Beschreibung des Problems" data-testid="cp-tkt-subject" /></div>
                    <div className="cp-field"><label>Beschreibung</label><textarea rows={4} value={ticketForm.description} onChange={e => setTicketForm({...ticketForm, description: e.target.value})} placeholder="Beschreiben Sie das Problem oder Ihre Frage..." data-testid="cp-tkt-description" /></div>
                    <div style={{display:'flex',gap:8}}><button className="cp-btn cp-btn-primary" onClick={submitTicket} disabled={formBusy||!ticketForm.subject.trim()||!ticketForm.description.trim()} data-testid="cp-tkt-submit">{formBusy ? 'Wird erstellt...' : 'Ticket erstellen'}</button><button className="cp-btn cp-btn-secondary" onClick={() => setShowNewTicket(false)}>Abbrechen</button></div>
                  </div>
                </div>
              )}
              {supportTickets.length === 0 && !showNewTicket ? (
                <div className="cp-empty"><I n="support_agent"/><p>Noch keine Support-Tickets vorhanden.</p></div>
              ) : supportTickets.map(t => {
                const priMap = { low:{l:'Niedrig',c:'#6b7b8d'}, normal:{l:'Normal',c:'#3b82f6'}, high:{l:'Hoch',c:'#f59e0b'}, critical:{l:'Kritisch',c:'#ef4444'} };
                const stMap = { open:{l:'Offen',c:'#3b82f6'}, in_progress:{l:'In Bearbeitung',c:'#f59e0b'}, resolved:{l:'Gelöst',c:'#10b981'}, closed:{l:'Geschlossen',c:'#6b7b8d'} };
                const pr = priMap[t.priority] || priMap.normal;
                const st = stMap[t.status] || stMap.open;
                return (
                  <div key={t.ticket_id} className="cp-card" data-testid={`cp-tkt-${t.ticket_id}`}>
                    <div className="cp-card-header"><span className="cp-card-title">{t.subject}</span><div style={{display:'flex',gap:6}}><span className="cp-badge" style={{background:pr.c+'22',color:pr.c}}>{pr.l}</span><span className="cp-badge" style={{background:st.c+'22',color:st.c}}>{st.l}</span></div></div>
                    <p style={{fontSize:'.8125rem',color:'#c8d1dc',margin:'4px 0',lineHeight:1.5}}>{t.description}</p>
                    <div className="cp-card-footer"><span>{{general:'Allgemein',technical:'Technisch',billing:'Abrechnung',contract:'Vertrag',project:'Projekt'}[t.category]||t.category}</span><span>{fmtTime(t.created_at)}</span></div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ══════════ COMMUNICATION ══════════ */}
          {tab === 'communication' && (
            <div data-testid="cp-communication">
              <h2>Kommunikation</h2>
              {(!data?.communications || data.communications.length === 0) ? (
                <div className="cp-empty"><I n="forum"/><p>Noch keine Kommunikation vorhanden.</p><button className="cp-btn cp-btn-primary" onClick={() => { setTab('messages'); setShowNewMessage(true); }} style={{marginTop:12}}>Nachricht senden</button></div>
              ) : data.communications.map((c, i) => {
                const isConvo = c.type === 'conversation';
                return (
                  <div key={i} className="cp-card cp-comm-card" data-testid={`cp-comm-${i}`}>
                    <div className="cp-card-header"><span className="cp-card-title">{c.subject || c.channel || 'Gespräch'}</span><span className="cp-card-date">{fmtDate(c.date || c.created_at)}</span></div>
                    <div className="cp-comm-messages">
                      {(c.messages || []).slice(0, 4).map((m, j) => (
                        <div key={j} className={`cp-comm-msg ${m.role==='user' || m.sender_type==='customer' ? 'user' : 'ai'}`}>
                          <span className="cp-comm-role">{m.role === 'user' || m.sender_type === 'customer' ? 'Sie' : 'NeXifyAI'}</span>
                          <span className="cp-comm-text">{m.content}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ══════════ DOCUMENTS ══════════ */}
          {tab === 'documents' && (
            <div data-testid="cp-documents">
              <h2>Ihre Dokumente</h2>
              {docsLoading ? <div className="cp-empty"><div className="cp-spinner"></div><p>Dokumente laden...</p></div> : customerDocs.length === 0 ? (
                <div className="cp-empty"><I n="folder_open"/><p>Noch keine Dokumente vorhanden.</p></div>
              ) : (
                <div className="cp-doc-list">
                  {customerDocs.map(doc => (
                    <div key={doc.document_id} className="cp-card cp-doc-item" data-testid={`cp-doc-${doc.document_id}`}>
                      <div className="cp-doc-icon"><I n={{pdf:'picture_as_pdf',contract:'gavel',invoice:'receipt',quote:'description'}[doc.type]||'description'}/></div>
                      <div className="cp-doc-info"><div className="cp-doc-label">{doc.title || doc.document_id}</div><div className="cp-doc-meta"><span className="cp-badge cp-badge-sm" style={{background:'rgba(255,107,0,0.1)',color:'#FF6B00'}}>{doc.type}</span><span className="cp-doc-date">{fmtDate(doc.created_at)}</span></div></div>
                      {doc.download_url && <a href={`${API}${doc.download_url}`} target="_blank" rel="noreferrer" className="cp-btn cp-btn-sm"><I n="download"/> Herunterladen</a>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ══════════ TIMELINE ══════════ */}
          {tab === 'timeline' && (
            <div data-testid="cp-timeline">
              <h2>Aktivitäten</h2>
              {(!data?.timeline || data.timeline.length === 0) ? <div className="cp-empty"><I n="timeline"/><p>Noch keine Aktivitäten.</p></div> : (
                <div className="cp-timeline-list">
                  {data.timeline.map((ev, i) => (
                    <div key={i} className="cp-timeline-item" data-testid={`cp-tl-${i}`}>
                      <div className="cp-timeline-dot"></div>
                      <div className="cp-timeline-content">
                        <span className="cp-timeline-action">{ev.action}</span>
                        {ev.entity_type && <span className="cp-badge cp-badge-sm" style={{background:'rgba(255,107,0,0.1)',color:'#FF6B00'}}>{ev.entity_type}</span>}
                        <span className="cp-timeline-date">{fmtTime(ev.timestamp || ev.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ══════════ SETTINGS ══════════ */}
          {tab === 'settings' && (
            <div data-testid="cp-settings">
              <h2>Einstellungen</h2>
              <div className="cp-card cp-settings-section">
                <h3><I n="person"/> Profil</h3>
                {profileData ? (
                  <>
                    <div className="cp-form-grid">
                      <div className="cp-field"><label>Vorname</label><input value={profileForm.first_name} onChange={e => setProfileForm({...profileForm, first_name: e.target.value})} data-testid="cp-profile-firstname" /></div>
                      <div className="cp-field"><label>Nachname</label><input value={profileForm.last_name} onChange={e => setProfileForm({...profileForm, last_name: e.target.value})} data-testid="cp-profile-lastname" /></div>
                      <div className="cp-field"><label>Telefon</label><input value={profileForm.phone} onChange={e => setProfileForm({...profileForm, phone: e.target.value})} data-testid="cp-profile-phone" /></div>
                      <div className="cp-field"><label>Unternehmen</label><input value={profileForm.company} onChange={e => setProfileForm({...profileForm, company: e.target.value})} data-testid="cp-profile-company" /></div>
                      <div className="cp-field"><label>Land</label><select value={profileForm.country} onChange={e => setProfileForm({...profileForm, country: e.target.value})} data-testid="cp-profile-country">
                        <option value="DE">Deutschland</option><option value="AT">Österreich</option><option value="CH">Schweiz</option><option value="NL">Niederlande</option>
                      </select></div>
                      <div className="cp-field"><label>E-Mail</label><input value={profileData.email||''} disabled /></div>
                    </div>
                    <button className="cp-btn cp-btn-primary" onClick={saveProfile} disabled={profileSaving} style={{marginTop:16}} data-testid="cp-save-profile">{profileSaving ? 'Speichern...' : 'Profil speichern'}</button>
                  </>
                ) : <p style={{color:'#6b7b8d'}}>Profildaten werden geladen...</p>}
              </div>
              {consentsData && (
                <div className="cp-card cp-settings-section">
                  <h3><I n="security"/> Datenschutz & Einwilligungen</h3>
                  <div className="cp-consent-row">
                    <div><div className="cp-consent-label">Marketing-Kommunikation</div><div className="cp-consent-desc">Neuigkeiten und Angebote per E-Mail erhalten</div></div>
                    <div className={`cp-toggle ${!consentsData.opted_out ? 'cp-toggle-active' : ''}`} onClick={() => toggleOptOut(!consentsData.opted_out)} data-testid="cp-marketing-toggle"><div className="cp-toggle-slider"></div></div>
                  </div>
                  {consentsData.history && consentsData.history.length > 0 && (
                    <div style={{marginTop:16}}><h4 style={{fontSize:'.8125rem',color:'#fff',marginBottom:8}}>Einwilligungsverlauf</h4>
                      {consentsData.history.map((h, i) => <div key={i} className="cp-consent-entry"><I n={h.action==='opt_out'?'block':'check_circle'}/><span>{h.action === 'opt_out' ? 'Opt-Out' : 'Opt-In'} — {fmtTime(h.timestamp)}</span></div>)}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default CustomerPortal;
