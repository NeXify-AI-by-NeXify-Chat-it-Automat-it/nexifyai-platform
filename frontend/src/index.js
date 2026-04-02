import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import App from './App';
import Admin from './pages/Admin';

const CO = {
  legal: 'NeXify Automate', ceo: 'Pascal Courbois, Geschäftsführer (Directeur)',
  nl: 'Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande',
  de: 'Wallstraße 9, 41334 Nettetal-Kaldenkirchen, Deutschland',
  phone: '+31 6 133 188 56', email: 'support@nexify-automate.com',
  web: 'nexify-automate.com', kvk: '90483944', vat: 'NL865786276B01'
};

const LegalWrap = ({ children, title }) => (
  <div className="legal-page">
    <nav className="legal-nav">
      <div className="legal-nav-inner">
        <a href="/" className="legal-logo-link">
          <img src="/icon-mark.svg" alt="" width="28" height="28" />
          <span className="legal-logo-text">NeXify<span className="legal-logo-accent">AI</span></span>
        </a>
        <span className="legal-tagline">Chat it. Automate it.</span>
      </div>
      <a href="/" className="legal-back">&larr; Zurück zur Startseite</a>
    </nav>
    <main className="legal-content"><h1>{title}</h1>{children}</main>
  </div>
);

function Impressum() {
  return (
    <LegalWrap title="Impressum">
      <section>
        <h2>Angaben gemäß Art. 3:15d Burgerlijk Wetboek (BW), § 5 Telemediengesetz (TMG) und Art. 5 ECG</h2>
        <p><strong>{CO.legal}</strong><br/>(Eenmanszaak, eingetragen bei der Kamer van Koophandel)</p>
        <p><strong>Hauptsitz (Niederlande):</strong><br/>{CO.nl}</p>
        <p><strong>Niederlassung (Deutschland):</strong><br/>{CO.de}</p>
      </section>
      <section>
        <h2>Vertreten durch</h2>
        <p>{CO.ceo}</p>
      </section>
      <section>
        <h2>Kontakt</h2>
        <p>Telefon: <a href={`tel:${CO.phone.replace(/\s/g,'')}`}>{CO.phone}</a><br/>
        E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>
        Web: <a href={`https://${CO.web}`} target="_blank" rel="noopener noreferrer">{CO.web}</a></p>
      </section>
      <section>
        <h2>Handelsregister</h2>
        <p>Kamer van Koophandel (KvK-Nummer): {CO.kvk}<br/>
        Umsatzsteuer-Identifikationsnummer (BTW-ID): {CO.vat}</p>
        <p>Hinweis: {CO.legal} ist als niederländisches Unternehmen im Handelsregister der Kamer van Koophandel eingetragen. Der deutsche Standort dient als Niederlassung für den DACH-Markt.</p>
      </section>
      <section>
        <h2>Verantwortlich für den Inhalt</h2>
        <p>Pascal Courbois<br/>{CO.nl}</p>
        <p>Verantwortlich gemäß § 18 Abs. 2 Medienstaatsvertrag (MStV) für journalistisch-redaktionelle Inhalte.</p>
      </section>
      <section>
        <h2>Anwendbares Recht</h2>
        <p>Auf {CO.legal} als niederländisches Unternehmen findet grundsätzlich niederländisches Recht Anwendung, insbesondere das Burgerlijk Wetboek (BW). Für Verbraucher im DACH-Raum bleiben die zwingenden Verbraucherschutzvorschriften ihres jeweiligen Wohnsitzstaates unberührt (Art. 6 Abs. 2 Rom-I-Verordnung).</p>
      </section>
      <section>
        <h2>EU-Streitschlichtung</h2>
        <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a></p>
        <p>Wir sind weder bereit noch verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
      </section>
      <section>
        <h2>Haftungshinweis</h2>
        <p>Die Inhalte dieser Website wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität übernehmen wir keine Gewähr. Für verlinkte externe Inhalte übernehmen wir keine Haftung; für deren Inhalt sind ausschließlich die jeweiligen Betreiber verantwortlich.</p>
        <p>Gemäß Art. 6:196c BW (niederländisches Telekomgesetz / E-Commerce-Implementierung) sind wir als Diensteanbieter für eigene Informationen verantwortlich, jedoch nicht verpflichtet, übermittelte oder gespeicherte Informationen Dritter aktiv zu überwachen.</p>
      </section>
      <section>
        <h2>Urheberrecht</h2>
        <p>Alle Inhalte, Grafiken und Texte auf dieser Website unterliegen dem Urheberrecht von {CO.legal} bzw. der jeweiligen Rechteinhaber. Jede Verwertung außerhalb der Grenzen des Urheberrechts bedarf der schriftlichen Zustimmung.</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </LegalWrap>
  );
}

function Datenschutz() {
  return (
    <LegalWrap title="Datenschutzerklärung">
      <p>gemäß Verordnung (EU) 2016/679 (DSGVO) und dem niederländischen Uitvoeringswet Algemene verordening gegevensbescherming (UAVG)</p>
      <section>
        <h2>1. Verantwortlicher</h2>
        <p>{CO.legal}<br/>{CO.ceo}<br/>{CO.nl}<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>Telefon: {CO.phone}</p>
        <p>Die niederländische Datenschutzbehörde (Autoriteit Persoonsgegevens) ist die zuständige Aufsichtsbehörde für {CO.legal}. Betroffene im DACH-Raum können sich zudem an ihre nationale Datenschutzaufsicht wenden.</p>
      </section>
      <section>
        <h2>2. Verarbeitungstätigkeiten</h2>
        <h3>2.1 Kontaktformular</h3>
        <p>Verarbeitete Daten: Vorname, Nachname, geschäftliche E-Mail, Telefon (optional), Unternehmen (optional), Nachricht, Zeitstempel, IP-Adresse (anonymisiert).</p>
        <p>Zweck: Bearbeitung Ihrer Anfrage und vorvertragliche Kommunikation.</p>
        <p>Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (Durchführung vorvertraglicher Maßnahmen).</p>
        <p>Speicherdauer: 24 Monate nach letztem Kontakt, sofern kein Vertragsverhältnis entsteht.</p>

        <h3>2.2 Terminbuchung (Strategiegespräch)</h3>
        <p>Verarbeitete Daten: Vorname, Nachname, E-Mail, Telefon (optional), Unternehmen (optional), gewünschtes Datum und Uhrzeit, Gesprächsthema.</p>
        <p>Zweck: Organisation und Durchführung des Beratungsgesprächs.</p>
        <p>Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO.</p>
        <p>Speicherdauer: 12 Monate nach dem Termin.</p>

        <h3>2.3 KI-gestützter Live-Chat (NeXifyAI Advisor)</h3>
        <p>Verarbeitete Daten: Chatverlauf, Session-ID, Qualifizierungsdaten (erkanntes Thema), Zeitstempel.</p>
        <p>Zweck: Fachliche Erstberatung, Bedarfsermittlung, Lead-Qualifizierung und ggf. Terminbuchung.</p>
        <p>Technologie: Der Chat wird durch ein KI-Sprachmodell (OpenAI GPT) unterstützt. Ihre Chatnachrichten werden an die OpenAI-API übermittelt, um kontextbezogene Antworten zu generieren. OpenAI handelt als Auftragsverarbeiter und verwendet Ihre Daten nicht für eigenes Modelltraining (Zero Data Retention Policy).</p>
        <p>Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an effizienter Kundenberatung). Sie können jederzeit widersprechen.</p>
        <p>Speicherdauer: Chat-Sessions werden nach 90 Tagen automatisch anonymisiert.</p>

        <h3>2.4 Analyse und Nutzungsstatistik</h3>
        <p>Wir erfassen anonymisierte Nutzungsdaten: Seitenaufrufe, Scroll-Tiefe, Klickverhalten, Session-Dauer. Es werden keine Cookies für Tracking gesetzt und keine personenbezogenen Profile erstellt.</p>
        <p>Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO. Sie können der Erfassung über die Cookie-Einstellungen im Footer widersprechen.</p>
      </section>
      <section>
        <h2>3. Auftragsverarbeiter</h2>
        <p>Wir setzen folgende Auftragsverarbeiter ein:</p>
        <ul>
          <li><strong>Resend, Inc.</strong> (USA): E-Mail-Versand von Bestätigungen und Benachrichtigungen. Standardvertragsklauseln (SCC) gemäß Art. 46 Abs. 2 lit. c DSGVO als Transfergarantie.</li>
          <li><strong>OpenAI, Inc.</strong> (USA): Verarbeitung von Chat-Nachrichten durch das Sprachmodell. Standardvertragsklauseln und Zero Data Retention als Schutzmaßnahmen.</li>
          <li><strong>MongoDB Atlas</strong>: Datenbankspeicherung in EU-Rechenzentren (Frankfurt am Main).</li>
        </ul>
      </section>
      <section>
        <h2>4. Ihre Rechte</h2>
        <p>Gemäß DSGVO Kapitel III haben Sie folgende Rechte:</p>
        <ul>
          <li><strong>Auskunft</strong> (Art. 15): Kostenfreie Kopie Ihrer gespeicherten Daten</li>
          <li><strong>Berichtigung</strong> (Art. 16): Korrektur unrichtiger Daten</li>
          <li><strong>Löschung</strong> (Art. 17): Recht auf Vergessenwerden</li>
          <li><strong>Einschränkung</strong> (Art. 18): Einschränkung der Verarbeitung</li>
          <li><strong>Datenübertragbarkeit</strong> (Art. 20): Export in maschinenlesbarem Format</li>
          <li><strong>Widerspruch</strong> (Art. 21): Widerspruch gegen Verarbeitung auf Basis von Art. 6 Abs. 1 lit. f DSGVO</li>
        </ul>
        <p>Anfragen richten Sie bitte an: <a href={`mailto:${CO.email}`}>{CO.email}</a>. Wir antworten innerhalb von 30 Tagen.</p>
        <p>Beschwerderecht: Sie haben das Recht, sich bei der zuständigen Aufsichtsbehörde zu beschweren. Für {CO.legal} ist dies die Autoriteit Persoonsgegevens (AP), Postbus 93374, 2509 AJ Den Haag, Niederlande (<a href="https://autoriteitpersoonsgegevens.nl" target="_blank" rel="noopener noreferrer">autoriteitpersoonsgegevens.nl</a>).</p>
      </section>
      <section>
        <h2>5. Cookies und lokale Speicherung</h2>
        <p>Diese Website verwendet ausschließlich technisch notwendige Session-Cookies sowie localStorage für Cookie-Einstellungen und Session-IDs. Es werden keine Drittanbieter-Tracking-Cookies gesetzt.</p>
        <p>Sie können Ihre Cookie-Einstellungen jederzeit über den Link „Cookie-Einstellungen" im Footer ändern.</p>
      </section>
      <section>
        <h2>6. Datensicherheit</h2>
        <p>Wir verwenden SSL/TLS-Verschlüsselung für alle Datenübertragungen, Argon2-basiertes Passwort-Hashing, rollenbasierte Zugriffskontrolle (RBAC) und regelmäßige Sicherheitsaudits. Administrative Zugriffe werden vollständig protokolliert.</p>
      </section>
      <section>
        <h2>7. Interner CRM-Bereich</h2>
        <p>Eingehende Kontaktanfragen, Terminbuchungen und Chat-Verläufe werden in einem internen CRM-System verarbeitet. Der Zugang ist durch JWT-Authentifizierung und Argon2-Passwort-Hashing geschützt. Verarbeitete Daten: Kontaktdaten, Anfrageinhalte, Qualifizierungsstatus, interne Notizen. Rechtsgrundlage: Art. 6 Abs. 1 lit. b/f DSGVO.</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </LegalWrap>
  );
}

function AGB() {
  return (
    <LegalWrap title="Allgemeine Geschäftsbedingungen">
      <p>der {CO.legal}, eingetragen bei der Kamer van Koophandel unter Nr. {CO.kvk}</p>
      <section>
        <h2>§ 1 Geltungsbereich und anwendbares Recht</h2>
        <p>(1) Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für alle Geschäftsbeziehungen zwischen {CO.legal} (nachfolgend „Anbieter") und dem Auftraggeber (nachfolgend „Kunde").</p>
        <p>(2) Da der Anbieter seinen Sitz in den Niederlanden hat, findet grundsätzlich niederländisches Recht Anwendung, insbesondere Boek 6 des Burgerlijk Wetboek (BW). Für Verbraucher im DACH-Raum bleiben zwingende Verbraucherschutzvorschriften des jeweiligen Wohnsitzstaates unberührt (Art. 6 Abs. 2 Rom-I-Verordnung, Verordnung (EG) Nr. 593/2008).</p>
        <p>(3) Abweichende AGB des Kunden werden nicht anerkannt, es sei denn, der Anbieter stimmt diesen ausdrücklich schriftlich zu.</p>
      </section>
      <section>
        <h2>§ 2 Vertragsgegenstand</h2>
        <p>(1) Der Anbieter erbringt Beratungs- und Implementierungsleistungen in den Bereichen: Künstliche Intelligenz, Prozessautomation, CRM/ERP-Integration, Softwareentwicklung (Web-Apps, Mobile-Apps, Kundenportale), Wissenssysteme und IT-Beratung.</p>
        <p>(2) Der genaue Leistungsumfang wird in einem individuellen Angebot, einer Leistungsbeschreibung oder einem Projektvertrag (Statement of Work, SoW) festgelegt.</p>
      </section>
      <section>
        <h2>§ 3 Vertragsschluss</h2>
        <p>(1) Angebote des Anbieters sind freibleibend. Ein Vertrag kommt erst durch schriftliche Auftragsbestätigung (per E-Mail ausreichend) oder durch Unterzeichnung eines individuellen Projektvertrags zustande.</p>
        <p>(2) Das initiale Beratungsgespräch (Strategiegespräch) ist unverbindlich und kostenfrei. Hieraus entsteht keine vertragliche Verpflichtung.</p>
      </section>
      <section>
        <h2>§ 4 Leistungserbringung</h2>
        <p>(1) Die Leistungen werden nach dem Stand der Technik, unter Beachtung der vereinbarten Spezifikationen und mit der Sorgfalt eines ordentlichen Auftragnehmers (Art. 7:401 BW) erbracht.</p>
        <p>(2) Genannte Termine sind Richttermine, sofern nicht ausdrücklich als Fixtermine vereinbart (Art. 6:83 BW). Bei Verzögerungen informiert der Anbieter den Kunden unverzüglich.</p>
        <p>(3) Der Anbieter ist berechtigt, zur Leistungserbringung qualifizierte Dritte einzusetzen.</p>
      </section>
      <section>
        <h2>§ 5 Vergütung und Zahlung</h2>
        <p>(1) Die Vergütung richtet sich nach dem individuellen Angebot bzw. dem vereinbarten Tarif. Alle Preise verstehen sich netto zuzüglich der gesetzlichen Umsatzsteuer (BTW).</p>
        <p>(2) Rechnungen sind innerhalb von 14 Tagen nach Rechnungsdatum zahlbar, sofern nicht anders vereinbart.</p>
        <p>(3) Bei Zahlungsverzug ist der Anbieter berechtigt, die gesetzlichen Verzugszinsen (Art. 6:119a BW für Handelsgeschäfte) zu berechnen.</p>
      </section>
      <section>
        <h2>§ 6 Mitwirkungspflichten des Kunden</h2>
        <p>(1) Der Kunde stellt die für die Leistungserbringung erforderlichen Informationen, Zugänge, Testdaten und Ansprechpartner rechtzeitig zur Verfügung.</p>
        <p>(2) Verzögerungen aufgrund fehlender oder verspäteter Mitwirkung gehen nicht zu Lasten des Anbieters und berechtigen zur angemessenen Anpassung von Terminen und Vergütung.</p>
      </section>
      <section>
        <h2>§ 7 Datenschutz und Vertraulichkeit</h2>
        <p>(1) Die Verarbeitung personenbezogener Daten erfolgt gemäß der DSGVO und dem niederländischen UAVG. Details entnehmen Sie unserer <a href="/datenschutz">Datenschutzerklärung</a>.</p>
        <p>(2) Sofern der Anbieter im Auftrag des Kunden personenbezogene Daten verarbeitet, wird ein Auftragsverarbeitungsvertrag (AVV / Verwerkersovereenkomst) gemäß Art. 28 DSGVO geschlossen.</p>
        <p>(3) Beide Parteien verpflichten sich, vertrauliche Informationen der jeweils anderen Partei nicht an Dritte weiterzugeben und nur für die Zwecke der Zusammenarbeit zu verwenden. Diese Pflicht besteht auch nach Beendigung des Vertrags fort.</p>
      </section>
      <section>
        <h2>§ 8 Gewährleistung</h2>
        <p>(1) Der Anbieter gewährleistet, dass die Leistungen den vereinbarten Spezifikationen entsprechen. Mängelanzeigen sind unverzüglich nach Feststellung schriftlich mitzuteilen.</p>
        <p>(2) Bei berechtigten Mängeln hat der Anbieter das Recht zur Nachbesserung innerhalb einer angemessenen Frist.</p>
      </section>
      <section>
        <h2>§ 9 Haftung</h2>
        <p>(1) Die Haftung des Anbieters ist auf Vorsatz (opzet) und grobe Fahrlässigkeit (grove schuld) beschränkt, soweit gesetzlich zulässig.</p>
        <p>(2) Die Gesamthaftung des Anbieters ist je Schadensereignis begrenzt auf den Netto-Auftragswert der betroffenen Leistung, maximal jedoch auf den Betrag, den die Berufshaftpflichtversicherung des Anbieters im konkreten Fall auszahlt.</p>
        <p>(3) Indirekte Schäden, entgangener Gewinn und Datenverlust sind von der Haftung ausgeschlossen, sofern nicht durch Vorsatz oder grobe Fahrlässigkeit verursacht.</p>
      </section>
      <section>
        <h2>§ 10 Geistiges Eigentum</h2>
        <p>(1) Alle vom Anbieter erstellten Werke, Konzepte, Designs, Quellcode und Dokumentationen sind urheberrechtlich geschützt. Nach vollständiger Bezahlung geht das nicht-exklusive Nutzungsrecht für den vereinbarten Zweck auf den Kunden über.</p>
        <p>(2) Der Anbieter behält das Recht, allgemeine Methoden, Frameworks und generische Komponenten in anderen Projekten weiterzuverwenden.</p>
      </section>
      <section>
        <h2>§ 11 Laufzeit und Kündigung</h2>
        <p>(1) Dauerverträge (z.B. monatliche Tarife) können mit einer Frist von 30 Tagen zum Monatsende gekündigt werden, sofern nicht anders vereinbart.</p>
        <p>(2) Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt.</p>
      </section>
      <section>
        <h2>§ 12 Schlussbestimmungen</h2>
        <p>(1) Es gilt niederländisches Recht unter Ausschluss des UN-Kaufrechts (CISG).</p>
        <p>(2) Gerichtsstand ist Limburg (Niederlande), sofern nicht zwingende gesetzliche Vorschriften einen anderen Gerichtsstand vorsehen.</p>
        <p>(3) Sollten einzelne Bestimmungen dieser AGB unwirksam sein oder werden, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt. Die unwirksame Bestimmung ist durch eine wirksame zu ersetzen, die dem wirtschaftlichen Zweck am nächsten kommt.</p>
        <p>(4) Änderungen und Ergänzungen dieser AGB bedürfen der Schriftform (E-Mail ausreichend).</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </LegalWrap>
  );
}

function KIHinweise() {
  return (
    <LegalWrap title="KI-Hinweise & Transparenz">
      <p>gemäß den Transparenzanforderungen der Verordnung (EU) 2024/1689 über Künstliche Intelligenz (EU AI Act)</p>
      <section>
        <h2>1. Einsatz von KI-Systemen</h2>
        <p>{CO.legal} setzt im Rahmen seiner Dienstleistungen und auf dieser Website KI-gestützte Systeme ein. Diese Transparenzseite informiert Sie gemäß Art. 52 der Verordnung (EU) 2024/1689 (AI Act) über den Einsatz, die Funktionsweise und die Grenzen dieser Technologien.</p>
      </section>
      <section>
        <h2>2. KI-Systeme auf dieser Website</h2>
        <h3>2.1 NeXifyAI Advisor (Live-Chat)</h3>
        <p><strong>Art des Systems:</strong> KI-gestütztes Dialogsystem auf Basis eines Large Language Models (OpenAI GPT-4o-mini).</p>
        <p><strong>Funktionsweise:</strong> Der Chat verarbeitet Ihre Textnachrichten kontextbezogen. Das System wurde mit einem spezifischen Systemprompter konfiguriert, der Informationen über unsere Leistungen, Tarife und das Unternehmen enthält. Es generiert Antworten basierend auf diesem Wissenskontext und dem Gesprächsverlauf.</p>
        <p><strong>Zweck:</strong> Fachliche Erstberatung, Bedarfsermittlung, Lead-Qualifizierung und Terminbuchung.</p>
        <p><strong>Fähigkeiten und Grenzen:</strong></p>
        <ul>
          <li>Das System kann allgemeine Fragen zu unseren Leistungen beantworten und Termine buchen.</li>
          <li>Es kann KEINE rechtsverbindlichen Zusagen, Preisgarantien oder vertragliche Verpflichtungen eingehen.</li>
          <li>Es kann Fakten halluzinieren — alle Angaben sind im Beratungsgespräch zu verifizieren.</li>
          <li>Es ersetzt KEINE individuelle Rechts-, Steuer- oder Fachberatung.</li>
        </ul>
        <p><strong>Risikoklassifizierung:</strong> Minimales Risiko gemäß Art. 6 AI Act. Das System trifft keine automatisierten Entscheidungen mit rechtlicher Wirkung.</p>
        <p><strong>Kennzeichnung:</strong> Alle Interaktionen mit dem NeXifyAI Advisor sind als KI-gestützt erkennbar (Status-Anzeige „NeXifyAI Advisor" im Chat-Header).</p>

        <h3>2.2 Nutzungsanalyse</h3>
        <p>Die Website erfasst anonymisierte Nutzungsdaten (Seitenaufrufe, Scroll-Tiefe, Klickereignisse). Es kommen keine KI-basierten Profilierungs-, Scoring- oder Empfehlungssysteme zum Einsatz.</p>
      </section>
      <section>
        <h2>3. KI in unseren Dienstleistungen</h2>
        <p>Im Rahmen unserer Beratungs- und Implementierungsprojekte setzen wir verschiedene KI-Technologien ein:</p>
        <ul>
          <li><strong>Large Language Models (LLMs):</strong> Für Textverarbeitung, Zusammenfassung, Übersetzung, Chat-Assistenten und Content-Generierung. Eingesetzte Modelle werden projektspezifisch ausgewählt.</li>
          <li><strong>Retrieval-Augmented Generation (RAG):</strong> Für faktenbasierte Antworten aus Unternehmensdaten. Die KI sucht in einer definierten Wissensbasis und generiert Antworten auf Basis gefundener Dokumente.</li>
          <li><strong>Agentische KI-Systeme:</strong> Autonome Agenten, die definierte Aufgaben in CRM-, ERP- und Support-Systemen ausführen. Kritische Aktionen erfordern Human-in-the-Loop-Bestätigung.</li>
          <li><strong>Dokumentenverarbeitung:</strong> Intelligente Extraktion strukturierter Daten aus unstrukturierten Dokumenten (OCR, NER, Klassifizierung).</li>
        </ul>
      </section>
      <section>
        <h2>4. Transparenz und Kontrolle</h2>
        <ul>
          <li>Alle KI-gestützten Interaktionen werden als solche gekennzeichnet (Art. 52 AI Act).</li>
          <li>Kritische Geschäftsentscheidungen werden nicht vollautomatisch durch KI getroffen — Human-in-the-Loop ist bei allen kundenspezifischen Implementierungen Standard.</li>
          <li>Sie haben jederzeit die Möglichkeit, menschliche Bearbeitung statt KI-gestützter Prozesse zu verlangen.</li>
          <li>Alle KI-Interaktionen werden protokolliert und sind nachvollziehbar (Audit-Trail gemäß Art. 12 AI Act).</li>
          <li>Wir führen keine biometrische Identifikation, kein Social Scoring und keine Emotionserkennung durch (verbotene Praktiken gemäß Art. 5 AI Act).</li>
        </ul>
      </section>
      <section>
        <h2>5. Datenverarbeitung durch KI-Systeme</h2>
        <p>Ihre Daten werden nicht für das Training allgemeiner KI-Modelle verwendet. Kundendaten verbleiben in isolierten Umgebungen. Bei der Nutzung von Drittanbieter-APIs (z.B. OpenAI) gelten zusätzlich die Zero-Data-Retention-Vereinbarungen des jeweiligen Anbieters.</p>
        <p>Details zur Datenverarbeitung finden Sie in unserer <a href="/datenschutz">Datenschutzerklärung</a>.</p>
      </section>
      <section>
        <h2>6. Compliance-Übersicht</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
              <th style={{ padding: '8px 0', color: '#fff' }}>Thema</th>
              <th style={{ padding: '8px 0', color: '#fff' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {[
              ['DSGVO / AVG Konformität', 'Implementiert'],
              ['EU AI Act Transparenz (Art. 52)', 'Implementiert'],
              ['Cookie-Einwilligung (TTDSG/ePrivacy)', 'Implementiert'],
              ['Impressum (TMG §5, Art. 3:15d BW)', 'Implementiert'],
              ['AGB (Boek 6 BW)', 'Implementiert'],
              ['KI-Kennzeichnung', 'Implementiert'],
              ['Auftragsverarbeitung (AVV)', 'Projektspezifisch verfügbar'],
              ['SSL/TLS Verschlüsselung', 'Implementiert'],
              ['ISO 27001', 'Angestrebt (nicht zertifiziert)'],
              ['SOC 2 Type II', 'In Vorbereitung (nicht zertifiziert)'],
              ['Verarbeitungsverzeichnis (Art. 30)', 'Intern vorhanden'],
              ['DPIA (Art. 35)', 'Bei Bedarf durchgeführt']
            ].map(([topic, status], i) => (
              <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <td style={{ padding: '8px 0', color: 'var(--nx-muted)' }}>{topic}</td>
                <td style={{ padding: '8px 0', color: status.includes('Implementiert') ? 'var(--nx-ok)' : status.includes('Angestrebt') || status.includes('Vorbereitung') ? 'var(--nx-accent)' : 'var(--nx-muted)' }}>{status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ marginTop: '16px', fontSize: '.8125rem' }}>Hinweis: Diese Übersicht ersetzt keine individuelle rechtliche Prüfung. Wir empfehlen, projektspezifische Compliance-Anforderungen mit Ihrer Rechtsberatung abzustimmen.</p>
      </section>
      <section>
        <h2>7. Kontakt für KI-bezogene Anfragen</h2>
        <p>Bei Fragen zum Einsatz von KI-Systemen, zu dieser Transparenzerklärung oder zur Ausübung Ihrer Rechte wenden Sie sich bitte an:</p>
        <p>{CO.legal}<br/>z.Hd. Pascal Courbois<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>Telefon: {CO.phone}</p>
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
