import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useLanguage, SUPPORTED } from '../i18n/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';
import SEOHead from '../components/SEOHead';

const CO = {
  legal: 'NeXifyAI by NeXify - Chat it. Automate it.', ceo: 'Pascal Courbois, Geschäftsführer (Directeur)',
  nl: 'Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande',
  phone: '+31 6 133 188 56', email: 'support@nexify-automate.com',
  web: 'nexify-automate.com', kvk: '90483944', vat: 'NL865786276B01'
};

const BACK = { de: 'Zurück zur Startseite', nl: 'Terug naar de startpagina', en: 'Back to homepage' };

const LegalWrap = ({ children, title }) => {
  const { lang } = useLanguage();
  return (
    <div className="legal-page">
      <SEOHead lang={lang} page="legal" />
      <nav className="legal-nav">
        <div className="legal-nav-inner">
          <a href={`/${lang}`} className="legal-logo-link">
            <img src="/icon-mark.svg" alt="" width="28" height="28" />
            <span className="legal-logo-text">NeXify<span className="legal-logo-accent">AI</span></span>
          </a>
          <span className="legal-tagline">Chat it. Automate it.</span>
          <LanguageSwitcher />
        </div>
        <a href={`/${lang}`} className="legal-back">&larr; {BACK[lang] || BACK.en}</a>
      </nav>
      <main className="legal-content"><h1>{title}</h1>{children}</main>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════
   IMPRESSUM
   ═══════════════════════════════════════════════════════════ */
const ImpressumContent = {
  de: () => (
    <>
      <section>
        <h2>Impressum</h2>
        <p><strong>NeXifyAI by NeXify &ndash; Chat it. Automate it.</strong><br/>
        (Eenmanszaak &ndash; Einzelunternehmen)</p>
        <p><strong>Inhaber:</strong><br/>
        Pascal Courbois</p>
        <p><strong>Adresse:</strong><br/>
        Graaf van Loonstraat 1E<br/>
        5921 JA Venlo<br/>
        Niederlande</p>
        <p><strong>Kontakt:</strong><br/>
        E-Mail: <a href="mailto:support@nexify-automate.com">support@nexify-automate.com</a><br/>
        Telefon: <a href="tel:+31613318856">+31 6 133 188 56</a></p>
        <p><strong>Handelsregister:</strong><br/>
        Kamer van Koophandel (KvK): 90483944</p>
        <p><strong>Umsatzsteuer-ID:</strong><br/>
        NL865786276B01</p>
        <p><strong>Hinweis:</strong><br/>
        Dieses Angebot richtet sich ausschlie&szlig;lich an Unternehmer.</p>
      </section>
    </>
  ),
  nl: () => (
    <>
      <section>
        <h2>Impressum</h2>
        <p><strong>NeXifyAI by NeXify &ndash; Chat it. Automate it.</strong><br/>
        (Eenmanszaak)</p>
        <p><strong>Eigenaar:</strong><br/>
        Pascal Courbois</p>
        <p><strong>Adres:</strong><br/>
        Graaf van Loonstraat 1E<br/>
        5921 JA Venlo<br/>
        Nederland</p>
        <p><strong>Contact:</strong><br/>
        E-mail: <a href="mailto:support@nexify-automate.com">support@nexify-automate.com</a><br/>
        Telefoon: <a href="tel:+31613318856">+31 6 133 188 56</a></p>
        <p><strong>Handelsregister:</strong><br/>
        Kamer van Koophandel (KvK): 90483944</p>
        <p><strong>BTW-ID:</strong><br/>
        NL865786276B01</p>
        <p><strong>Opmerking:</strong><br/>
        Dit aanbod is uitsluitend gericht op ondernemers.</p>
      </section>
    </>
  ),
  en: () => (
    <>
      <section>
        <h2>Imprint</h2>
        <p><strong>NeXifyAI by NeXify &ndash; Chat it. Automate it.</strong><br/>
        (Eenmanszaak &ndash; Sole Proprietorship)</p>
        <p><strong>Owner:</strong><br/>
        Pascal Courbois</p>
        <p><strong>Address:</strong><br/>
        Graaf van Loonstraat 1E<br/>
        5921 JA Venlo<br/>
        Netherlands</p>
        <p><strong>Contact:</strong><br/>
        Email: <a href="mailto:support@nexify-automate.com">support@nexify-automate.com</a><br/>
        Phone: <a href="tel:+31613318856">+31 6 133 188 56</a></p>
        <p><strong>Commercial Register:</strong><br/>
        Chamber of Commerce (KvK): 90483944</p>
        <p><strong>VAT ID:</strong><br/>
        NL865786276B01</p>
        <p><strong>Notice:</strong><br/>
        This offer is exclusively directed at entrepreneurs.</p>
      </section>
    </>
  )
};const DatenschutzContent = {
  de: () => (
    <>
      <p>gemäß Verordnung (EU) 2016/679 (Datenschutz-Grundverordnung, DSGVO), dem niederländischen Uitvoeringswet Algemene verordening gegevensbescherming (UAVG), dem Bundesdatenschutzgesetz (BDSG) sowie der Datenschutzgesetz-Novelle (Schweiz, revDSG)</p>

      <section>
        <h2>§ 1 Verantwortlicher</h2>
        <p>{CO.legal}<br/>{CO.ceo}<br/>{CO.nl}<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>Telefon: {CO.phone}</p>
        <p>Da {CO.legal} weniger als 250 Mitarbeiter beschäftigt und keine Verarbeitung in großem Umfang vornimmt, ist die Benennung eines Datenschutzbeauftragten gemäß Art. 37 DSGVO nicht verpflichtend. Datenschutzanfragen richten Sie bitte direkt an die oben genannte E-Mail-Adresse.</p>
        <p><strong>Zuständige Aufsichtsbehörde:</strong> Autoriteit Persoonsgegevens (AP), Bezuidenhoutseweg 30, 2594 AV Den Haag, Niederlande. Verbraucher in Deutschland können sich alternativ an die zuständige Landesdatenschutzbehörde wenden.</p>
      </section>

      <section>
        <h2>§ 2 Grundsätze der Datenverarbeitung</h2>
        <p>Wir verarbeiten personenbezogene Daten ausschließlich nach den Grundsätzen des Art. 5 DSGVO:</p>
        <ul>
          <li><strong>Rechtmäßigkeit, Verarbeitung nach Treu und Glauben, Transparenz</strong> (Art. 5 Abs. 1 lit. a)</li>
          <li><strong>Zweckbindung</strong> (Art. 5 Abs. 1 lit. b)</li>
          <li><strong>Datenminimierung</strong> (Art. 5 Abs. 1 lit. c)</li>
          <li><strong>Richtigkeit</strong> (Art. 5 Abs. 1 lit. d)</li>
          <li><strong>Speicherbegrenzung</strong> (Art. 5 Abs. 1 lit. e)</li>
          <li><strong>Integrität und Vertraulichkeit</strong> (Art. 5 Abs. 1 lit. f)</li>
          <li><strong>Rechenschaftspflicht</strong> (Art. 5 Abs. 2)</li>
        </ul>
      </section>

      <section>
        <h2>§ 3 Verarbeitungstätigkeiten im Detail</h2>

        <h3>3.1 Bereitstellung der Website und Server-Logfiles</h3>
        <p><strong>Verarbeitete Daten:</strong> IP-Adresse (anonymisiert nach 7 Tagen), Browsertyp und -version, Betriebssystem, Referrer-URL, aufgerufene Seiten, Datum und Uhrzeit des Zugriffs, übertragene Datenmenge.</p>
        <p><strong>Zweck:</strong> Gewährleistung eines reibungslosen Verbindungsaufbaus der Website, Gewährleistung einer komfortablen Nutzung, Auswertung der Systemsicherheit und -stabilität, Missbrauchserkennung.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an der technischen Bereitstellung und Sicherheit).</p>
        <p><strong>Speicherdauer:</strong> Server-Logfiles werden nach 7 Tagen anonymisiert und nach 30 Tagen gelöscht.</p>

        <h3>3.2 Kontaktformular und Erstberatung</h3>
        <p><strong>Verarbeitete Daten:</strong> Vor- und Nachname, E-Mail-Adresse, Telefonnummer (optional), Unternehmen, Branche, Nachrichteninhalt, Zeitstempel, IP-Adresse.</p>
        <p><strong>Zweck:</strong> Bearbeitung Ihrer Anfrage, Zuordnung zum CRM-System, Vorbereitung eines Erstgesprächs, Erstellung eines individualisierten Angebots.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (vorvertragliche Maßnahmen auf Anfrage der betroffenen Person).</p>
        <p><strong>Speicherdauer:</strong> 24 Monate nach letztem Kontakt. Bei Vertragsabschluss gelten die handelsrechtlichen Aufbewahrungsfristen (siehe § 3.5).</p>

        <h3>3.3 Terminbuchung</h3>
        <p><strong>Verarbeitete Daten:</strong> Vor- und Nachname, E-Mail-Adresse, gewünschtes Datum und Uhrzeit, Termintyp (Erstberatung, Review, Strategie-Call, Support), Anmerkungen, Zeitstempel.</p>
        <p><strong>Zweck:</strong> Organisation und Durchführung des Beratungsgesprächs, Kalenderintegration, Erinnerungsbenachrichtigungen.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO.</p>
        <p><strong>Speicherdauer:</strong> 12 Monate nach dem Termin.</p>

        <h3>3.4 KI-Chat (NeXifyAI Advisor)</h3>
        <p><strong>Verarbeitete Daten:</strong> Chatverlauf (Textnachrichten), Session-ID, Zeitstempel, vom Nutzer freiwillig eingegebene Daten (Name, E-Mail, Unternehmen).</p>
        <p><strong>Technologie:</strong> OpenAI GPT (API-Zugriff mit Zero Data Retention Policy). Die Eingaben werden nicht zum Training der KI-Modelle verwendet.</p>
        <p><strong>Zweck:</strong> Automatisierte Erstberatung, Terminbuchung, Informationsbereitstellung über Dienstleistungen.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an effizienter Kundeninteraktion). Der Einsatz des KI-Systems ist gemäß Art. 52 der KI-Verordnung (EU) 2024/1689 gekennzeichnet.</p>
        <p><strong>Speicherdauer:</strong> Chat-Protokolle werden nach 90 Tagen anonymisiert. Bei Überführung in ein Kundenkonto gelten die jeweiligen Aufbewahrungsfristen des Kundenkontos.</p>
        <p><strong>Hinweis:</strong> Der KI-Chat kann keine rechtsverbindlichen Zusagen oder Preisgarantien geben. Jeder Nutzer hat das Recht, jederzeit die Bearbeitung durch einen menschlichen Mitarbeiter zu verlangen (Art. 22 Abs. 3 DSGVO analog).</p>

        <h3>3.5 Angebotsanfrage, Vertragsanbahnung und Vertragsabwicklung</h3>
        <p><strong>Verarbeitete Daten:</strong> Vor- und Nachname, E-Mail, Unternehmen, Telefon, Land, Branche, Use Case, Tarifdaten, Projektumfang, Budgetrahmen, Vertragsdaten (Vertragsnummer, Laufzeit, Konditionen), digitale Unterschrift (Zeichnungsdaten oder Name), Zeitstempel.</p>
        <p><strong>Zweck:</strong> Erstellung und Versand individueller Angebote, Vertragsanbahnung, Vertragsdurchführung, digitale Vertragsannahme (Magic-Link-basiert), Projektmanagement, Kommunikation im Projektchat.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung und vorvertragliche Maßnahmen).</p>
        <p><strong>Speicherdauer:</strong> Vertragsdaten: 10 Jahre nach Vertragsende (§ 2:10 BW Niederlande, § 257 HGB Deutschland). Angebote ohne Vertragsabschluss: 36 Monate.</p>

        <h3>3.6 Rechnungsstellung und Zahlungsabwicklung</h3>
        <p><strong>Verarbeitete Daten:</strong> Name, E-Mail, Unternehmen, Rechnungsadresse, USt-IdNr., Rechnungsdaten (Nummer, Beträge netto/brutto, USt-Satz), Zahlungsstatus, Zahlungsreferenzen, Mahnstufe.</p>
        <p><strong>Zahlungsdienstleister:</strong> Revolut Ltd. (Litauen/EU), PCI DSS Level 1 zertifiziert. Kreditkartendaten werden ausschließlich durch Revolut verarbeitet und zu keinem Zeitpunkt auf unseren Servern gespeichert. Alternative: Banküberweisung (IBAN: NL66 REVO 3601 4304 36, BIC: REVONL22).</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung), Art. 6 Abs. 1 lit. c DSGVO (gesetzliche Aufbewahrungspflichten).</p>
        <p><strong>Speicherdauer:</strong> 10 Jahre (Art. 2:10 BW, § 257 HGB, § 132 BAO Österreich, Art. 958f OR Schweiz).</p>

        <h3>3.7 Sicherer Dokumentenzugriff (Magic Links)</h3>
        <p><strong>Verarbeitete Daten:</strong> E-Mail-Adresse, Zugriffszeitpunkt, IP-Adresse, User-Agent, Token-Hash (SHA-256).</p>
        <p><strong>Zweck:</strong> Passwortlose, sichere Bereitstellung von Angeboten, Verträgen und Rechnungen über zeitlich begrenzte Einmal-Links.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO.</p>
        <p><strong>Speicherdauer:</strong> Token-Gültigkeit: 24 Stunden. Audit-Logs: 24 Monate. Nachweisprotokoll für Vertragsannahme: 10 Jahre.</p>

        <h3>3.8 Kundenportal</h3>
        <p><strong>Verarbeitete Daten:</strong> Alle im Kundenkonto hinterlegten Daten (Profildaten, Anfragen, Nachrichten, Support-Tickets, Terminbuchungen, Vertragsdaten, Rechnungsdaten, Kommunikationsverlauf, Aktivitätsprotokoll).</p>
        <p><strong>Zweck:</strong> Bereitstellung eines personalisierten Kundenbereichs, Self-Service-Funktionen, Projektübersicht, Dokumentenverwaltung, Kommunikation.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO.</p>
        <p><strong>Speicherdauer:</strong> Dauer der Geschäftsbeziehung, anschließend gemäß den gesetzlichen Aufbewahrungsfristen.</p>

        <h3>3.9 E-Mail-Kommunikation</h3>
        <p><strong>Verarbeitete Daten:</strong> E-Mail-Adresse, Inhalt der Korrespondenz, Zeitstempel, technische Metadaten (Zustellstatus, Öffnungsstatus bei transaktionalen E-Mails).</p>
        <p><strong>E-Mail-Dienstleister:</strong> Hostinger SMTP (Litauen/EU) als primärer Zustelldienst.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (vertragsbezogene Kommunikation), Art. 6 Abs. 1 lit. f DSGVO (geschäftliche Kommunikation).</p>
        <p><strong>Speicherdauer:</strong> E-Mails im Zusammenhang mit Verträgen: 10 Jahre. Allgemeine Korrespondenz: 36 Monate.</p>

        <h3>3.10 Analyse und Nutzungsstatistiken</h3>
        <p><strong>Verarbeitete Daten:</strong> Anonymisierte Session-Daten (Session-ID ohne Personenbezug), aufgerufene Seiten, Interaktionsereignisse, Verweildauer.</p>
        <p><strong>Zweck:</strong> Verbesserung des Nutzererlebnisses, Erkennung technischer Fehler.</p>
        <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO.</p>
        <p><strong>Hinweis:</strong> Wir setzen keine Drittanbieter-Tracking-Tools (Google Analytics, Meta Pixel o. ä.) ein. Es findet keine geräteübergreifende Nachverfolgung statt.</p>
      </section>

      <section>
        <h2>§ 4 Auftragsverarbeiter und Datenübermittlung</h2>
        <p>Wir setzen folgende Auftragsverarbeiter gemäß Art. 28 DSGVO ein:</p>
        <table style={{width:'100%',borderCollapse:'collapse',marginBottom:16}}>
          <thead><tr style={{borderBottom:'2px solid rgba(254,155,123,0.2)'}}>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Dienstleister</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Zweck</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Standort</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Garantien</th>
          </tr></thead>
          <tbody style={{fontSize:'.8125rem'}}>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>MongoDB, Inc.</td><td style={{padding:'8px 12px'}}>Datenbankhaltung</td><td style={{padding:'8px 12px'}}>EU (Frankfurt)</td><td style={{padding:'8px 12px'}}>AES-256 at rest, TLS in transit</td></tr>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>OpenAI, Inc.</td><td style={{padding:'8px 12px'}}>KI-Chat-Verarbeitung</td><td style={{padding:'8px 12px'}}>USA</td><td style={{padding:'8px 12px'}}>SCC (Art. 46 DSGVO), Zero Data Retention</td></tr>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>Revolut Ltd.</td><td style={{padding:'8px 12px'}}>Zahlungsabwicklung</td><td style={{padding:'8px 12px'}}>EU (Litauen)</td><td style={{padding:'8px 12px'}}>PCI DSS Level 1, EZB-lizenziert</td></tr>
            <tr><td style={{padding:'8px 12px'}}>Hostinger International Ltd.</td><td style={{padding:'8px 12px'}}>E-Mail-Versand (SMTP)</td><td style={{padding:'8px 12px'}}>EU (Litauen)</td><td style={{padding:'8px 12px'}}>TLS 1.2+, DKIM/SPF/DMARC</td></tr>
          </tbody>
        </table>
        <p><strong>Drittlandübermittlung (USA):</strong> Soweit personenbezogene Daten an OpenAI, Inc. in die USA übermittelt werden, erfolgt dies auf Basis von Standardvertragsklauseln gemäß Art. 46 Abs. 2 lit. c DSGVO (Durchführungsbeschluss (EU) 2021/914 der Kommission) in Verbindung mit ergänzenden technischen Maßnahmen (Verschlüsselung, Pseudonymisierung, Zero Data Retention).</p>
      </section>

      <section>
        <h2>§ 5 Technisch-organisatorische Maßnahmen (TOM)</h2>
        <p>Gemäß Art. 32 DSGVO setzen wir folgende Maßnahmen ein:</p>
        <ul>
          <li><strong>Verschlüsselung:</strong> TLS 1.2+ für alle Datenübertragungen (HSTS mit Preload). AES-256-Verschlüsselung der Datenbank at rest (MongoDB Atlas).</li>
          <li><strong>Zugriffskontrolle:</strong> Rollenbasierte Zugriffskontrolle (RBAC) mit strikter Rollentrennung (Admin, Kunde). JWT-Token mit 24-Stunden-Ablauf. Brute-Force-Schutz durch Rate Limiting.</li>
          <li><strong>Passwort-Sicherheit:</strong> Argon2id-Hashing (OWASP-empfohlen, Speicher: 64 MB, Iterationen: 3, Parallelismus: 4).</li>
          <li><strong>Authentifizierung:</strong> Zeitlich begrenzte Magic Links (SHA-256 gehasht, 24 Stunden gültig) als Alternative zu Passwörtern. Kein Klartextspeicher von Credentials.</li>
          <li><strong>Security-Header:</strong> Content-Security-Policy (CSP), X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Strict-Transport-Security (HSTS), Referrer-Policy: strict-origin-when-cross-origin.</li>
          <li><strong>Audit-Logging:</strong> Vollständiges Audit-Trail für alle kommerziellen Transaktionen (Angebote, Verträge, Rechnungen, Zahlungen) mit Zeitstempel, IP-Adresse und Dokumenten-Hash.</li>
          <li><strong>Incident Response:</strong> Meldung von Datenschutzverletzungen an die Autoriteit Persoonsgegevens innerhalb von 72 Stunden gemäß Art. 33 DSGVO.</li>
          <li><strong>Datensicherung:</strong> Tägliche verschlüsselte Backups mit 30-Tage-Retention. Point-in-Time-Recovery über MongoDB Atlas.</li>
        </ul>
      </section>

      <section>
        <h2>§ 6 Ihre Rechte als betroffene Person</h2>
        <p>Ihnen stehen folgende Rechte gemäß Kapitel III DSGVO zu:</p>
        <ul>
          <li><strong>Auskunftsrecht (Art. 15 DSGVO):</strong> Sie haben das Recht, eine Bestätigung zu verlangen, ob personenbezogene Daten verarbeitet werden, und Auskunft über diese Daten zu erhalten.</li>
          <li><strong>Recht auf Berichtigung (Art. 16 DSGVO):</strong> Sie haben das Recht, die Berichtigung unrichtiger oder die Vervollständigung unvollständiger Daten zu verlangen.</li>
          <li><strong>Recht auf Löschung (Art. 17 DSGVO):</strong> Sie haben das Recht, die Löschung Ihrer Daten zu verlangen, sofern keine gesetzlichen Aufbewahrungspflichten oder vorrangige berechtigte Interessen entgegenstehen.</li>
          <li><strong>Recht auf Einschränkung der Verarbeitung (Art. 18 DSGVO):</strong> Sie können die Einschränkung der Verarbeitung verlangen, z. B. wenn die Richtigkeit der Daten bestritten wird.</li>
          <li><strong>Recht auf Datenübertragbarkeit (Art. 20 DSGVO):</strong> Sie haben das Recht, Ihre Daten in einem strukturierten, gängigen und maschinenlesbaren Format (JSON, CSV) zu erhalten.</li>
          <li><strong>Widerspruchsrecht (Art. 21 DSGVO):</strong> Sie können jederzeit gegen die Verarbeitung auf Basis von Art. 6 Abs. 1 lit. f DSGVO Widerspruch einlegen. Wir stellen die Verarbeitung dann ein, es sei denn, wir können zwingende schutzwürdige Gründe nachweisen.</li>
          <li><strong>Recht auf Widerruf der Einwilligung (Art. 7 Abs. 3 DSGVO):</strong> Soweit die Verarbeitung auf einer Einwilligung beruht, können Sie diese jederzeit mit Wirkung für die Zukunft widerrufen.</li>
          <li><strong>Recht auf Beschwerde (Art. 77 DSGVO):</strong> Sie haben das Recht, eine Beschwerde bei der zuständigen Aufsichtsbehörde einzureichen.</li>
        </ul>
        <p><strong>Kontakt für Datenschutzanfragen:</strong> <a href={`mailto:${CO.email}`}>{CO.email}</a>. Wir beantworten Ihre Anfrage innerhalb von 30 Tagen (Art. 12 Abs. 3 DSGVO). Eine Fristverlängerung um weitere 60 Tage ist bei Komplexität unter Benachrichtigung möglich.</p>
      </section>

      <section>
        <h2>§ 7 Automatisierte Entscheidungsfindung</h2>
        <p>Wir setzen keine automatisierte Entscheidungsfindung einschließlich Profiling im Sinne des Art. 22 DSGVO ein, die Ihnen gegenüber rechtliche Wirkung entfaltet oder Sie in ähnlicher Weise erheblich beeinträchtigt. Der KI-Chat dient ausschließlich der Informationsbereitstellung und trifft keine rechtsverbindlichen Entscheidungen.</p>
      </section>

      <section>
        <h2>§ 8 Cookies und lokale Speicherung</h2>
        <p>Die Verarbeitung erfolgt unter Einsatz datenschutzoptimierter Einstellungen. Funktionen wie Zero Data Retention werden verwendet, soweit technisch verf&uuml;gbar und aktiviert. Eine Speicherung durch Drittanbieter kann nicht vollst&auml;ndig ausgeschlossen werden.

Wir verwenden ausschlie&szlig;lich technisch notwendige Cookies und localStorage-Eintr&auml;ge gemäß § 25 Abs. 2 Nr. 2 TDDDG (Deutschland), Art. 11.7a Abs. 3 Telecommunicatiewet (Niederlande) und § 165 Abs. 3 TKG 2021 (Österreich):</p>
        <table style={{width:'100%',borderCollapse:'collapse',marginBottom:16}}>
          <thead><tr style={{borderBottom:'2px solid rgba(254,155,123,0.2)'}}>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Name</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Typ</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Zweck</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Dauer</th>
          </tr></thead>
          <tbody style={{fontSize:'.8125rem'}}>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>nx_cookie_consent</td><td style={{padding:'8px 12px'}}>localStorage</td><td style={{padding:'8px 12px'}}>Speichert Ihre Cookie-Präferenz</td><td style={{padding:'8px 12px'}}>Unbegrenzt (manuell löschbar)</td></tr>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>nx_auth</td><td style={{padding:'8px 12px'}}>localStorage</td><td style={{padding:'8px 12px'}}>Authentifizierungsdaten (JWT)</td><td style={{padding:'8px 12px'}}>24 Stunden (Token-Ablauf)</td></tr>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>nx_lang</td><td style={{padding:'8px 12px'}}>localStorage</td><td style={{padding:'8px 12px'}}>Sprachpräferenz</td><td style={{padding:'8px 12px'}}>Unbegrenzt</td></tr>
            <tr><td style={{padding:'8px 12px'}}>nx_s</td><td style={{padding:'8px 12px'}}>sessionStorage</td><td style={{padding:'8px 12px'}}>Anonyme Session-ID</td><td style={{padding:'8px 12px'}}>Browsersitzung</td></tr>
          </tbody>
        </table>
        <p>Es werden keine Drittanbieter-Tracking-Cookies, Marketing-Cookies oder Cross-Site-Tracking-Mechanismen eingesetzt. Eine gesonderte Einwilligung ist für rein technisch notwendige Cookies nicht erforderlich.</p>
      </section>

      <section>
        <h2>§ 9 Änderungen dieser Datenschutzerklärung</h2>
        <p>Wir behalten uns vor, diese Datenschutzerklärung bei Änderungen der Rechtslage, Geschäftstätigkeit oder technischen Infrastruktur anzupassen. Die aktuelle Version ist stets unter <a href={`https://${CO.web}/de/datenschutz`}>{CO.web}/de/datenschutz</a> abrufbar. Wesentliche Änderungen werden per E-Mail an aktive Kunden mitgeteilt.</p>
      </section>

      <p className="legal-date">Stand: April 2026</p>
    </>
  ),
  nl: () => (
    <>
      <p>conform Verordening (EU) 2016/679 (AVG) en de Uitvoeringswet Algemene verordening gegevensbescherming (UAVG)</p>
      <section><h2>§ 1 Verwerkingsverantwoordelijke</h2><p>{CO.legal}<br/>{CO.ceo}<br/>{CO.nl}<br/>E-mail: <a href={`mailto:${CO.email}`}>{CO.email}</a></p><p>Toezichthouder: Autoriteit Persoonsgegevens (AP), Den Haag.</p></section>
      <section><h2>§ 2 Beginselen</h2><p>Wij verwerken persoonsgegevens uitsluitend conform Art. 5 AVG: rechtmatigheid, doelbinding, minimale gegevensverwerking, juistheid, opslagbeperking, integriteit en vertrouwelijkheid.</p></section>
      <section><h2>§ 3 Verwerkingsactiviteiten</h2>
        <h3>3.1 Website en logbestanden</h3><p>IP-adres (geanonimiseerd na 7 dagen), browsertype, OS, bezochte pagina's. Rechtsgrondslag: Art. 6 lid 1 sub f AVG. Bewaartermijn: 30 dagen.</p>
        <h3>3.2 Contactformulier</h3><p>Naam, e-mail, telefoon, bedrijf, bericht. Rechtsgrondslag: Art. 6 lid 1 sub b AVG. Bewaartermijn: 24 maanden.</p>
        <h3>3.3 Afspraak boeken</h3><p>Naam, e-mail, datum/tijd, type, opmerkingen. Rechtsgrondslag: Art. 6 lid 1 sub b AVG. Bewaartermijn: 12 maanden.</p>
        <h3>3.4 AI-Chat</h3><p>Chatgeschiedenis, sessie-ID. OpenAI GPT (Zero Data Retention). Rechtsgrondslag: Art. 6 lid 1 sub f AVG. Bewaartermijn: 90 dagen.</p>
        <h3>3.5 Offertes, contracten en facturering</h3><p>Contactgegevens, contractgegevens, factuurgegevens, betalingsgegevens (via Revolut). Rechtsgrondslag: Art. 6 lid 1 sub b, c AVG. Bewaartermijn: 10 jaar (Art. 2:10 BW).</p>
        <h3>3.6 Klantenportaal</h3><p>Profielgegevens, aanvragen, berichten, tickets, boekingen. Rechtsgrondslag: Art. 6 lid 1 sub b AVG.</p>
      </section>
      <section><h2>§ 4 Verwerkers</h2><ul><li><strong>MongoDB, Inc.</strong> — Database (EU/Frankfurt). AES-256.</li><li><strong>OpenAI, Inc.</strong> — AI-chat (VS). SCC + Zero Data Retention.</li><li><strong>Revolut Ltd.</strong> — Betalingen (EU/Litouwen). PCI DSS Level 1.</li><li><strong>Hostinger</strong> — E-mail (EU/Litouwen). TLS 1.2+.</li></ul></section>
      <section><h2>§ 5 Beveiligingsmaatregelen (Art. 32 AVG)</h2><p>TLS 1.2+, AES-256, Argon2id, RBAC, JWT met 24-uurs vervaldatum, CSP, HSTS, auditlogging, dagelijkse versleutelde back-ups.</p></section>
      <section><h2>§ 6 Uw rechten</h2><p>Inzage (Art. 15), rectificatie (Art. 16), wissing (Art. 17), beperking (Art. 18), overdraagbaarheid (Art. 20), bezwaar (Art. 21), intrekking toestemming (Art. 7 lid 3), klachtrecht (Art. 77).</p><p>Contact: <a href={`mailto:${CO.email}`}>{CO.email}</a>. Reactie binnen 30 dagen.</p></section>
      <section><h2>§ 7 Cookies</h2><p>Uitsluitend technisch noodzakelijke cookies/localStorage (nx_cookie_consent, nx_auth, nx_lang, nx_s). Geen tracking-cookies van derden.</p></section>
      <p className="legal-date">Status: april 2026</p>
    </>
  ),
  en: () => (
    <>
      <p>pursuant to Regulation (EU) 2016/679 (GDPR) and the Dutch UAVG Implementation Act</p>
      <section><h2>§ 1 Data Controller</h2><p>{CO.legal}<br/>{CO.ceo}<br/>{CO.nl}<br/>Email: <a href={`mailto:${CO.email}`}>{CO.email}</a></p><p>Supervisory authority: Autoriteit Persoonsgegevens (AP), The Hague.</p></section>
      <section><h2>§ 2 Principles</h2><p>We process personal data exclusively in accordance with Art. 5 GDPR: lawfulness, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality.</p></section>
      <section><h2>§ 3 Processing Activities</h2>
        <h3>3.1 Website and server logs</h3><p>IP address (anonymised after 7 days), browser, OS, pages visited. Legal basis: Art. 6(1)(f) GDPR. Retention: 30 days.</p>
        <h3>3.2 Contact form</h3><p>Name, email, phone, company, message. Legal basis: Art. 6(1)(b) GDPR. Retention: 24 months.</p>
        <h3>3.3 Appointment booking</h3><p>Name, email, date/time, type, notes. Legal basis: Art. 6(1)(b) GDPR. Retention: 12 months.</p>
        <h3>3.4 AI Chat</h3><p>Chat transcript, session ID. OpenAI GPT (Zero Data Retention). Legal basis: Art. 6(1)(f) GDPR. Retention: 90 days.</p>
        <h3>3.5 Quotes, contracts and invoicing</h3><p>Contact data, contract data, invoice data, payment data (via Revolut). Legal basis: Art. 6(1)(b)(c) GDPR. Retention: 10 years.</p>
        <h3>3.6 Customer Portal</h3><p>Profile data, requests, messages, tickets, bookings. Legal basis: Art. 6(1)(b) GDPR.</p>
      </section>
      <section><h2>§ 4 Processors</h2><ul><li><strong>MongoDB, Inc.</strong> — Database (EU/Frankfurt). AES-256.</li><li><strong>OpenAI, Inc.</strong> — AI chat (US). SCC + Zero Data Retention.</li><li><strong>Revolut Ltd.</strong> — Payments (EU/Lithuania). PCI DSS Level 1.</li><li><strong>Hostinger</strong> — Email (EU/Lithuania). TLS 1.2+.</li></ul></section>
      <section><h2>§ 5 Security Measures (Art. 32 GDPR)</h2><p>TLS 1.2+, AES-256, Argon2id, RBAC, JWT with 24h expiry, CSP, HSTS, audit logging, daily encrypted backups.</p></section>
      <section><h2>§ 6 Your Rights</h2><p>Access (Art. 15), Rectification (Art. 16), Erasure (Art. 17), Restriction (Art. 18), Portability (Art. 20), Objection (Art. 21), Withdraw consent (Art. 7(3)), Complaint (Art. 77).</p><p>Contact: <a href={`mailto:${CO.email}`}>{CO.email}</a>. Response within 30 days.</p></section>
      <section><h2>§ 7 Cookies</h2><p>Only technically necessary cookies/localStorage (nx_cookie_consent, nx_auth, nx_lang, nx_s). No third-party tracking cookies.</p></section>
      <p className="legal-date">Last updated: April 2026</p>
    </>
  )
};

/* ═══════════════════════════════════════════════════════════
   AGB — ALLGEMEINE GESCHÄFTSBEDINGUNGEN
   ═══════════════════════════════════════════════════════════ */
const AGBContent = {
  de: () => (
    <>
      <section>
        <h2>Allgemeine Gesch&auml;ftsbedingungen (B2B)</h2>
        <p><strong>NeXifyAI by NeXify &ndash; Chat it. Automate it.</strong></p>

        <h3>&sect;1 Geltungsbereich</h3>
        <p>(1) Diese Allgemeinen Gesch&auml;ftsbedingungen gelten ausschlie&szlig;lich f&uuml;r Unternehmer im Sinne von Art. 7:5 Burgerlijk Wetboek (BW), &sect; 14 BGB sowie &sect; 1 UGB.</p>
        <p>(2) Verbraucher sind von der Nutzung ausgeschlossen. Ein Vertragsschluss mit Verbrauchern erfolgt nicht.</p>
        <p>(3) Abweichende oder entgegenstehende Bedingungen des Auftraggebers finden keine Anwendung, es sei denn, ihrer Geltung wird ausdr&uuml;cklich schriftlich zugestimmt.</p>

        <h3>&sect;2 Vertragsgegenstand</h3>
        <p>Der Anbieter erbringt Leistungen im Bereich:</p>
        <ul>
          <li>KI-Agenten (Software-as-a-Service)</li>
          <li>Automatisierungsl&ouml;sungen</li>
          <li>Softwareentwicklung</li>
          <li>Systemintegration</li>
          <li>IT-Beratung</li>
        </ul>
        <p>Der konkrete Leistungsumfang ergibt sich aus dem jeweiligen Angebot oder Individualvertrag.</p>

        <h3>&sect;3 Vertragsschluss</h3>
        <p>(1) Angebote sind freibleibend und unverbindlich.</p>
        <p>(2) Der Vertrag kommt zustande durch:</p>
        <ul>
          <li>Annahme eines Angebots</li>
          <li>oder Nutzung der Plattform</li>
          <li>oder digitale Best&auml;tigung</li>
        </ul>

        <h3>&sect;4 Verg&uuml;tung und Zahlungsbedingungen</h3>
        <p>(1) Alle Preise verstehen sich netto zuz&uuml;glich gesetzlicher Steuern.</p>
        <p>(2) Rechnungen sind innerhalb von 14 Tagen ohne Abzug zahlbar.</p>

        <h3>&sect;5 Zahlungsverzug und Sperrung</h3>
        <p>(1) Der Anbieter ist berechtigt, Leistungen ganz oder teilweise auszusetzen oder den Zugang zu Systemen zu sperren, wenn der Auftraggeber mit f&auml;lligen Zahlungen in Verzug ist.</p>
        <p>(2) Voraussetzung ist eine Mahnung mit einer Frist von mindestens 7 Tagen.</p>
        <p>(3) Die Sperrung wird vorab angek&uuml;ndigt.</p>
        <p>(4) Die Zahlungspflicht bleibt w&auml;hrend der Sperrung bestehen.</p>
        <p>(5) Nach vollst&auml;ndigem Ausgleich erfolgt die Freischaltung unverz&uuml;glich.</p>

        <h3>&sect;6 Laufzeit und K&uuml;ndigung</h3>
        <p>(1) SaaS-Vertr&auml;ge haben eine Mindestlaufzeit von 24 Monaten.</p>
        <p>(2) Die Vertragslaufzeit verl&auml;ngert sich automatisch um 12 Monate, sofern nicht mit einer Frist von 3 Monaten gek&uuml;ndigt wird.</p>
        <p>(3) Das Recht zur au&szlig;erordentlichen K&uuml;ndigung aus wichtigem Grund bleibt unber&uuml;hrt.</p>
        <p>(4) Im Falle einer vorzeitigen K&uuml;ndigung ohne wichtigen Grund ist eine angemessene Ausfallverg&uuml;tung zu leisten.</p>

        <h3>&sect;7 Verf&uuml;gbarkeit</h3>
        <p>Der Anbieter strebt eine Verf&uuml;gbarkeit von 99,5 % im Jahresmittel an.</p>

        <h3>&sect;8 Haftung</h3>
        <p>(1) Der Anbieter haftet unbeschr&auml;nkt bei Vorsatz, grober Fahrl&auml;ssigkeit und bei Sch&auml;den aus der Verletzung von Leben, K&ouml;rper oder Gesundheit.</p>
        <p>(2) Bei einfacher Fahrl&auml;ssigkeit haftet der Anbieter nur bei Verletzung wesentlicher Vertragspflichten.</p>
        <p>(3) Die Haftung ist der H&ouml;he nach auf den Auftragswert begrenzt.</p>

        <h3>&sect;9 Nutzungsrechte</h3>
        <p>(1) Nutzungsrechte werden erst nach vollst&auml;ndiger Zahlung einger&auml;umt.</p>
        <p>(2) Der Anbieter beh&auml;lt s&auml;mtliche Rechte an Systemen, Frameworks und Technologien.</p>

        <h3>&sect;10 Zugangssperre</h3>
        <p>Der Anbieter ist berechtigt, Systeme und Dienstleistungen vor&uuml;bergehend zu deaktivieren, wenn vertragliche Pflichten verletzt werden.</p>

        <h3>&sect;11 Datenschutz</h3>
        <p>Es gelten die Datenschutzerkl&auml;rung sowie der Auftragsverarbeitungsvertrag.</p>

        <h3>&sect;12 Rechtswahl und Gerichtsstand</h3>
        <p>(1) Es gilt niederl&auml;ndisches Recht.</p>
        <p>(2) Gerichtsstand ist der Sitz des Anbieters.</p>

        <h3>&sect;13 Schlussbestimmungen</h3>
        <p>Sollten einzelne Bestimmungen unwirksam sein, bleibt die Wirksamkeit der &uuml;brigen unber&uuml;hrt.</p>
      </section>
    </>
  )
};const KIContent = {
  de: () => (
    <>
      <section>
        <h2>Hinweise zur Nutzung von KI</h2>
        <p>Die eingesetzten KI-Systeme dienen der Unterst&uuml;tzung und Automatisierung.</p>
        <p>Ergebnisse k&ouml;nnen fehlerhaft oder unvollst&auml;ndig sein.</p>
        <p>Der Nutzer ist verpflichtet, alle Ergebnisse eigenst&auml;ndig zu pr&uuml;fen.</p>
        <p>Der Anbieter &uuml;bernimmt keine Haftung f&uuml;r Entscheidungen, die auf KI-Ergebnissen basieren.</p>
      </section>
    </>
  ),
  nl: () => (
    <>
      <section>
        <h2>Informatie over het gebruik van AI</h2>
        <p>De gebruikte AI-systemen dienen ter ondersteuning en automatisering.</p>
        <p>Resultaten kunnen onjuist of onvolledig zijn.</p>
        <p>De gebruiker is verplicht alle resultaten zelfstandig te controleren.</p>
        <p>De aanbieder is niet aansprakelijk voor beslissingen op basis van AI-resultaten.</p>
      </section>
    </>
  ),
  en: () => (
    <>
      <section>
        <h2>AI Usage Notice</h2>
        <p>The AI systems used are intended for support and automation purposes.</p>
        <p>Results may be incomplete or contain errors.</p>
        <p>The user is obligated to independently verify all results.</p>
        <p>The provider assumes no liability for decisions based on AI results.</p>
      </section>
    </>
  )
};const WiderrufContent = {
  de: () => (
    <>
      <section>
        <h2>Hinweis zum Widerrufsrecht</h2>
        <p>Die angebotenen Leistungen richten sich ausschlie&szlig;lich an Unternehmer.</p>
        <p>Ein gesetzliches Widerrufsrecht besteht daher nicht.</p>
      </section>
    </>
  ),
  nl: () => (
    <>
      <section>
        <h2>Informatie over herroepingsrecht</h2>
        <p>De aangeboden diensten zijn uitsluitend gericht op ondernemers.</p>
        <p>Er bestaat daarom geen wettelijk herroepingsrecht.</p>
      </section>
    </>
  ),
  en: () => (
    <>
      <section>
        <h2>Cancellation Policy Notice</h2>
        <p>The offered services are exclusively directed at entrepreneurs.</p>
        <p>Therefore, no statutory right of withdrawal exists.</p>
      </section>
    </>
  )
};const CookieContent = {
  de: () => (
    <>
      <p>gemäß § 25 TDDDG (Deutschland), Art. 11.7a Telecommunicatiewet (Niederlande), § 165 TKG 2021 (Österreich) und der ePrivacy-Richtlinie 2002/58/EG</p>
      <section>
        <h2>§ 1 Was sind Cookies?</h2>
        <p>Cookies und vergleichbare Technologien (localStorage, sessionStorage) sind kleine Textinformationen, die auf Ihrem Endgerät gespeichert werden. Sie dienen der Funktionsfähigkeit und Verbesserung von Websites.</p>
      </section>
      <section>
        <h2>§ 2 Unsere Cookie-Strategie</h2>
        <p>{CO.legal} verfolgt einen datenschutzfreundlichen Ansatz: Wir setzen <strong>ausschließlich technisch notwendige Cookies und Speichermechanismen</strong> ein, die für den ordnungsgemäßen Betrieb der Website unverzichtbar sind. Wir verwenden <strong>keine</strong> Marketing-, Werbe- oder Tracking-Cookies von Drittanbietern.</p>
        <p>Da wir ausschließlich technisch notwendige Cookies einsetzen, ist gemäß § 25 Abs. 2 Nr. 2 TDDDG, Art. 11.7a Abs. 3 Telecommunicatiewet und § 165 Abs. 3 TKG 2021 keine gesonderte Einwilligung erforderlich.</p>
      </section>
      <section>
        <h2>§ 3 Eingesetzte Technologien im Detail</h2>
        <table style={{width:'100%',borderCollapse:'collapse',marginBottom:16}}>
          <thead><tr style={{borderBottom:'2px solid rgba(254,155,123,0.2)'}}>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Name</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Typ</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Zweck</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Speicherdauer</th>
            <th style={{textAlign:'left',padding:'8px 12px',fontSize:'.8125rem',color:'#FE9B7B'}}>Kategorie</th>
          </tr></thead>
          <tbody style={{fontSize:'.8125rem'}}>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>nx_cookie_consent</td><td style={{padding:'8px 12px'}}>localStorage</td><td style={{padding:'8px 12px'}}>Speichert Ihre Cookie-Einstellungen (Werte: „all" oder „essential")</td><td style={{padding:'8px 12px'}}>Persistent (manuell löschbar)</td><td style={{padding:'8px 12px'}}>Notwendig</td></tr>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>nx_auth</td><td style={{padding:'8px 12px'}}>localStorage</td><td style={{padding:'8px 12px'}}>JWT-Authentifizierungstoken, Rolle und E-Mail (verschlüsselt)</td><td style={{padding:'8px 12px'}}>24 Stunden (automatische Token-Expiration)</td><td style={{padding:'8px 12px'}}>Notwendig</td></tr>
            <tr style={{borderBottom:'1px solid rgba(255,255,255,0.05)'}}><td style={{padding:'8px 12px'}}>nx_lang</td><td style={{padding:'8px 12px'}}>localStorage</td><td style={{padding:'8px 12px'}}>Spracheinstellung (de/nl/en)</td><td style={{padding:'8px 12px'}}>Persistent</td><td style={{padding:'8px 12px'}}>Notwendig</td></tr>
            <tr><td style={{padding:'8px 12px'}}>nx_s</td><td style={{padding:'8px 12px'}}>sessionStorage</td><td style={{padding:'8px 12px'}}>Anonyme Session-ID für anonymisierte Nutzungsstatistiken (kein Personenbezug)</td><td style={{padding:'8px 12px'}}>Browsersitzung</td><td style={{padding:'8px 12px'}}>Notwendig</td></tr>
          </tbody>
        </table>
      </section>
      <section>
        <h2>§ 4 Was wir NICHT verwenden</h2>
        <ul>
          <li>Keine Google Analytics oder vergleichbare Tracking-Dienste</li>
          <li>Keine Meta/Facebook Pixel</li>
          <li>Keine Retargeting- oder Remarketing-Cookies</li>
          <li>Keine Werbe-Netzwerke oder Datenhändler</li>
          <li>Kein Cross-Site-Tracking</li>
          <li>Keine Fingerprinting-Technologien</li>
          <li>Keine Social-Media-Tracking-Plugins (nur reine Links)</li>
        </ul>
      </section>
      <section>
        <h2>§ 5 Ihre Kontrollmöglichkeiten</h2>
        <p>Sie können Cookies und localStorage-Daten jederzeit über die Einstellungen Ihres Browsers verwalten oder löschen. Bitte beachten Sie, dass das Löschen von „nx_auth" zu einer Abmeldung und das Löschen von „nx_lang" zum Zurücksetzen der Spracheinstellung führt.</p>
        <p>Sie können Ihre Cookie-Präferenz auch über den Link „Cookie-Einstellungen" im Footer unserer Website ändern.</p>
      </section>
      <section>
        <h2>§ 6 Änderungen</h2>
        <p>Bei Änderungen unserer Cookie-Praxis aktualisieren wir diese Seite und informieren Sie über das Cookie-Banner.</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </>
  ),
  nl: () => (
    <>
      <p>conform Art. 11.7a Telecommunicatiewet en de ePrivacy-richtlijn 2002/58/EG</p>
      <section><h2>§ 1 Ons cookiebeleid</h2><p>Wij gebruiken uitsluitend technisch noodzakelijke cookies en localStorage. Geen marketing-, tracking- of advertentiecookies. Geen toestemming vereist (Art. 11.7a lid 3 Tw).</p></section>
      <section><h2>§ 2 Gebruikte technologieën</h2><ul><li><strong>nx_cookie_consent</strong> (localStorage) — cookievoorkeuren</li><li><strong>nx_auth</strong> (localStorage) — authenticatie (24 uur)</li><li><strong>nx_lang</strong> (localStorage) — taalinstelling</li><li><strong>nx_s</strong> (sessionStorage) — anonieme sessie-ID</li></ul></section>
      <section><h2>§ 3 Wat wij NIET gebruiken</h2><p>Geen Google Analytics, geen Meta Pixel, geen retargeting, geen fingerprinting, geen cross-site tracking.</p></section>
      <section><h2>§ 4 Uw controle</h2><p>Beheer via browserinstellingen of „Cookie-instellingen" in de footer.</p></section>
      <p className="legal-date">Status: april 2026</p>
    </>
  ),
  en: () => (
    <>
      <p>pursuant to § 25 TDDDG (Germany), Art. 11.7a Telecommunicatiewet (Netherlands) and ePrivacy Directive 2002/58/EC</p>
      <section><h2>§ 1 Our Cookie Strategy</h2><p>We use only technically necessary cookies and localStorage. No marketing, tracking or advertising cookies. No consent required per applicable law.</p></section>
      <section><h2>§ 2 Technologies Used</h2><ul><li><strong>nx_cookie_consent</strong> (localStorage) — cookie preferences</li><li><strong>nx_auth</strong> (localStorage) — authentication (24h expiry)</li><li><strong>nx_lang</strong> (localStorage) — language setting</li><li><strong>nx_s</strong> (sessionStorage) — anonymous session ID</li></ul></section>
      <section><h2>§ 3 What We Do NOT Use</h2><p>No Google Analytics, no Meta Pixel, no retargeting, no fingerprinting, no cross-site tracking.</p></section>
      <section><h2>§ 4 Your Control</h2><p>Manage via browser settings or "Cookie Settings" in footer.</p></section>
      <p className="legal-date">Last updated: April 2026</p>
    </>
  )
};

/* ═══════════════════════════════════════════════════════════
   AVV — AUFTRAGSVERARBEITUNGSVERTRAG
   ═══════════════════════════════════════════════════════════ */
const AVVContent = {
  de: () => (
    <>
      <p>gemäß Art. 28 Verordnung (EU) 2016/679 (DSGVO) in Verbindung mit Art. 28 UAVG</p>
      <section>
        <h2>§ 1 Gegenstand und Dauer</h2>
        <p>(1) Dieser Auftragsverarbeitungsvertrag (AVV) regelt die Rechte und Pflichten im Zusammenhang mit der Verarbeitung personenbezogener Daten durch {CO.legal} (nachfolgend „Auftragsverarbeiter") im Auftrag des Kunden (nachfolgend „Verantwortlicher").</p>
        <p>(2) Der AVV gilt für die Dauer des Hauptvertrags und darüber hinaus, bis alle personenbezogenen Daten vollständig gelöscht oder zurückgegeben sind.</p>
        <p>(3) Gegenstand der Verarbeitung: Implementierung, Betrieb und Wartung von KI-Agenten, Automatisierungslösungen, CRM/ERP-Integrationen und zugehörigen Webservices gemäß dem Hauptvertrag.</p>
      </section>
      <section>
        <h2>§ 2 Art und Zweck der Verarbeitung</h2>
        <p><strong>Art der Verarbeitung:</strong> Erheben, Erfassen, Ordnen, Speichern, Anpassen, Abfragen, Verwenden, Übermitteln, Einschränken, Löschen von Daten im Rahmen der vereinbarten Dienstleistungen.</p>
        <p><strong>Zweck:</strong> Erbringung der im Hauptvertrag vereinbarten IT-Dienstleistungen (KI-Agenten, Automation, Webentwicklung, Beratung).</p>
        <p><strong>Art der Daten:</strong> Kontaktdaten (Name, E-Mail, Telefon), Unternehmensdaten, Kommunikationsinhalte, Nutzungsdaten, technische Daten (IP, User-Agent), ggf. vom Verantwortlichen bereitgestellte Kundendaten.</p>
        <p><strong>Kategorien betroffener Personen:</strong> Mitarbeiter, Kunden, Interessenten und Geschäftspartner des Verantwortlichen.</p>
      </section>
      <section>
        <h2>§ 3 Pflichten des Auftragsverarbeiters</h2>
        <p>Der Auftragsverarbeiter verpflichtet sich:</p>
        <ul>
          <li>(a) Personenbezogene Daten ausschließlich auf dokumentierte Weisung des Verantwortlichen zu verarbeiten (Art. 28 Abs. 3 lit. a DSGVO), es sei denn, eine gesetzliche Pflicht erfordert die Verarbeitung.</li>
          <li>(b) Sicherzustellen, dass sich die zur Verarbeitung befugten Personen zur Vertraulichkeit verpflichtet haben (Art. 28 Abs. 3 lit. b DSGVO).</li>
          <li>(c) Geeignete technische und organisatorische Maßnahmen gemäß Art. 32 DSGVO zu ergreifen (siehe § 5).</li>
          <li>(d) Den Verantwortlichen bei der Erfüllung der Betroffenenrechte (Art. 15–22 DSGVO) zu unterstützen (Art. 28 Abs. 3 lit. e DSGVO).</li>
          <li>(e) Den Verantwortlichen bei der Einhaltung der Pflichten aus Art. 32–36 DSGVO (Sicherheit, Datenschutz-Folgenabschätzung, vorherige Konsultation) zu unterstützen.</li>
          <li>(f) Nach Beendigung der Verarbeitung alle personenbezogenen Daten nach Wahl des Verantwortlichen zu löschen oder zurückzugeben (Art. 28 Abs. 3 lit. g DSGVO).</li>
          <li>(g) Dem Verantwortlichen alle erforderlichen Informationen zum Nachweis der Einhaltung zur Verfügung zu stellen und Überprüfungen zu ermöglichen (Art. 28 Abs. 3 lit. h DSGVO).</li>
        </ul>
      </section>
      <section>
        <h2>§ 4 Unterauftragsverarbeiter</h2>
        <p>(1) Der Verantwortliche erteilt dem Auftragsverarbeiter eine allgemeine schriftliche Genehmigung zum Einsatz der in § 4 der Datenschutzerklärung genannten Unterauftragsverarbeiter (Art. 28 Abs. 2 DSGVO).</p>
        <p>(2) Der Auftragsverarbeiter informiert den Verantwortlichen mindestens 30 Tage im Voraus über beabsichtigte Änderungen in Bezug auf die Hinzuziehung oder Ersetzung von Unterauftragsverarbeitern. Der Verantwortliche kann innerhalb dieser Frist Einspruch erheben.</p>
        <p>(3) Der Auftragsverarbeiter schließt mit jedem Unterauftragsverarbeiter einen Vertrag, der mindestens die gleichen Datenschutzpflichten auferlegt wie dieser AVV.</p>
      </section>
      <section>
        <h2>§ 5 Technisch-organisatorische Maßnahmen</h2>
        <p>Der Auftragsverarbeiter hat folgende Maßnahmen gemäß Art. 32 DSGVO implementiert:</p>
        <ul>
          <li><strong>Vertraulichkeit:</strong> Zugriffskontrolle (RBAC), Verschlüsselung (TLS 1.2+, AES-256), Argon2id-Passworthashing, JWT mit 24h-Ablauf.</li>
          <li><strong>Integrität:</strong> Input-Validierung, Audit-Logging, Dokumenten-Hashing (SHA-256), Versionierung.</li>
          <li><strong>Verfügbarkeit:</strong> Redundante Infrastruktur (MongoDB Atlas), tägliche verschlüsselte Backups, Point-in-Time-Recovery.</li>
          <li><strong>Belastbarkeit:</strong> Rate Limiting, DDoS-Schutz, horizontale Skalierung, Monitoring und Alerting.</li>
          <li><strong>Wiederherstellbarkeit:</strong> Backup-Restore-Tests, dokumentierte Incident-Response-Prozesse.</li>
        </ul>
      </section>
      <section>
        <h2>§ 6 Meldung von Datenschutzverletzungen</h2>
        <p>(1) Der Auftragsverarbeiter meldet dem Verantwortlichen jede Verletzung des Schutzes personenbezogener Daten unverzüglich und möglichst innerhalb von 24 Stunden nach Kenntnisnahme (Art. 33 Abs. 2 DSGVO).</p>
        <p>(2) Die Meldung enthält mindestens: Art der Verletzung, betroffene Datenkategorien und Personenzahl, wahrscheinliche Folgen, ergriffene Gegenmaßnahmen.</p>
      </section>
      <section>
        <h2>§ 7 Datenübermittlung in Drittländer</h2>
        <p>Soweit personenbezogene Daten in Drittländer übermittelt werden (derzeit: USA via OpenAI), geschieht dies ausschließlich auf Basis von Standardvertragsklauseln gemäß Art. 46 Abs. 2 lit. c DSGVO (Durchführungsbeschluss (EU) 2021/914) in Verbindung mit den ergänzenden Maßnahmen gemäß den EDPB-Empfehlungen 01/2020.</p>
      </section>
      <section>
        <h2>§ 8 Kontakt</h2>
        <p>{CO.legal}<br/>{CO.ceo}<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>Telefon: {CO.phone}</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </>
  ),
  nl: () => (
    <>
      <p>conform Art. 28 Verordening (EU) 2016/679 (AVG)</p>
      <section><h2>§ 1 Onderwerp en duur</h2><p>Deze verwerkersovereenkomst regelt de verwerking van persoonsgegevens door {CO.legal} (verwerker) in opdracht van de klant (verwerkingsverantwoordelijke). Geldig voor de duur van het hoofdcontract.</p></section>
      <section><h2>§ 2 Aard en doel</h2><p>Implementatie en beheer van AI-agenten, automatisering, CRM/ERP-integraties. Gegevens: contactgegevens, bedrijfsgegevens, communicatie-inhoud, technische gegevens. Betrokkenen: medewerkers, klanten, prospects van de verantwoordelijke.</p></section>
      <section><h2>§ 3 Verplichtingen verwerker</h2><p>Verwerking uitsluitend op instructie (Art. 28 lid 3 sub a). Vertrouwelijkheid (sub b). Beveiligingsmaatregelen Art. 32 (sub c). Ondersteuning betrokkenenrechten (sub e). Wissing/teruggave na beëindiging (sub g). Medewerking bij audits (sub h).</p></section>
      <section><h2>§ 4 Sub-verwerkers</h2><p>Algemene toestemming voor genoemde sub-verwerkers. 30 dagen voorafgaande kennisgeving bij wijziging. Dezelfde verplichtingen doorgelegd.</p></section>
      <section><h2>§ 5 Beveiligingsmaatregelen</h2><p>RBAC, TLS 1.2+, AES-256, Argon2id, JWT 24h, audit-logging, dagelijkse back-ups, rate limiting, monitoring.</p></section>
      <section><h2>§ 6 Datalekken</h2><p>Melding binnen 24 uur na kennisname (Art. 33 lid 2 AVG).</p></section>
      <section><h2>§ 7 Doorgifte</h2><p>Naar VS (OpenAI) uitsluitend op basis van SCC (Art. 46 lid 2 sub c AVG) + aanvullende maatregelen.</p></section>
      <p className="legal-date">Status: april 2026</p>
    </>
  ),
  en: () => (
    <>
      <p>pursuant to Art. 28 Regulation (EU) 2016/679 (GDPR)</p>
      <section><h2>§ 1 Subject and Duration</h2><p>This DPA governs the processing of personal data by {CO.legal} (processor) on behalf of the client (controller). Valid for the duration of the main contract.</p></section>
      <section><h2>§ 2 Nature and Purpose</h2><p>Implementation and operation of AI agents, automation, CRM/ERP integrations. Data: contact, company, communication, technical data. Subjects: employees, customers, prospects of the controller.</p></section>
      <section><h2>§ 3 Processor Obligations</h2><p>Processing only on instructions (Art. 28(3)(a)). Confidentiality (b). Security measures Art. 32 (c). Support for data subject rights (e). Deletion/return upon termination (g). Audit cooperation (h).</p></section>
      <section><h2>§ 4 Sub-processors</h2><p>General authorization for listed sub-processors. 30 days prior notice for changes. Same obligations flow down.</p></section>
      <section><h2>§ 5 Security Measures</h2><p>RBAC, TLS 1.2+, AES-256, Argon2id, JWT 24h, audit logging, daily backups, rate limiting, monitoring.</p></section>
      <section><h2>§ 6 Data Breaches</h2><p>Notification within 24 hours of discovery (Art. 33(2) GDPR).</p></section>
      <section><h2>§ 7 Transfers</h2><p>To US (OpenAI) solely based on SCC (Art. 46(2)(c) GDPR) + supplementary measures.</p></section>
      <p className="legal-date">Last updated: April 2026</p>
    </>
  )
};

/* ═══════════════════════════════════════════════════════════
   ROUTING & CONTENT MAP
   ═══════════════════════════════════════════════════════════ */
const TITLES = {
  impressum: { de: 'Impressum', nl: 'Impressum', en: 'Imprint' },
  datenschutz: { de: 'Datenschutzerklärung', nl: 'Privacybeleid', en: 'Privacy Policy' },
  agb: { de: 'Allgemeine Geschäftsbedingungen', nl: 'Algemene Voorwaarden', en: 'Terms and Conditions' },
  ki: { de: 'KI-Hinweise & Transparenz', nl: 'AI-Informatie & Transparantie', en: 'AI Transparency Notice' },
  widerruf: { de: 'Widerrufsbelehrung', nl: 'Herroepingsrecht', en: 'Cancellation Policy' },
  cookies: { de: 'Cookie-Richtlinie', nl: 'Cookiebeleid', en: 'Cookie Policy' },
  avv: { de: 'Auftragsverarbeitungsvertrag (AVV)', nl: 'Verwerkersovereenkomst', en: 'Data Processing Agreement (DPA)' }
};

const CONTENT_MAP = {
  impressum: ImpressumContent,
  datenschutz: DatenschutzContent,
  agb: AGBContent,
  ki: KIContent,
  widerruf: WiderrufContent,
  cookies: CookieContent,
  avv: AVVContent
};

const SLUG_MAP = {
  impressum: 'impressum', imprint: 'impressum',
  datenschutz: 'datenschutz', privacy: 'datenschutz', privacybeleid: 'datenschutz',
  agb: 'agb', terms: 'agb', voorwaarden: 'agb',
  'ki-hinweise': 'ki', 'ai-transparency': 'ki', 'ai-informatie': 'ki',
  widerrufsbelehrung: 'widerruf', herroepingsrecht: 'widerruf', 'cancellation-policy': 'widerruf',
  'cookie-richtlinie': 'cookies', cookiebeleid: 'cookies', 'cookie-policy': 'cookies',
  avv: 'avv', verwerkersovereenkomst: 'avv', dpa: 'avv'
};

export default function LegalPage() {
  const { lang: urlLang, page: slug } = useParams();
  const { lang } = useLanguage();

  if (!SUPPORTED.includes(urlLang)) {
    return <Navigate to={`/de/${slug || ''}`} replace />;
  }

  const pageKey = SLUG_MAP[slug];
  if (!pageKey) return <Navigate to={`/${lang}`} replace />;

  const content = CONTENT_MAP[pageKey];
  const Render = content[lang] || content.en;
  const title = TITLES[pageKey][lang] || TITLES[pageKey].en;

  return <LegalWrap title={title}><Render /></LegalWrap>;
}
