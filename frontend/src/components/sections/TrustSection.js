import React from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '../../i18n/LanguageContext';
import { AnimSection, I, fadeUp } from '../shared';

const T = {
  de: {
    label: 'VERTRAUEN & SICHERHEIT',
    title: 'Datenschutzorientiert für den europäischen Rechtsraum entwickelt',
    subtitle: 'Ihre Daten, Ihre Kontrolle. Privacy by Design, gehostet in der EU.',
    cards: [
      { icon: 'shield', title: 'DSGVO / AVG', desc: 'Vollständige Umsetzung der Datenschutz-Grundverordnung (EU) 2016/679 — von der Datenerhebung bis zur Löschung.' },
      { icon: 'policy', title: 'EU AI Act', desc: 'Transparenz- und Kennzeichnungspflichten gemäß (EU) 2024/1689. Kein Social Scoring, keine manipulativen Techniken.' },
      { icon: 'cloud_done', title: 'EU-Hosting', desc: 'Datenverarbeitung ausschließlich in EU-Rechenzentren (Frankfurt, Amsterdam). Keine Drittlandübermittlung ohne SCC.' },
      { icon: 'lock', title: 'Verschlüsselung', desc: 'TLS 1.3 bei Übertragung, AES-256 bei Speicherung, Argon2id-Passwort-Hashing (OWASP-empfohlen).' },
      { icon: 'vpn_lock', title: 'Privacy by Design', desc: 'Datenminimierung, Zweckbindung, definierte Speicherfristen und rollenbasierte Zugriffskontrolle als Architekturprinzip.' },
      { icon: 'verified_user', title: 'ISO 27001/27701', desc: 'Orientiert an ISO/IEC 27001 und 27701 — Enterprise-Standard für Informationssicherheit und Datenschutzmanagement.' },
    ],
    ops: [
      { icon: 'link', title: 'Sichere Dokumentenzugriffe', desc: 'Zeitbegrenzte Magic Links statt Passwörter. Einmal-Tokens mit automatischer Ablaufzeit und SHA-256-Hash-Verifizierung.' },
      { icon: 'history', title: 'Audit Trail', desc: 'Lückenlose Protokollierung aller kommerziellen Transaktionen, Dokumentenzugriffe und Systemeingriffe mit Zeitstempel und IP.' },
      { icon: 'auto_delete', title: 'Daten-Lebenszyklus', desc: 'Definierte Aufbewahrungs- und Löschfristen pro Datenkategorie. Automatisierte Bereinigungsprozesse nach Art. 5 Abs. 1 lit. e DSGVO.' },
      { icon: 'admin_panel_settings', title: 'RBAC', desc: 'Rollenbasierte Zugriffskontrolle mit Minimal-Rechte-Prinzip über alle Systeme. Strikte Admin-/Kunden-Rollentrennung.' },
    ],
    euNote: 'Datenschutzorientiert für den europäischen Rechtsraum entwickelt. Dies stellt keine offizielle EU-Billigung, Zertifizierung oder Partnerschaft dar.'
  },
  nl: {
    label: 'VERTROUWEN & VEILIGHEID',
    title: 'Gegevensbescherming voor de Europese rechtsruimte',
    subtitle: 'Uw data, uw controle. Privacy by Design, gehost in de EU.',
    cards: [
      { icon: 'shield', title: 'AVG / DSGVO', desc: 'Volledige naleving van de Algemene verordening gegevensbescherming (EU) 2016/679 — van dataverzameling tot verwijdering.' },
      { icon: 'policy', title: 'EU AI Act', desc: 'Transparantie- en etiketteringsverplichtingen conform (EU) 2024/1689. Geen social scoring, geen manipulatieve technieken.' },
      { icon: 'cloud_done', title: 'EU-Hosting', desc: 'Gegevensverwerking uitsluitend in EU-datacenters (Frankfurt, Amsterdam). Geen doorgifte naar derde landen zonder SCC.' },
      { icon: 'lock', title: 'Encryptie', desc: 'TLS 1.3 bij overdracht, AES-256 bij opslag, Argon2id-wachtwoord-hashing (OWASP-aanbevolen).' },
      { icon: 'vpn_lock', title: 'Privacy by Design', desc: 'Dataminimalisatie, doelbinding, gedefinieerde bewaartermijnen en rolgebaseerde toegangscontrole als architectuurprincipe.' },
      { icon: 'verified_user', title: 'ISO 27001/27701', desc: 'Georiënteerd op ISO/IEC 27001 en 27701 — enterprise-standaard voor informatiebeveiliging en privacybeheer.' },
    ],
    ops: [
      { icon: 'link', title: 'Veilige documenttoegang', desc: 'Tijdgebonden Magic Links in plaats van wachtwoorden. Eenmalige tokens met automatische vervaldatum en SHA-256-hashverificatie.' },
      { icon: 'history', title: 'Audit Trail', desc: 'Volledige registratie van alle commerciële transacties, documenttoegang en systeemwijzigingen met tijdstempel en IP.' },
      { icon: 'auto_delete', title: 'Data-levenscyclus', desc: 'Gedefinieerde bewaar- en verwijderingstermijnen per datacategorie. Geautomatiseerde opschoningsprocessen conform Art. 5 lid 1 sub e AVG.' },
      { icon: 'admin_panel_settings', title: 'RBAC', desc: 'Rolgebaseerde toegangscontrole met minimale-rechtenprincipe over alle systemen. Strikte admin-/klant-rolscheiding.' },
    ],
    euNote: 'Ontwikkeld in overeenstemming met Europese gegevensbeschermings- en AI-wetgeving. Dit vertegenwoordigt geen officiële EU-goedkeuring, certificering of partnerschap.'
  },
  en: {
    label: 'TRUST & SECURITY',
    title: 'Data protection built for the European legal framework',
    subtitle: 'Your data, your control. Privacy by Design, hosted in the EU.',
    cards: [
      { icon: 'shield', title: 'GDPR / AVG', desc: 'Full compliance with the EU General Data Protection Regulation (2016/679) — from data collection to deletion.' },
      { icon: 'policy', title: 'EU AI Act', desc: 'Transparency and labeling obligations under (EU) 2024/1689. No social scoring, no manipulative techniques.' },
      { icon: 'cloud_done', title: 'EU Hosting', desc: 'Data processing exclusively in EU data centers (Frankfurt, Amsterdam). No third-country transfers without SCC.' },
      { icon: 'lock', title: 'Encryption', desc: 'TLS 1.3 in transit, AES-256 at rest, Argon2id password hashing (OWASP-recommended).' },
      { icon: 'vpn_lock', title: 'Privacy by Design', desc: 'Data minimization, purpose limitation, defined retention periods, and role-based access control as architectural principles.' },
      { icon: 'verified_user', title: 'ISO 27001/27701', desc: 'Aligned with ISO/IEC 27001 and 27701 — enterprise standard for information security and privacy management.' },
    ],
    ops: [
      { icon: 'link', title: 'Secure Document Access', desc: 'Time-limited Magic Links instead of passwords. Single-use tokens with automatic expiration and SHA-256 hash verification.' },
      { icon: 'history', title: 'Audit Trail', desc: 'Complete audit logging of all commercial transactions, document access, and system changes with timestamp and IP.' },
      { icon: 'auto_delete', title: 'Data Lifecycle', desc: 'Defined retention and deletion periods per data category. Automated cleanup processes per Art. 5(1)(e) GDPR.' },
      { icon: 'admin_panel_settings', title: 'RBAC', desc: 'Role-based access control with principle of least privilege across all systems. Strict admin/customer role separation.' },
    ],
    euNote: 'Developed in compliance with European data protection and AI legislation. This does not represent an official EU endorsement, certification, or partnership.'
  }
};

const TrustSection = () => {
  const { lang } = useLanguage();
  const d = T[lang] || T.de;
  return (
    <AnimSection id="trust" className="section bg-dark" data-testid="trust-section">
      <div className="container">
        <motion.header className="section-header centered" variants={fadeUp}>
          <span className="label">{d.label}</span>
          <h2>{d.title}</h2>
          <p className="section-subtitle">{d.subtitle}</p>
        </motion.header>
        <div className="trust-grid" role="list">
          {d.cards.map((item, i) => (
            <motion.div key={i} className="trust-card" role="listitem" variants={fadeUp}>
              <I n={item.icon} c="trust-icon" />
              <h3>{item.title}</h3>
              <p>{item.desc}</p>
            </motion.div>
          ))}
        </div>
        <div className="trust-ops-grid" data-testid="trust-ops">
          {d.ops.map((item, i) => (
            <motion.div key={i} className="trust-ops-card" role="listitem" variants={fadeUp}>
              <I n={item.icon} c="trust-ops-icon" />
              <div>
                <h4>{item.title}</h4>
                <p>{item.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
        <motion.div className="trust-eu-note" variants={fadeUp}>
          <div className="eu-emblem-row">
            <svg viewBox="0 0 810 540" width="48" height="32" className="eu-flag-svg" aria-label="EU Flag">
              <rect width="810" height="540" fill="#003399"/>
              {[...Array(12)].map((_, i) => {
                const angle = (i * 30 - 90) * Math.PI / 180;
                const cx = 405 + 160 * Math.cos(angle);
                const cy = 270 + 160 * Math.sin(angle);
                return <polygon key={i} points={`${cx},${cy-20} ${cx+6},${cy-6} ${cx+19},${cy-6} ${cx+8},${cy+4} ${cx+12},${cy+19} ${cx},${cy+10} ${cx-12},${cy+19} ${cx-8},${cy+4} ${cx-19},${cy-6} ${cx-6},${cy-6}`} fill="#FFCC00"/>;
              })}
            </svg>
            <span>{d.euNote}</span>
          </div>
        </motion.div>
      </div>
    </AnimSection>
  );
};

export default TrustSection;
