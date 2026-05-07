import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I } from '../components/shared';
import '../App.css';

const META = {
  de: { title: 'KI-Agenten & Automatisierung — Leistungen | NeXifyAI',
    description: 'Von KI-Assistenz bis Enterprise Solutions: 6 Kernleistungen für Ihren DACH-Mittelstand. Chatbots, CRM-Integration, Prozessautomation, RAG-Wissenssysteme. DSGVO-konform.',
    keywords: 'KI-Agenten Leistungen, KI-Beratung, Prozessautomation, CRM-Integration, RAG-Wissenssysteme, Dokumentenautomation, Enterprise KI' },
  nl: { title: 'AI-Agenten & Automatisering — Diensten | NeXifyAI',
    description: 'Van AI-assistentie tot Enterprise-oplossingen: 6 kerndiensten. Chatbots, CRM-integratie, procesautomatisering, RAG-kennissystemen. AVG-conform.',
    keywords: 'AI-agenten diensten, AI-advies, procesautomatisering, CRM-integratie, RAG-kennissystemen' },
  en: { title: 'AI Agents & Automation — Services | NeXifyAI',
    description: 'From AI assistance to Enterprise Solutions: 6 core services. Chatbots, CRM integration, process automation, RAG knowledge systems. GDPR-compliant.',
    keywords: 'AI agents services, AI consulting, process automation, CRM integration, RAG knowledge systems' }
};

export default function LeistungenPage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const m = META[lang] || META.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();

  return (
    <div className="app">
      <SEOHead lang={lang} page="leistungen" />
      <Helmet>
        <title>{m.title}</title>
        <meta name="description" content={m.description} />
        <meta name="keywords" content={m.keywords} />
        <meta property="og:title" content={m.title} />
        <meta property="og:description" content={m.description} />
        <meta name="twitter:title" content={m.title} />
        <meta name="twitter:description" content={m.description} />
        <script type="application/ld+json">{JSON.stringify({
          '@context': 'https://schema.org', '@type': 'Service',
          name: m.title, description: m.description,
          provider: { '@type': 'Organization', name: 'NeXifyAI by NeXify' },
          areaServed: ['DE', 'AT', 'CH', 'NL', 'EU']
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
            <div className="section-header" style={{ textAlign: 'center', marginBottom: '4rem' }}>
              <span className="label">{t.solutions.label}</span>
              <h1 style={{ fontSize: 'clamp(2rem,4vw,3rem)', fontWeight: 800, marginTop: '0.5rem' }}>{t.solutions.title}</h1>
              <p className="section-subtitle">{t.solutions.subtitle}</p>
            </div>
            <div className="solutions-grid" role="list">
              {t.solutions.items.map((s, i) => (
                <article key={i} className="sol-card" role="listitem" style={{ cursor: 'default' }}>
                  <div className="sol-icon-wrap"><I n={s.icon} c="sol-icon" /></div>
                  <h2 className="sol-title" style={{ fontSize: '1.2rem' }}>{s.title}</h2>
                  <p className="sol-desc">{s.desc}</p>
                  <div className="sol-bar"></div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section bg-s1" style={{ textAlign: 'center', padding: '4rem 0' }}>
          <div className="container">
            <h2 style={{ fontSize: 'clamp(1.5rem,3vw,2rem)', fontWeight: 700, marginBottom: '1rem' }}>
              {lang === 'en' ? 'Ready to start?' : lang === 'nl' ? 'Klaar om te beginnen?' : 'Bereit zu starten?'}
            </h2>
            <p className="section-subtitle" style={{ maxWidth: 600, margin: '0 auto 2rem' }}>
              {lang === 'en' ? 'Book a free consultation and let us analyze your requirements.' :
               lang === 'nl' ? 'Boek een gratis adviesgesprek en laat ons uw wensen analyseren.' :
               'Vereinbaren Sie ein kostenloses Beratungsgespräch und lassen Sie uns Ihre Anforderungen analysieren.'}
            </p>
            <a href="/termin" className="btn btn-primary btn-lg btn-glow">
              {lang === 'en' ? 'Book consultation' : lang === 'nl' ? 'Adviesgesprek boeken' : 'Beratung buchen'}
            </a>
          </div>
        </section>
      </main>

      <footer className="footer" role="contentinfo">
        <div className="container">
          <div className="footer-grid">
            <div className="footer-brand">
              <div className="footer-logo"><img src="/nexifyai-logo-light.png" alt="neXifyAI" height="28" style="height:28px;width:auto" /><span>NeXify<span className="brand-ai">AI</span></span></div>
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
