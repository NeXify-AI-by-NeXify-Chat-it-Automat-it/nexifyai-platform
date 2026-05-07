import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I } from '../components/shared';
import '../App.css';

const META = {
  de: { title: 'Blog — KI-Wissen für Unternehmen | NeXifyAI',
    description: 'Praktisches KI-Wissen für den DACH-Mittelstand: KI-Agenten, Prozessautomation, CRM-Integration, RAG-Wissenssysteme, DSGVO, ROI und mehr.',
    keywords: 'KI-Blog, KI-Wissen, KI-Agenten Blog, Prozessautomation Blog, CRM Integration Blog, DACH Mittelstand KI' },
  nl: { title: 'Blog — AI-Kennis voor Bedrijven | NeXifyAI',
    description: 'Praktische AI-kennis voor bedrijven: AI-agenten, procesautomatisering, CRM-integratie, RAG-kennissystemen, AVG en meer.',
    keywords: 'AI-blog, AI-kennis, AI-agenten blog, procesautomatisering blog' },
  en: { title: 'Blog — AI Knowledge for Business | NeXifyAI',
    description: 'Practical AI knowledge for businesses: AI agents, process automation, CRM integration, RAG knowledge systems, GDPR, ROI and more.',
    keywords: 'AI blog, AI knowledge, AI agents blog, process automation blog' }
};

const BLOG_POSTS = {
  de: [
    { title: 'KI-Agenten im Mittelstand: Konkrete Anwendungsfälle 2026', desc: 'Wie Unternehmen mit 50-500 Mitarbeitern KI-Agenten produktiv einsetzen — von der Kundenbetreuung bis zur Backend-Automation.', date: '2026-05', cat: 'KI-Agenten' },
    { title: 'CRM + KI: So automatisieren Sie Vertriebsprozesse', desc: 'Integration von KI-Agenten in HubSpot, Salesforce und SAP — Praxisleitfaden für DACH-Unternehmen.', date: '2026-05', cat: 'Integration' },
    { title: 'DSGVO-konforme KI-Assistenten: Was Unternehmen wissen müssen', desc: 'Rechtssichere KI-Implementierung im DACH-Raum. Datenschutz, Auftragsverarbeitung und Haftung.', date: '2026-05', cat: 'Compliance' },
    { title: 'Starter vs. Growth: Welcher KI-Tarif passt zu Ihnen?', desc: 'Detaillierter Vergleich der NeXifyAI-Tarife mit Kosten-Nutzen-Analyse für den Mittelstand.', date: '2026-05', cat: 'Preise' }
  ],
  nl: [
    { title: 'AI-Agenten voor het MKB: Concrete Toepassingen 2026', desc: 'Hoe bedrijven met 50-500 werknemers AI-agenten productief inzetten.', date: '2026-05', cat: 'AI-Agenten' },
    { title: 'AVG-conforme AI-Assistenten: Wat u moet weten', desc: 'Wettelijke AI-implementatie in Nederland en België.', date: '2026-05', cat: 'Compliance' }
  ],
  en: [
    { title: 'AI Agents for SMEs: Practical Use Cases 2026', desc: 'How companies with 50-500 employees use AI agents productively.', date: '2026-05', cat: 'AI Agents' },
    { title: 'GDPR-Compliant AI Assistants: What to Know', desc: 'Legal AI implementation in the EU — data protection, DPA, and liability.', date: '2026-05', cat: 'Compliance' }
  ]
};

export default function BlogPage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const m = META[lang] || META.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();
  const posts = BLOG_POSTS[lang] || BLOG_POSTS.de;

  return (
    <div className="app">
      <SEOHead lang={lang} page="blog" />
      <Helmet>
        <title>{m.title}</title>
        <meta name="description" content={m.description} />
        <meta name="keywords" content={m.keywords} />
        <meta property="og:title" content={m.title} />
        <meta property="og:description" content={m.description} />
        <meta name="twitter:title" content={m.title} />
        <meta name="twitter:description" content={m.description} />
        <script type="application/ld+json">{JSON.stringify({
          '@context': 'https://schema.org', '@type': 'Blog',
          name: m.title, description: m.description,
          blogPost: posts.map(p => ({
            '@type': 'BlogPosting',
            headline: p.title, description: p.desc,
            datePublished: p.date, author: { '@type': 'Organization', name: 'NeXifyAI' }
          }))
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
              <span className="label">{lang === 'en' ? 'BLOG' : lang === 'nl' ? 'BLOG' : 'BLOG'}</span>
              <h1 style={{ fontSize: 'clamp(2rem,4vw,3rem)', fontWeight: 800, marginTop: '0.5rem' }}>
                {lang === 'en' ? 'AI Knowledge for Business' : lang === 'nl' ? 'AI-Kennis voor Bedrijven' : 'KI-Wissen für Unternehmen'}
              </h1>
              <p className="section-subtitle">
                {lang === 'en' ? 'Practical insights, guides, and best practices.' :
                 lang === 'nl' ? 'Praktische inzichten, gidsen en best practices.' :
                 'Praktische Einblicke, Leitfäden und Best Practices.'}
              </p>
            </div>

            <div className="solutions-grid" role="list">
              {posts.map((p, i) => (
                <article key={i} className="sol-card" role="listitem" style={{ cursor: 'default', textAlign: 'left' }}>
                  <span style={{ fontSize: '0.75rem', color: '#FE9B7B', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600 }}>{p.cat}</span>
                  <h2 className="sol-title" style={{ fontSize: '1.2rem', marginTop: '0.5rem' }}>{p.title}</h2>
                  <p className="sol-desc">{p.desc}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
                    <span style={{ fontSize: '0.85rem', color: '#8892a0' }}>{p.date}</span>
                    <span style={{ fontSize: '0.85rem', color: '#FE9B7B' }}>
                      {lang === 'en' ? 'Coming soon →' : lang === 'nl' ? 'Binnenkort →' : 'Bald verfügbar →'}
                    </span>
                  </div>
                  <div className="sol-bar"></div>
                </article>
              ))}
            </div>

            <div style={{ textAlign: 'center', marginTop: '4rem', padding: '3rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1rem' }}>
                {lang === 'en' ? 'Want to stay updated?' : lang === 'nl' ? 'Op de hoogte blijven?' : 'Auf dem Laufenden bleiben?'}
              </h2>
              <p className="section-subtitle" style={{ maxWidth: 500, margin: '0 auto 2rem' }}>
                {lang === 'en' ? 'Subscribe to our newsletter and get AI insights directly in your inbox.' :
                 lang === 'nl' ? 'Abonneer op onze nieuwsbrief en ontvang AI-inzichten.' :
                 'Abonnieren Sie unseren Newsletter und erhalten Sie KI-Wissen direkt ins Postfach.'}
              </p>
              <a href={`mailto:${COMPANY.email}?subject=Newsletter`} className="btn btn-primary btn-glow">
                <I n="mail" /> {lang === 'en' ? 'Subscribe' : lang === 'nl' ? 'Abonneren' : 'Abonnieren'}
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
