import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const fmtEur = (v) => {
  if (v == null) return '';
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v);
};

export default function QuotePortal() {
  useEffect(() => { document.body.classList.add('hide-wa'); return () => document.body.classList.remove('hide-wa'); }, []);
  const [quote, setQuote] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [action, setAction] = useState(null);
  const [result, setResult] = useState(null);
  const [declineReason, setDeclineReason] = useState('');
  const [revisionFeedback, setRevisionFeedback] = useState('');
  const [panel, setPanel] = useState(null);
  /* Account Setup */
  const [accountStatus, setAccountStatus] = useState(null);
  const [showSetup, setShowSetup] = useState(false);
  const [setupPassword, setSetupPassword] = useState('');
  const [setupConfirm, setSetupConfirm] = useState('');
  const [setupLoading, setSetupLoading] = useState(false);
  const [setupError, setSetupError] = useState('');
  const [setupDone, setSetupDone] = useState(false);

  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');
  const qid = params.get('qid');

  useEffect(() => {
    if (!token || !qid) { setError('Kein gültiger Zugangslink.'); setLoading(false); return; }
    fetch(`${API}/api/portal/quote/${qid}?token=${encodeURIComponent(token)}`)
      .then(r => { if (!r.ok) throw new Error(r.status === 403 ? 'Zugangslink abgelaufen oder ungültig' : 'Fehler beim Laden'); return r.json(); })
      .then(d => {
        setQuote(d.quote);
        setCompany(d.company);
        setAccountStatus(d.account_status || null);
        if (d.account_status && !d.account_status.has_account) {
          setShowSetup(true);
        }
        setLoading(false);
      })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [token, qid]);

  const handleSetupAccount = async (e) => {
    e.preventDefault();
    setSetupError('');
    if (setupPassword.length < 8) { setSetupError('Mindestens 8 Zeichen erforderlich'); return; }
    if (setupPassword !== setupConfirm) { setSetupError('Passwörter stimmen nicht überein'); return; }
    setSetupLoading(true);
    try {
      const r = await fetch(`${API}/api/portal/setup-account`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, quote_id: qid, password: setupPassword })
      });
      if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.detail || 'Fehler bei der Kontoerstellung'); }
      const data = await r.json();
      if (data.access_token) {
        localStorage.setItem('nx_portal_token', data.access_token);
        localStorage.setItem('nx_portal_email', data.email);
        localStorage.setItem('nx_portal_name', data.name || '');
      }
      setSetupDone(true);
      setShowSetup(false);
    } catch (err) {
      setSetupError(err.message);
    } finally { setSetupLoading(false); }
  };

  const doAction = async (endpoint, body = null) => {
    setAction(endpoint);
    try {
      const opts = { method: 'POST' };
      if (body) { opts.headers = { 'Content-Type': 'application/json' }; opts.body = JSON.stringify(body); }
      const r = await fetch(`${API}/api/portal/quote/${qid}/${endpoint}?token=${encodeURIComponent(token)}`, opts);
      if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.detail || 'Fehler'); }
      return await r.json();
    } finally { setAction(null); }
  };

  const handleAccept = async () => {
    try {
      const data = await doAction('accept');
      setResult({ type: 'accepted', data });
    } catch (e) { setError(e.message); }
  };
  const handleDecline = async () => {
    try {
      const data = await doAction('decline', { reason: declineReason });
      setResult({ type: 'declined', data });
    } catch (e) { setError(e.message); }
  };
  const handleRevision = async () => {
    try {
      const data = await doAction('revision', { feedback: revisionFeedback });
      setResult({ type: 'revision', data });
      setPanel(null);
    } catch (e) { setError(e.message); }
  };

  const S = {
    page: { minHeight: '100vh', background: '#0a0e14', color: '#e2e8f0', fontFamily: "'Inter', system-ui, sans-serif", padding: '40px 20px' },
    card: { maxWidth: 720, margin: '0 auto', background: 'rgba(15,21,28,0.95)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: '36px 32px', boxShadow: '0 20px 60px rgba(0,0,0,0.4)' },
    accent: '#FE9B7B',
    h1: { fontSize: '1.75rem', fontWeight: 700, marginBottom: 4, color: '#fff' },
    sub: { fontSize: '.875rem', color: '#8a9bb0', marginBottom: 24 },
    section: { marginBottom: 24, padding: '16px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' },
    label: { fontSize: '.6875rem', color: '#6b7b8d', textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 4 },
    val: { fontSize: '.9375rem', color: '#c8d1dc', fontWeight: 500 },
    total: { fontSize: '1.5rem', color: '#FE9B7B', fontWeight: 700 },
    btn: (primary) => ({
      padding: '12px 24px', borderRadius: 8, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '.875rem',
      background: primary ? 'linear-gradient(135deg, #FE9B7B, #e8856a)' : 'rgba(255,255,255,0.06)',
      color: primary ? '#0a0e14' : '#c8d1dc',
      transition: 'all .2s',
    }),
    input: { width: '100%', padding: '12px 14px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.3)', color: '#e2e8f0', fontSize: '.875rem', outline: 'none' },
  };

  if (loading) return <div style={S.page}><div style={S.card}><p style={{textAlign:'center',color:'#8a9bb0'}}>Angebot wird geladen...</p></div></div>;
  if (error && !quote) return <div style={S.page}><div style={S.card}><p style={{textAlign:'center',color:'#ef4444'}}>{error}</p></div></div>;

  /* ─── ACCOUNT SETUP SCREEN ─── */
  if (showSetup && !setupDone) {
    return (
      <div style={S.page}>
        <div style={{...S.card, maxWidth: 520}}>
          <div style={{textAlign:'center', marginBottom: 32}}>
            <div style={{width:56,height:56,borderRadius:'50%',background:'linear-gradient(135deg,#FE9B7B,#e8856a)',display:'inline-flex',alignItems:'center',justifyContent:'center',marginBottom:16}}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0a0e14" strokeWidth="2"><path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            </div>
            <h1 style={S.h1}>Kundenportal einrichten</h1>
            <p style={S.sub}>Legen Sie Ihr Passwort fest, um Ihr persönliches Kundenportal zu aktivieren. Dort finden Sie Ihr Angebot und können es direkt annehmen.</p>
          </div>

          <div style={{padding:'16px 20px',borderRadius:8,background:'rgba(254,155,123,0.06)',border:'1px solid rgba(254,155,123,0.15)',marginBottom:24}}>
            <div style={S.label}>Ihr Konto</div>
            <div style={{...S.val, color:'#fff'}}>{accountStatus?.email}</div>
          </div>

          <form onSubmit={handleSetupAccount}>
            <div style={{marginBottom:16}}>
              <label style={{...S.label, display:'block', marginBottom:8}}>Passwort</label>
              <input
                data-testid="setup-password"
                type="password"
                style={S.input}
                placeholder="Mindestens 8 Zeichen"
                value={setupPassword}
                onChange={e => setSetupPassword(e.target.value)}
                autoFocus
              />
            </div>
            <div style={{marginBottom:24}}>
              <label style={{...S.label, display:'block', marginBottom:8}}>Passwort bestätigen</label>
              <input
                data-testid="setup-password-confirm"
                type="password"
                style={S.input}
                placeholder="Passwort wiederholen"
                value={setupConfirm}
                onChange={e => setSetupConfirm(e.target.value)}
              />
            </div>

            {setupError && <p style={{color:'#ef4444',fontSize:'.8125rem',marginBottom:16}} data-testid="setup-error">{setupError}</p>}

            <button
              data-testid="setup-submit"
              type="submit"
              disabled={setupLoading}
              style={{...S.btn(true), width:'100%', padding:'14px', fontSize:'.9375rem', opacity: setupLoading ? 0.7 : 1}}
            >
              {setupLoading ? 'Wird eingerichtet...' : 'Portal aktivieren & Angebot öffnen'}
            </button>
          </form>

          <p style={{fontSize:'.75rem',color:'#4a5568',textAlign:'center',marginTop:16}}>
            Nach der Aktivierung können Sie sich jederzeit unter <strong style={{color:'#8a9bb0'}}>nexifyai.cloud/login</strong> mit Ihrer E-Mail und diesem Passwort anmelden.
          </p>
        </div>
      </div>
    );
  }

  /* ─── SUCCESS SCREEN ─── */
  if (result) {
    return (
      <div style={S.page}>
        <div style={S.card}>
          <div style={{textAlign:'center',padding:'20px 0'}}>
            <div style={{width:64,height:64,borderRadius:'50%',background:result.type==='accepted'?'rgba(16,185,129,0.12)':'rgba(239,68,68,0.12)',display:'inline-flex',alignItems:'center',justifyContent:'center',marginBottom:16}}>
              <span style={{fontSize:'2rem'}}>{result.type==='accepted'?'✓':result.type==='revision'?'↻':'✕'}</span>
            </div>
            <h2 style={{...S.h1,fontSize:'1.375rem'}}>{result.type==='accepted'?'Angebot angenommen!':result.type==='revision'?'Überarbeitungswunsch gesendet':'Angebot abgelehnt'}</h2>
            <p style={{...S.sub,maxWidth:400,margin:'8px auto 0'}}>
              {result.type==='accepted'
                ? 'Vielen Dank! Wir erstellen jetzt Ihre Rechnung und melden uns in Kürze.'
                : result.type==='revision'
                ? 'Ihr Feedback wurde übermittelt. Wir erstellen eine überarbeitete Version.'
                : 'Schade. Falls Sie Ihre Meinung ändern, kontaktieren Sie uns gern.'}
            </p>
            {setupDone && (
              <a href="/portal" style={{display:'inline-block',marginTop:20,...S.btn(true),textDecoration:'none'}}>
                Zum Kundenportal
              </a>
            )}
          </div>
        </div>
      </div>
    );
  }

  /* ─── QUOTE VIEW ─── */
  const items = quote.items || [];
  const subtitle = quote.subtitle || quote.project_name || '';

  return (
    <div style={S.page}>
      <div style={S.card}>
        {/* Header */}
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:24,flexWrap:'wrap',gap:12}}>
          <div>
            <h1 style={S.h1}>Ihr Angebot</h1>
            <p style={S.sub}>{quote.quote_id} • {subtitle}</p>
          </div>
          <div style={{textAlign:'right'}}>
            <div style={S.label}>Gültig bis</div>
            <div style={{...S.val, fontSize:'.8125rem'}}>{quote.valid_until ? new Date(quote.valid_until).toLocaleDateString('de-DE') : '—'}</div>
          </div>
        </div>

        {setupDone && (
          <div style={{padding:'12px 16px',borderRadius:8,background:'rgba(16,185,129,0.08)',border:'1px solid rgba(16,185,129,0.2)',marginBottom:20,fontSize:'.8125rem',color:'#10b981'}}>
            ✓ Ihr Kundenportal-Konto wurde aktiviert. Sie können sich ab jetzt jederzeit unter <strong>nexifyai.cloud/login</strong> einloggen.
          </div>
        )}

        {/* Customer Info */}
        <div style={S.section}>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
            <div><div style={S.label}>Kunde</div><div style={S.val}>{quote.customer_name}</div></div>
            <div><div style={S.label}>Firma</div><div style={S.val}>{quote.company_name || '—'}</div></div>
          </div>
        </div>

        {/* Items */}
        <div style={S.section}>
          <div style={{...S.label, marginBottom:12}}>Leistungen</div>
          {items.map((it, i) => (
            <div key={i} style={{display:'flex',justifyContent:'space-between',padding:'10px 0',borderBottom:i<items.length-1?'1px solid rgba(255,255,255,0.03)':'none'}}>
              <div>
                <div style={{...S.val, fontSize:'.8125rem'}}>{it.name || it.title}</div>
                {it.description && <div style={{fontSize:'.75rem',color:'#6b7b8d',marginTop:2}}>{it.description}</div>}
              </div>
              <div style={{...S.val, whiteSpace:'nowrap'}}>{fmtEur(it.price || it.total)}</div>
            </div>
          ))}
        </div>

        {/* Total */}
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'20px 0',borderTop:'2px solid rgba(254,155,123,0.2)'}}>
          <div style={{...S.label,fontSize:'.8125rem'}}>Gesamtbetrag (netto)</div>
          <div style={S.total}>{fmtEur(quote.total_net || quote.total)}</div>
        </div>
        {quote.total_gross && (
          <div style={{display:'flex',justifyContent:'space-between',marginTop:4}}>
            <div style={{fontSize:'.75rem',color:'#6b7b8d'}}>inkl. {quote.tax_rate || 19}% MwSt.</div>
            <div style={{fontSize:'.9375rem',color:'#8a9bb0'}}>{fmtEur(quote.total_gross)}</div>
          </div>
        )}

        {/* Actions */}
        {quote.status !== 'accepted' && quote.status !== 'declined' && (
          <div style={{marginTop:32,display:'flex',gap:12,flexWrap:'wrap'}}>
            <button onClick={handleAccept} disabled={!!action} style={S.btn(true)} data-testid="quote-accept-btn">
              {action==='accept'?'Wird verarbeitet...':'Angebot annehmen'}
            </button>
            <button onClick={() => setPanel(panel==='decline'?null:'decline')} style={S.btn(false)} data-testid="quote-decline-btn">
              Ablehnen
            </button>
            <button onClick={() => setPanel(panel==='revision'?null:'revision')} style={S.btn(false)} data-testid="quote-revision-btn">
              Überarbeitung anfordern
            </button>
          </div>
        )}

        {/* Decline Panel */}
        {panel === 'decline' && (
          <div style={{marginTop:16,padding:16,borderRadius:8,background:'rgba(239,68,68,0.06)',border:'1px solid rgba(239,68,68,0.15)'}}>
            <textarea style={{...S.input,minHeight:80,marginBottom:12}} placeholder="Grund (optional)..." value={declineReason} onChange={e => setDeclineReason(e.target.value)} />
            <button onClick={handleDecline} disabled={!!action} style={{...S.btn(false),borderColor:'rgba(239,68,68,0.3)',color:'#ef4444'}}>
              {action==='decline'?'...':'Endgültig ablehnen'}
            </button>
          </div>
        )}

        {/* Revision Panel */}
        {panel === 'revision' && (
          <div style={{marginTop:16,padding:16,borderRadius:8,background:'rgba(59,130,246,0.06)',border:'1px solid rgba(59,130,246,0.15)'}}>
            <textarea style={{...S.input,minHeight:80,marginBottom:12}} placeholder="Was soll geändert werden?" value={revisionFeedback} onChange={e => setRevisionFeedback(e.target.value)} />
            <button onClick={handleRevision} disabled={!!action || !revisionFeedback.trim()} style={{...S.btn(false),borderColor:'rgba(59,130,246,0.3)',color:'#3b82f6'}}>
              {action==='revision'?'...':'Feedback senden'}
            </button>
          </div>
        )}

        {/* Company Footer */}
        {company && (
          <div style={{marginTop:32,paddingTop:20,borderTop:'1px solid rgba(255,255,255,0.04)',fontSize:'.75rem',color:'#4a5568',textAlign:'center'}}>
            {company.brand || company.name} • {company.phone} • {company.email}
          </div>
        )}
      </div>
    </div>
  );
}
