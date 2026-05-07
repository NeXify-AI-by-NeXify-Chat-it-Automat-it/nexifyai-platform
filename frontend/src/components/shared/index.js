import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

export const API = process.env.REACT_APP_BACKEND_URL || '';

export const COMPANY = {
  name: 'NeXifyAI by NeXify', tagline: 'Chat it. Automate it.', legal: 'neXify - Chat it. Automat it.',
  ceo: 'Pascal Courbois, Geschäftsführer',
  phone: '+31 6 133 188 56', email: 'support@nexify-automate.com', web: 'nexify-automate.com', kvk: '90483944', vat: 'NL865786276B01', addr: { nl: { s: 'Graaf van Loonstraat 1E', c: '5921 JA Venlo' } }
};

export const LEGAL_PATHS = {
  de: { impressum: '/de/impressum', datenschutz: '/de/datenschutz', agb: '/de/agb', ki: '/de/ki-hinweise', widerruf: '/de/widerrufsbelehrung', cookies: '/de/cookie-richtlinie', avv: '/de/avv' },
  nl: { impressum: '/nl/impressum', datenschutz: '/nl/privacybeleid', agb: '/nl/voorwaarden', ki: '/nl/ai-informatie', widerruf: '/nl/herroepingsrecht', cookies: '/nl/cookiebeleid', avv: '/nl/verwerkersovereenkomst' },
  en: { impressum: '/en/imprint', datenschutz: '/en/privacy', agb: '/en/terms', ki: '/en/ai-transparency', widerruf: '/en/cancellation-policy', cookies: '/en/cookie-policy', avv: '/en/dpa' }
};

export const LOCALE_MAP = { de: 'de-DE', nl: 'nl-NL', en: 'en-GB' };

export const genSid = () => `s_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;

export const track = async (ev, props = {}) => {
  try {
    const sid = sessionStorage.getItem('nx_s') || genSid();
    sessionStorage.setItem('nx_s', sid);
    await fetch(`${API}/api/analytics/track`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ event: ev, properties: { ...props, ts: new Date().toISOString() }, session_id: sid }) });
  } catch (_) { if (process.env.NODE_ENV === 'development') console.error('Analytics track failed:', _); }
};

export const I = ({ n, c = '' }) => <span className={`material-symbols-outlined ${c}`} aria-hidden="true">{n}</span>;

export const fadeUp = { hidden: { opacity: 0, y: 40 }, visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.25, 0.4, 0, 1] } } };
export const fadeIn = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { duration: 0.6 } } };
export const stagger = { visible: { transition: { staggerChildren: 0.1 } } };
export const scaleIn = { hidden: { opacity: 0, scale: 0.9 }, visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: [0.25, 0.4, 0, 1] } } };

export function AnimSection({ children, className = '', id, ...props }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });
  return (
    <motion.section ref={ref} id={id} className={className} initial="hidden" animate={isInView ? 'visible' : 'hidden'} variants={stagger} {...props}>
      {children}
    </motion.section>
  );
}

export const BrandName = ({ className }) => <span className={className}>NeXify<span className="brand-ai">AI</span></span>;

export const Logo = ({ size = 'md' }) => {
  const h = size === 'sm' ? 24 : size === 'lg' ? 40 : 32;
  return (
    <img src="/nexifyai-logo-light.png" alt="neXifyAI" style={{ display: 'block', height: h, width: 'auto' }} />
  );
};


export const Footer = ({ onCookieSettings, t, lang }) => {
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();
  return (
    <footer className="footer" role="contentinfo" data-testid="footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="footer-logo"><img src="/nexifyai-logo-light.png" alt="neXifyAI" height="28" /></div>
            <div className="footer-tagline">{t?.footer?.tagline || 'Chat it. Automate it.'}</div>
            <div className="footer-legal-name">{COMPANY.legal}</div>
            <div className="footer-founder-row">
              <img src={`/pascal_courbois.png?v=20260508`} alt="Pascal Courbois" className="footer-founder-img" width="48" height="48" />
              <div>
                <div className="footer-founder-name">Pascal Courbois</div>
                <div className="footer-founder-role">{lang === 'en' ? 'CEO & Founder' : lang === 'nl' ? 'CEO & Oprichter' : 'Geschäftsführer & Inhaber'}</div>
              </div>
            </div>
            <address className="footer-contact">
              <p><strong>NL:</strong> {COMPANY.addr.nl.s}, {COMPANY.addr.nl.c}</p>
              <p>Tel: <a href={`tel:${COMPANY.phone.replace(/\s/g, '')}`}>{COMPANY.phone}</a></p>
              <p>E-Mail: <a href={`mailto:${COMPANY.email}`}>{COMPANY.email}</a></p>
            </address>
          </div>
          <nav className="footer-nav-col">
            <h3 className="footer-nav-title">{t?.footer?.nav || 'Navigation'}</h3>
            <ul className="footer-links">
              <li><a href="#loesungen">{t?.nav?.leistungen || 'Leistungen'}</a></li>
              <li><a href="#use-cases">{t?.nav?.usecases || 'Use Cases'}</a></li>
              <li><a href="#app-dev">{t?.nav?.appdev || 'App-Entwicklung'}</a></li>
              <li><a href="#integrationen">{t?.nav?.integrationen || 'Integrationen'}</a></li>
              <li><a href="#preise">{t?.nav?.tarife || 'Tarife'}</a></li>
              <li><a href="#ki-seo">{lang === 'en' ? 'SEO' : 'KI-SEO'}</a></li>
              <li><a href="#services">{lang === 'en' ? 'Services' : lang === 'nl' ? 'Diensten' : 'Services'}</a></li>
              <li><a href={`/${lang}/blog`}>Blog</a></li>
            </ul>
          </nav>
          <nav className="footer-nav-col">
            <h3 className="footer-nav-title">{t?.footer?.legal || 'Rechtliches'}</h3>
            <ul className="footer-links">
              <li><a href={lp.impressum}>{t?.footer?.impressum || 'Impressum'}</a></li>
              <li><a href={lp.datenschutz}>{t?.footer?.datenschutz || 'Datenschutz'}</a></li>
              <li><a href={lp.agb}>{t?.footer?.agb || 'AGB'}</a></li>
              <li><a href={lp.ki}>{t?.footer?.ki || 'KI-Hinweise'}</a></li>
              <li><a href={lp.widerruf}>{lang === 'nl' ? 'Herroepingsrecht' : lang === 'en' ? 'Cancellation Policy' : 'Widerrufsbelehrung'}</a></li>
              <li><a href={lp.cookies}>{lang === 'nl' ? 'Cookiebeleid' : lang === 'en' ? 'Cookie Policy' : 'Cookie-Richtlinie'}</a></li>
              <li><a href={lp.avv}>{lang === 'nl' ? 'Verwerkersovereenkomst' : lang === 'en' ? 'Data Processing Agreement' : 'AVV'}</a></li>
            </ul>
            <div className="footer-ids"><p>KvK: {COMPANY.kvk}</p><p>USt-ID: {COMPANY.vat}</p><p className="footer-iban">IBAN: NL66 REVO 3601 4304 36</p></div>
          </nav>
          <div>
            <h3 className="footer-nav-title">{t?.footer?.kontakt || 'Kontakt'}</h3>
            <ul className="footer-links">
              <li><a href="/termin" data-testid="footer-booking-link"><I n="calendar_month" /> {lang === 'en' ? 'Book Meeting' : lang === 'nl' ? 'Gesprek boeken' : 'Termin buchen'}</a></li>
              <li><a href={`tel:${COMPANY.phone.replace(/\s/g, '')}`}><I n="call" /> {COMPANY.phone}</a></li>
              <li><a href={`mailto:${COMPANY.email}`}><I n="mail" /> {COMPANY.email}</a></li>
              <li><a href={`https://${COMPANY.web}`} target="_blank" rel="noopener noreferrer"><I n="open_in_new" /> {COMPANY.web}</a></li>
            </ul>
            <h3 className="footer-nav-title footer-social-title">{lang === 'en' ? 'Social' : lang === 'nl' ? 'Social' : 'Social'}</h3>
            <div className="footer-social">
              <a href="https://de.pinterest.com/NeXifyAutomate/" target="_blank" rel="noopener noreferrer" aria-label="Pinterest"><I n="public" /></a>
              <a href="https://www.instagram.com/nexify.automate/" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><I n="camera_alt" /></a>
              <a href="https://www.tiktok.com/@nexify_automate" target="_blank" rel="noopener noreferrer" aria-label="TikTok"><I n="music_note" /></a>
              <a href="https://x.com/nexify_automate" target="_blank" rel="noopener noreferrer" aria-label="X"><I n="close" /></a>
              <a href="https://www.facebook.com/nexify.automate.it" target="_blank" rel="noopener noreferrer" aria-label="Facebook"><I n="groups" /></a>
              <a href="https://www.linkedin.com/in/nexifyai-nexify-0b068a398" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><I n="work" /></a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <span className="footer-copy">{(t?.footer?.copy || '© {y} NeXifyAI').replace('{y}', thisYear)}</span>
          <div className="footer-bottom-links">
            <button className="footer-cookie-btn" onClick={onCookieSettings}>{t?.footer?.cookie || 'Cookie-Einstellungen'}</button>
            <div className="footer-status"><span className="status-dot on"></span>{t?.footer?.status || 'Alle Systeme aktiv'}</div>
          </div>
        </div>
      </div>
    </footer>
  );
};
