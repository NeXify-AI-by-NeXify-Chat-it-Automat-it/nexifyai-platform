import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import { HeroScene, IntegrationsGlobe, ProcessScene } from './components/Scene3D';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || '';

const COMPANY = {
  name: 'NeXifyAI by NeXify', tagline: 'Chat it. Automate it.', legal: 'NeXify Automate',
  ceo: 'Pascal Courbois, Geschäftsführer',
  addr: { de: { s: 'Wallstraße 9', c: '41334 Nettetal-Kaldenkirchen', co: 'Deutschland' }, nl: { s: 'Graaf van Loonstraat 1E', c: '5921 JA Venlo', co: 'Niederlande' } },
  phone: '+31 6 133 188 56', email: 'support@nexify-automate.com', web: 'nexify-automate.com', kvk: '90483944', vat: 'NL865786276B01'
};

const genSid = () => `s_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;

const track = async (ev, props = {}) => {
  try {
    const sid = sessionStorage.getItem('nx_s') || genSid();
    sessionStorage.setItem('nx_s', sid);
    await fetch(`${API}/api/analytics/track`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ event: ev, properties: { ...props, ts: new Date().toISOString() }, session_id: sid }) });
  } catch (_) {}
};

const fmtDate = (d) => new Date(d).toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
const I = ({ n, c = '' }) => <span className={`material-symbols-outlined ${c}`} aria-hidden="true">{n}</span>;

/* ═══════════ ANIMATION VARIANTS ═══════════ */
const fadeUp = { hidden: { opacity: 0, y: 40 }, visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.25, 0.4, 0, 1] } } };
const fadeIn = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { duration: 0.6 } } };
const stagger = { visible: { transition: { staggerChildren: 0.1 } } };
const scaleIn = { hidden: { opacity: 0, scale: 0.9 }, visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: [0.25, 0.4, 0, 1] } } };

function AnimSection({ children, className = '', id, ...props }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  return (
    <motion.section ref={ref} id={id} className={className} initial="hidden" animate={isInView ? 'visible' : 'hidden'} variants={stagger} {...props}>
      {children}
    </motion.section>
  );
}

/* ═══════════ LOGO ═══════════ */
const Logo = ({ size = 'md' }) => {
  const s = size === 'sm' ? 24 : size === 'lg' ? 40 : 32;
  const fs = size === 'sm' ? '.9375rem' : size === 'lg' ? '1.375rem' : '1.125rem';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: size === 'sm' ? 8 : 10 }}>
      <img src="/icon-mark.svg" alt="" width={s} height={s} style={{ display: 'block' }} />
      <span style={{ fontFamily: 'var(--f-display)', fontWeight: 800, fontSize: fs, color: '#fff', letterSpacing: '-.02em' }}>
        NeXify<span style={{ color: 'var(--nx-accent)' }}>AI</span>
      </span>
    </div>
  );
};

/* ═══════════ NAVIGATION ═══════════ */
const Nav = ({ onBook }) => {
  const [mob, setMob] = useState(false);
  const [sc, setSc] = useState(false);
  useEffect(() => { const h = () => setSc(window.scrollY > 50); window.addEventListener('scroll', h, { passive: true }); return () => window.removeEventListener('scroll', h); }, []);
  const links = [{ l: 'Leistungen', h: '#loesungen' }, { l: 'Use Cases', h: '#use-cases' }, { l: 'App-Entwicklung', h: '#app-dev' }, { l: 'Integrationen', h: '#integrationen' }, { l: 'Tarife', h: '#preise' }, { l: 'FAQ', h: '#faq' }];
  const go = (h) => { setMob(false); track('nav_click', { target: h }); };
  return (
    <nav className={`nav ${sc ? 'scrolled' : ''}`} role="navigation" aria-label="Hauptnavigation" data-testid="main-nav">
      <div className="container nav-inner">
        <a href="#hero" className="nav-logo" onClick={() => track('logo_click')} data-testid="nav-logo"><Logo /></a>
        <div className="nav-links" role="menubar">
          {links.map(l => <a key={l.h} href={l.h} className="nav-link" role="menuitem" onClick={() => go(l.h)}>{l.l}</a>)}
        </div>
        <div className="nav-actions">
          <button className="btn btn-primary nav-cta" onClick={() => { onBook(); track('cta_click', { loc: 'nav' }); }} data-testid="nav-book-btn">Strategiegespräch buchen</button>
          <button className="nav-toggle" onClick={() => setMob(!mob)} aria-label={mob ? 'Menü schließen' : 'Menü öffnen'} aria-expanded={mob} data-testid="nav-toggle"><I n={mob ? 'close' : 'menu'} /></button>
        </div>
        <AnimatePresence>
          {mob && (
            <motion.div className="nav-mobile" role="menu" data-testid="nav-mobile-menu" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
              {links.map(l => <a key={l.h} href={l.h} role="menuitem" onClick={() => go(l.h)}>{l.l}</a>)}
              <button className="btn btn-primary nav-mobile-cta" onClick={() => { setMob(false); onBook(); }}>Strategiegespräch buchen</button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
};

/* ═══════════ HERO ═══════════ */
const Hero = ({ onBook }) => {
  useEffect(() => { track('page_view', { section: 'hero' }); }, []);
  return (
    <section id="hero" className="hero" aria-labelledby="hero-t" data-testid="hero-section">
      <HeroScene />
      <div className="container hero-container">
        <div className="hero-inner">
          <motion.div className="hero-content" initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1, ease: [0.25, 0.4, 0, 1] }}>
            <motion.span className="label hero-label" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>NeXifyAI by NeXify</motion.span>
            <h1 id="hero-t">Aus Chats werden <span className="text-accent">Prozesse.</span><br />Aus Prozessen wird Wachstum.</h1>
            <p className="hero-desc">Enterprise KI-Lösungen für den DACH-Mittelstand. Intelligente Chatbots, CRM/ERP-Integration, Prozessautomation, Web-Apps und Wissenssysteme — DSGVO-konform und skalierbar.</p>
            <motion.div className="hero-actions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
              <button className="btn btn-primary btn-lg btn-glow" onClick={() => { onBook(); track('cta_click', { loc: 'hero' }); }} data-testid="hero-book-btn">STRATEGIEGESPRÄCH BUCHEN <I n="arrow_forward" /></button>
              <a href="#loesungen" className="btn btn-secondary btn-lg" onClick={() => track('cta_click', { loc: 'hero', t: 'explore' })}>LEISTUNGEN ENTDECKEN</a>
            </motion.div>
            <motion.div className="hero-stats" data-testid="hero-stats" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
              {[{ t: 'Ausrichtung', v: 'Strategische Integration' }, { t: 'Fokus', v: 'Operative Wertschöpfung' }, { t: 'Leistung', v: 'Skalierbare Workflows' }, { t: 'Delivery', v: 'Pünktlich & Präzise' }].map((s, i) => (
                <div key={i} className="hero-stat"><div className="hero-stat-title">{s.t}</div><div className="hero-stat-value">{s.v}</div></div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

/* ═══════════ SOLUTIONS ═══════════ */
const Solutions = () => {
  const items = [
    { i: 'smart_toy', t: 'KI-Assistenz', d: 'Kontextbewusste Co-Piloten für spezifische Fachabteilungen, integriert in Ihre bestehenden Tools und Systeme.' },
    { i: 'settings_input_component', t: 'Automationen', d: 'End-to-End Workflow-Automatisierung durch agentische KI-Systeme ohne Medienbrüche.' },
    { i: 'hub', t: 'Integrationen', d: 'Nahtlose Anbindung an SAP, Salesforce, HubSpot und Microsoft 365 mit höchster Datensicherheit.' },
    { i: 'menu_book', t: 'Wissenssysteme', d: 'RAG-Architekturen für sofortigen Zugriff auf Ihr gesamtes Firmenwissen — strukturiert und suchbar.' },
    { i: 'description', t: 'Dokumentenautomation', d: 'KI-gestützte Extraktion und Validierung komplexer Vertragsdaten, Rechnungen und Dokumente.' },
    { i: 'corporate_fare', t: 'Enterprise Solutions', d: 'Custom-Modelle und On-Premise Deployments für maximale Souveränität Ihrer Daten.' }
  ];
  return (
    <AnimSection id="loesungen" className="section bg-s1" aria-labelledby="sol-t" data-testid="solutions-section">
      <div className="container">
        <motion.header className="section-header" variants={fadeUp}>
          <h2 id="sol-t">Infrastruktur für Intelligenz</h2>
          <p className="section-subtitle">Fundamentale KI-Fähigkeiten für die moderne Enterprise-Architektur — keine Spielereien, sondern echte operative Hebel.</p>
        </motion.header>
        <div className="solutions-grid" role="list">
          {items.map((s, i) => (
            <motion.article key={i} className="sol-card" role="listitem" variants={scaleIn} whileHover={{ y: -6, transition: { duration: 0.25 } }}>
              <div className="sol-icon-wrap"><I n={s.i} c="sol-icon" /></div>
              <h3 className="sol-title">{s.t}</h3>
              <p className="sol-desc">{s.d}</p>
              <div className="sol-bar"></div>
            </motion.article>
          ))}
        </div>
      </div>
    </AnimSection>
  );
};

/* ═══════════ USE CASES ═══════════ */
const UseCases = () => (
  <AnimSection id="use-cases" className="section bg-dark" aria-labelledby="uc-t" data-testid="usecases-section">
    <div className="container">
      <motion.header className="section-header" variants={fadeUp}><h2 id="uc-t">Operative Realität</h2><p className="section-subtitle">Konkrete Implementierungsszenarien, die heute bereits Produktivität freisetzen.</p></motion.header>
      <div className="uc-grid">
        <motion.article className="uc-card uc-lg" variants={fadeUp} whileHover={{ borderColor: 'rgba(255,155,122,0.3)' }}>
          <div className="uc-bg-icon"><I n="analytics" /></div>
          <div className="uc-content"><span className="label">Effizienz-Boost</span><h3 className="uc-title">Vertriebsanfragen & Lead-Qualifizierung</h3><p className="uc-desc">Automatisierte Triage eingehender Leads mit CRM-Abgleich und automatisierter Terminkoordination. Bis zu 60% weniger manuelle Arbeit.</p></div>
        </motion.article>
        <motion.article className="uc-card uc-sm" variants={scaleIn} whileHover={{ y: -4 }}><I n="notes" c="uc-icon" /><h3 className="uc-title">Angebotserstellung</h3><p className="uc-desc">Präzise Angebote aus unstrukturierten Projektnotizen — in Sekunden statt Stunden.</p></motion.article>
        <motion.article className="uc-card uc-sm" variants={scaleIn} whileHover={{ y: -4 }}><I n="database" c="uc-icon" /><h3 className="uc-title">Wissensbestände</h3><p className="uc-desc">Zentralisierung von Silo-Wissen für Support und technischen Service.</p></motion.article>
        <motion.article className="uc-card uc-wd" variants={fadeUp}>
          <div className="uc-split"><div><h3 className="uc-title">CRM/ERP Orchestrierung</h3><p className="uc-desc">Die KI als intelligenter Agent zwischen Ihren Datensilos — führt Aktionen autonom in SAP, HubSpot und Salesforce aus.</p></div>
          <div className="orch-visual"><div className="orch-circle"><I n="sync_alt" /><span className="orch-label top">SAP</span><span className="orch-label btm">HubSpot</span></div></div></div>
        </motion.article>
        <motion.article className="uc-card uc-sm" variants={scaleIn} whileHover={{ y: -4 }}><I n="support_agent" c="uc-icon" /><h3 className="uc-title">Support-Automation</h3><p className="uc-desc">Intelligente Ticket-Klassifizierung und automatisierte Erstantworten in Ihrer Tonalität.</p></motion.article>
      </div>
    </div>
  </AnimSection>
);

/* ═══════════ APP DEVELOPMENT ═══════════ */
const AppDev = ({ onBook }) => {
  const items = [
    { i: 'web', t: 'Web-Applikationen', d: 'Maßgeschneiderte Web-Apps mit modernen Frameworks, responsivem Design und nahtloser KI-Integration.' },
    { i: 'smartphone', t: 'Mobile Apps', d: 'Native und Cross-Platform Mobile-Apps für iOS und Android — performant, sicher und nutzerfreundlich.' },
    { i: 'dashboard', t: 'Kundenportale', d: 'Self-Service-Portale mit Echtzeit-Daten, Ticketing und automatisierten Workflows für Ihre Kunden.' },
    { i: 'handyman', t: 'Interne Tools', d: 'Betriebsinterne Applikationen für Datenmanagement, Reporting und Prozesssteuerung.' },
    { i: 'conversion_path', t: 'Workflow-Apps', d: 'Companion-Apps, die Ihre Mitarbeiter im Tagesgeschäft unterstützen — mobil, kontextsensitiv und KI-gestützt.' },
    { i: 'cloud_sync', t: 'KI-Ökosysteme', d: 'Vernetzte App-Landschaften, die Ihre bestehende Infrastruktur mit intelligenten Schnittstellen verbinden.' }
  ];
  return (
    <AnimSection id="app-dev" className="section bg-s2" aria-labelledby="appdev-t" data-testid="appdev-section">
      <div className="container">
        <motion.header className="section-header" variants={fadeUp}><span className="label">Neu: App-Entwicklung</span><h2 id="appdev-t">Web-Apps, Mobile-Apps & Kundenportale</h2><p className="section-subtitle">Wir entwickeln digitale Produkte, die Ihre KI-Strategie in nutzbare Anwendungen übersetzen — von der Idee bis zum Go-Live.</p></motion.header>
        <div className="appdev-grid">
          {items.map((s, i) => (
            <motion.div key={i} className="appdev-card" variants={scaleIn} whileHover={{ y: -6, borderColor: 'rgba(255,155,122,0.25)' }}>
              <div className="appdev-icon-wrap"><I n={s.i} c="appdev-icon" /></div>
              <h3 className="appdev-title">{s.t}</h3>
              <p className="appdev-desc">{s.d}</p>
            </motion.div>
          ))}
          <motion.div className="appdev-highlight" variants={fadeUp}>
            <h3>Warum App-Entwicklung mit NeXifyAI?</h3>
            <p className="appdev-desc">Weil wir KI nicht nur integrieren — wir bauen die Anwendungen, die Ihre Prozesse wirklich transformieren. Alles aus einer Hand, alles DSGVO-konform.</p>
            <div className="appdev-highlight-inner">
              <div className="appdev-metric"><div className="appdev-metric-val">100%</div><div className="appdev-metric-label">Maßgeschneidert</div></div>
              <div className="appdev-metric"><div className="appdev-metric-val">KI-native</div><div className="appdev-metric-label">Von Grund auf</div></div>
              <div className="appdev-metric"><div className="appdev-metric-val">DSGVO</div><div className="appdev-metric-label">Konform</div></div>
            </div>
            <button className="btn btn-primary btn-glow" onClick={() => { onBook(); track('cta_click', { loc: 'appdev' }); }} data-testid="appdev-book-btn">PROJEKT BESPRECHEN <I n="arrow_forward" /></button>
          </motion.div>
        </div>
      </div>
    </AnimSection>
  );
};

/* ═══════════ PROCESS ═══════════ */
const Process = () => {
  const steps = [
    { n: '01', t: 'Analyse', d: 'Status-quo Audit Ihrer Prozesse und Identifikation der größten Hebel für KI-Automation.', p: 1 },
    { n: '02', t: 'Architektur', d: 'Entwurf der technischen Infrastruktur unter Berücksichtigung von Governance und IT-Security.', p: 2 },
    { n: '03', t: 'Umsetzung', d: 'Iterative Entwicklung und Integration in Ihre Toolchain mit klarem Fokus auf UI/UX.', p: 3 },
    { n: '04', t: 'Optimierung', d: 'Kontinuierliches Monitoring, Feedback-Loop und Performance-Tuning der Modelle.', p: 4 }
  ];
  return (
    <AnimSection id="prozess" className="section bg-dark bg-grid" aria-labelledby="proc-t" data-testid="process-section">
      <div className="container">
        <motion.header className="section-header centered" variants={fadeUp}><span className="label">Workflow</span><h2 id="proc-t">Von der Vision zum Deployment</h2></motion.header>
        <ProcessScene />
        <div className="process-grid" role="list">
          {steps.map((s, i) => (
            <motion.article key={i} className="proc-step" role="listitem" variants={fadeUp} whileHover={{ y: -4 }}>
              <div className="proc-num">{s.n}</div>
              <h3 className="proc-title">{s.t}</h3>
              <p className="proc-desc">{s.d}</p>
              <div className="proc-bars">{[1,2,3,4].map(n => <div key={n} className={`proc-bar ${n <= s.p ? 'on' : ''}`}></div>)}</div>
            </motion.article>
          ))}
        </div>
      </div>
    </AnimSection>
  );
};

/* ═══════════ INTEGRATIONS (50+) ═══════════ */
const INTEGRATIONS = [
  { cat: 'CRM & Vertrieb', items: ['HubSpot', 'Salesforce', 'Pipedrive', 'Zoho CRM', 'Microsoft Dynamics', 'Freshsales', 'Close', 'Monday Sales CRM', 'Copper'] },
  { cat: 'ERP & Buchhaltung', items: ['SAP S/4HANA', 'SAP Business One', 'Oracle NetSuite', 'DATEV', 'Lexware', 'Sage', 'Exact Online', 'sevDesk'] },
  { cat: 'Kommunikation', items: ['Microsoft Teams', 'Slack', 'Zoom', 'Google Meet', 'WhatsApp Business', 'Twilio', 'RingCentral'] },
  { cat: 'Produktivität', items: ['Microsoft 365', 'Google Workspace', 'Notion', 'Confluence', 'Jira', 'Asana', 'Monday.com', 'ClickUp'] },
  { cat: 'Support & Service', items: ['Zendesk', 'Freshdesk', 'Intercom', 'ServiceNow', 'Jira Service Management', 'Help Scout'] },
  { cat: 'Marketing & E-Mail', items: ['Mailchimp', 'ActiveCampaign', 'Brevo', 'HubSpot Marketing', 'CleverReach', 'Rapidmail'] },
  { cat: 'E-Commerce', items: ['Shopify', 'WooCommerce', 'Shopware', 'Magento', 'OXID'] },
  { cat: 'Cloud & Infrastruktur', items: ['AWS', 'Microsoft Azure', 'Google Cloud', 'Hetzner', 'Docker', 'Kubernetes'] },
  { cat: 'Dokumente & DMS', items: ['SharePoint', 'DocuSign', 'Adobe Sign', 'Google Drive', 'Dropbox Business'] },
  { cat: 'HR & Personal', items: ['Personio', 'BambooHR', 'SAP SuccessFactors', 'Workday'] }
];
const TOTAL_INTEG = INTEGRATIONS.reduce((a, c) => a + c.items.length, 0);

const Integrations = () => (
  <AnimSection id="integrationen" className="section bg-s1" aria-labelledby="integ-t" data-testid="integrations-section">
    <div className="container">
      <div className="integ-layout">
        <div className="integ-left">
          <motion.div variants={fadeUp}>
            <span className="label">Konnektivität</span>
            <h2 id="integ-t" style={{ marginTop: 8 }}>Perfekte Symbiose mit Ihrer Software</h2>
            <p className="section-subtitle">Unsere Agenten sprechen die Sprache Ihrer bestehenden Systeme. Keine neuen Silos, sondern intelligente Vernetzung.</p>
          </motion.div>
          <motion.div className="integ-counter" variants={fadeUp}>
            <div className="integ-count">{TOTAL_INTEG}+</div>
            <div className="integ-count-label">Integrationen</div>
            <div className="integ-badges" style={{ marginTop: 12 }}>
              {['REST API', 'WEBHOOKS', 'PYTHON SDK', 'GRAPHQL'].map(b => <span key={b} className="integ-badge">{b}</span>)}
            </div>
          </motion.div>
          <IntegrationsGlobe />
        </div>
        <motion.div className="integ-cats" data-testid="integrations-list" variants={stagger}>
          {INTEGRATIONS.map((cat, ci) => (
            <motion.div key={ci} variants={fadeUp}>
              <div className="integ-cat-name">{cat.cat}</div>
              <div className="integ-cat-items">{cat.items.map((item, ii) => <span key={ii} className="integ-item">{item}</span>)}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  </AnimSection>
);

/* ═══════════ GOVERNANCE ═══════════ */
const Governance = () => (
  <AnimSection className="section bg-s2" style={{ borderTop: '1px solid var(--nx-border)', borderBottom: '1px solid var(--nx-border)' }} aria-labelledby="gov-t" data-testid="governance-section">
    <div className="container">
      <div className="gov-grid">
        <motion.div variants={fadeUp}>
          <h2 id="gov-t">Governance & Compliance</h2>
          <div className="gov-list">
            {[
              { i: 'gavel', t: 'Rechtssicher im DACH-Raum', d: 'DSGVO-Konformität, Datenspeicherung in deutschen Rechenzentren (Frankfurt/München). Auftragsverarbeitungsvertrag (AVV) verfügbar.' },
              { i: 'shield_person', t: 'Role-Based Access Control', d: 'Präzise Steuerung, welche KI-Modelle auf welche Daten zugreifen — auf Benutzerebene und mit vollständiger Protokollierung.' },
              { i: 'policy', t: 'Audit-Log Management', d: 'Lückenlose Protokollierung aller KI-Entscheidungen und Zugriffe für maximale Transparenz und Nachvollziehbarkeit.' }
            ].map((f, i) => (
              <motion.div key={i} className="gov-item" variants={fadeUp} whileHover={{ x: 4 }}>
                <div className="gov-icon-box"><I n={f.i} /></div>
                <div><h3 className="gov-item-title">{f.t}</h3><p className="gov-item-desc">{f.d}</p></div>
              </motion.div>
            ))}
          </div>
        </motion.div>
        <motion.div className="cert-grid" variants={stagger}>
          {[
            { l: 'Standard', t: 'DSGVO', d: '100% Datenschutzkonform' },
            { l: 'Barrierefreiheit', t: 'WCAG 2.2', d: 'Barrierefreie Schnittstellen' },
            { l: 'Zielsetzung', t: 'ISO 27001', d: 'Informationssicherheit angestrebt', hl: true },
            { l: 'Roadmap', t: 'SOC 2 Type II', d: 'In Vorbereitung', hl: true }
          ].map((c, i) => (
            <motion.div key={i} className={`cert-card ${c.hl ? 'hl' : ''}`} variants={scaleIn} whileHover={{ scale: 1.03 }}>
              <span className="cert-label">{c.l}</span><div className="cert-title">{c.t}</div><p className="cert-desc">{c.d}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  </AnimSection>
);

/* ═══════════ PRICING ═══════════ */
const Pricing = ({ onBook }) => {
  const plans = [
    { n: 'Starter', p: 'ab 1.900', per: '/Mo', f: ['2 Custom KI-Agenten', 'Shared Infrastructure', 'E-Mail-Support (48h)', 'Basis-Integrationen'], hl: false },
    { n: 'Growth', p: 'ab 4.500', per: '/Mo', f: ['10 Custom KI-Agenten', 'Private Cloud Deployment', 'Priority Support (4h)', 'CRM/ERP Integration-Kit', 'Dedicated Onboarding'], hl: true, badge: 'Empfehlung' },
    { n: 'Enterprise', p: 'Individuell', per: '', f: ['Unlimitierte KI-Agenten', 'On-Premise Option', 'Dedicated Account Manager', 'Custom LLM Training', 'SLA-Garantien'], hl: false }
  ];
  return (
    <AnimSection id="preise" className="section bg-dark" aria-labelledby="price-t" data-testid="pricing-section">
      <div className="container">
        <motion.header className="section-header centered" variants={fadeUp}><h2 id="price-t">Transparente Architektur-Tarife</h2><p className="section-subtitle">Wählen Sie das Fundament, das zu Ihrer Unternehmensgröße passt. Alle Tarife beinhalten ein Erstgespräch zur Bedarfsanalyse.</p></motion.header>
        <div className="pricing-grid" role="list">
          {plans.map((pl, i) => (
            <motion.article key={i} className={`price-card ${pl.hl ? 'hl' : ''}`} role="listitem" variants={scaleIn} whileHover={{ y: -8, transition: { duration: 0.25 } }}>
              {pl.badge && <span className="price-badge">{pl.badge}</span>}
              <div className="price-name">{pl.n}</div>
              <div className="price-val">{pl.p}<span className="price-period">{pl.per}</span></div>
              <ul className="price-features">{pl.f.map((f, fi) => <li key={fi} className="price-feat"><I n="check_circle" c="price-check" />{f}</li>)}</ul>
              <button className={`btn ${pl.hl ? 'btn-primary btn-glow' : 'btn-secondary'} price-cta`} onClick={() => { onBook(); track('pricing_click', { plan: pl.n }); }} data-testid={`price-cta-${pl.n.toLowerCase()}`}>GESPRÄCH VEREINBAREN</button>
            </motion.article>
          ))}
        </div>
      </div>
    </AnimSection>
  );
};

/* ═══════════ FAQ ═══════════ */
const FAQ = () => {
  const [open, setOpen] = useState(0);
  const faqs = [
    { q: 'Werden unsere Daten zum Training der Modelle genutzt?', a: 'Nein. Alle Kundendaten verbleiben in isolierten Instanzen. Wir nutzen Ihre geschäftskritischen Daten niemals zum Training allgemeiner Sprachmodelle. Ihre Daten bleiben Ihr Eigentum.' },
    { q: 'Wie lange dauert eine Standard-Implementierung?', a: 'Ein einfacher KI-Assistent kann innerhalb von 2-4 Wochen produktiv sein. Komplexere CRM/ERP-Integrationen benötigen 6-12 Wochen. Im Erstgespräch erstellen wir einen realistischen Zeitplan.' },
    { q: 'Ist die Lösung mit SAP kompatibel?', a: 'Ja. Wir bieten native Konnektoren für SAP S/4HANA und SAP Business One. Die Integration erfolgt über standardisierte APIs und berücksichtigt alle Sicherheitskonzepte.' },
    { q: 'Wie minimieren Sie Halluzinationen?', a: 'Durch RAG-Architekturen und strukturierte Validierungsschritte liegt die Genauigkeit bei faktenbasierten Aufgaben über 95%. Kritische Prozesse können mit Human-in-the-Loop abgesichert werden.' },
    { q: 'Welche Datenschutz-Garantien gibt es?', a: 'Alle Daten werden in zertifizierten deutschen Rechenzentren verarbeitet. Wir sind DSGVO-konform und bieten AVV. Für sensible Daten bieten wir On-Premise-Deployments.' },
    { q: 'Entwickeln Sie auch Web-Apps und Mobile-Apps?', a: 'Ja. Wir bauen maßgeschneiderte Web-Applikationen, Kundenportale und Mobile-Apps — immer mit nativer KI-Integration. Von der Idee über Prototyp bis zum produktiven Betrieb.' },
    { q: 'Wie sieht die Preisgestaltung aus?', a: 'Die Tarife beginnen bei 1.900 EUR/Monat für kleinere Setups. Komplexere Enterprise-Projekte werden individuell kalkuliert. Das Erstgespräch ist immer unverbindlich und kostenfrei.' }
  ];
  return (
    <AnimSection id="faq" className="section bg-s1" aria-labelledby="faq-t" data-testid="faq-section">
      <div className="container">
        <div className="faq-layout">
          <motion.div variants={fadeUp}><h2 id="faq-t">Häufige Fragen</h2><p className="section-subtitle">Details zur technischen Umsetzung, Datensicherheit und Integration.</p></motion.div>
          <div className="faq-list" role="list">
            {faqs.map((f, i) => (
              <motion.div key={i} className={`faq-item ${open === i ? 'open' : ''}`} role="listitem" variants={fadeUp}>
                <button type="button" className="faq-q" onClick={() => setOpen(open === i ? -1 : i)} aria-expanded={open === i} data-testid={`faq-q-${i}`}><span>{f.q}</span><I n={open === i ? 'expand_less' : 'expand_more'} /></button>
                <AnimatePresence>
                  {open === i && (
                    <motion.div className="faq-a" data-testid={`faq-a-${i}`} initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }}>
                      <div className="faq-a-inner">{f.a}</div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </AnimSection>
  );
};

/* ═══════════ CONTACT ═══════════ */
const Contact = ({ onBook }) => {
  const [form, setForm] = useState({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', nachricht: '', _hp: '' });
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null);
  const v = () => { const e = {}; if (form.vorname.trim().length < 2) e.vorname = 'Bitte Vornamen eingeben'; if (form.nachname.trim().length < 2) e.nachname = 'Bitte Nachnamen eingeben'; if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Gültige E-Mail erforderlich'; if (form.nachricht.trim().length < 10) e.nachricht = 'Mindestens 10 Zeichen'; setErrors(e); return !Object.keys(e).length; };
  const submit = async (e) => {
    e.preventDefault(); if (!v()) return; setBusy(true); track('form_submit', { form: 'contact' });
    try {
      const r = await fetch(`${API}/api/contact`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
      const d = await r.json();
      if (r.ok) { setStatus({ t: 'success', m: d.message }); setForm({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', nachricht: '', _hp: '' }); }
      else throw new Error(d.detail || 'Fehler');
    } catch (err) { setStatus({ t: 'error', m: 'Übertragung fehlgeschlagen. Bitte versuchen Sie es erneut.' }); track('form_error', { error: err.message }); }
    finally { setBusy(false); }
  };
  return (
    <AnimSection id="kontakt" className="section bg-dark" aria-labelledby="contact-t" data-testid="contact-section">
      <div className="container">
        <div className="contact-grid">
          <motion.div className="contact-info" variants={fadeUp}>
            <h2 id="contact-t" style={{ fontSize: 'clamp(1.75rem,4vw,2.5rem)', fontWeight: 800 }}>Bereit für die Architektur des Wachstums?</h2>
            <p className="section-subtitle">Lassen Sie uns in einem 30-minütigen Gespräch Ihre operativen Potenziale identifizieren.</p>
            <div className="contact-benefits">
              {['Unverbindliches Erstgespräch', 'Prozess-Audit inklusive', 'Konkrete Handlungsempfehlungen'].map((b, i) => <div key={i} className="contact-benefit"><I n="verified" /><span>{b}</span></div>)}
            </div>
            <button className="btn btn-primary btn-lg btn-glow contact-cta-btn" onClick={() => { onBook(); track('cta_click', { loc: 'contact' }); }} data-testid="contact-book-btn">TERMIN DIREKT BUCHEN <I n="calendar_month" /></button>
          </motion.div>
          <motion.div className="contact-form-box" variants={fadeUp}>
            <form onSubmit={submit} className="contact-form" noValidate data-testid="contact-form">
              <input type="text" name="_hp" value={form._hp} onChange={e => setForm({ ...form, _hp: e.target.value })} style={{ display: 'none' }} tabIndex={-1} autoComplete="off" />
              <div className="form-row">
                <div className="form-group"><label htmlFor="vorname" className="form-label">Vorname *</label><input type="text" id="vorname" className={`form-input ${errors.vorname ? 'error' : ''}`} value={form.vorname} onChange={e => setForm({ ...form, vorname: e.target.value })} disabled={busy} required data-testid="input-vorname" />{errors.vorname && <span className="form-error" role="alert">{errors.vorname}</span>}</div>
                <div className="form-group"><label htmlFor="nachname" className="form-label">Nachname *</label><input type="text" id="nachname" className={`form-input ${errors.nachname ? 'error' : ''}`} value={form.nachname} onChange={e => setForm({ ...form, nachname: e.target.value })} disabled={busy} required data-testid="input-nachname" />{errors.nachname && <span className="form-error" role="alert">{errors.nachname}</span>}</div>
              </div>
              <div className="form-row">
                <div className="form-group"><label htmlFor="email" className="form-label">Geschäftliche E-Mail *</label><input type="email" id="email" className={`form-input ${errors.email ? 'error' : ''}`} value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} disabled={busy} required data-testid="input-email" />{errors.email && <span className="form-error" role="alert">{errors.email}</span>}</div>
                <div className="form-group"><label htmlFor="telefon" className="form-label">Telefon</label><input type="tel" id="telefon" className="form-input" value={form.telefon} onChange={e => setForm({ ...form, telefon: e.target.value })} disabled={busy} /></div>
              </div>
              <div className="form-group"><label htmlFor="unternehmen" className="form-label">Unternehmen</label><input type="text" id="unternehmen" className="form-input" value={form.unternehmen} onChange={e => setForm({ ...form, unternehmen: e.target.value })} disabled={busy} /></div>
              <div className="form-group"><label htmlFor="nachricht" className="form-label">Ihre Anfrage *</label><textarea id="nachricht" rows="4" className={`form-textarea ${errors.nachricht ? 'error' : ''}`} value={form.nachricht} onChange={e => setForm({ ...form, nachricht: e.target.value })} disabled={busy} required data-testid="input-nachricht"></textarea>{errors.nachricht && <span className="form-error" role="alert">{errors.nachricht}</span>}</div>
              <button type="submit" className="btn btn-primary btn-glow contact-submit" disabled={busy} data-testid="contact-submit-btn">{busy ? <><span className="spinner"></span>WIRD GESENDET...</> : 'ANFRAGE SENDEN'}</button>
              {status && <div className={`form-status ${status.t}`} role="alert" data-testid="contact-status"><I n={status.t === 'success' ? 'check_circle' : 'error'} />{status.m}</div>}
            </form>
          </motion.div>
        </div>
      </div>
    </AnimSection>
  );
};

/* ═══════════ LIVE CHAT (FUNCTIONALITY IDENTICAL) ═══════════ */
const LiveChat = ({ isOpen, onClose, initialQ }) => {
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sid] = useState(() => genSid());
  const [qual, setQual] = useState({});
  const endRef = useRef(null);
  const inputRef = useRef(null);
  const sentInitial = useRef(false);

  const presets = [
    { i: 'trending_up', t: 'Wie kann KI unseren Vertrieb automatisieren?' },
    { i: 'hub', t: 'Welche CRM/ERP-Integrationen bieten Sie?' },
    { i: 'menu_book', t: 'Wie funktioniert ein internes Wissenssystem?' },
    { i: 'support_agent', t: 'Können Sie unseren Support automatisieren?' },
    { i: 'smartphone', t: 'Entwickeln Sie auch Web-Apps und Mobile-Apps?' },
    { i: 'shield', t: 'Wie sicher sind unsere Daten bei Ihnen?' }
  ];

  useEffect(() => {
    if (isOpen && msgs.length === 0) {
      setMsgs([{ role: 'assistant', content: 'Willkommen bei NeXifyAI. Ich helfe Ihnen, das richtige KI-Szenario für Ihr Unternehmen zu identifizieren. Wählen Sie eine Frage oder beschreiben Sie Ihr Anliegen.', ts: Date.now() }]);
      track('chat_started');
    }
  }, [isOpen, msgs.length]);

  useEffect(() => {
    if (initialQ && isOpen && !sentInitial.current) {
      sentInitial.current = true;
      setTimeout(() => send(initialQ), 300);
    }
  }, [initialQ, isOpen]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);
  useEffect(() => {
    if (isOpen) { inputRef.current?.focus(); document.body.style.overflow = 'hidden'; }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const send = async (text = input) => {
    const t = (typeof text === 'string' ? text : input).trim();
    if (!t || loading) return;
    setMsgs(prev => [...prev, { role: 'user', content: t, ts: Date.now() }]);
    setInput('');
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/chat/message`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid, message: t })
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Fehler');
      setMsgs(prev => [...prev, { role: 'assistant', content: d.message, ts: Date.now(), actions: d.actions }]);
      setQual(d.qualification || {});
      if (d.should_escalate) track('chat_escalation', { qual: d.qualification });
    } catch (_) {
      setMsgs(prev => [...prev, { role: 'assistant', content: 'Entschuldigung, es gab ein technisches Problem. Bitte versuchen Sie es erneut oder nutzen Sie unser Kontaktformular.', ts: Date.now() }]);
    } finally { setLoading(false); }
  };

  const onKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } };

  if (!isOpen) return null;
  return (
    <div className="chat-overlay" onClick={e => e.target === e.currentTarget && onClose()} role="dialog" aria-modal="true" aria-labelledby="chat-t" data-testid="chat-modal">
      <motion.div className="chat-modal" initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <button className="chat-close" onClick={onClose} aria-label="Chat schließen" data-testid="chat-close"><I n="close" /></button>
        <div className="chat-layout">
          <div className="chat-sidebar">
            <h2 id="chat-t" className="chat-sidebar-title">Wie können wir helfen?</h2>
            <p className="chat-sidebar-desc">Wählen Sie eine Frage oder starten Sie direkt.</p>
            <div className="chat-presets">
              {presets.map((q, i) => (
                <button key={i} className="chat-preset" onClick={() => { track('preset_click', { q: q.t }); send(q.t); }} data-testid={`chat-preset-${i}`}><I n={q.i} /><span>{q.t}</span></button>
              ))}
            </div>
            <div className="chat-sidebar-cta"><button className="btn btn-primary btn-glow" onClick={() => { track('chat_booking_click'); send('Ich möchte einen Termin für ein Strategiegespräch buchen.'); }} style={{ width: '100%' }} data-testid="chat-sidebar-book-btn">Termin buchen</button></div>
          </div>
          <div className="chat-main">
            <div className="chat-header"><div className="chat-status"><span className="status-dot on"></span>NeXifyAI Advisor</div>{qual.use_case && <span className="chat-topic">Thema: {qual.use_case}</span>}</div>
            <div className="chat-msgs" data-testid="chat-messages">
              {msgs.map((m, i) => (
                <motion.div key={i} className={`chat-msg ${m.role}`} data-testid={`chat-msg-${i}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
                  <div>{m.content}</div>
                  {m.actions && m.actions.length > 0 && <div className="chat-msg-actions">{m.actions.map((a, ai) => <button key={ai} className="btn btn-sm btn-primary" onClick={() => send('Ich möchte einen Termin buchen.')}>{a.label}</button>)}</div>}
                </motion.div>
              ))}
              {loading && <div className="chat-msg assistant"><div className="chat-typing"><span></span><span></span><span></span></div></div>}
              <div ref={endRef} />
            </div>
            <div className="chat-input-area">
              <input ref={inputRef} type="text" className="chat-input" placeholder="Ihre Nachricht..." value={input} onChange={e => setInput(e.target.value)} onKeyDown={onKey} disabled={loading} aria-label="Nachricht eingeben" data-testid="chat-input" />
              <button className="chat-send" onClick={() => send()} disabled={!input.trim() || loading} aria-label="Senden" data-testid="chat-send"><I n="send" /></button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

/* ═══════════ BOOKING MODAL (FUNCTIONALITY IDENTICAL) ═══════════ */
const Booking = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(1);
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [slots, setSlots] = useState([]);
  const [form, setForm] = useState({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', thema: '' });
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const [ok, setOk] = useState(null);
  const dates = useMemo(() => { const d = []; const t = new Date(); for (let i = 1; i <= 14; i++) { const x = new Date(t); x.setDate(t.getDate() + i); if (x.getDay() !== 0 && x.getDay() !== 6) d.push(x.toISOString().split('T')[0]); } return d; }, []);
  useEffect(() => { if (date) { fetch(`${API}/api/booking/slots?date=${date}`).then(r => r.json()).then(d => setSlots(d.slots || [])).catch(() => setSlots(['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'])); } }, [date]);
  useEffect(() => { if (isOpen) { document.body.style.overflow = 'hidden'; track('booking_modal_opened'); } return () => { document.body.style.overflow = ''; }; }, [isOpen]);
  const v = () => { const e = {}; if (form.vorname.trim().length < 2) e.vorname = 'Pflichtfeld'; if (form.nachname.trim().length < 2) e.nachname = 'Pflichtfeld'; if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Gültige E-Mail'; setErrors(e); return !Object.keys(e).length; };
  const submit = async () => {
    if (!v()) return; setBusy(true); track('booking_submit', { date, time });
    try {
      const r = await fetch(`${API}/api/booking`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, date, time }) });
      const d = await r.json();
      if (r.ok) { setOk(d); track('calendar_booked', { id: d.booking_id }); } else throw new Error(d.detail);
    } catch (e) { setErrors({ submit: e.message || 'Buchung fehlgeschlagen' }); } finally { setBusy(false); }
  };
  if (!isOpen) return null;
  return (
    <div className="booking-overlay" onClick={e => e.target === e.currentTarget && onClose()} role="dialog" aria-modal="true" aria-labelledby="book-t" data-testid="booking-modal">
      <motion.div className="booking-modal" initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <button className="booking-close" onClick={onClose} aria-label="Schließen" data-testid="booking-close"><I n="close" /></button>
        {ok ? (
          <div className="booking-success" data-testid="booking-success"><I n="check_circle" c="booking-success-icon" /><h2>Termin bestätigt!</h2><p>Ihr Beratungsgespräch am <strong>{fmtDate(date)}</strong> um <strong>{time} Uhr</strong> ist gebucht.</p><p>Sie erhalten eine Bestätigung per E-Mail an {form.email}.</p><button className="btn btn-primary btn-glow" onClick={onClose}>Schließen</button></div>
        ) : (
          <>
            <h2 id="book-t" className="booking-title">Strategiegespräch buchen</h2>
            <div className="booking-steps"><div className={`booking-step-ind ${step >= 1 ? 'active' : ''}`}>1. Termin wählen</div><div className={`booking-step-ind ${step >= 2 ? 'active' : ''}`}>2. Daten eingeben</div></div>
            {step === 1 && (
              <div className="booking-step" data-testid="booking-step-1">
                <h3>Wählen Sie einen Termin</h3>
                <div className="booking-dates">{dates.map(d => <button key={d} className={`booking-date ${date === d ? 'sel' : ''}`} onClick={() => setDate(d)} data-testid={`booking-date-${d}`}>{new Date(d).toLocaleDateString('de-DE', { weekday: 'short', day: 'numeric', month: 'short' })}</button>)}</div>
                {date && <><h3>Verfügbare Zeiten</h3><div className="booking-times">{slots.length > 0 ? slots.map(t => <button key={t} className={`booking-time ${time === t ? 'sel' : ''}`} onClick={() => setTime(t)} data-testid={`booking-time-${t}`}>{t} Uhr</button>) : <p style={{ color: 'var(--nx-muted)' }}>Keine Zeiten verfügbar</p>}</div></>}
                <button className="btn btn-primary btn-glow booking-next" disabled={!date || !time} onClick={() => setStep(2)} data-testid="booking-next">Weiter <I n="arrow_forward" /></button>
              </div>
            )}
            {step === 2 && (
              <div className="booking-step" data-testid="booking-step-2">
                <button className="booking-back" onClick={() => setStep(1)}><I n="arrow_back" /> Zurück</button>
                <div className="booking-selected"><I n="event" /><span>{fmtDate(date)} um {time} Uhr</span></div>
                <div className="booking-form">
                  <div className="form-row">
                    <div className="form-group"><label htmlFor="b-vn" className="form-label">Vorname *</label><input type="text" id="b-vn" className={`form-input ${errors.vorname ? 'error' : ''}`} value={form.vorname} onChange={e => setForm({ ...form, vorname: e.target.value })} data-testid="booking-vorname" /></div>
                    <div className="form-group"><label htmlFor="b-nn" className="form-label">Nachname *</label><input type="text" id="b-nn" className={`form-input ${errors.nachname ? 'error' : ''}`} value={form.nachname} onChange={e => setForm({ ...form, nachname: e.target.value })} data-testid="booking-nachname" /></div>
                  </div>
                  <div className="form-group"><label htmlFor="b-em" className="form-label">E-Mail *</label><input type="email" id="b-em" className={`form-input ${errors.email ? 'error' : ''}`} value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} data-testid="booking-email" /></div>
                  <div className="form-row">
                    <div className="form-group"><label htmlFor="b-tel" className="form-label">Telefon</label><input type="tel" id="b-tel" className="form-input" value={form.telefon} onChange={e => setForm({ ...form, telefon: e.target.value })} /></div>
                    <div className="form-group"><label htmlFor="b-co" className="form-label">Unternehmen</label><input type="text" id="b-co" className="form-input" value={form.unternehmen} onChange={e => setForm({ ...form, unternehmen: e.target.value })} /></div>
                  </div>
                  <div className="form-group"><label htmlFor="b-th" className="form-label">Worüber möchten Sie sprechen?</label><select id="b-th" className="form-input" value={form.thema} onChange={e => setForm({ ...form, thema: e.target.value })}><option value="">Bitte wählen...</option><option value="KI-Assistenz / Chatbot">KI-Assistenz / Chatbot</option><option value="CRM/ERP-Integration">CRM/ERP-Integration</option><option value="Prozessautomation">Prozessautomation</option><option value="Wissenssystem / RAG">Wissenssystem / RAG</option><option value="Web-App / Mobile-App">Web-App / Mobile-App</option><option value="Support-Automation">Support-Automation</option><option value="Allgemeine Beratung">Allgemeine Beratung</option></select></div>
                  {errors.submit && <div className="form-error">{errors.submit}</div>}
                  <button className="btn btn-primary btn-glow booking-submit" onClick={submit} disabled={busy} data-testid="booking-submit">{busy ? <><span className="spinner"></span>Wird gebucht...</> : 'Termin verbindlich buchen'}</button>
                </div>
              </div>
            )}
          </>
        )}
      </motion.div>
    </div>
  );
};

/* ═══════════ FOOTER ═══════════ */
const Ft = ({ onCookieSettings }) => (
  <footer className="footer" role="contentinfo" data-testid="footer">
    <div className="container">
      <div className="footer-grid">
        <div className="footer-brand">
          <div className="footer-logo"><img src="/icon-mark.svg" alt="" width="28" height="28" /><span>NeXify<em>AI</em></span></div>
          <div className="footer-tagline">{COMPANY.tagline}</div>
          <div className="footer-legal-name">Ein Produkt von {COMPANY.legal}</div>
          <address className="footer-contact">
            <p><strong>NL:</strong> {COMPANY.addr.nl.s}, {COMPANY.addr.nl.c}</p>
            <p><strong>DE:</strong> {COMPANY.addr.de.s}, {COMPANY.addr.de.c}</p>
            <p>Tel: <a href={`tel:${COMPANY.phone.replace(/\s/g, '')}`}>{COMPANY.phone}</a></p>
            <p>E-Mail: <a href={`mailto:${COMPANY.email}`}>{COMPANY.email}</a></p>
          </address>
        </div>
        <nav className="footer-nav-col" aria-label="Navigation">
          <h3 className="footer-nav-title">Navigation</h3>
          <ul className="footer-links">
            <li><a href="#loesungen">Leistungen</a></li><li><a href="#use-cases">Use Cases</a></li><li><a href="#app-dev">App-Entwicklung</a></li><li><a href="#integrationen">Integrationen</a></li><li><a href="#preise">Tarife</a></li><li><a href="#kontakt">Kontakt</a></li>
          </ul>
        </nav>
        <nav className="footer-nav-col" aria-label="Rechtliches">
          <h3 className="footer-nav-title">Rechtliches</h3>
          <ul className="footer-links">
            <li><a href="/impressum">Impressum</a></li><li><a href="/datenschutz">Datenschutz</a></li><li><a href="/agb">AGB</a></li><li><a href="/ki-hinweise">KI-Hinweise</a></li>
            <li><button onClick={onCookieSettings} style={{ background: 'none', border: 'none', color: 'inherit', font: 'inherit', cursor: 'pointer', padding: 0 }}>Cookie-Einstellungen</button></li>
          </ul>
          <div className="footer-ids"><p>KvK: {COMPANY.kvk}</p><p>USt-ID: {COMPANY.vat}</p></div>
        </nav>
        <div>
          <h3 className="footer-nav-title">Kontakt</h3>
          <ul className="footer-links">
            <li><a href={`tel:${COMPANY.phone.replace(/\s/g, '')}`}>{COMPANY.phone}</a></li>
            <li><a href={`mailto:${COMPANY.email}`}>{COMPANY.email}</a></li>
            <li><a href={`https://${COMPANY.web}`} target="_blank" rel="noopener noreferrer">{COMPANY.web}</a></li>
          </ul>
        </div>
      </div>
      <div className="footer-bottom">
        <span className="footer-copy">&copy; {new Date().getFullYear()} {COMPANY.legal}. Alle Rechte vorbehalten.</span>
        <div className="footer-status"><span className="status-dot on"></span>System Status: Operational</div>
      </div>
    </div>
  </footer>
);

/* ═══════════ CHAT TRIGGER ═══════════ */
const ChatTrigger = ({ onClick }) => (
  <motion.button className="chat-trigger" onClick={onClick} aria-label="Beratung starten" data-testid="chat-trigger" whileHover={{ y: -3, scale: 1.02 }} whileTap={{ scale: 0.98 }}>
    <span className="chat-trigger-text">Beratung starten</span>
    <span className="chat-trigger-icon"><I n="forum" /></span>
  </motion.button>
);

/* ═══════════ COOKIE CONSENT ═══════════ */
const CookieConsent = ({ show, onAccept, onReject }) => {
  if (!show) return null;
  return (
    <motion.div className="cookie-banner" role="dialog" aria-label="Cookie-Einstellungen" data-testid="cookie-banner" initial={{ y: 100 }} animate={{ y: 0 }} transition={{ duration: 0.4 }}>
      <div className="cookie-inner">
        <div className="cookie-text">
          Wir verwenden technisch notwendige Cookies für den Betrieb dieser Website. Optionale Analyse-Cookies helfen uns, die Nutzererfahrung zu verbessern. Mehr dazu in unserer <a href="/datenschutz">Datenschutzerklärung</a>.
        </div>
        <div className="cookie-actions">
          <button className="btn btn-sm btn-secondary" onClick={onReject} data-testid="cookie-reject">Nur Notwendige</button>
          <button className="btn btn-sm btn-primary" onClick={onAccept} data-testid="cookie-accept">Alle akzeptieren</button>
        </div>
      </div>
    </motion.div>
  );
};

/* ═══════════ MAIN APP ═══════════ */
function App() {
  const [chatOpen, setChatOpen] = useState(false);
  const [bookOpen, setBookOpen] = useState(false);
  const [chatQ, setChatQ] = useState('');
  const [showCookie, setShowCookie] = useState(false);

  useEffect(() => {
    track('page_view', { page: 'landing' });
    const consent = localStorage.getItem('nx_cookie_consent');
    if (!consent) setShowCookie(true);
    let maxSc = 0;
    const h = () => { const p = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100); if (p > maxSc) { maxSc = p; if ([25, 50, 75, 100].includes(p)) track('scroll_depth', { depth: p }); } };
    window.addEventListener('scroll', h, { passive: true });
    return () => window.removeEventListener('scroll', h);
  }, []);

  const acceptCookies = () => { localStorage.setItem('nx_cookie_consent', 'all'); setShowCookie(false); };
  const rejectCookies = () => { localStorage.setItem('nx_cookie_consent', 'essential'); setShowCookie(false); };
  const openCookieSettings = () => { localStorage.removeItem('nx_cookie_consent'); setShowCookie(true); };

  return (
    <div className="app" data-testid="app-root">
      <a href="#loesungen" className="skip-link">Zum Inhalt springen</a>
      <Nav onBook={() => setBookOpen(true)} />
      <main id="main-content">
        <Hero onBook={() => setBookOpen(true)} />
        <Solutions />
        <UseCases />
        <AppDev onBook={() => setBookOpen(true)} />
        <Process />
        <Integrations />
        <Governance />
        <Pricing onBook={() => setBookOpen(true)} />
        <FAQ />
        <Contact onBook={() => setBookOpen(true)} />
      </main>
      <Ft onCookieSettings={openCookieSettings} />
      <ChatTrigger onClick={() => { setChatOpen(true); track('chat_trigger_click'); }} />
      <LiveChat isOpen={chatOpen} onClose={() => setChatOpen(false)} initialQ={chatQ} />
      <Booking isOpen={bookOpen} onClose={() => setBookOpen(false)} />
      <CookieConsent show={showCookie} onAccept={acceptCookies} onReject={rejectCookies} />
    </div>
  );
}

export default App;
