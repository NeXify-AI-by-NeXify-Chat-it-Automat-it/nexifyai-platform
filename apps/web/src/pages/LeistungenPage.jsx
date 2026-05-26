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
  de: { title: 'KI-Agenten, Webentwicklung & Automatisierung — Leistungen | NeXifyAI',
    description: 'Von KI-Assistenz über Webentwicklung bis Enterprise Solutions: 10 Kernleistungen für Ihren DACH-Mittelstand. Chatbots, CRM-Integration, Prozessautomation, RAG-Wissenssysteme. DSGVO-konform.',
    keywords: 'KI-Agenten Leistungen, KI-Beratung, Prozessautomation, CRM-Integration, RAG-Wissenssysteme, Webentwicklung, Plattformen, Portale, Managed Services' },
  nl: { title: 'AI-Agenten, Webontwikkeling & Automatisering — Diensten | NeXifyAI',
    description: 'Van AI-assistentie tot webontwikkeling en Enterprise-oplossingen: 10 kerndiensten. Chatbots, CRM-integratie, procesautomatisering, RAG-kennissystemen. AVG-conform.',
    keywords: 'AI-agenten diensten, AI-advies, procesautomatisering, CRM-integratie, RAG-kennissystemen, webontwikkeling, platformen, portalen' },
  en: { title: 'AI Agents, Web Development & Automation — Services | NeXifyAI',
    description: 'From AI assistance to web development and Enterprise Solutions: 10 core services. Chatbots, CRM integration, process automation, RAG knowledge systems. GDPR-compliant.',
    keywords: 'AI agents services, AI consulting, process automation, CRM integration, RAG knowledge systems, web development, platforms, portals' }
};

export default function LeistungenPage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const m = META[lang] || META.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;

  const [chatOpen, setChatOpen] = useState(false);
  const [bookOpen, setBookOpen] = useState(false);
  const [chatQ, setChatQ] = useState('');

  const openChat = (msg = '') => { setChatQ(msg); setChatOpen(true); track('chat_open', { source: 'leistungen_cta', msg }); };
  const openBooking = () => { setBookOpen(true); };

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
          <div className="nav-links" role="menubar">
            <a href={`/${lang}/leistungen`} className="nav-link" role="menuitem">{t.nav.leistungen}</a>
            <a href={`/${lang}/preise`} className="nav-link" role="menuitem">{t.nav.tarife}</a>
            <a href={`/${lang}/kontakt`} className="nav-link" role="menuitem">{lang === 'en' ? 'Contact' : lang === 'nl' ? 'Contact' : 'Kontakt'}</a>
          </div>
          <div className="nav-actions">
            <LanguageSwitcher />
            <button className="btn btn-primary nav-cta" onClick={() => { openChat(); track('cta_click', { loc: 'nav_leistungen' }); }}>
              {lang === 'en' ? 'Start Consultation' : lang === 'nl' ? 'Advies starten' : 'Beratung starten'}
            </button>
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
            <button className="btn btn-primary btn-lg btn-glow" onClick={() => { openBooking(); track('cta_click', { loc: 'leistungen_cta' }); }}>
              {lang === 'en' ? 'Book consultation' : lang === 'nl' ? 'Adviesgesprek boeken' : 'Beratung buchen'}
            </button>
          </div>
        </section>
      </main>

      <Footer onCookieSettings={() => {}} t={t} lang={lang} />
      <LiveChat isOpen={chatOpen} onClose={() => setChatOpen(false)} initialQ={chatQ} onBook={openBooking} t={t} lang={lang} />
      <Booking isOpen={bookOpen} onClose={() => setBookOpen(false)} t={t} lang={lang} />
    </div>
  );
}
