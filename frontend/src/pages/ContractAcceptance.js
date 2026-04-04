import React, { useState, useEffect, useRef, useCallback } from 'react';
import { I } from '../components/shared';

const API = process.env.REACT_APP_BACKEND_URL;

const ContractAcceptance = () => {
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token') || '';
  const cid = params.get('cid') || '';

  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [accepting, setAccepting] = useState(false);
  const [signatureName, setSignatureName] = useState('');
  const [legalAccepted, setLegalAccepted] = useState({});
  const [showSignPad, setShowSignPad] = useState(false);
  const canvasRef = useRef(null);
  const isDrawingRef = useRef(false);

  const loadContract = useCallback(async () => {
    if (!token || !cid) { setError('Ungültiger Link'); setLoading(false); return; }
    try {
      const r = await fetch(`${API}/api/public/contracts/view?token=${encodeURIComponent(token)}&cid=${encodeURIComponent(cid)}`);
      if (!r.ok) { const d = await r.json().catch(() => ({})); setError(d.detail || 'Vertrag nicht gefunden'); setLoading(false); return; }
      const d = await r.json();
      setContract(d);
      if (d.status === 'accepted') setAccepted(true);
    } catch { setError('Verbindungsfehler'); }
    setLoading(false);
  }, [token, cid]);

  useEffect(() => { loadContract(); }, [loadContract]);

  // Canvas drawing
  useEffect(() => {
    if (!showSignPad || !canvasRef.current) return;
    const c = canvasRef.current;
    const ctx = c.getContext('2d');
    c.width = c.offsetWidth * 2; c.height = c.offsetHeight * 2;
    ctx.scale(2, 2); ctx.strokeStyle = '#0c1117'; ctx.lineWidth = 2; ctx.lineCap = 'round';
    const getPos = (e) => { const r = c.getBoundingClientRect(); const t = e.touches ? e.touches[0] : e; return { x: t.clientX - r.left, y: t.clientY - r.top }; };
    const start = (e) => { e.preventDefault(); isDrawingRef.current = true; const p = getPos(e); ctx.beginPath(); ctx.moveTo(p.x, p.y); };
    const draw = (e) => { if (!isDrawingRef.current) return; e.preventDefault(); const p = getPos(e); ctx.lineTo(p.x, p.y); ctx.stroke(); };
    const end = () => { isDrawingRef.current = false; };
    c.addEventListener('mousedown', start); c.addEventListener('mousemove', draw); c.addEventListener('mouseup', end); c.addEventListener('mouseleave', end);
    c.addEventListener('touchstart', start, { passive: false }); c.addEventListener('touchmove', draw, { passive: false }); c.addEventListener('touchend', end);
    return () => { c.removeEventListener('mousedown', start); c.removeEventListener('mousemove', draw); c.removeEventListener('mouseup', end); c.removeEventListener('mouseleave', end); c.removeEventListener('touchstart', start); c.removeEventListener('touchmove', draw); c.removeEventListener('touchend', end); };
  }, [showSignPad]);

  const clearCanvas = () => { if (!canvasRef.current) return; const ctx = canvasRef.current.getContext('2d'); ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height); };

  const acceptContract = async () => {
    const allRequired = (contract.legal_module_definitions || []).filter(m => m.required).every(m => legalAccepted[m.key]);
    if (!allRequired) { alert('Bitte akzeptieren Sie alle Pflichtmodule.'); return; }
    let sigType = 'name', sigData = signatureName.trim();
    if (showSignPad && canvasRef.current) { sigType = 'drawing'; sigData = canvasRef.current.toDataURL('image/png'); }
    if (!sigData) { alert('Bitte geben Sie Ihren Namen ein oder zeichnen Sie Ihre Unterschrift.'); return; }
    setAccepting(true);
    try {
      const r = await fetch(`${API}/api/public/contracts/accept`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, contract_id: cid, signature_type: sigType, signature_data: sigData, legal_modules_accepted: legalAccepted, customer_name: signatureName }),
      });
      if (r.ok) { setAccepted(true); } else { const d = await r.json().catch(() => ({})); alert(d.detail || 'Fehler bei der Annahme'); }
    } catch { alert('Verbindungsfehler'); }
    setAccepting(false);
  };

  const fmtDate = (d) => d ? new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '-';
  const fmtCurrency = (v) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v || 0);

  if (loading) return (
    <div style={styles.page}><div style={styles.container}><div style={styles.loading}><I n="hourglass_empty" /> Vertrag wird geladen...</div></div></div>
  );
  if (error) return (
    <div style={styles.page}><div style={styles.container}><div style={styles.errorBox}><I n="error" style={{fontSize:32,color:'#ef4444'}} /><h2 style={{margin:'12px 0 8px',color:'#fff'}}>Zugriff nicht möglich</h2><p style={{color:'#6b7b8d'}}>{error}</p></div></div></div>
  );
  if (accepted) return (
    <div style={styles.page}><div style={styles.container}>
      <div style={styles.successBox} data-testid="contract-accepted">
        <div style={{width:64,height:64,borderRadius:'50%',background:'rgba(16,185,129,0.1)',border:'2px solid rgba(16,185,129,0.3)',display:'flex',alignItems:'center',justifyContent:'center',margin:'0 auto 20px'}}><I n="check_circle" style={{fontSize:36,color:'#10b981'}} /></div>
        <h2 style={{color:'#fff',marginBottom:8}}>Vertrag angenommen</h2>
        <p style={{color:'#6b7b8d',marginBottom:16}}>Vielen Dank! Ihr Vertrag <strong style={{color:'#fff'}}>{contract?.contract_number}</strong> wurde erfolgreich digital angenommen.</p>
        <p style={{color:'#6b7b8d',fontSize:'.8125rem'}}>Sie erhalten in Kürze eine Bestätigung per E-Mail. Bei Fragen wenden Sie sich bitte an Ihren Ansprechpartner.</p>
      </div>
    </div></div>
  );

  const c = contract;
  const calc = c.calculation || {};
  return (
    <div style={styles.page}>
      <div style={styles.container}>
        {/* Header */}
        <div style={styles.header} data-testid="contract-view">
          <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:8}}>
            <div style={{width:40,height:40,borderRadius:8,background:'rgba(255,107,0,0.1)',display:'flex',alignItems:'center',justifyContent:'center'}}><I n="gavel" style={{color:'#FF6B00',fontSize:20}} /></div>
            <div>
              <div style={{fontSize:'.6875rem',color:'#6b7b8d',textTransform:'uppercase',letterSpacing:1}}>Vertrag</div>
              <div style={{fontSize:'1.125rem',fontWeight:700,color:'#fff'}}>{c.contract_number}</div>
            </div>
          </div>
          {c.title && <h1 style={{margin:'8px 0 0',fontSize:'1.375rem',fontWeight:700,color:'#fff'}}>{c.title}</h1>}
        </div>

        {/* Meta */}
        <div style={styles.metaGrid}>
          <div style={styles.metaCard}><div style={styles.metaLabel}>Kunde</div><div style={styles.metaValue}>{c.customer?.name}</div></div>
          <div style={styles.metaCard}><div style={styles.metaLabel}>Typ</div><div style={styles.metaValue}>{c.contract_type === 'master' ? 'Mastervertrag' : c.contract_type}</div></div>
          <div style={styles.metaCard}><div style={styles.metaLabel}>Erstellt</div><div style={styles.metaValue}>{fmtDate(c.created_at)}</div></div>
          <div style={styles.metaCard}><div style={styles.metaLabel}>Netto</div><div style={styles.metaValue}>{fmtCurrency(calc.net_total)}</div></div>
          <div style={styles.metaCard}><div style={styles.metaLabel}>MwSt. (21%)</div><div style={styles.metaValue}>{fmtCurrency(calc.vat_amount)}</div></div>
          <div style={styles.metaCard}><div style={styles.metaLabel}>Gesamt</div><div style={{...styles.metaValue,color:'#FF6B00',fontSize:'1rem'}}>{fmtCurrency(calc.gross_total)}</div></div>
        </div>

        {/* Appendices */}
        {(c.appendices_detail || []).length > 0 && (
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}><I n="attach_file" /> Anlagen ({c.appendices_detail.length})</h3>
            {c.appendices_detail.map((a, i) => (
              <div key={a.appendix_id || i} style={styles.appendixCard}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:6}}>
                  <span style={{fontWeight:600,color:'#fff',fontSize:'.875rem'}}>{a.title}</span>
                  <span style={{fontSize:'.6875rem',color:'#6b7b8d',background:'rgba(255,255,255,0.04)',padding:'2px 8px',borderRadius:4}}>{(c.appendix_type_labels || {})[a.appendix_type] || a.appendix_type}</span>
                </div>
                {a.content?.scope && <p style={{margin:0,fontSize:'.8125rem',color:'#c8d1dc'}}>{a.content.scope}</p>}
                {a.content?.value && <div style={{marginTop:4,fontSize:'.8125rem',color:'#FF6B00',fontWeight:600}}>{fmtCurrency(a.content.value)}</div>}
              </div>
            ))}
          </div>
        )}

        {/* Legal Modules */}
        <div style={styles.section}>
          <h3 style={styles.sectionTitle}><I n="shield" /> Rechtsmodule & Einwilligungen</h3>
          {(c.legal_module_definitions || []).map(lm => (
            <label key={lm.key} style={styles.legalRow} data-testid={`legal-${lm.key}`}>
              <input type="checkbox" checked={!!legalAccepted[lm.key]} onChange={e => setLegalAccepted({...legalAccepted, [lm.key]: e.target.checked})} style={{accentColor:'#FF6B00',width:18,height:18}} />
              <div>
                <div style={{fontWeight:600,color:'#fff',fontSize:'.8125rem'}}>{lm.label} {lm.required && <span style={{color:'#ef4444'}}>*</span>}</div>
                <div style={{fontSize:'.75rem',color:'#6b7b8d'}}>{lm.description}</div>
              </div>
            </label>
          ))}
        </div>

        {/* Signature */}
        <div style={styles.section}>
          <h3 style={styles.sectionTitle}><I n="draw" /> Digitale Signatur</h3>
          <div style={{display:'flex',gap:8,marginBottom:16}}>
            <button onClick={() => setShowSignPad(false)} style={{...styles.tabBtn,...(!showSignPad ? styles.tabBtnActive : {})}} data-testid="sig-name-tab">Name eingeben</button>
            <button onClick={() => setShowSignPad(true)} style={{...styles.tabBtn,...(showSignPad ? styles.tabBtnActive : {})}} data-testid="sig-draw-tab">Unterschrift zeichnen</button>
          </div>
          {!showSignPad ? (
            <input type="text" value={signatureName} onChange={e => setSignatureName(e.target.value)} placeholder="Vollständiger Name (z.B. Max Mustermann)" style={styles.input} data-testid="sig-name-input" />
          ) : (
            <div>
              <canvas ref={canvasRef} style={styles.canvas} data-testid="sig-canvas" />
              <button onClick={clearCanvas} style={{...styles.secondaryBtn,marginTop:8,fontSize:'.75rem',padding:'4px 12px'}}><I n="refresh" /> Löschen</button>
            </div>
          )}
        </div>

        {/* Accept Button */}
        <button onClick={acceptContract} disabled={accepting} style={styles.acceptBtn} data-testid="accept-contract-btn">
          <I n="check_circle" /> {accepting ? 'Wird angenommen...' : 'Vertrag verbindlich annehmen'}
        </button>

        {/* Document Hash */}
        <div style={{textAlign:'center',marginTop:24,fontSize:'.6875rem',color:'#4a5568'}}>
          Dokument-Hash: <code style={{color:'#6b7b8d'}}>{c.document_hash?.slice(0, 16)}...</code>
        </div>
      </div>
    </div>
  );
};

const styles = {
  page: { minHeight:'100vh', background:'#0c1117', fontFamily:"'DM Sans',sans-serif", padding:'40px 16px' },
  container: { maxWidth:720, margin:'0 auto' },
  loading: { textAlign:'center', padding:60, color:'#6b7b8d', fontSize:'.875rem', display:'flex', alignItems:'center', justifyContent:'center', gap:8 },
  errorBox: { textAlign:'center', padding:60, background:'rgba(239,68,68,0.04)', border:'1px solid rgba(239,68,68,0.15)', borderRadius:12 },
  successBox: { textAlign:'center', padding:60, background:'rgba(16,185,129,0.04)', border:'1px solid rgba(16,185,129,0.15)', borderRadius:12 },
  header: { background:'rgba(19,26,34,0.6)', border:'1px solid rgba(255,255,255,0.06)', borderRadius:12, padding:'24px 28px', marginBottom:16 },
  metaGrid: { display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(140px,1fr))', gap:8, marginBottom:16 },
  metaCard: { background:'rgba(19,26,34,0.6)', border:'1px solid rgba(255,255,255,0.04)', borderRadius:8, padding:'12px 16px' },
  metaLabel: { fontSize:'.6875rem', color:'#6b7b8d', textTransform:'uppercase', letterSpacing:.5, marginBottom:4 },
  metaValue: { fontSize:'.875rem', fontWeight:600, color:'#fff' },
  section: { background:'rgba(19,26,34,0.6)', border:'1px solid rgba(255,255,255,0.06)', borderRadius:12, padding:'20px 24px', marginBottom:16 },
  sectionTitle: { margin:'0 0 16px', fontSize:'.9375rem', fontWeight:700, color:'#fff', display:'flex', alignItems:'center', gap:8 },
  appendixCard: { background:'rgba(255,255,255,0.02)', border:'1px solid rgba(255,255,255,0.04)', borderRadius:8, padding:'14px 18px', marginBottom:8 },
  legalRow: { display:'flex', gap:12, alignItems:'flex-start', padding:'10px 0', borderBottom:'1px solid rgba(255,255,255,0.03)', cursor:'pointer' },
  tabBtn: { padding:'8px 16px', borderRadius:6, border:'1px solid rgba(255,255,255,0.08)', background:'transparent', color:'#6b7b8d', fontSize:'.8125rem', cursor:'pointer', transition:'all .2s' },
  tabBtnActive: { background:'rgba(255,107,0,0.1)', borderColor:'rgba(255,107,0,0.3)', color:'#FF6B00' },
  input: { width:'100%', padding:'12px 16px', background:'rgba(19,26,34,0.8)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:8, color:'#fff', fontSize:'.875rem', boxSizing:'border-box' },
  canvas: { width:'100%', height:120, background:'#fff', borderRadius:8, cursor:'crosshair', touchAction:'none' },
  secondaryBtn: { background:'transparent', border:'1px solid rgba(255,255,255,0.08)', color:'#6b7b8d', borderRadius:6, cursor:'pointer', display:'inline-flex', alignItems:'center', gap:4 },
  acceptBtn: { width:'100%', padding:'16px 24px', background:'#FF6B00', color:'#fff', border:'none', borderRadius:10, fontSize:'1rem', fontWeight:700, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, transition:'all .2s' },
};

export default ContractAcceptance;
