import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import App from './App';
import Admin from './pages/Admin';

const CO = {
  legal: 'NeXify Automate', ceo: 'Pascal Courbois, Geschäftsführer',
  nl: 'Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande',
  de: 'Wallstraße 9, 41334 Nettetal-Kaldenkirchen, Deutschland',
  phone: '+31 6 133 188 56', email: 'support@nexify-automate.com',
  web: 'nexify-automate.com', kvk: '90483944', vat: 'NL865786276B01'
};

const LegalWrap = ({ children, title }) => (
  <div className="legal-page">
    <nav className="legal-nav"><a href="/" className="legal-back">&larr; Zurück zur Startseite</a></nav>
    <main className="legal-content"><h1>{title}</h1>{children}</main>
  </div>
);

function Impressum() {
  return (
    <LegalWrap title="Impressum">
      <section>
        <h2>Angaben gemäß § 5 TMG / Art. 5 E-Commerce-Gesetz</h2>
        <p><strong>{CO.legal}</strong></p>
        <p>{CO.nl}</p>
        <p>{CO.de}</p>
      </section>
      <section>
        <h2>Vertreten durch</h2>
        <p>{CO.ceo}</p>
      </section>
      <section>
        <h2>Kontakt</h2>
        <p>Telefon: {CO.phone}<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a></p>
      </section>
      <section>
        <h2>Registereintrag</h2>
        <p>Kamer van Koophandel (KvK): {CO.kvk}<br/>USt-IdNr.: {CO.vat}</p>
      </section>
      <section>
        <h2>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
        <p>{CO.ceo}<br/>{CO.nl}</p>
      </section>
      <section>
        <h2>EU-Streitschlichtung</h2>
        <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a></p>
        <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
      </section>
      <section>
        <h2>Haftungsausschluss</h2>
        <h3>Haftung für Inhalte</h3>
        <p>Die Inhalte unserer Seiten wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen. Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich.</p>
        <h3>Haftung für Links</h3>
        <p>Unser Angebot enthält Links zu externen Webseiten Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen.</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </LegalWrap>
  );
}

function Datenschutz() {
  return (
    <LegalWrap title="Datenschutzerklärung">
      <section>
        <h2>1. Verantwortlicher</h2>
        <p>Verantwortlich für die Datenverarbeitung:</p>
        <p>{CO.legal}<br/>{CO.ceo}<br/>{CO.nl}<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a></p>
      </section>
      <section>
        <h2>2. Erhebung personenbezogener Daten</h2>
        <h3>2.1 Kontaktformular</h3>
        <p>Bei Nutzung des Kontaktformulars werden Name, E-Mail-Adresse, Telefonnummer (optional), Unternehmen (optional) und Ihre Nachricht verarbeitet. Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (vorvertragliche Maßnahmen).</p>
        <h3>2.2 Terminbuchung</h3>
        <p>Bei der Buchung eines Beratungsgesprächs werden Name, E-Mail, Telefon, Unternehmen, gewünschtes Datum/Uhrzeit und Gesprächsthema verarbeitet. Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO.</p>
        <h3>2.3 Live-Chat</h3>
        <p>Chatverläufe werden mit einer Session-ID gespeichert. Der Chat dient der Beratung und Lead-Qualifizierung. Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an Kundenberatung).</p>
        <h3>2.4 Analyse / Tracking</h3>
        <p>Wir erfassen anonymisierte Nutzungsdaten (Seitenaufrufe, Scroll-Tiefe, Klicks). Es werden keine personenbezogenen Profile erstellt. Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO. Sie können dem über die Cookie-Einstellungen widersprechen.</p>
      </section>
      <section>
        <h2>3. E-Mail-Kommunikation</h2>
        <p>Für den Versand von Bestätigungs- und Benachrichtigungs-E-Mails nutzen wir den Dienst Resend (Resend, Inc.). Es werden die für den E-Mail-Versand notwendigen Daten (E-Mail-Adresse, Name) an Resend übermittelt. Resend verarbeitet die Daten gemäß deren Datenschutzrichtlinie und handelt als Auftragsverarbeiter.</p>
      </section>
      <section>
        <h2>4. Ihre Rechte</h2>
        <p>Sie haben das Recht auf:</p>
        <ul>
          <li>Auskunft über Ihre gespeicherten Daten (Art. 15 DSGVO)</li>
          <li>Berichtigung unrichtiger Daten (Art. 16 DSGVO)</li>
          <li>Löschung Ihrer Daten (Art. 17 DSGVO)</li>
          <li>Einschränkung der Verarbeitung (Art. 18 DSGVO)</li>
          <li>Datenübertragbarkeit (Art. 20 DSGVO)</li>
          <li>Widerspruch gegen die Verarbeitung (Art. 21 DSGVO)</li>
        </ul>
        <p>Kontaktieren Sie uns unter <a href={`mailto:${CO.email}`}>{CO.email}</a>.</p>
      </section>
      <section>
        <h2>5. Cookies</h2>
        <p>Diese Website verwendet technisch notwendige Session-Cookies. Optionale Analyse-Cookies werden nur mit Ihrer Einwilligung gesetzt. Sie können Ihre Cookie-Einstellungen jederzeit über den Link im Footer ändern.</p>
      </section>
      <section>
        <h2>6. Datenspeicherung</h2>
        <p>Ihre Daten werden in einer Datenbank gespeichert, die in EU-Rechenzentren gehostet wird. Eine Übermittlung in Drittländer findet nur im Rahmen der E-Mail-Zustellung statt (Resend, mit angemessenen Schutzmaßnahmen).</p>
      </section>
      <section>
        <h2>7. Admin-Bereich / CRM</h2>
        <p>Eingehende Anfragen und Buchungen werden in einem internen CRM-System verarbeitet. Der Zugang ist durch Authentifizierung geschützt. Verarbeitete Daten: Kontaktdaten, Anfrage-Inhalt, Status, interne Notizen. Rechtsgrundlage: Art. 6 Abs. 1 lit. b/f DSGVO.</p>
      </section>
      <section>
        <h2>8. SSL-Verschlüsselung</h2>
        <p>Diese Seite nutzt SSL/TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie an "https://" in der Adresszeile.</p>
      </section>
      <section>
        <h2>9. Änderungen</h2>
        <p>Wir behalten uns vor, diese Datenschutzerklärung anzupassen, damit sie stets den aktuellen rechtlichen Anforderungen entspricht.</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </LegalWrap>
  );
}

function AGB() {
  return (
    <LegalWrap title="Allgemeine Geschäftsbedingungen">
      <section>
        <h2>§ 1 Geltungsbereich</h2>
        <p>Diese Allgemeinen Geschäftsbedingungen gelten für alle Geschäftsbeziehungen zwischen {CO.legal} (nachfolgend "Anbieter") und dem Kunden. Maßgeblich ist die jeweils zum Zeitpunkt des Vertragsschlusses gültige Fassung.</p>
      </section>
      <section>
        <h2>§ 2 Vertragsgegenstand</h2>
        <p>Der Anbieter erbringt Beratungs- und Implementierungsleistungen im Bereich Künstliche Intelligenz, Prozessautomation, Softwareentwicklung und IT-Integration. Der genaue Leistungsumfang wird in einem individuellen Angebot oder Projektvertrag vereinbart.</p>
      </section>
      <section>
        <h2>§ 3 Vertragsschluss</h2>
        <p>Ein Vertrag kommt erst durch schriftliche Auftragsbestätigung oder durch Unterzeichnung eines individuellen Projektvertrags zustande. Das Beratungsgespräch (Strategiegespräch) ist unverbindlich und kostenfrei.</p>
      </section>
      <section>
        <h2>§ 4 Leistungserbringung</h2>
        <p>Die Leistungen werden nach dem Stand der Technik und unter Beachtung der vereinbarten Spezifikationen erbracht. Soweit nicht anders vereinbart, gelten genannte Termine als Richtwerte und nicht als Fixtermine im Sinne des § 323 Abs. 2 Nr. 2 BGB.</p>
      </section>
      <section>
        <h2>§ 5 Vergütung</h2>
        <p>Die Vergütung richtet sich nach dem individuellen Angebot bzw. dem vereinbarten Tarif. Alle Preise verstehen sich zuzüglich der gesetzlichen Umsatzsteuer, sofern nicht anders angegeben. Rechnungen sind innerhalb von 14 Tagen nach Rechnungsdatum zahlbar.</p>
      </section>
      <section>
        <h2>§ 6 Mitwirkungspflichten des Kunden</h2>
        <p>Der Kunde stellt die für die Leistungserbringung erforderlichen Informationen, Zugänge und Daten rechtzeitig zur Verfügung. Verzögerungen aufgrund fehlender Mitwirkung gehen nicht zu Lasten des Anbieters.</p>
      </section>
      <section>
        <h2>§ 7 Datenschutz</h2>
        <p>Die Verarbeitung personenbezogener Daten erfolgt gemäß unserer Datenschutzerklärung und den Anforderungen der DSGVO. Sofern erforderlich, wird ein Auftragsverarbeitungsvertrag (AVV) geschlossen.</p>
      </section>
      <section>
        <h2>§ 8 Haftung</h2>
        <p>Der Anbieter haftet unbeschränkt bei Vorsatz und grober Fahrlässigkeit. Bei leichter Fahrlässigkeit haftet der Anbieter nur bei Verletzung wesentlicher Vertragspflichten und der Höhe nach begrenzt auf den vorhersehbaren, vertragstypischen Schaden.</p>
      </section>
      <section>
        <h2>§ 9 Vertraulichkeit</h2>
        <p>Beide Parteien verpflichten sich, vertrauliche Informationen der jeweils anderen Partei nicht an Dritte weiterzugeben und nur für die Zwecke der Zusammenarbeit zu verwenden.</p>
      </section>
      <section>
        <h2>§ 10 Schlussbestimmungen</h2>
        <p>Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts. Gerichtsstand ist, soweit gesetzlich zulässig, der Sitz des Anbieters. Sollten einzelne Bestimmungen unwirksam sein, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt.</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </LegalWrap>
  );
}

function KIHinweise() {
  return (
    <LegalWrap title="KI-Hinweise & Transparenz">
      <section>
        <h2>1. Einsatz von KI-Systemen</h2>
        <p>{CO.legal} setzt im Rahmen seiner Dienstleistungen und auf dieser Website KI-gestützte Systeme ein. Diese Transparenzseite informiert Sie gemäß den Anforderungen des EU AI Act (Verordnung (EU) 2024/1689) über den Einsatz dieser Technologien.</p>
      </section>
      <section>
        <h2>2. KI auf dieser Website</h2>
        <h3>2.1 Advisory Chat</h3>
        <p>Der Live-Chat auf dieser Website nutzt ein regelbasiertes Dialogsystem zur Erstberatung und Lead-Qualifizierung. Der Chat identifiziert Ihr Anliegen anhand von Schlüsselwörtern und liefert vorbereitete Fachinformationen. Es handelt sich nicht um ein autonom generierendes KI-System.</p>
        <h3>2.2 Analyse</h3>
        <p>Die Website erfasst anonymisierte Nutzungsdaten. Es kommen keine KI-basierten Profilierungs- oder Scoring-Systeme zum Einsatz.</p>
      </section>
      <section>
        <h2>3. KI in unseren Dienstleistungen</h2>
        <p>Im Rahmen unserer Beratungs- und Implementierungsprojekte setzen wir verschiedene KI-Technologien ein:</p>
        <ul>
          <li><strong>Large Language Models (LLMs):</strong> Für Textverarbeitung, Zusammenfassung, Übersetzung und Chatbots.</li>
          <li><strong>RAG-Systeme:</strong> Retrieval-Augmented Generation für faktenbasierte Antworten aus Ihren Unternehmensdaten.</li>
          <li><strong>Agentische Systeme:</strong> KI-Agenten, die Aufgaben in Ihren Systemen (CRM, ERP) ausführen.</li>
          <li><strong>Dokumentenverarbeitung:</strong> Extraktion strukturierter Daten aus unstrukturierten Dokumenten.</li>
        </ul>
      </section>
      <section>
        <h2>4. Transparenz & Kontrolle</h2>
        <ul>
          <li>Alle KI-gestützten Interaktionen werden als solche gekennzeichnet.</li>
          <li>Kritische Geschäftsentscheidungen werden nicht vollautomatisch durch KI getroffen — Human-in-the-Loop ist Standard.</li>
          <li>Sie haben jederzeit die Möglichkeit, KI-generierte Ergebnisse durch menschliche Bearbeitung prüfen zu lassen.</li>
          <li>Alle KI-Interaktionen werden protokolliert und sind nachvollziehbar (Audit-Trail).</li>
        </ul>
      </section>
      <section>
        <h2>5. Datenverarbeitung durch KI</h2>
        <p>Ihre Daten werden nicht für das Training allgemeiner KI-Modelle verwendet. Kundendaten verbleiben in isolierten Umgebungen. Details zur Datenverarbeitung finden Sie in unserer <a href="/datenschutz">Datenschutzerklärung</a>.</p>
      </section>
      <section>
        <h2>6. Kontakt für KI-bezogene Anfragen</h2>
        <p>Bei Fragen zum Einsatz von KI-Systemen wenden Sie sich an:<br/><a href={`mailto:${CO.email}`}>{CO.email}</a></p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </LegalWrap>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/impressum" element={<Impressum />} />
        <Route path="/datenschutz" element={<Datenschutz />} />
        <Route path="/agb" element={<AGB />} />
        <Route path="/ki-hinweise" element={<KIHinweise />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
