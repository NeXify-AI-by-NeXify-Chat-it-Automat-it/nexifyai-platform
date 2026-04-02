import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import './App.css';

// ============== CONSTANTS ==============
const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const COMPANY = {
  name: "NeXifyAI by NeXify",
  tagline: "Chat it. Automate it.",
  legalName: "NeXify Automate",
  ceo: "Pascal Courbois, Geschäftsführer",
  addresses: {
    de: { street: "Wallstraße 9", city: "41334 Nettetal-Kaldenkirchen", country: "Deutschland" },
    nl: { street: "Graaf van Loonstraat 1E", city: "5921 JA Venlo", country: "Niederlande" }
  },
  phone: "+31 6 133 188 56",
  email: "support@nexify-automate.com",
  website: "nexify-automate.com",
  kvk: "90483944",
  vatId: "NL865786276B01"
};

const LEAD_STATUSES = {
  neu: { label: 'Neu', color: '#3b82f6' },
  qualifiziert: { label: 'Qualifiziert', color: '#8b5cf6' },
  termin_gebucht: { label: 'Termin gebucht', color: '#f59e0b' },
  in_bearbeitung: { label: 'In Bearbeitung', color: '#06b6d4' },
  gewonnen: { label: 'Gewonnen', color: '#22c55e' },
  verloren: { label: 'Verloren', color: '#ef4444' },
  archiviert: { label: 'Archiviert', color: '#6b7280' }
};

// ============== UTILITIES ==============
const generateSessionId = () => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

const trackEvent = async (event, properties = {}) => {
  try {
    const sessionId = sessionStorage.getItem('nx_session') || generateSessionId();
    sessionStorage.setItem('nx_session', sessionId);
    
    await fetch(`${API_URL}/api/analytics/track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event,
        properties: { ...properties, timestamp: new Date().toISOString() },
        session_id: sessionId,
        page: window.location.pathname
      })
    });
  } catch (e) {
    console.debug('Analytics:', e);
  }
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
};

// ============== COMPONENTS ==============
const Icon = ({ name, className = '' }) => (
  <span className={`material-symbols-outlined ${className}`} aria-hidden="true">{name}</span>
);

// Navigation
const Navigation = ({ onOpenChat, onOpenBooking }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { label: 'Lösungen', href: '#loesungen' },
    { label: 'Anwendungsfälle', href: '#use-cases' },
    { label: 'Prozess', href: '#prozess' },
    { label: 'Integrationen', href: '#integrationen' },
    { label: 'Leistungen', href: '#preise' },
    { label: 'FAQ', href: '#faq' },
  ];

  const handleNavClick = (href) => {
    setMobileOpen(false);
    trackEvent('navigation_click', { target: href });
  };

  return (
    <nav className={`nav ${scrolled ? 'scrolled' : ''}`} role="navigation" aria-label="Hauptnavigation">
      <div className="nav-container container">
        <a href="#hero" className="nav-logo" onClick={() => trackEvent('logo_click')}>
          <img src="/logo-light.svg" alt="NeXifyAI Logo" className="nav-logo-img" width="140" height="32" loading="eager" />
        </a>
        
        <div className="nav-links" role="menubar">
          {navLinks.map(link => (
            <a key={link.href} href={link.href} className="nav-link" role="menuitem" onClick={() => handleNavClick(link.href)}>
              {link.label}
            </a>
          ))}
        </div>

        <div className="nav-actions">
          <button className="btn btn-primary nav-cta" onClick={() => { onOpenBooking(); trackEvent('cta_click', { location: 'nav', cta: 'gespräch_buchen' }); }}>
            Gespräch buchen
          </button>
          <button className="nav-mobile-toggle" onClick={() => setMobileOpen(!mobileOpen)} aria-label={mobileOpen ? 'Menü schließen' : 'Menü öffnen'} aria-expanded={mobileOpen}>
            <Icon name={mobileOpen ? 'close' : 'menu'} />
          </button>
        </div>

        {mobileOpen && (
          <div className="nav-mobile-menu" role="menu">
            {navLinks.map(link => (
              <a key={link.href} href={link.href} className="nav-mobile-link" role="menuitem" onClick={() => handleNavClick(link.href)}>
                {link.label}
              </a>
            ))}
            <button className="btn btn-primary nav-mobile-cta" onClick={() => { setMobileOpen(false); onOpenBooking(); }}>
              Gespräch buchen
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

// Hero Section
const HeroSection = ({ onOpenBooking }) => {
  useEffect(() => {
    trackEvent('page_view', { section: 'hero' });
  }, []);

  return (
    <section id="hero" className="hero architectural-grid" aria-labelledby="hero-title">
      <div className="container hero-grid">
        <div className="hero-content">
          <span className="hero-label">NeXifyAI by NeXify</span>
          <h1 id="hero-title" className="hero-title">
            Aus Chats werden <span className="text-primary">Prozesse.</span><br />
            Aus Prozessen wird Wachstum.
          </h1>
          <p className="hero-description">
            Enterprise KI-Lösungen für den DACH-Mittelstand. Intelligente Chatbots, CRM/ERP-Integration, 
            Prozessautomation und Wissenssysteme – DSGVO-konform und skalierbar.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary btn-lg" onClick={() => { onOpenBooking(); trackEvent('cta_click', { location: 'hero', cta: 'beratung_buchen' }); }}>
              BERATUNGSGESPRÄCH BUCHEN
              <Icon name="arrow_forward" />
            </button>
            <a href="#loesungen" className="btn btn-secondary btn-lg" onClick={() => trackEvent('cta_click', { location: 'hero', cta: 'loesungen' })}>
              LÖSUNGEN ENTDECKEN
            </a>
          </div>
          <div className="hero-stats">
            {[
              { title: 'Ausrichtung', value: 'Strategische Integration' },
              { title: 'Fokus', value: 'Operative Wertschöpfung' },
              { title: 'Leistung', value: 'Skalierbare Workflows' },
              { title: 'Delivery', value: 'Pünktlich & Präzise' }
            ].map((stat, i) => (
              <div key={i} className="hero-stat">
                <div className="hero-stat-title">{stat.title}</div>
                <div className="hero-stat-value">{stat.value}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="hero-visual">
          <ArchitecturePanel />
        </div>
      </div>
    </section>
  );
};

// Architecture Panel
const ArchitecturePanel = () => (
  <div className="architecture-panel" aria-label="KI-Architektur Visualisierung">
    <div className="architecture-inner">
      <div className="architecture-header">
        <div className="architecture-icon"><Icon name="account_tree" /></div>
        <div className="architecture-title">
          <div className="architecture-code">NEXIFY_CORE_V4</div>
          <div className="architecture-name">Inferenz-Architektur</div>
        </div>
      </div>
      <div className="architecture-progress"><div className="architecture-progress-bar" style={{width: '75%'}}></div></div>
      <div className="architecture-modules">
        <div className="architecture-module"><Icon name="psychology" /><span>LLM</span></div>
        <div className="architecture-module active"><Icon name="memory" /><span>Memory</span></div>
        <div className="architecture-module"><Icon name="hub" /><span>API</span></div>
      </div>
      <div className="architecture-flow">
        <div className="architecture-node">Input</div>
        <div className="architecture-connector"></div>
        <div className="architecture-node highlight">Processing</div>
        <div className="architecture-connector"></div>
        <div className="architecture-node">Action</div>
      </div>
    </div>
  </div>
);

// Solutions Section
const SolutionsSection = () => {
  const solutions = [
    { icon: 'smart_toy', title: 'KI-Assistenz', description: 'Kontextbewusste Co-Piloten für spezifische Fachabteilungen, integriert in Ihre bestehenden Tools und Systeme.' },
    { icon: 'settings_input_component', title: 'Automationen', description: 'End-to-End Workflow-Automatisierung durch agentische KI-Systeme ohne Medienbrüche.' },
    { icon: 'hub', title: 'Integrationen', description: 'Nahtlose Anbindung an SAP, Salesforce, HubSpot und Microsoft 365 mit höchster Datensicherheit.' },
    { icon: 'menu_book', title: 'Wissenssysteme', description: 'RAG-Architekturen für sofortigen Zugriff auf Ihr gesamtes Firmenwissen – strukturiert und suchbar.' },
    { icon: 'description', title: 'Dokumentenautomation', description: 'KI-gestützte Extraktion und Validierung komplexer Vertragsdaten, Rechnungen und Dokumente.' },
    { icon: 'corporate_fare', title: 'Enterprise Solutions', description: 'Custom-Modelle und On-Premise Deployments für maximale Souveränität Ihrer Daten.' }
  ];

  return (
    <section id="loesungen" className="solutions-section" aria-labelledby="solutions-title">
      <div className="container">
        <header className="section-header">
          <h2 id="solutions-title" className="section-title">Infrastruktur für Intelligenz</h2>
          <p className="section-description">Fundamentale KI-Fähigkeiten für die moderne Enterprise-Architektur – keine Spielereien, sondern echte operative Hebel.</p>
        </header>
        <div className="solutions-grid" role="list">
          {solutions.map((s, i) => (
            <article key={i} className="solution-card" role="listitem">
              <Icon name={s.icon} className="solution-icon" />
              <h3 className="solution-title">{s.title}</h3>
              <p className="solution-description">{s.description}</p>
              <div className="solution-indicator"></div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

// Use Cases Section
const UseCasesSection = () => (
  <section id="use-cases" className="use-cases-section" aria-labelledby="usecases-title">
    <div className="container">
      <header className="section-header">
        <h2 id="usecases-title" className="section-title">Operative Realität</h2>
        <p className="section-description">Konkrete Implementierungsszenarien, die heute bereits Produktivität freisetzen.</p>
      </header>
      <div className="use-cases-grid">
        <article className="use-case-card large">
          <div className="use-case-bg-icon"><Icon name="analytics" /></div>
          <div className="use-case-content">
            <span className="use-case-label">Effizienz-Boost</span>
            <h3 className="use-case-title">Vertriebsanfragen & Lead-Qualifizierung</h3>
            <p className="use-case-description">Automatisierte Triage eingehender Leads mit CRM-Abgleich und automatisierter Terminkoordination. Bis zu 60% weniger manuelle Arbeit.</p>
          </div>
        </article>
        <article className="use-case-card">
          <Icon name="notes" className="use-case-icon" />
          <h3 className="use-case-title">Angebotserstellung</h3>
          <p className="use-case-description">Präzise Angebote aus unstrukturierten Projektnotizen – in Sekunden statt Stunden.</p>
        </article>
        <article className="use-case-card">
          <Icon name="database" className="use-case-icon" />
          <h3 className="use-case-title">Wissensbestände</h3>
          <p className="use-case-description">Zentralisierung von Silo-Wissen für Support und technischen Service.</p>
        </article>
        <article className="use-case-card wide">
          <div className="use-case-split">
            <div>
              <h3 className="use-case-title">CRM/ERP Orchestrierung</h3>
              <p className="use-case-description">Die KI als intelligenter Agent zwischen Ihren Datensilos – führt Aktionen autonom in SAP, HubSpot und Salesforce aus.</p>
            </div>
            <div className="orchestration-visual">
              <div className="orchestration-circle">
                <Icon name="sync_alt" />
                <span className="orchestration-label top">SAP</span>
                <span className="orchestration-label bottom">HubSpot</span>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
);

// Process Section
const ProcessSection = () => {
  const steps = [
    { num: '01', title: 'Analyse', description: 'Status-quo Audit Ihrer Prozesse und Identifikation der größten Hebel für KI-Automation.', progress: 1 },
    { num: '02', title: 'Architektur', description: 'Entwurf der technischen Infrastruktur unter Berücksichtigung von Governance und IT-Security.', progress: 2 },
    { num: '03', title: 'Umsetzung', description: 'Iterative Entwicklung und Integration in Ihre Toolchain mit klarem Fokus auf UI/UX.', progress: 3 },
    { num: '04', title: 'Optimierung', description: 'Kontinuierliches Monitoring, Feedback-Loop und Performance-Tuning der Modelle.', progress: 4 }
  ];

  return (
    <section id="prozess" className="process-section architectural-grid" aria-labelledby="process-title">
      <div className="container">
        <header className="section-header centered">
          <span className="section-label">Workflow</span>
          <h2 id="process-title" className="section-title">Von der Vision zum Deployment</h2>
        </header>
        <div className="process-grid" role="list">
          {steps.map((step, i) => (
            <article key={i} className="process-step" role="listitem">
              <div className="process-num">{step.num}</div>
              <h3 className="process-title-item">{step.title}</h3>
              <p className="process-description">{step.description}</p>
              <div className="process-progress">
                {[1,2,3,4].map(n => <div key={n} className={`process-bar ${n <= step.progress ? 'active' : ''}`}></div>)}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

// Integrations Section
const IntegrationsSection = () => (
  <section id="integrationen" className="integrations-section" aria-labelledby="integrations-title">
    <div className="container integrations-container">
      <div className="integrations-info">
        <h2 id="integrations-title" className="section-title">Perfekte Symbiose</h2>
        <p className="section-description">Unsere Agenten sprechen die Sprache Ihrer bestehenden Software. Keine neuen Silos, sondern intelligente Vernetzung.</p>
        <div className="api-badges">
          {['REST API', 'WEBHOOKS', 'PYTHON SDK'].map(api => <span key={api} className="api-badge">{api}</span>)}
        </div>
      </div>
      <div className="integrations-grid">
        {['Microsoft 365', 'HubSpot', 'Salesforce', 'SAP S/4HANA'].map(name => (
          <div key={name} className="integration-card"><span className="integration-name">{name}</span></div>
        ))}
      </div>
    </div>
  </section>
);

// Governance Section
const GovernanceSection = () => (
  <section className="governance-section" aria-labelledby="governance-title">
    <div className="container governance-container">
      <div className="governance-features">
        <h2 id="governance-title" className="section-title">Governance & Compliance</h2>
        <div className="governance-list">
          {[
            { icon: 'gavel', title: 'Rechtssicher im DACH-Raum', desc: 'DSGVO-Konformität, Datenspeicherung in deutschen Rechenzentren (Frankfurt/München).' },
            { icon: 'shield_person', title: 'Role-Based Access Control', desc: 'Präzise Steuerung, welche KI-Modelle auf welche Daten zugreifen – auf Benutzerebene.' },
            { icon: 'policy', title: 'Audit-Log Management', desc: 'Lückenlose Protokollierung aller KI-Entscheidungen für maximale Transparenz.' }
          ].map((f, i) => (
            <div key={i} className="governance-item">
              <div className="governance-icon"><Icon name={f.icon} /></div>
              <div><h3 className="governance-item-title">{f.title}</h3><p className="governance-item-description">{f.desc}</p></div>
            </div>
          ))}
        </div>
      </div>
      <div className="certifications-grid">
        {[
          { label: 'Standard', title: 'GDPR/DSGVO', desc: '100% Datenschutzkonform.', highlight: false },
          { label: 'Barrierefreiheit', title: 'WCAG 2.2', desc: 'Barrierefreie Schnittstellen.', highlight: false },
          { label: 'Zielsetzung', title: 'ISO 27001', desc: 'Informationssicherheit angestrebt.', highlight: true },
          { label: 'Roadmap', title: 'SOC 2 Type II', desc: 'In Vorbereitung.', highlight: true }
        ].map((c, i) => (
          <div key={i} className={`certification-card ${c.highlight ? 'highlight' : ''}`}>
            <span className="certification-label">{c.label}</span>
            <div className="certification-title">{c.title}</div>
            <p className="certification-description">{c.desc}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

// Pricing Section  
const PricingSection = ({ onOpenBooking }) => {
  const plans = [
    { name: 'Starter', price: '€1.900', period: '/Mo', features: ['2 Custom KI-Agenten', 'Shared Infrastructure', 'Email Support (48h)', 'Basis-Integrationen'], cta: 'GESPRÄCH VEREINBAREN', highlight: false },
    { name: 'Growth', price: '€4.500', period: '/Mo', features: ['10 Custom KI-Agenten', 'Private Cloud Deployment', 'Priority Support (4h)', 'CRM/ERP Integration-Kit', 'Dedicated Onboarding'], cta: 'GESPRÄCH VEREINBAREN', highlight: true, badge: 'Empfehlung' },
    { name: 'Enterprise', price: 'Individuell', period: '', features: ['Unlimitierte KI-Agenten', 'On-Premise Option', 'Dedicated Account Manager', 'Custom LLM Training', 'SLA-Garantien'], cta: 'ANFRAGE SENDEN', highlight: false }
  ];

  return (
    <section id="preise" className="pricing-section" aria-labelledby="pricing-title">
      <div className="container">
        <header className="section-header centered">
          <h2 id="pricing-title" className="section-title">Transparente Architektur-Tarife</h2>
          <p className="section-description">Wählen Sie das Fundament, das zu Ihrer Unternehmensgröße passt. Alle Tarife beinhalten ein Erstgespräch zur Bedarfsanalyse.</p>
        </header>
        <div className="pricing-grid" role="list">
          {plans.map((plan, i) => (
            <article key={i} className={`pricing-card ${plan.highlight ? 'highlight' : ''}`} role="listitem">
              {plan.badge && <span className="pricing-badge">{plan.badge}</span>}
              <div className="pricing-name">{plan.name}</div>
              <div className="pricing-price">{plan.price}<span className="pricing-period">{plan.period}</span></div>
              <ul className="pricing-features">
                {plan.features.map((f, fi) => <li key={fi} className="pricing-feature"><Icon name="check_circle" className="pricing-check" />{f}</li>)}
              </ul>
              <button className={`btn ${plan.highlight ? 'btn-primary' : 'btn-secondary'} pricing-cta`} onClick={() => { onOpenBooking(); trackEvent('pricing_click', { plan: plan.name }); }}>
                {plan.cta}
              </button>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

// FAQ Section
const FAQSection = () => {
  const [openIdx, setOpenIdx] = useState(0);
  const faqs = [
    { q: 'Werden unsere Daten zum Training der Modelle genutzt?', a: 'Nein. Alle Kundendaten verbleiben in isolierten Instanzen. Wir nutzen Ihre geschäftskritischen Daten niemals zum Training allgemeiner Sprachmodelle. Ihre Daten bleiben Ihr Eigentum.' },
    { q: 'Wie lange dauert eine Standard-Implementierung?', a: 'Ein einfacher KI-Assistent kann innerhalb von 2-4 Wochen produktiv sein. Komplexere CRM/ERP-Integrationen benötigen 6-12 Wochen. Im Erstgespräch erstellen wir einen realistischen Zeitplan.' },
    { q: 'Ist die Lösung mit SAP kompatibel?', a: 'Ja. Wir bieten native Konnektoren für SAP S/4HANA und SAP Business One. Die Integration erfolgt über standardisierte APIs und berücksichtigt alle Sicherheitskonzepte.' },
    { q: 'Wie minimieren Sie Halluzinationen?', a: 'Durch RAG-Architekturen und strukturierte Validierungsschritte liegt die Genauigkeit bei faktenbasierten Aufgaben über 95%. Kritische Prozesse können mit Human-in-the-Loop abgesichert werden.' },
    { q: 'Welche Datenschutz-Garantien gibt es?', a: 'Alle Daten werden in zertifizierten deutschen Rechenzentren verarbeitet. Wir sind DSGVO-konform und bieten AVV. Für sensible Daten bieten wir On-Premise-Deployments.' }
  ];

  return (
    <section id="faq" className="faq-section" aria-labelledby="faq-title">
      <div className="container faq-container">
        <div className="faq-info">
          <h2 id="faq-title" className="section-title">Häufige Fragen</h2>
          <p className="section-description">Details zur technischen Umsetzung, Datensicherheit und Integration.</p>
        </div>
        <div className="faq-list" role="list">
          {faqs.map((faq, i) => (
            <div key={i} className={`faq-item ${openIdx === i ? 'open' : ''}`} role="listitem">
              <button type="button" className="faq-question" onClick={() => setOpenIdx(openIdx === i ? -1 : i)} aria-expanded={openIdx === i}>
                <span>{faq.q}</span>
                <Icon name={openIdx === i ? 'expand_less' : 'expand_more'} />
              </button>
              {openIdx === i && <div className="faq-answer">{faq.a}</div>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Contact Section
const ContactSection = ({ onOpenBooking }) => {
  const [form, setForm] = useState({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', nachricht: '', _hp: '' });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [status, setStatus] = useState(null);

  const validate = () => {
    const e = {};
    if (form.vorname.trim().length < 2) e.vorname = 'Bitte Vornamen eingeben';
    if (form.nachname.trim().length < 2) e.nachname = 'Bitte Nachnamen eingeben';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Gültige E-Mail erforderlich';
    if (form.nachricht.trim().length < 10) e.nachricht = 'Mindestens 10 Zeichen';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    trackEvent('form_submit', { form: 'contact' });
    
    try {
      const res = await fetch(`${API_URL}/api/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (res.ok) {
        setStatus({ type: 'success', message: data.message });
        setForm({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', nachricht: '', _hp: '' });
      } else {
        throw new Error(data.detail || 'Fehler');
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Übertragung fehlgeschlagen. Bitte versuchen Sie es erneut.' });
      trackEvent('form_error', { form: 'contact', error: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="kontakt" className="contact-section" aria-labelledby="contact-title">
      <div className="container contact-container">
        <div className="contact-info">
          <h2 id="contact-title" className="section-title large">Bereit für die Architektur des Wachstums?</h2>
          <p className="section-description">Lassen Sie uns in einem 30-minütigen Gespräch Ihre operativen Potenziale identifizieren.</p>
          <div className="contact-benefits">
            {['Unverbindliches Erstgespräch', 'Prozess-Audit inklusive', 'Konkrete Handlungsempfehlungen'].map((b, i) => (
              <div key={i} className="contact-benefit"><Icon name="verified" /><span>{b}</span></div>
            ))}
          </div>
          <button className="btn btn-primary btn-lg contact-booking-cta" onClick={() => { onOpenBooking(); trackEvent('cta_click', { location: 'contact', cta: 'termin_buchen' }); }}>
            TERMIN DIREKT BUCHEN
            <Icon name="calendar_month" />
          </button>
        </div>
        <div className="contact-form-container">
          <form onSubmit={handleSubmit} className="contact-form" noValidate>
            <input type="text" name="_hp" value={form._hp} onChange={e => setForm({...form, _hp: e.target.value})} style={{display:'none'}} tabIndex={-1} autoComplete="off" />
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="vorname" className="form-label">Vorname *</label>
                <input type="text" id="vorname" className={`form-input ${errors.vorname ? 'error' : ''}`} value={form.vorname} onChange={e => setForm({...form, vorname: e.target.value})} disabled={submitting} required />
                {errors.vorname && <span className="form-error" role="alert">{errors.vorname}</span>}
              </div>
              <div className="form-group">
                <label htmlFor="nachname" className="form-label">Nachname *</label>
                <input type="text" id="nachname" className={`form-input ${errors.nachname ? 'error' : ''}`} value={form.nachname} onChange={e => setForm({...form, nachname: e.target.value})} disabled={submitting} required />
                {errors.nachname && <span className="form-error" role="alert">{errors.nachname}</span>}
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email" className="form-label">Geschäftliche E-Mail *</label>
                <input type="email" id="email" className={`form-input ${errors.email ? 'error' : ''}`} value={form.email} onChange={e => setForm({...form, email: e.target.value})} disabled={submitting} required />
                {errors.email && <span className="form-error" role="alert">{errors.email}</span>}
              </div>
              <div className="form-group">
                <label htmlFor="telefon" className="form-label">Telefon</label>
                <input type="tel" id="telefon" className="form-input" value={form.telefon} onChange={e => setForm({...form, telefon: e.target.value})} disabled={submitting} />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="unternehmen" className="form-label">Unternehmen</label>
              <input type="text" id="unternehmen" className="form-input" value={form.unternehmen} onChange={e => setForm({...form, unternehmen: e.target.value})} disabled={submitting} />
            </div>
            <div className="form-group">
              <label htmlFor="nachricht" className="form-label">Ihre Anfrage *</label>
              <textarea id="nachricht" rows="4" className={`form-textarea ${errors.nachricht ? 'error' : ''}`} value={form.nachricht} onChange={e => setForm({...form, nachricht: e.target.value})} disabled={submitting} required></textarea>
              {errors.nachricht && <span className="form-error" role="alert">{errors.nachricht}</span>}
            </div>
            <button type="submit" className="btn btn-primary contact-submit" disabled={submitting}>
              {submitting ? <><span className="spinner"></span>WIRD GESENDET...</> : 'ANFRAGE SENDEN'}
            </button>
            {status && <div className={`form-status ${status.type}`} role="alert"><Icon name={status.type === 'success' ? 'check_circle' : 'error'} />{status.message}</div>}
          </form>
        </div>
      </div>
    </section>
  );
};

// Live Chat Component
const LiveChat = ({ isOpen, onClose, initialQuestion }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const [qualification, setQualification] = useState({});
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const presetQuestions = [
    { icon: 'trending_up', text: 'Wie kann KI unseren Vertrieb automatisieren?' },
    { icon: 'hub', text: 'Welche CRM/ERP-Integrationen bieten Sie?' },
    { icon: 'menu_book', text: 'Wie funktioniert ein internes Wissenssystem?' },
    { icon: 'support_agent', text: 'Können Sie unseren Support automatisieren?' },
    { icon: 'analytics', text: 'Wie identifizieren Sie Automationspotenziale?' },
    { icon: 'shield', text: 'Wie sicher sind unsere Daten bei Ihnen?' }
  ];

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: 'Willkommen bei NeXifyAI! Ich helfe Ihnen, das richtige KI-Szenario für Ihr Unternehmen zu identifizieren. Wählen Sie eine Frage oder beschreiben Sie Ihr Anliegen.',
        timestamp: new Date().toISOString()
      }]);
      trackEvent('chat_started');
    }
  }, [isOpen, messages.length]);

  useEffect(() => {
    if (initialQuestion && isOpen) {
      handleSend(initialQuestion);
    }
  }, [initialQuestion, isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      document.body.style.overflow = 'hidden';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const handleSend = async (text = input) => {
    if (!text.trim() || loading) return;
    
    const userMsg = { role: 'user', content: text.trim(), timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/chat/message?session_id=${sessionId}&message=${encodeURIComponent(text)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString(),
        actions: data.suggested_actions
      }]);
      setQualification(data.qualification || {});
      
      if (data.should_escalate) {
        trackEvent('chat_escalation', { qualification: data.qualification });
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Entschuldigung, es gab ein technisches Problem. Bitte versuchen Sie es erneut oder nutzen Sie unser Kontaktformular.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handlePresetClick = (question) => {
    trackEvent('preset_question_clicked', { question });
    handleSend(question);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="chat-overlay" onClick={(e) => e.target === e.currentTarget && onClose()} role="dialog" aria-modal="true" aria-labelledby="chat-title">
      <div className="chat-modal">
        <button className="chat-close" onClick={onClose} aria-label="Chat schließen"><Icon name="close" /></button>
        
        <div className="chat-layout">
          <div className="chat-sidebar">
            <h2 id="chat-title" className="chat-sidebar-title">Wie können wir Ihnen helfen?</h2>
            <p className="chat-sidebar-desc">Wählen Sie eine Frage oder starten Sie direkt das Gespräch.</p>
            <div className="chat-presets">
              {presetQuestions.map((q, i) => (
                <button key={i} className="chat-preset-btn" onClick={() => handlePresetClick(q.text)}>
                  <Icon name={q.icon} />
                  <span>{q.text}</span>
                </button>
              ))}
            </div>
            <div className="chat-sidebar-cta">
              <a href="#kontakt" className="btn btn-primary" onClick={onClose}>Direkt Termin buchen</a>
            </div>
          </div>
          
          <div className="chat-main">
            <div className="chat-header">
              <div className="chat-status"><span className="status-dot online"></span>NeXifyAI Advisor</div>
              {qualification.use_case && <span className="chat-topic">Thema: {qualification.use_case}</span>}
            </div>
            
            <div className="chat-messages">
              {messages.map((msg, i) => (
                <div key={i} className={`chat-message ${msg.role}`}>
                  <div className="chat-message-content">{msg.content}</div>
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="chat-message-actions">
                      {msg.actions.map((action, ai) => (
                        <a key={ai} href={action.type === 'booking' ? '#kontakt' : '#kontakt'} className="btn btn-sm btn-primary" onClick={onClose}>
                          {action.label}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {loading && <div className="chat-message assistant"><div className="chat-typing"><span></span><span></span><span></span></div></div>}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="chat-input-area">
              <input
                ref={inputRef}
                type="text"
                className="chat-input"
                placeholder="Ihre Nachricht..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                aria-label="Nachricht eingeben"
              />
              <button className="chat-send" onClick={() => handleSend()} disabled={!input.trim() || loading} aria-label="Senden">
                <Icon name="send" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Booking Modal
const BookingModal = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [slots, setSlots] = useState([]);
  const [form, setForm] = useState({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', thema: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);

  const availableDates = useMemo(() => {
    const dates = [];
    const today = new Date();
    for (let i = 1; i <= 14; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      if (d.getDay() !== 0 && d.getDay() !== 6) {
        dates.push(d.toISOString().split('T')[0]);
      }
    }
    return dates;
  }, []);

  useEffect(() => {
    if (selectedDate) {
      fetchSlots(selectedDate);
    }
  }, [selectedDate]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      trackEvent('booking_modal_opened');
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const fetchSlots = async (date) => {
    try {
      const res = await fetch(`${API_URL}/api/booking/slots?date=${date}`);
      const data = await res.json();
      setSlots(data.slots || []);
    } catch (e) {
      setSlots(['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']);
    }
  };

  const validate = () => {
    const e = {};
    if (form.vorname.trim().length < 2) e.vorname = 'Pflichtfeld';
    if (form.nachname.trim().length < 2) e.nachname = 'Pflichtfeld';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Gültige E-Mail';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    trackEvent('booking_submit', { date: selectedDate, time: selectedTime });

    try {
      const res = await fetch(`${API_URL}/api/booking`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, date: selectedDate, time: selectedTime })
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess(data);
        trackEvent('calendar_booked', { booking_id: data.booking_id });
      } else {
        throw new Error(data.detail);
      }
    } catch (err) {
      setErrors({ submit: err.message || 'Buchung fehlgeschlagen' });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="booking-overlay" onClick={e => e.target === e.currentTarget && onClose()} role="dialog" aria-modal="true" aria-labelledby="booking-title">
      <div className="booking-modal">
        <button className="booking-close" onClick={onClose} aria-label="Schließen"><Icon name="close" /></button>
        
        {success ? (
          <div className="booking-success">
            <Icon name="check_circle" className="booking-success-icon" />
            <h2>Termin bestätigt!</h2>
            <p>Ihr Beratungsgespräch am <strong>{formatDate(selectedDate)}</strong> um <strong>{selectedTime} Uhr</strong> ist gebucht.</p>
            <p>Sie erhalten eine Bestätigung per E-Mail an {form.email}.</p>
            <button className="btn btn-primary" onClick={onClose}>Schließen</button>
          </div>
        ) : (
          <>
            <h2 id="booking-title" className="booking-title">Beratungsgespräch buchen</h2>
            <div className="booking-steps">
              <div className={`booking-step ${step >= 1 ? 'active' : ''}`}>1. Termin wählen</div>
              <div className={`booking-step ${step >= 2 ? 'active' : ''}`}>2. Daten eingeben</div>
            </div>
            
            {step === 1 && (
              <div className="booking-step-content">
                <h3>Wählen Sie einen Termin</h3>
                <div className="booking-dates">
                  {availableDates.map(date => (
                    <button key={date} className={`booking-date ${selectedDate === date ? 'selected' : ''}`} onClick={() => setSelectedDate(date)}>
                      {new Date(date).toLocaleDateString('de-DE', { weekday: 'short', day: 'numeric', month: 'short' })}
                    </button>
                  ))}
                </div>
                {selectedDate && (
                  <>
                    <h3>Verfügbare Zeiten</h3>
                    <div className="booking-times">
                      {slots.length > 0 ? slots.map(time => (
                        <button key={time} className={`booking-time ${selectedTime === time ? 'selected' : ''}`} onClick={() => setSelectedTime(time)}>
                          {time} Uhr
                        </button>
                      )) : <p>Keine Zeiten verfügbar</p>}
                    </div>
                  </>
                )}
                <button className="btn btn-primary booking-next" disabled={!selectedDate || !selectedTime} onClick={() => setStep(2)}>
                  Weiter <Icon name="arrow_forward" />
                </button>
              </div>
            )}
            
            {step === 2 && (
              <div className="booking-step-content">
                <button className="booking-back" onClick={() => setStep(1)}><Icon name="arrow_back" /> Zurück</button>
                <div className="booking-selected">
                  <Icon name="event" />
                  <span>{formatDate(selectedDate)} um {selectedTime} Uhr</span>
                </div>
                <div className="booking-form">
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="b-vorname" className="form-label">Vorname *</label>
                      <input type="text" id="b-vorname" className={`form-input ${errors.vorname ? 'error' : ''}`} value={form.vorname} onChange={e => setForm({...form, vorname: e.target.value})} />
                    </div>
                    <div className="form-group">
                      <label htmlFor="b-nachname" className="form-label">Nachname *</label>
                      <input type="text" id="b-nachname" className={`form-input ${errors.nachname ? 'error' : ''}`} value={form.nachname} onChange={e => setForm({...form, nachname: e.target.value})} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label htmlFor="b-email" className="form-label">E-Mail *</label>
                    <input type="email" id="b-email" className={`form-input ${errors.email ? 'error' : ''}`} value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="b-telefon" className="form-label">Telefon</label>
                      <input type="tel" id="b-telefon" className="form-input" value={form.telefon} onChange={e => setForm({...form, telefon: e.target.value})} />
                    </div>
                    <div className="form-group">
                      <label htmlFor="b-unternehmen" className="form-label">Unternehmen</label>
                      <input type="text" id="b-unternehmen" className="form-input" value={form.unternehmen} onChange={e => setForm({...form, unternehmen: e.target.value})} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label htmlFor="b-thema" className="form-label">Worüber möchten Sie sprechen?</label>
                    <select id="b-thema" className="form-input" value={form.thema} onChange={e => setForm({...form, thema: e.target.value})}>
                      <option value="">Bitte wählen...</option>
                      <option value="KI-Assistenz / Chatbot">KI-Assistenz / Chatbot</option>
                      <option value="CRM/ERP-Integration">CRM/ERP-Integration</option>
                      <option value="Prozessautomation">Prozessautomation</option>
                      <option value="Wissenssystem / RAG">Wissenssystem / RAG</option>
                      <option value="Support-Automation">Support-Automation</option>
                      <option value="Allgemeine Beratung">Allgemeine Beratung</option>
                    </select>
                  </div>
                  {errors.submit && <div className="form-error">{errors.submit}</div>}
                  <button className="btn btn-primary booking-submit" onClick={handleSubmit} disabled={loading}>
                    {loading ? <><span className="spinner"></span>Wird gebucht...</> : 'Termin verbindlich buchen'}
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Footer
const Footer = () => (
  <footer className="footer" role="contentinfo">
    <div className="container">
      <div className="footer-grid">
        <div className="footer-company">
          <img src="/logo-light.svg" alt="NeXifyAI" className="footer-logo" width="120" height="28" loading="lazy" />
          <p className="footer-tagline">{COMPANY.tagline}</p>
          <p className="footer-legal-name">Ein Produkt von {COMPANY.legalName}</p>
          <address className="footer-contact-info">
            <p><strong>NL:</strong> {COMPANY.addresses.nl.street}, {COMPANY.addresses.nl.city}</p>
            <p><strong>DE:</strong> {COMPANY.addresses.de.street}, {COMPANY.addresses.de.city}</p>
            <p>Tel: <a href={`tel:${COMPANY.phone.replace(/\s/g, '')}`}>{COMPANY.phone}</a></p>
            <p>E-Mail: <a href={`mailto:${COMPANY.email}`}>{COMPANY.email}</a></p>
          </address>
        </div>
        <nav className="footer-nav" aria-label="Navigation">
          <h3 className="footer-nav-title">Navigation</h3>
          <ul className="footer-links">
            <li><a href="#loesungen">Lösungen</a></li>
            <li><a href="#use-cases">Anwendungsfälle</a></li>
            <li><a href="#preise">Leistungen</a></li>
            <li><a href="#kontakt">Kontakt</a></li>
          </ul>
        </nav>
        <nav className="footer-nav" aria-label="Rechtliches">
          <h3 className="footer-nav-title">Rechtliches</h3>
          <ul className="footer-links">
            <li><a href="/impressum">Impressum</a></li>
            <li><a href="/datenschutz">Datenschutz</a></li>
            <li><a href="/agb">AGB</a></li>
          </ul>
          <div className="footer-legal-ids">
            <p>KvK: {COMPANY.kvk}</p>
            <p>USt-ID: {COMPANY.vatId}</p>
          </div>
        </nav>
      </div>
      <div className="footer-bottom">
        <span className="footer-copyright">© {new Date().getFullYear()} {COMPANY.legalName}. Alle Rechte vorbehalten.</span>
        <div className="footer-status"><span className="status-dot online"></span>System Status: Optimal</div>
      </div>
    </div>
  </footer>
);

// Chat Trigger
const ChatTrigger = ({ onClick }) => (
  <button className="chat-trigger" onClick={onClick} aria-label="Beratung starten">
    <span className="chat-trigger-text">Beratung starten</span>
    <span className="chat-trigger-icon"><Icon name="forum" /></span>
  </button>
);

// Main App
function App() {
  const [chatOpen, setChatOpen] = useState(false);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [chatQuestion, setChatQuestion] = useState('');

  useEffect(() => {
    trackEvent('page_view', { page: 'landing' });
    
    // Scroll tracking
    let maxScroll = 0;
    const handleScroll = () => {
      const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
      if (scrollPercent > maxScroll) {
        maxScroll = scrollPercent;
        if ([25, 50, 75, 100].includes(scrollPercent)) {
          trackEvent('scroll_depth', { depth: scrollPercent });
        }
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const openChatWithQuestion = (question) => {
    setChatQuestion(question);
    setChatOpen(true);
  };

  return (
    <div className="app">
      <a href="#loesungen" className="skip-link">Zum Inhalt springen</a>
      
      <Navigation onOpenChat={() => setChatOpen(true)} onOpenBooking={() => setBookingOpen(true)} />
      
      <main id="main-content">
        <HeroSection onOpenBooking={() => setBookingOpen(true)} />
        <SolutionsSection />
        <UseCasesSection />
        <ProcessSection />
        <IntegrationsSection />
        <GovernanceSection />
        <PricingSection onOpenBooking={() => setBookingOpen(true)} />
        <FAQSection />
        <ContactSection onOpenBooking={() => setBookingOpen(true)} />
      </main>
      
      <Footer />
      
      <ChatTrigger onClick={() => { setChatOpen(true); trackEvent('chat_trigger_click'); }} />
      
      <LiveChat isOpen={chatOpen} onClose={() => setChatOpen(false)} initialQuestion={chatQuestion} />
      <BookingModal isOpen={bookingOpen} onClose={() => setBookingOpen(false)} />
    </div>
  );
}

export default App;
