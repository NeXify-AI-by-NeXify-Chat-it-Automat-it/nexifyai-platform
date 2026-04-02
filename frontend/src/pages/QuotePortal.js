import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const fmtEur = (v) => {
  if (v == null) return '—';
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v);
};

export default function QuotePortal() {
  const [quote, setQuote] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [action, setAction] = useState(null);
  const [result, setResult] = useState(null);
  const [declineReason, setDeclineReason] = useState('');
  const [revisionFeedback, setRevisionFeedback] = useState('');
  const [showDecline, setShowDecline] = useState(false);
  const [showRevision, setShowRevision] = useState(false);

  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');
  const qid = params.get('qid');

  useEffect(() => {
    if (!token || !qid) {
      setError('Kein gueltiger Zugangslink.');
      setLoading(false);
      return;
    }
    fetch(`${API}/api/portal/quote/${qid}?token=${encodeURIComponent(token)}`)
      .then(r => { if (!r.ok) throw new Error('Zugangslink ungueltig oder abgelaufen'); return r.json(); })
      .then(d => { setQuote(d.quote); setCompany(d.company); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [token, qid]);

  const handleAccept = async () => {
    setAction('accepting');
    try {
      const r = await fetch(`${API}/api/portal/quote/${qid}/accept?token=${encodeURIComponent(token)}`, { method: 'POST' });
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail || 'Fehler'); }
      const data = await r.json();
      setResult({ type: 'accepted', data });
    } catch (e) { setError(e.message); }
    setAction(null);
  };

  const handleDecline = async () => {
    setAction('declining');
    try {
      const r = await fetch(`${API}/api/portal/quote/${qid}/decline?token=${encodeURIComponent(token)}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: declineReason }),
      });
      if (!r.ok) throw new Error('Fehler');
      setResult({ type: 'declined' });
    } catch (e) { setError(e.message); }
    setAction(null);
  };

  const handleRevision = async () => {
    setAction('revision');
    try {
      const r = await fetch(`${API}/api/portal/quote/${qid}/revision?token=${encodeURIComponent(token)}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback: revisionFeedback }),
      });
      if (!r.ok) throw new Error('Fehler');
      setResult({ type: 'revision' });
    } catch (e) { setError(e.message); }
    setAction(null);
  };

  if (loading) return (
    <div style={styles.container}>
      <div style={styles.card}><div style={styles.loader}>Angebot wird geladen...</div></div>
    </div>
  );

  if (error && !quote) return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.errorBox}>{error}</div>
        <p style={styles.muted}>Bitte verwenden Sie den Link aus Ihrer E-Mail.</p>
      </div>
    </div>
  );

  if (result) {
    if (result.type === 'accepted') {
      const d = result.data;
      return (
        <div style={styles.container}>
          <div style={styles.card}>
            <div style={styles.brandHeader}><span style={styles.brand}>NeXify</span><span style={styles.brandAI}>AI</span></div>
            <div style={{...styles.statusBox, borderLeftColor: '#22c55e'}}>
              <h2 style={styles.statusTitle}>Angebot angenommen</h2>
              <p style={styles.muted}>Ihre Anzahlungsrechnung wurde erstellt.</p>
            </div>
            <div style={styles.detailGrid}>
              <div style={styles.detailItem}>
                <span style={styles.detailLabel}>Rechnungsnr.</span>
                <span style={styles.detailValue}>{d.invoice_number}</span>
              </div>
              <div style={styles.detailItem}>
                <span style={styles.detailLabel}>Betrag (brutto)</span>
                <span style={{...styles.detailValue, color: '#ff9b7a'}}>{fmtEur(d.amount_gross)}</span>
              </div>
              <div style={styles.detailItem}>
                <span style={styles.detailLabel}>Faellig am</span>
                <span style={styles.detailValue}>{d.due_date}</span>
              </div>
            </div>
            {d.checkout_url && (
              <a href={d.checkout_url} style={styles.payBtn} data-testid="pay-online-btn">Jetzt online bezahlen</a>
            )}
            <div style={styles.bankBox}>
              <p style={styles.bankTitle}>Alternativ per Bankueberweisung:</p>
              <p style={styles.bankDetail}>IBAN: {d.bank_transfer?.iban}</p>
              <p style={styles.bankDetail}>BIC: {d.bank_transfer?.bic}</p>
              <p style={styles.bankDetail}>Verwendungszweck: {d.bank_transfer?.reference}</p>
            </div>
          </div>
        </div>
      );
    }
    if (result.type === 'declined') return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={styles.brandHeader}><span style={styles.brand}>NeXify</span><span style={styles.brandAI}>AI</span></div>
          <div style={{...styles.statusBox, borderLeftColor: '#ef4444'}}>
            <h2 style={styles.statusTitle}>Angebot abgelehnt</h2>
            <p style={styles.muted}>Vielen Dank fuer Ihre Rueckmeldung.</p>
          </div>
        </div>
      </div>
    );
    if (result.type === 'revision') return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={styles.brandHeader}><span style={styles.brand}>NeXify</span><span style={styles.brandAI}>AI</span></div>
          <div style={{...styles.statusBox, borderLeftColor: '#f59e0b'}}>
            <h2 style={styles.statusTitle}>Aenderungswunsch gesendet</h2>
            <p style={styles.muted}>Wir melden uns in Kuerze bei Ihnen.</p>
          </div>
        </div>
      </div>
    );
  }

  const calc = quote?.calculation || {};
  const customer = quote?.customer || {};
  const alreadyHandled = ['accepted', 'declined'].includes(quote?.status);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.brandHeader}>
          <span style={styles.brand}>NeXify</span><span style={styles.brandAI}>AI</span>
        </div>

        <h1 style={styles.title} data-testid="quote-title">Angebot {quote?.quote_number}</h1>
        <p style={styles.subtitle}>{calc.tier_name} | Tarif-Nr. {calc.tariff_number}</p>

        <div style={styles.customerBox}>
          <p style={styles.customerName}>{customer.company || customer.name}</p>
          <p style={styles.muted}>{customer.name}{customer.company ? ` | ${customer.company}` : ''}</p>
        </div>

        <div style={styles.section}>
          <h3 style={styles.sectionTitle}>Leistungsumfang</h3>
          {quote?.discovery?.use_case && (
            <p style={{color: '#c5c9d2', fontSize: '14px', marginBottom: '12px'}}>
              <strong>Use Case:</strong> {quote.discovery.use_case}
            </p>
          )}
          <a href={`${API}/api/documents/quote/${qid}/pdf`} target="_blank" rel="noreferrer"
             style={{color: '#ff9b7a', fontSize: '14px', textDecoration: 'underline'}}>
            PDF-Angebot herunterladen
          </a>
        </div>

        <div style={styles.section}>
          <h3 style={styles.sectionTitle}>Kommerzielle Konditionen</h3>
          <div style={styles.finGrid}>
            <div style={styles.finRow}>
              <span>Tarifpreis pro Monat</span><span>{fmtEur(calc.reference_monthly_eur)}</span>
            </div>
            <div style={styles.finRow}>
              <span>Vertragslaufzeit</span><span>{calc.contract_months} Monate</span>
            </div>
            <div style={{...styles.finRow, ...styles.finHighlight}}>
              <span><strong>Gesamtvertragswert (netto)</strong></span>
              <span><strong>{fmtEur(calc.total_contract_eur)}</strong></span>
            </div>
            <div style={styles.finRow}>
              <span>Aktivierungsanzahlung (30 %)</span><span>{fmtEur(calc.upfront_eur)}</span>
            </div>
            <div style={{...styles.finRow, fontSize: '13px', color: '#78829a'}}>
              <span>zzgl. {calc.vat_rate}% USt.</span><span>{fmtEur(calc.upfront_vat)}</span>
            </div>
            <div style={{...styles.finRow, ...styles.finHighlight}}>
              <span><strong>Anzahlung (brutto)</strong></span>
              <span style={{color: '#ff9b7a'}}><strong>{fmtEur(calc.upfront_gross)}</strong></span>
            </div>
            <div style={styles.finRow}>
              <span>Restbetrag (netto)</span><span>{fmtEur(calc.remaining_eur)}</span>
            </div>
            <div style={styles.finRow}>
              <span>Monatliche Folgerate ({calc.recurring_count}x)</span><span>{fmtEur(calc.recurring_eur)}</span>
            </div>
          </div>
        </div>

        <div style={styles.validBox}>
          Gueltig bis: {quote?.valid_until ? new Date(quote.valid_until).toLocaleDateString('de-DE') : '—'}
        </div>

        {alreadyHandled ? (
          <div style={{...styles.statusBox, borderLeftColor: quote.status === 'accepted' ? '#22c55e' : '#ef4444'}}>
            <p>Dieses Angebot wurde bereits <strong>{quote.status === 'accepted' ? 'angenommen' : 'abgelehnt'}</strong>.</p>
          </div>
        ) : (
          <div style={styles.actionArea}>
            <button style={styles.acceptBtn} onClick={handleAccept} disabled={!!action} data-testid="accept-quote-btn">
              {action === 'accepting' ? 'Wird verarbeitet...' : 'Angebot annehmen'}
            </button>
            <div style={styles.secondaryActions}>
              <button style={styles.revisionBtn} onClick={() => setShowRevision(!showRevision)} data-testid="revision-btn">
                Aenderung anfragen
              </button>
              <button style={styles.declineBtn} onClick={() => setShowDecline(!showDecline)} data-testid="decline-btn">
                Angebot ablehnen
              </button>
            </div>

            {showRevision && (
              <div style={styles.feedbackBox}>
                <textarea style={styles.textarea} value={revisionFeedback} onChange={e => setRevisionFeedback(e.target.value)}
                  placeholder="Beschreiben Sie Ihren Aenderungswunsch..." data-testid="revision-textarea" />
                <button style={styles.submitFeedback} onClick={handleRevision} disabled={!revisionFeedback || !!action}>
                  Aenderungswunsch senden
                </button>
              </div>
            )}

            {showDecline && (
              <div style={styles.feedbackBox}>
                <textarea style={styles.textarea} value={declineReason} onChange={e => setDeclineReason(e.target.value)}
                  placeholder="Grund (optional)..." data-testid="decline-textarea" />
                <button style={{...styles.submitFeedback, background: '#dc2626'}} onClick={handleDecline} disabled={!!action}>
                  Ablehnung bestaetigen
                </button>
              </div>
            )}
          </div>
        )}

        {error && <div style={styles.errorBox}>{error}</div>}

        <div style={styles.footer}>
          <p>{company?.name} | {company?.phone} | {company?.email}</p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#0a0f14', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px', fontFamily: '-apple-system, BlinkMacSystemFont, system-ui, sans-serif' },
  card: { background: '#12171e', borderRadius: '12px', maxWidth: '720px', width: '100%', padding: '40px', boxShadow: '0 4px 24px rgba(0,0,0,0.4)' },
  brandHeader: { marginBottom: '24px' },
  brand: { fontSize: '24px', fontWeight: 700, color: '#fff' },
  brandAI: { fontSize: '24px', fontWeight: 700, color: '#ff9b7a' },
  title: { fontSize: '28px', fontWeight: 700, color: '#fff', margin: '0 0 4px' },
  subtitle: { fontSize: '14px', color: '#78829a', margin: '0 0 24px' },
  customerBox: { background: '#1a2028', padding: '16px', borderRadius: '8px', marginBottom: '24px' },
  customerName: { color: '#fff', fontWeight: 600, margin: '0 0 4px', fontSize: '16px' },
  muted: { color: '#78829a', fontSize: '14px', margin: 0 },
  section: { marginBottom: '24px' },
  sectionTitle: { color: '#fff', fontSize: '16px', fontWeight: 600, marginBottom: '12px', paddingBottom: '8px', borderBottom: '1px solid #252a32' },
  featureList: { listStyle: 'none', padding: 0, margin: 0 },
  featureItem: { color: '#c5c9d2', fontSize: '14px', padding: '4px 0', paddingLeft: '16px', position: 'relative' },
  finGrid: { display: 'flex', flexDirection: 'column', gap: '8px' },
  finRow: { display: 'flex', justifyContent: 'space-between', color: '#c5c9d2', fontSize: '14px', padding: '6px 0' },
  finHighlight: { background: '#1a2028', padding: '8px 12px', borderRadius: '6px', borderLeft: '3px solid #ff9b7a' },
  validBox: { textAlign: 'center', color: '#78829a', fontSize: '13px', padding: '12px', background: '#1a2028', borderRadius: '6px', marginBottom: '24px' },
  actionArea: { display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' },
  acceptBtn: { width: '100%', padding: '16px', background: '#ff9b7a', color: '#0c1117', fontWeight: 700, fontSize: '16px', border: 'none', borderRadius: '8px', cursor: 'pointer' },
  secondaryActions: { display: 'flex', gap: '12px' },
  revisionBtn: { flex: 1, padding: '12px', background: 'transparent', border: '1px solid #ff9b7a', color: '#ff9b7a', fontWeight: 600, borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
  declineBtn: { flex: 1, padding: '12px', background: 'transparent', border: '1px solid #555', color: '#999', fontWeight: 600, borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
  feedbackBox: { marginTop: '8px' },
  textarea: { width: '100%', minHeight: '80px', background: '#1a2028', border: '1px solid #333', borderRadius: '6px', color: '#fff', padding: '12px', fontSize: '14px', resize: 'vertical', boxSizing: 'border-box' },
  submitFeedback: { marginTop: '8px', padding: '10px 20px', background: '#ff9b7a', color: '#0c1117', fontWeight: 600, border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  statusBox: { padding: '20px', background: '#1a2028', borderRadius: '8px', borderLeft: '4px solid #ff9b7a', marginBottom: '24px' },
  statusTitle: { color: '#fff', fontSize: '20px', margin: '0 0 8px' },
  detailGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '24px' },
  detailItem: { display: 'flex', flexDirection: 'column', gap: '4px' },
  detailLabel: { fontSize: '12px', color: '#78829a', textTransform: 'uppercase' },
  detailValue: { fontSize: '16px', color: '#fff', fontWeight: 600 },
  payBtn: { display: 'block', width: '100%', textAlign: 'center', padding: '16px', background: '#ff9b7a', color: '#0c1117', fontWeight: 700, fontSize: '16px', borderRadius: '8px', textDecoration: 'none', marginBottom: '16px' },
  bankBox: { background: '#1a2028', padding: '16px', borderRadius: '8px', marginBottom: '24px' },
  bankTitle: { color: '#c5c9d2', fontSize: '14px', margin: '0 0 8px', fontWeight: 600 },
  bankDetail: { color: '#78829a', fontSize: '13px', margin: '2px 0' },
  errorBox: { background: '#3f1111', color: '#f87171', padding: '12px 16px', borderRadius: '6px', fontSize: '14px', marginBottom: '16px' },
  loader: { color: '#78829a', textAlign: 'center', padding: '40px', fontSize: '16px' },
  footer: { textAlign: 'center', paddingTop: '24px', borderTop: '1px solid #252a32', color: '#555', fontSize: '12px' },
};
