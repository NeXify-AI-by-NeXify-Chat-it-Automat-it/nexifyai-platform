import React from 'react';

export default function LegalView() {
  const pages = [
    { title: 'Impressum', path: '/legal/impressum' },
    { title: 'Datenschutz', path: '/legal/datenschutz' },
    { title: 'AGB', path: '/legal/agb' },
    { title: 'Widerruf', path: '/legal/widerruf' },
    { title: 'Cookie-Richtlinie', path: '/legal/cookies' },
    { title: 'DSGVO/AVV', path: '/legal/dsgvo-avv' },
    { title: 'Barrierefreiheit', path: '/legal/barrierefreiheit' },
  ];

  return (
    <div className="ac-view" style={{ padding: '24px', overflow: 'auto', flexDirection: 'column' }}>
      <h3>Rechtsseiten</h3>
      <p style={{ color: '#6b7b8d', marginBottom: '24px' }}>
        Die Rechtsseiten werden im Frontend unter /legal/* gerendert und sind mehrsprachig (DE/NL/EN).
      </p>
      <div className="ac-skill-grid">
        {pages.map(p => (
          <a key={p.path} href={p.path} target="_blank" rel="noopener noreferrer" className="ac-result-card" style={{ textDecoration: 'none' }}>
            <div className="ac-result-title">{p.title}</div>
            <div className="ac-result-content" style={{ color: '#6b7b8d', fontSize: '0.8125rem' }}>{p.path}</div>
          </a>
        ))}
      </div>
    </div>
  );
}
