import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I } from '../components/shared';
import '../App.css';

const META = {
  de: { title: 'Preise & Tarife — KI-Agenten für Unternehmen | NeXifyAI',
    description: 'Flexible Tarife für KI-Agenten: Starter 499€, Growth 1.299€ oder Enterprise ab 39.900€. Individuelle Angebote. DSGVO-konform. Jetzt Beratungsgespräch buchen.',
    keywords: 'KI-Agenten Preise, KI-Tarife, Starter 499€, Growth 1.299€, Enterprise ab 39.900€, KI-Beratung Kosten, DACH Mittelstand' },
  nl: { title: 'Prijzen & Tarieven — AI-Agenten voor Bedrijven | NeXifyAI',
    description: 'Flexibele tarieven voor AI-agenten: Starter €499, Growth €1.299 of Enterprise vanaf €39.900. AVG-conform. Vrijblijvend adviesgesprek.',
    keywords: 'AI-agenten prijzen, AI-tarieven, Starter, Growth, Enterprise, AI-advies kosten' },
  en: { title: 'Pricing & Plans — AI Agents for Business | NeXifyAI',
    description: 'Flexible pricing for AI agents: Starter €499, Growth €1.299 or Enterprise from €39.900. GDPR-compliant. Book a free consultation.',
    keywords: 'AI agents pricing, AI plans, Starter €499, Growth €1.299, Enterprise from €39.900, AI consulting cost' }
};

export default function PreisePage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const m = META[lang] || META.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();

  const customLabel = { de: 'Individuelles Angebot', nl: 'Individuele offerte', en: 'Custom Quote' };
  const customDesc = {
    de: 'Sie benötigen eine maßgeschneiderte Lösung? Wir analysieren Ihre Anforderungen und erstellen ein individuelles Angebot — kostenlos und unverbindlich.',
    nl: 'Heeft u een oplossing op maat nodig? Wij analyseren uw behoeften en stellen een individuele offerte op — gratis en vrijblijvend.',
    en: 'Need a tailored solution? We analyze your requirements and create a custom quote — free and non-binding.'
  };

  return (
    <div className="app">
      <SEOHead lang={lang} page="preise" />
      <Helmet>
        <title>{m.title}</title>
        <meta name="description" content={m.description} />
        <meta name="keywords" content={m.keywords} />
        <meta property="og:title" content={m.title} />
        <meta property="og:description" content={m.description} />
        <meta name="twitter:title" content={m.title} />
        <meta name="twitter:description" content={m.description} />
        <script type="application/ld+json">{JSON.stringify({
          '@context': 'https://schema.org', '@type': 'Product',
          name: 'KI-Agenten für Unternehmen', description: m.description,
          offers: [
            { '@type': 'Offer', name: 'Starter', price: '499', priceCurrency: 'EUR' },
            { '@type': 'Offer', name: 'Growth', price: '1299', priceCurrency: 'EUR' },
            { '@type': 'Offer', name: 'Enterprise', price: '39900', priceCurrency: 'EUR' }
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
        <section className="section bg-dark" style={{ paddingTop: '8rem' }}>
          <div className="container">
            <div className="section-header" style={{ textAlign: 'center', marginBottom: '4rem' }}>
              <span className="label">{t.pricing.label}</span>
              <h1 style={{ fontSize: 'clamp(2rem,4vw,3rem)', fontWeight: 800, marginTop: '0.5rem' }}>{t.pricing.title}</h1>
              <p className="section-subtitle">{t.pricing.subtitle}</p>
            </div>
            <div className="pricing-grid" role="list">
              {t.pricing.plans.map((pl, i) => (
                <article key={i} className={`price-card ${pl.hl ? 'hl' : ''}`} role="listitem" style={{ cursor: 'default' }}>
                  {pl.badge && <span className="price-badge">{pl.badge}</span>}
                  {pl.hl && <div className="price-glow-ring" />}
                  <div className="price-name">{pl.name}</div>
                  <div className="price-val">{pl.price}<span className="price-period"> {pl.period}</span></div>
                  <div className="price-divider" />
                  <ul className="price-features">{pl.features.map((f, fi) => <li key={fi} className="price-feat"><I n="check_circle" c="price-check" />{f}</li>)}</ul>
                  <a href="/termin" className={`btn ${pl.hl ? 'btn-primary btn-glow' : 'btn-secondary'} price-cta`}>{pl.cta}</a>
                </article>
              ))}
            </div>
            <div className="custom-quote-bar">
              <div className="custom-quote-inner">
                <div className="custom-quote-icon"><I n="architecture" /></div>
                <div className="custom-quote-text">
                  <h4>{customLabel[lang] || customLabel.de}</h4>
                  <p>{customDesc[lang] || customDesc.de}</p>
                </div>
                <div className="custom-quote-actions">
                  <a href="/termin" className="btn btn-primary">{lang === 'en' ? 'Request custom quote' : lang === 'nl' ? 'Individueel aanvragen' : 'Individuell anfragen'} <I n="arrow_forward" /></a>
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
              <div className="footer-logo"><img src="/nexifyai-logo-light.png" alt="" width="28" height="28" /><span>NeXify<span className="brand-ai">AI</span></span></div>
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
