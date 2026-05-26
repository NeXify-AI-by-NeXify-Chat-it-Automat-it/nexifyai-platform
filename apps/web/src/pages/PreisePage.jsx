import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import LanguageSwitcher from '../components/LanguageSwitcher';
import LiveChat from '../components/sections/LiveChat';
import Booking from '../components/sections/BookingModal';
import { COMPANY, LEGAL_PATHS, Logo, I, Footer, track } from '../components/shared';
import '../App.css';

const META = {
  de: { title: 'Preise & Tarife — KI-Agenten für Unternehmen | NeXifyAI',
    description: 'Flexible Tarife für KI-Agenten: Starter 499€, Growth 1.299€ oder Enterprise ab 39.900€/Jahr. Individuelle Angebote. DSGVO-konform. Jetzt Beratungsgespräch buchen.',
    keywords: 'KI-Agenten Preise, KI-Tarife, Starter 499€, Growth 1.299€, Enterprise 39.900€, KI-Beratung Kosten, DACH Mittelstand' },
  nl: { title: 'Prijzen & Tarieven — AI-Agenten voor Bedrijven | NeXifyAI',
    description: 'Flexibele tarieven voor AI-agenten: Starter €499, Growth €1.299 of Enterprise vanaf €39.900/jaar. AVG-conform. Vrijblijvend adviesgesprek.',
    keywords: 'AI-agenten prijzen, AI-tarieven, Starter, Growth, Enterprise, AI-advies kosten' },
  en: { title: 'Pricing & Plans — AI Agents for Business | NeXifyAI',
    description: 'Flexible pricing for AI agents: Starter €499, Growth €1.299 or Enterprise from €39,900/year. GDPR-compliant. Book a free consultation.',
    keywords: 'AI agents pricing, AI plans, Starter €499, Growth €1.299, Enterprise €39,900, AI consulting cost' }
};

export default function PreisePage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const m = META[lang] || META.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;

  const [chatOpen, setChatOpen] = useState(false);
  const [bookOpen, setBookOpen] = useState(false);
  const [chatQ, setChatQ] = useState('');

  const openChat = (msg = '') => { setChatQ(msg); setChatOpen(true); track('chat_open', { source: 'preise_cta', msg }); };
  const openBooking = () => { setBookOpen(true); };

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
          <div className="nav-links" role="menubar">
            <a href={`/${lang}/leistungen`} className="nav-link" role="menuitem">{t.nav.leistungen}</a>
            <a href={`/${lang}/preise`} className="nav-link" role="menuitem">{t.nav.tarife}</a>
            <a href={`/${lang}/kontakt`} className="nav-link" role="menuitem">{lang === 'en' ? 'Contact' : lang === 'nl' ? 'Contact' : 'Kontakt'}</a>
          </div>
          <div className="nav-actions">
            <LanguageSwitcher />
            <button className="btn btn-primary nav-cta" onClick={() => { openChat(); track('cta_click', { loc: 'nav_preise' }); }}>
              {lang === 'en' ? 'Start Consultation' : lang === 'nl' ? 'Advies starten' : 'Beratung starten'}
            </button>
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
                  <button className={`btn ${pl.hl ? 'btn-primary btn-glow' : pl.name.includes('Enterprise') ? 'btn-primary' : 'btn-secondary'} price-cta`}
                    onClick={() => {
                      if (pl.name.includes('Enterprise')) {
                        openChat(lang === 'en' ? `I'm interested in the Enterprise plan — please contact me` : lang === 'nl' ? `Ik ben geïnteresseerd in het Enterprise-plan — neem contact met me op` : `Ich interessiere mich für den Enterprise-Tarif — bitte kontaktieren Sie mich`);
                      } else {
                        openBooking();
                      }
                      track('pricing_click', { plan: pl.name });
                    }}>
                    {pl.cta}
                  </button>
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
                  <button className="btn btn-primary" onClick={() => { openChat(lang === 'en' ? 'I need a custom solution — please create an individual quote' : lang === 'nl' ? 'Ik heb een maatwerkoplossing nodig — maak een individuele offerte' : 'Ich benötige eine individuelle Lösung — bitte erstellen Sie mir ein maßgeschneidertes Angebot'); track('custom_quote_click'); }}>
                    {lang === 'en' ? 'Request custom quote' : lang === 'nl' ? 'Individueel aanvragen' : 'Individuell anfragen'} <I n="arrow_forward" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer onCookieSettings={() => {}} t={t} lang={lang} />
      <LiveChat isOpen={chatOpen} onClose={() => setChatOpen(false)} initialQ={chatQ} onBook={openBooking} t={t} lang={lang} />
      <Booking isOpen={bookOpen} onClose={() => setBookOpen(false)} t={t} lang={lang} />
    </div>
  );
}
