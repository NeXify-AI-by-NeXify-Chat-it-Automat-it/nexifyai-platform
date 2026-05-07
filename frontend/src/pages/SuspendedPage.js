import React from 'react';
import { Helmet } from 'react-helmet-async';

const CO = {
  legal: 'neXify — Chat it. Automat it.',
  email: 'buchhaltung@nexify-automate.com'
};

const CONTENT = {
  de: {
    title: 'Website vorübergehend deaktiviert — NeXifyAI',
    h1: 'Diese Website ist vorübergehend deaktiviert',
    msg: 'Diese Website ist derzeit vorübergehend deaktiviert.',
    action: 'Bei Fragen wenden Sie sich bitte an:',
    email: 'support@nexify-automate.com'
  },
  nl: {
    title: 'Website tijdelijk gedeactiveerd — NeXifyAI',
    h1: 'Deze website is tijdelijk gedeactiveerd',
    msg: 'Deze website is momenteel tijdelijk gedeactiveerd.',
    action: 'Neem bij vragen contact op met:',
    email: 'support@nexify-automate.com'
  },
  en: {
    title: 'Website Temporarily Deactivated — NeXifyAI',
    h1: 'This website is temporarily deactivated',
    msg: 'This website is currently temporarily deactivated.',
    action: 'For questions, please contact:',
    email: 'support@nexify-automate.com'
  }
};

export default function SuspendedPage() {
  // Detect language from URL
  const lang = typeof window !== 'undefined' 
    ? (window.location.pathname.split('/')[1] || 'de')
    : 'de';
  const c = CONTENT[lang] || CONTENT.de;
  
  return (
    <>
      <Helmet>
        <title>{c.title}</title>
        <meta name="robots" content="noindex, nofollow" />
      </Helmet>
      <div style={{
        minHeight: '100vh',
        background: '#0f1923',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        padding: '24px'
      }}>
        <div style={{
          maxWidth: '520px',
          width: '100%',
          background: 'rgba(19,26,34,0.85)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '12px',
          padding: '48px 40px',
          textAlign: 'center'
        }}>
          {/* Logo */}
          <div style={{
            fontSize: '28px',
            fontWeight: 800,
            letterSpacing: '-0.02em',
            color: '#e2e8f0',
            marginBottom: '32px',
            fontFamily: 'Manrope, system-ui, sans-serif'
          }}>
            NeXify<span style={{ color: '#FE9B7B' }}>AI</span>
          </div>
          
          {/* Icon */}
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(254,155,123,0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px'
          }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#FE9B7B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
          </div>
          
          {/* Message */}
          <h1 style={{
            fontSize: '22px',
            fontWeight: 700,
            color: '#e2e8f0',
            margin: '0 0 16px',
            lineHeight: 1.3,
            fontFamily: 'Manrope, system-ui, sans-serif'
          }}>
            {c.h1}
          </h1>
          
          <p style={{
            fontSize: '14px',
            lineHeight: 1.65,
            color: '#c8d1dc',
            margin: '0 0 8px'
          }}>
            {c.msg}
          </p>
          
          <p style={{
            fontSize: '14px',
            lineHeight: 1.65,
            color: '#c8d1dc',
            margin: '0 0 24px'
          }}>
            {c.action}
          </p>
          
          {/* Contact Button */}
          <a href={`mailto:${c.email}`} style={{
            display: 'inline-block',
            padding: '14px 32px',
            background: '#FE9B7B',
            color: '#0f1923',
            fontSize: '15px',
            fontWeight: 700,
            textDecoration: 'none',
            borderRadius: '8px',
            marginBottom: '24px',
            fontFamily: 'Manrope, system-ui, sans-serif'
          }}>
            {c.email}
          </a>
          
          {/* Note */}
          <p style={{
            fontSize: '13px',
            lineHeight: 1.65,
            color: '#c8d1dc',
            margin: '0 0 24px'
          }}>
            Die Deaktivierung kann aus vertraglichen oder administrativen Gr&uuml;nden erfolgt sein.
          </p>
          
          {/* Footer with legal links */}
          <div style={{
            fontSize: '11px',
            color: '#4a5568',
            lineHeight: 1.8,
            borderTop: '1px solid rgba(255,255,255,0.04)',
            paddingTop: '16px',
            marginTop: '8px'
          }}>
            <div style={{marginBottom:'4px'}}>{CO.legal}</div>
            <div>
              <a href="/de/impressum" style={{color:'#6b7b8d',textDecoration:'none'}}>Impressum</a>
              <span style={{color:'rgba(255,255,255,0.15)',margin:'0 6px'}}>|</span>
              <a href="/de/datenschutz" style={{color:'#6b7b8d',textDecoration:'none'}}>Datenschutz</a>
              <span style={{color:'rgba(255,255,255,0.15)',margin:'0 6px'}}>|</span>
              <a href="/de/agb" style={{color:'#6b7b8d',textDecoration:'none'}}>AGB</a>
              <span style={{color:'rgba(255,255,255,0.15)',margin:'0 6px'}}>|</span>
              <a href="/de/ki-hinweise" style={{color:'#6b7b8d',textDecoration:'none'}}>KI</a>
              <span style={{color:'rgba(255,255,255,0.15)',margin:'0 6px'}}>|</span>
              <a href="/de/widerrufsbelehrung" style={{color:'#6b7b8d',textDecoration:'none'}}>Widerruf</a>
              <span style={{color:'rgba(255,255,255,0.15)',margin:'0 6px'}}>|</span>
              <a href="/de/cookie-richtlinie" style={{color:'#6b7b8d',textDecoration:'none'}}>Cookies</a>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
