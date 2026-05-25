import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I, Footer } from '../components/shared';
import '../App.css';

const META = {
  de: { title: 'Kontakt — KI-Beratung für Unternehmen | NeXifyAI',
    description: 'Kontaktieren Sie NeXifyAI für KI-Beratung im DACH-Mittelstand. Telefon: +31 6 133 188 56, E-Mail: support@nexifyai.cloud. Kostenloses Erstgespräch vereinbaren.',
    keywords: 'KI-Beratung Kontakt, KI-Agentur Kontakt, NeXifyAI Kontakt, KI-Beratung Telefon, DACH KI Agentur Venlo' },
  nl: { title: 'Contact — AI-Advies voor Bedrijven | NeXifyAI',
    description: 'Neem contact op met NeXifyAI voor AI-advies. Telefoon: +31 6 133 188 56, E-mail: support@nexifyai.cloud. Gratis eerste gesprek.',
    keywords: 'AI-advies contact, AI-agentuurscontact, NeXifyAI contact' },
  en: { title: 'Contact — AI Consulting for Business | NeXifyAI',
    description: 'Contact NeXifyAI for AI consulting. Phone: +31 6 133 188 56, Email: support@nexifyai.cloud. Free initial consultation.',
    keywords: 'AI consulting contact, AI agency contact, NeXifyAI contact' }
};

function ContactForm({ lang, t }) {
  const f = t.contact.form;
  const v = t.contact.validation;
  const [form, setForm] = useState({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', nachricht: '', consent: false, '_hp': '' });
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState('idle'); // idle | sending | success | error

  const validate = () => {
    const e = {};
    if (!form.vorname.trim() || form.vorname.trim().length < 2) e.vorname = v.firstName;
    if (!form.nachname.trim() || form.nachname.trim().length < 2) e.nachname = v.lastName;
    if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = v.email;
    if (!form.nachricht.trim() || form.nachricht.trim().length < 10) e.nachricht = v.message;
    if (!form.consent) e.consent = lang === 'en' ? 'Please accept the privacy policy.' : lang === 'nl' ? 'Accepteer het privacybeleid.' : 'Bitte Datenschutzerklärung akzeptieren.';
    return e;
  };

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => { const n = { ...prev }; delete n[field]; return n; });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setStatus('sending');
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vorname: form.vorname.trim(),
          nachname: form.nachname.trim(),
          email: form.email.trim(),
          telefon: form.telefon.trim() || null,
          unternehmen: form.unternehmen.trim() || null,
          nachricht: form.nachricht.trim(),
          source: 'contact_form',
          language: lang,
          consent: true,
          datenschutz_akzeptiert: true,
          _hp: form._hp
        })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setStatus('success');
      setForm({ vorname: '', nachname: '', email: '', telefon: '', unternehmen: '', nachricht: '', consent: false, '_hp': '' });
    } catch (err) {
      setStatus('error');
    }
  };

  const heading = lang === 'en' ? 'Send us a message' : lang === 'nl' ? 'Stuur een bericht' : 'Nachricht senden';
  const responseTime = lang === 'en' ? 'We typically respond within 24 hours.' : lang === 'nl' ? 'Wij reageren meestal binnen 24 uur.' : 'Wir antworten in der Regel innerhalb von 24 Stunden.';
  const consentText = lang === 'en' ? 'I accept the privacy policy and consent to the processing of my data.' : lang === 'nl' ? 'Ik accepteer het privacybeleid en stem in met de verwerking van mijn gegevens.' : 'Ich akzeptiere die Datenschutzerklärung und willige in die Verarbeitung meiner Daten ein.';

  if (status === 'success') {
    return (
      <div className="contact-form" style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>✅</div>
        <h2 style={{ marginBottom: '0.75rem', color: '#FE9B7B' }}>{lang === 'en' ? 'Message sent!' : lang === 'nl' ? 'Bericht verzonden!' : 'Nachricht gesendet!'}</h2>
        <p style={{ color: '#8892a0' }}>{f.success}</p>
        <button className="btn btn-ghost" style={{ marginTop: '1.5rem' }} onClick={() => setStatus('idle')}>
          {lang === 'en' ? 'Send another message' : lang === 'nl' ? 'Nog een bericht sturen' : 'Weitere Nachricht senden'}
        </button>
      </div>
    );
  }

  return (
    <form className="contact-form" style={{ padding: '2rem' }} onSubmit={handleSubmit} noValidate>
      <h2 style={{ marginBottom: '0.5rem', fontSize: '1.3rem' }}>{heading}</h2>
      <p style={{ color: '#8892a0', marginBottom: '1.25rem', fontSize: '0.875rem' }}>{responseTime}</p>

      {/* Honeypot — invisible to humans */}
      <div style={{ position: 'absolute', opacity: 0, height: 0, overflow: 'hidden' }}>
        <input type="text" name="_hp" tabIndex={-1} autoComplete="off" value={form._hp} onChange={e => handleChange('_hp', e.target.value)} />
      </div>

      <div className="form-split" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <div className="form-group">
          <label className="form-label">{f.firstName} *</label>
          <input type="text" className={`form-input${errors.vorname ? ' error' : ''}`} value={form.vorname} onChange={e => handleChange('vorname', e.target.value)} placeholder={f.firstName} />
          {errors.vorname && <span className="form-error">{errors.vorname}</span>}
        </div>
        <div className="form-group">
          <label className="form-label">{f.lastName} *</label>
          <input type="text" className={`form-input${errors.nachname ? ' error' : ''}`} value={form.nachname} onChange={e => handleChange('nachname', e.target.value)} placeholder={f.lastName} />
          {errors.nachname && <span className="form-error">{errors.nachname}</span>}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">{f.email} *</label>
        <input type="email" className={`form-input${errors.email ? ' error' : ''}`} value={form.email} onChange={e => handleChange('email', e.target.value)} placeholder="name@unternehmen.de" />
        {errors.email && <span className="form-error">{errors.email}</span>}
      </div>

      <div className="form-split" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <div className="form-group">
          <label className="form-label">{f.phone}</label>
          <input type="tel" className="form-input" value={form.telefon} onChange={e => handleChange('telefon', e.target.value)} placeholder="+31 6 133 188 56" />
        </div>
        <div className="form-group">
          <label className="form-label">{f.company}</label>
          <input type="text" className="form-input" value={form.unternehmen} onChange={e => handleChange('unternehmen', e.target.value)} placeholder={f.company} />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">{f.message} *</label>
        <textarea className={`form-textarea${errors.nachricht ? ' error' : ''}`} rows={4} value={form.nachricht} onChange={e => handleChange('nachricht', e.target.value)}
          placeholder={lang === 'en' ? 'Describe your challenge…' : lang === 'nl' ? 'Beschrijf uw uitdaging…' : 'Beschreiben Sie Ihre Herausforderung…'} />
        {errors.nachricht && <span className="form-error">{errors.nachricht}</span>}
      </div>

      <label style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', cursor: 'pointer', fontSize: '0.8125rem', color: '#8892a0', lineHeight: 1.5 }}>
        <input type="checkbox" checked={form.consent} onChange={e => handleChange('consent', e.target.checked)}
          style={{ marginTop: '2px', accentColor: '#FE9B7B', width: '16px', height: '16px', flexShrink: 0 }} />
        <span>{consentText} <a href={`/${lang}/datenschutz`} target="_blank" rel="noopener noreferrer" style={{ color: '#FE9B7B', textDecoration: 'underline' }}>
          {lang === 'en' ? 'Privacy Policy' : lang === 'nl' ? 'Privacybeleid' : 'Datenschutzerklärung'}
        </a></span>
      </label>
      {errors.consent && <span className="form-error">{errors.consent}</span>}

      <button type="submit" className="btn btn-primary btn-glow contact-submit" disabled={status === 'sending'}>
        {status === 'sending' ? (
          <><span className="spinner" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.2)', borderTopColor: '#fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.6s linear infinite', marginRight: 8, verticalAlign: 'middle' }} /> {f.sending}</>
        ) : (
          <><I n="mail" /> {f.submit}</>
        )}
      </button>

      {status === 'error' && (
        <div className="form-status" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', color: '#fca5a5' }}>
          <I n="warning" /> {f.error}
        </div>
      )}
    </form>
  );
}

export default function KontaktPage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const m = META[lang] || META.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();

  return (
    <div className="app">
      <SEOHead lang={lang} page="kontakt" />
      <Helmet>
        <title>{m.title}</title>
        <meta name="description" content={m.description} />
        <meta name="keywords" content={m.keywords} />
        <meta property="og:title" content={m.title} />
        <meta property="og:description" content={m.description} />
        <meta name="twitter:title" content={m.title} />
        <meta name="twitter:description" content={m.description} />
        <script type="application/ld+json">{JSON.stringify({
          '@context': 'https://schema.org', '@type': 'ContactPage',
          name: m.title, description: m.description,
          mainEntity: {
            '@type': 'Organization',
            name: 'NeXifyAI by NeXify',
            telephone: '+31 6 133 188 56',
            email: 'support@nexifyai.cloud',
            address: { '@type': 'PostalAddress', streetAddress: 'Graaf van Loonstraat 1E', addressLocality: 'Venlo', postalCode: '5921 JA', addressCountry: 'NL' }
          }
        })}</script>
      </Helmet>

      <nav className="nav scrolled" role="navigation">
        <div className="container nav-inner">
          <a href={`/${lang}`} className="nav-logo"><Logo /></a>
          <div className="nav-actions">
            <a href={`/${lang}`} className="btn btn-ghost">
              {lang === 'en' ? 'Back to Home' : lang === 'nl' ? 'Terug naar home' : 'Zurück zur Startseite'}
            </a>
          </div>
        </div>
      </nav>

      <main id="main-content">
        <section className="section bg-dark" style={{ paddingTop: '8rem' }}>
          <div className="container">
            <div className="contact-grid" style={{ alignItems: 'start' }}>
              <div>
                <span className="label">{t.contact.label}</span>
                <h1 style={{ fontSize: 'clamp(2rem,4vw,3rem)', fontWeight: 800, margin: '0.5rem 0 1rem' }}>{t.contact.title}</h1>
                <p className="section-subtitle">{t.contact.subtitle}</p>
                <div className="contact-benefits" style={{ margin: '2rem 0' }}>
                  {t.contact.benefits.map((b, i) => (
                    <div key={i} className="contact-benefit"><I n="verified" /><span>{b}</span></div>
                  ))}
                </div>
                <div className="contact-cta-group" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  <a href="/termin" className="btn btn-primary btn-lg btn-glow">
                    {lang === 'en' ? 'Book Consultation' : lang === 'nl' ? 'Advies starten' : 'Beratung starten'} <I n="forum" />
                  </a>
                </div>
                <div style={{ marginTop: '3rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', color: '#8892a0' }}>
                  <p><strong style={{ color: '#dee3ed' }}>Telefon:</strong> <a href="tel:+31613318856" style={{ color: '#FE9B7B' }}>+31 6 133 188 56</a></p>
                  <p><strong style={{ color: '#dee3ed' }}>E-Mail:</strong> <a href="mailto:support@nexifyai.cloud" style={{ color: '#FE9B7B' }}>support@nexifyai.cloud</a></p>
                  <p><strong style={{ color: '#dee3ed' }}>Adresse:</strong> {COMPANY.addr?.nl?.s ?? ''}, {COMPANY.addr?.nl?.c ?? ''}</p>
                  <p><strong style={{ color: '#dee3ed' }}>KvK:</strong> {COMPANY.kvk} | <strong style={{ color: '#dee3ed' }}>USt-ID:</strong> {COMPANY.vat}</p>
                </div>
              </div>
              <div className="contact-form-box" style={{ width: '100%', maxWidth: 500 }}>
                <ContactForm lang={lang} t={t} />
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer onCookieSettings={() => {}} t={t} lang={lang} />
    </div>
  );
}
