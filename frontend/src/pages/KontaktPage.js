import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I } from '../components/shared';
import '../App.css';

const META = {
  de: { title: 'Kontakt — KI-Beratung für Unternehmen | NeXifyAI',
    description: 'Kontaktieren Sie NeXifyAI für KI-Beratung im DACH-Mittelstand. Telefon: +31 6 133 188 56, E-Mail: support@nexify-automate.com. Kostenloses Erstgespräch vereinbaren.',
    keywords: 'KI-Beratung Kontakt, KI-Agentur Kontakt, NeXifyAI Kontakt, KI-Beratung Telefon, DACH KI Agentur Venlo' },
  nl: { title: 'Contact — AI-Advies voor Bedrijven | NeXifyAI',
    description: 'Neem contact op met NeXifyAI voor AI-advies. Telefoon: +31 6 133 188 56, E-mail: support@nexify-automate.com. Gratis eerste gesprek.',
    keywords: 'AI-advies contact, AI-agentuurscontact, NeXifyAI contact' },
  en: { title: 'Contact — AI Consulting for Business | NeXifyAI',
    description: 'Contact NeXifyAI for AI consulting. Phone: +31 6 133 188 56, Email: support@nexify-automate.com. Free initial consultation.',
    keywords: 'AI consulting contact, AI agency contact, NeXifyAI contact' }
};

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
            email: 'support@nexify-automate.com',
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
                  <p><strong style={{ color: '#dee3ed' }}>E-Mail:</strong> <a href="mailto:support@nexify-automate.com" style={{ color: '#FE9B7B' }}>support@nexify-automate.com</a></p>
                  <p><strong style={{ color: '#dee3ed' }}>Adresse:</strong> {COMPANY.addr.nl.s}, {COMPANY.addr.nl.c}</p>
                  <p><strong style={{ color: '#dee3ed' }}>KvK:</strong> {COMPANY.kvk} | <strong style={{ color: '#dee3ed' }}>USt-ID:</strong> {COMPANY.vat}</p>
                </div>
              </div>
              <div className="contact-form-box" style={{ width: '100%', maxWidth: 500 }}>
                <div className="contact-form" style={{ padding: '2rem', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <h2 style={{ marginBottom: '1.5rem', fontSize: '1.3rem' }}>
                    {lang === 'en' ? 'Send us a message' : lang === 'nl' ? 'Stuur een bericht' : 'Nachricht senden'}
                  </h2>
                  <p style={{ color: '#8892a0', marginBottom: '1.5rem' }}>
                    {lang === 'en' ? 'We typically respond within 24 hours.' :
                     lang === 'nl' ? 'Wij reageren meestal binnen 24 uur.' :
                     'Wir antworten in der Regel innerhalb von 24 Stunden.'}
                  </p>
                  <a href={`mailto:${COMPANY.email}`} className="btn btn-primary btn-glow" style={{ width: '100%', textAlign: 'center' }}>
                    <I n="mail" /> {lang === 'en' ? 'Send Email' : lang === 'nl' ? 'E-mail sturen' : 'E-Mail senden'}
                  </a>
                  <div style={{ marginTop: '1rem' }}>
                    <a href="https://wa.me/31613318856" target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ width: '100%', textAlign: 'center' }}>
                      <I n="chat" /> {lang === 'en' ? 'Chat on WhatsApp' : lang === 'nl' ? 'Chat op WhatsApp' : 'Chat auf WhatsApp'}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer" role="contentinfo">
        <div className="container">
          <div className="footer-grid">
            <div className="footer-brand">
              <div className="footer-logo"><img src="/nexifyai-logo-light.png" alt="neXifyAI" height="28" /><span>NeXify<span className="brand-ai">AI</span></span></div>
              <div className="footer-tagline">{t.footer.tagline}</div>
              <div className="footer-legal-name">{COMPANY.legal}</div>
              <address className="footer-contact">
                <p><strong>NL:</strong> {COMPANY.addr.nl.s}, {COMPANY.addr.nl.c}</p>
                <p>Tel: <a href={`tel:${COMPANY.phone.replace(/\s/g, '')}`}>{COMPANY.phone}</a></p>
                <p>E-Mail: <a href={`mailto:${COMPANY.email}`}>{COMPANY.email}</a></p>
              </address>
            </div>
            <nav className="footer-nav-col">
              <h3 className="footer-nav-title">{t.footer.legal}</h3>
              <ul className="footer-links">
                <li><a href={lp.impressum}>{t.footer.impressum}</a></li>
                <li><a href={lp.datenschutz}>{t.footer.datenschutz}</a></li>
                <li><a href={lp.agb}>{t.footer.agb}</a></li>
                <li><a href={lp.ki}>{t.footer.ki}</a></li>
              </ul>
            </nav>
          </div>
          <div className="footer-bottom">
            <span className="footer-copy">{t.footer.copy.replace('{y}', thisYear)}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
