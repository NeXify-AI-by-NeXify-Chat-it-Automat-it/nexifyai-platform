import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I, track } from '../components/shared';
import './BookingPage.css';

const TEXTS = {
  de: {
    title: 'Strategiegespräch buchen',
    subtitle: 'Wählen Sie einen passenden Termin — kostenlos, vertraulich und unverbindlich.',
    loadingText: 'Kalender wird geladen...',
  },
  nl: {
    title: 'Strategiegesprek boeken',
    subtitle: 'Kies een geschikte datum — gratis, vertrouwelijk en vrijblijvend.',
    loadingText: 'Agenda wordt geladen...',
  },
  en: {
    title: 'Book Strategy Call',
    subtitle: 'Choose a convenient time — free, confidential, and non-binding.',
    loadingText: 'Loading calendar...',
  }
};

export default function BookingPage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const tx = TEXTS[lang] || TEXTS.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();

  useEffect(() => {
    track('page_view', { page: 'booking' });
    // Load Calendly widget
    const script = document.createElement('script');
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.async = true;
    document.head.appendChild(script);
    return () => { document.head.removeChild(script); };
  }, []);

  return (
    <div className="app">
      <SEOHead lang={lang} page="booking" />
      <Helmet>
        <title>{tx.title} | NeXifyAI</title>
        <meta name="description" content={tx.subtitle} />
        <meta name="robots" content="index, follow" />
        <link rel="canonical" href={`https://www.nexify-automate.com/${lang}/termin`} />
        <script type="application/ld+json">{JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'BreadcrumbList',
          itemListElement: [
            { '@type': 'ListItem', position: 1, name: 'Home', item: `https://www.nexify-automate.com/${lang}` },
            { '@type': 'ListItem', position: 2, name: tx.title, item: `https://www.nexify-automate.com/${lang}/termin` }
          ]
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
        <section className="section bg-dark" style={{ paddingTop: '8rem', minHeight: '100vh' }}>
          <div className="container">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              style={{ textAlign: 'center', marginBottom: '3rem' }}
            >
              <span className="label">CALENDLY</span>
              <h1 style={{
                fontSize: 'clamp(1.8rem,4vw,2.5rem)',
                fontWeight: 800,
                marginTop: '0.5rem',
                marginBottom: '0.5rem'
              }}>
                {tx.title}
              </h1>
              <p className="section-subtitle" style={{ maxWidth: 600, margin: '0 auto' }}>
                {tx.subtitle}
              </p>

              <div style={{
                display: 'flex',
                gap: '1rem',
                justifyContent: 'center',
                flexWrap: 'wrap',
                marginTop: '2rem',
                color: '#8892a0',
                fontSize: '0.9rem'
              }}>
                <span><I n="schedule" /> 30 Min.</span>
                <span><I n="verified_user" /> {lang === 'en' ? 'GDPR-compliant' : lang === 'nl' ? 'AVG-conform' : 'DSGVO-konform'}</span>
                <span><I n="lock" /> {lang === 'en' ? 'Confidential' : lang === 'nl' ? 'Vertrouwelijk' : 'Vertraulich'}</span>
                <span><I n="workspace_premium" /> {lang === 'en' ? 'No obligation' : lang === 'nl' ? 'Vrijblijvend' : 'Unverbindlich'}</span>
              </div>
            </motion.div>

            {/* Calendly Inline Widget */}
            <div style={{
              maxWidth: 900,
              margin: '0 auto',
              background: 'rgba(255,255,255,0.02)',
              borderRadius: '16px',
              border: '1px solid rgba(255,255,255,0.06)',
              overflow: 'hidden',
              minHeight: 700
            }}>
              <div
                className="calendly-inline-widget"
                data-url={`https://calendly.com/pascal-courbois/30min`}
                style={{ minWidth: 320, height: 700 }}
              />
            </div>

            {/* Fallback link */}
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
              <p style={{ color: '#8892a0', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                {lang === 'en' ? 'Calendar not loading?' : lang === 'nl' ? 'Agenda niet zichtbaar?' : 'Kalender wird nicht angezeigt?'}
              </p>
              <a
                href="https://calendly.com/pascal-courbois/30min"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <I n="open_in_new" />
                {lang === 'en' ? 'Open in Calendly' : lang === 'nl' ? 'Openen in Calendly' : 'In Calendly öffnen'}
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer" role="contentinfo">
        <div className="container">
          <div className="footer-grid">
            <div className="footer-brand">
              <div className="footer-logo"><img src="/icon-mark.svg" alt="" width="28" height="28" /><span>NeXify<span className="brand-ai">AI</span></span></div>
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
