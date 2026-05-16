import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useLanguage, SUPPORTED } from '../i18n/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';
import SEOHead from '../components/SEOHead';

const CO = {
  legal: 'NeXify Automate', ceo: 'Pascal Courbois, Geschäftsführer (Directeur)',
  nl: 'Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande',
  de: 'Wallstraße 9, 41334 Nettetal-Kaldenkirchen, Deutschland',
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
        <h2>Angaben gemäß Art. 3:15d Burgerlijk Wetboek (BW), § 5 TMG, Art. 5 ECG und § 25 MedienG</h2>
        <p><strong>{CO.legal}</strong><br/>(Eenmanszaak, eingetragen bei der Kamer van Koophandel der Niederlande)</p>
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
        <h2>Handelsregister und Steuernummern</h2>
        <p>Kamer van Koophandel (KvK-Nummer): {CO.kvk}<br/>
        Umsatzsteuer-Identifikationsnummer (BTW-ID): {CO.vat}</p>
        <p>Hinweis: {CO.legal} ist als niederländisches Unternehmen (Eenmanszaak) im Handelsregister der Kamer van Koophandel eingetragen. Der Standort in Nettetal-Kaldenkirchen dient als operative Niederlassung für den D/A/CH-Markt gemäß § 12 HGB.</p>
      </section>
      <section>
        <h2>Berufsrechtliche Angaben</h2>
        <p>Branche: IT-Beratung, KI-Automation, Softwareentwicklung<br/>
        Berufsbezeichnung: IT-Berater (verliehen in den Niederlanden)<br/>
        Zuständige Berufsaufsicht: Nicht kammerpflichtig</p>
      </section>
      <section>
        <h2>Verantwortlich für den Inhalt</h2>
        <p>Pascal Courbois<br/>{CO.nl}</p>
        <p>Verantwortlich gemäß § 18 Abs. 2 Medienstaatsvertrag (MStV) für journalistisch-redaktionelle Inhalte sowie gemäß Art. 5 Abs. 1 der E-Commerce-Richtlinie (2000/31/EG).</p>
      </section>
      <section>
        <h2>Anwendbares Recht und Gerichtsstand</h2>
        <p>Auf {CO.legal} als niederländisches Unternehmen findet grundsätzlich niederländisches Recht Anwendung, insbesondere das Burgerlijk Wetboek (BW). Für Verbraucher im D/A/CH-Raum bleiben die zwingenden Verbraucherschutzvorschriften ihres jeweiligen Wohnsitzstaates unberührt (Art. 6 Abs. 2 Rom-I-Verordnung, VO (EG) Nr. 593/2008).</p>
        <p>Gerichtsstand für Streitigkeiten mit Unternehmern: Rechtbank Limburg, Maastricht (Niederlande). Verbraucher können alternativ den Gerichtsstand ihres Wohnsitzes wählen (Art. 18 Abs. 1 Brüssel-Ia-Verordnung, VO (EU) Nr. 1215/2012).</p>
      </section>
      <section>
        <h2>EU-Streitschlichtung</h2>
        <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:<br/>
        <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a></p>
        <p>Unsere E-Mail-Adresse finden Sie oben im Impressum. Wir sind weder bereit noch verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen (§ 36 VSBG).</p>
      </section>
      <section>
        <h2>Haftungsausschluss</h2>
        <h3>Haftung für Inhalte</h3>
        <p>Die Inhalte unserer Seiten wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen. Als Diensteanbieter sind wir gemäß Art. 6:196c BW, § 7 Abs. 1 TMG und Art. 6 ECG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen (Art. 6:196c Abs. 4 BW, § 7 Abs. 2 TMG, Art. 15 E-Commerce-Richtlinie).</p>
        <h3>Haftung für Links</h3>
        <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar. Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.</p>
      </section>
      <section>
        <h2>Urheberrecht</h2>
        <p>Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem niederländischen Urheberrecht (Auteurswet) sowie dem deutschen Urheberrechtsgesetz (UrhG). Beiträge Dritter sind als solche gekennzeichnet. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen Gebrauch gestattet.</p>
      </section>
      <section>
        <h2>Bildnachweise</h2>
        <p>Alle auf dieser Website verwendeten Grafiken, Icons und Illustrationen sind Eigentum von {CO.legal} oder werden unter gültigen Lizenzen verwendet. Material Symbols Icons: Google LLC (Apache License 2.0).</p>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </>
  ),
  nl: () => (
    <>
      <section><h2>Gegevens conform Art. 3:15d Burgerlijk Wetboek (BW)</h2><p><strong>{CO.legal}</strong><br/>(Eenmanszaak, ingeschreven bij de Kamer van Koophandel)</p><p><strong>Hoofdkantoor (Nederland):</strong><br/>{CO.nl}</p><p><strong>Vestiging (Duitsland):</strong><br/>{CO.de}</p></section>
      <section><h2>Vertegenwoordigd door</h2><p>{CO.ceo}</p></section>
      <section><h2>Contact</h2><p>Telefoon: <a href={`tel:${CO.phone.replace(/\s/g,'')}`}>{CO.phone}</a><br/>E-mail: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>Web: <a href={`https://${CO.web}`} target="_blank" rel="noopener noreferrer">{CO.web}</a></p></section>
      <section><h2>Handelsregister</h2><p>Kamer van Koophandel (KvK-nummer): {CO.kvk}<br/>BTW-identificatienummer: {CO.vat}</p></section>
      <section><h2>Verantwoordelijk voor de inhoud</h2><p>Pascal Courbois<br/>{CO.nl}</p></section>
      <section><h2>Toepasselijk recht</h2><p>Op {CO.legal} als Nederlands bedrijf is Nederlands recht van toepassing, in het bijzonder het Burgerlijk Wetboek (BW). Voor consumenten in de DACH-regio blijven de dwingende consumentenbeschermingsregels van hun woonplaats onverlet (Art. 6 lid 2 Rome I-verordening).</p><p>Bevoegde rechter: Rechtbank Limburg, Maastricht.</p></section>
      <section><h2>EU-Geschillenbeslechting</h2><p>De Europese Commissie biedt een platform voor online geschillenbeslechting (ODR): <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a></p></section>
      <section><h2>Aansprakelijkheid</h2><p>De inhoud van deze website is met de grootst mogelijke zorg samengesteld. Conform Art. 6:196c BW zijn wij als dienstverlener verantwoordelijk voor eigen informatie, maar niet verplicht tot actieve controle van opgeslagen informatie van derden.</p></section>
      <section><h2>Auteursrecht</h2><p>Alle inhoud valt onder het Nederlandse auteursrecht (Auteurswet). Reproductie zonder schriftelijke toestemming is niet toegestaan.</p></section>
      <p className="legal-date">Status: april 2026</p>
    </>
  ),
  en: () => (
    <>
      <section><h2>Information pursuant to Art. 3:15d Dutch Civil Code (BW), § 5 TMG, Art. 5 ECG</h2><p><strong>{CO.legal}</strong><br/>(Eenmanszaak, registered with the Dutch Chamber of Commerce)</p><p><strong>Headquarters (Netherlands):</strong><br/>{CO.nl}</p><p><strong>Branch Office (Germany):</strong><br/>{CO.de}</p></section>
      <section><h2>Represented by</h2><p>{CO.ceo}</p></section>
      <section><h2>Contact</h2><p>Phone: <a href={`tel:${CO.phone.replace(/\s/g,'')}`}>{CO.phone}</a><br/>Email: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>Web: <a href={`https://${CO.web}`} target="_blank" rel="noopener noreferrer">{CO.web}</a></p></section>
      <section><h2>Trade Register</h2><p>Chamber of Commerce (KvK number): {CO.kvk}<br/>VAT identification number (BTW-ID): {CO.vat}</p></section>
      <section><h2>Responsible for content</h2><p>Pascal Courbois<br/>{CO.nl}</p><p>Responsible pursuant to § 18(2) MStV for editorial content and Art. 5(1) E-Commerce Directive (2000/31/EC).</p></section>
      <section><h2>Applicable law and jurisdiction</h2><p>Dutch law applies. For consumers in the DACH region, mandatory consumer protection provisions remain unaffected (Art. 6(2) Rome I Regulation). Jurisdiction: Rechtbank Limburg, Maastricht (Netherlands). Consumers may choose their local court (Art. 18(1) Brussels Ia Regulation).</p></section>
      <section><h2>EU Dispute Resolution</h2><p>ODR platform: <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a></p></section>
      <section><h2>Liability</h2><p>Content created with utmost care. As a service provider, we are responsible for our own content per Art. 6:196c BW and § 7(1) TMG. No obligation to monitor third-party information.</p></section>
      <section><h2>Copyright</h2><p>All content is protected under Dutch copyright law (Auteurswet) and German UrhG. Reproduction requires written consent.</p></section>
      <p className="legal-date">Last updated: April 2026</p>
    </>
  )
};

/* ═══════════════════════════════════════════════════════════
   DATENSCHUTZERKLÄRUNG
   ═══════════════════════════════════════════════════════════ */
const DatenschutzContent = {
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
        <p>Wir verwenden ausschließlich technisch notwendige Cookies und localStorage-Einträge gemäß § 25 Abs. 2 Nr. 2 TDDDG (Deutschland), Art. 11.7a Abs. 3 Telecommunicatiewet (Niederlande) und § 165 Abs. 3 TKG 2021 (Österreich):</p>
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
      <p>der {CO.legal}, eingetragen bei der Kamer van Koophandel unter Nr. {CO.kvk}</p>

      <section>
        <h2>§ 1 Geltungsbereich und Begriffsbestimmungen</h2>
        <p>(1) Diese Allgemeinen Geschäftsbedingungen (nachfolgend „AGB") gelten für sämtliche Geschäftsbeziehungen zwischen {CO.legal} (nachfolgend „Anbieter") und dem Kunden (nachfolgend „Auftraggeber") in der zum Zeitpunkt der Auftragserteilung gültigen Fassung.</p>
        <p>(2) „Auftraggeber" im Sinne dieser AGB sind sowohl Unternehmer (Art. 7:5 BW; § 14 BGB; § 1 KSchG Österreich) als auch Verbraucher (Art. 6:230g BW; § 13 BGB). Die Eigenschaft als Verbraucher wird gesondert kenntlich gemacht, wo abweichende Regelungen gelten.</p>
        <p>(3) Entgegenstehende oder abweichende Bedingungen des Auftraggebers werden nicht anerkannt, es sei denn, der Anbieter stimmt ihrer Geltung ausdrücklich schriftlich zu.</p>
        <p>(4) Auf die Geschäftsbeziehung findet niederländisches Recht Anwendung, insbesondere die Bücher 6 und 7 des Burgerlijk Wetboek (BW). Für Verbraucher im D/A/CH-Raum bleiben die zwingenden Verbraucherschutzvorschriften ihres jeweiligen Wohnsitzstaates unberührt (Art. 6 Abs. 2 Rom-I-Verordnung, VO (EG) Nr. 593/2008).</p>
      </section>

      <section>
        <h2>§ 2 Vertragsgegenstand</h2>
        <p>(1) Gegenstand der Leistungen des Anbieters sind insbesondere: KI-Agenten-Entwicklung und -Bereitstellung (SaaS), Prozessautomation, CRM/ERP-Integration, Softwareentwicklung, Wissenssysteme (RAG-basiert), IT-Beratung und -Strategie, Webseitenentwicklung, SEO-Optimierung sowie laufende Betreuung und Support.</p>
        <p>(2) Der konkrete Leistungsumfang ergibt sich aus dem jeweils geschlossenen Individualvertrag, dem Angebot und den dazugehörigen Vertragsanlagen (Appendizes). Im Widerspruchsfall geht der Individualvertrag diesen AGB vor.</p>
        <p>(3) Der Anbieter erbringt seine Leistungen unter Beachtung des aktuellen Stands der Technik und der anerkannten Regeln der Informatik.</p>
      </section>

      <section>
        <h2>§ 3 Vertragsschluss</h2>
        <p>(1) Angebote des Anbieters sind freibleibend und unverbindlich (Art. 6:219 BW).</p>
        <p>(2) Der Vertrag kommt zustande durch: (a) schriftliche oder elektronische Auftragsbestätigung des Anbieters, oder (b) digitale Annahme des Vertrags über das NeXifyAI-Portal mittels qualifizierter elektronischer Signatur oder namentlicher Bestätigung über den gesicherten Magic-Link (§ 6:227a BW; § 126a BGB).</p>
        <p>(3) Das Erstgespräch (Discovery Call) ist kostenfrei und unverbindlich. Aus dem Erstgespräch ergibt sich keine Verpflichtung zur Auftragserteilung.</p>
        <p>(4) Bei digitaler Vertragsannahme wird ein Nachweisprotokoll (Evidence Package) erstellt, bestehend aus: Zeitstempel (UTC), IP-Adresse, User-Agent, Dokumenten-Hash (SHA-256), Signatur-Daten und akzeptierte Rechtsmodule. Dieses Protokoll hat die gleiche Beweiskraft wie eine handschriftliche Unterschrift (Art. 6:227a BW; Art. 25 eIDAS-Verordnung).</p>
      </section>

      <section>
        <h2>§ 4 Leistungserbringung</h2>
        <p>(1) Der Anbieter erbringt seine Leistungen mit der Sorgfalt eines ordentlichen Auftragnehmers (Art. 7:401 BW) und unter Einsatz qualifizierter Fachkräfte.</p>
        <p>(2) Leistungen werden grundsätzlich remote erbracht, soweit nicht ausdrücklich etwas anderes vereinbart ist.</p>
        <p>(3) Termine und Fristen sind Richtwerte (Art. 6:83 BW), sofern nicht ausdrücklich als Fixtermin vereinbart. Höhere Gewalt, Änderungswünsche des Auftraggebers und fehlende Mitwirkung berechtigen den Anbieter zur angemessenen Fristanpassung.</p>
        <p>(4) Teillieferungen sind zulässig, sofern dies dem Auftraggeber zumutbar ist.</p>
        <p>(5) Der Anbieter ist berechtigt, zur Leistungserbringung qualifizierte Subunternehmer einzusetzen. Die Verantwortung gegenüber dem Auftraggeber verbleibt beim Anbieter.</p>
      </section>

      <section>
        <h2>§ 5 Vergütung und Zahlungsbedingungen</h2>
        <p>(1) Alle Preise verstehen sich netto zuzüglich der jeweils geltenden gesetzlichen Umsatzsteuer (BTW 21 % NL / USt 19 % DE / USt 20 % AT / MwSt 8,1 % CH). Schweizer Kunden: Reverse-Charge-Verfahren gemäß Art. 45 MWSTG.</p>
        <p>(2) <strong>KI-Agenten-Verträge (Standardmodell):</strong></p>
        <ul>
          <li>Vertragslaufzeit: 24 Monate ab Projektstart.</li>
          <li>Aktivierungsanzahlung: 30 % des Gesamtvertragswerts, fällig bei Auftragserteilung. Die Anzahlung deckt: Projektstart, Setup, Kapazitätsreservierung, Implementierungsfreigabe und initiale Konfiguration.</li>
          <li>Restbetrag: 70 % des Gesamtvertragswerts, aufgeteilt in 24 gleiche monatliche Folgeraten, jeweils zum 1. des Monats fällig.</li>
        </ul>
        <p>(3) <strong>Projektbasierte Leistungen:</strong> Vergütung nach Aufwand (Time &amp; Material) oder Festpreis gemäß Angebot. Abrechnung monatlich oder nach Meilensteinen.</p>
        <p>(4) Rechnungen sind zahlbar innerhalb von 14 Tagen nach Rechnungsdatum ohne Abzug.</p>
        <p>(5) Zahlungsmethoden: Revolut Checkout (Online-Zahlung) oder Banküberweisung:<br/>IBAN: NL66 REVO 3601 4304 36<br/>BIC: REVONL22<br/>Für Zahlungen von außerhalb des EWR — BIC der zwischengeschalteten Bank: CHASDEFX.</p>
        <p>(6) Bei Zahlungsverzug gelten die gesetzlichen Verzugszinsen: Für Unternehmer: Art. 6:119a BW (Handelsgeschäfte, aktuell 12,5 %). Für Verbraucher: Art. 6:119 BW. Mahngebühren werden gemäß dem Besluit vergoeding voor buitengerechtelijke incassokosten erhoben.</p>
        <p>(7) Aufrechnungsrechte und Zurückbehaltungsrechte des Auftraggebers bestehen nur, soweit die Gegenforderung rechtskräftig festgestellt, unbestritten oder vom Anbieter anerkannt ist.</p>
      </section>

      <section>
        <h2>§ 6 Mitwirkungspflichten des Auftraggebers</h2>
        <p>(1) Der Auftraggeber stellt dem Anbieter rechtzeitig alle für die Leistungserbringung erforderlichen Informationen, Unterlagen, Zugangsdaten und Ansprechpartner zur Verfügung.</p>
        <p>(2) Der Auftraggeber benennt einen verantwortlichen Projektleiter als primären Ansprechpartner.</p>
        <p>(3) Feedback und Freigaben sind innerhalb von 5 Werktagen zu erteilen, sofern keine andere Frist vereinbart ist.</p>
        <p>(4) Verzögerungen, die auf fehlende oder verspätete Mitwirkung des Auftraggebers zurückzuführen sind, befreien den Anbieter von der Einhaltung vereinbarter Termine. Mehraufwand wird nach Aufwand berechnet.</p>
      </section>

      <section>
        <h2>§ 7 Abnahme</h2>
        <p>(1) Der Auftraggeber ist verpflichtet, die vertragsgemäß erbrachten Leistungen innerhalb von 10 Werktagen nach Bereitstellung abzunehmen.</p>
        <p>(2) Die Abnahme gilt als erteilt, wenn der Auftraggeber nicht innerhalb der Frist begründete Mängel schriftlich rügt (Art. 7:758 Abs. 3 BW).</p>
        <p>(3) Unwesentliche Mängel berechtigen nicht zur Verweigerung der Abnahme.</p>
      </section>

      <section>
        <h2>§ 8 Gewährleistung und Mängelhaftung</h2>
        <p>(1) Der Anbieter gewährleistet, dass die Leistungen den vertraglich vereinbarten Spezifikationen entsprechen (Art. 7:17 BW).</p>
        <p>(2) Mängel sind unverzüglich, spätestens innerhalb von 14 Tagen nach Entdeckung, schriftlich zu melden (Art. 7:23 BW). Die Meldung muss den Mangel nachvollziehbar beschreiben.</p>
        <p>(3) Bei berechtigten Mängelrügen hat der Anbieter das Recht zur Nachbesserung oder Ersatzlieferung innerhalb einer angemessenen Frist (mindestens 30 Tage).</p>
        <p>(4) Die Gewährleistungsfrist beträgt 12 Monate ab Abnahme für Unternehmer und 24 Monate ab Abnahme für Verbraucher (Art. 7:23 BW, § 438 BGB).</p>
        <p>(5) Von der Gewährleistung ausgenommen sind Mängel, die verursacht werden durch: (a) unsachgemäße Nutzung durch den Auftraggeber, (b) Änderungen durch den Auftraggeber oder Dritte ohne Zustimmung, (c) von Dritten bereitgestellte Hard- oder Software, (d) höhere Gewalt.</p>
      </section>

      <section>
        <h2>§ 9 Haftung</h2>
        <p>(1) Der Anbieter haftet unbeschränkt für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit, die auf einer fahrlässigen oder vorsätzlichen Pflichtverletzung beruhen.</p>
        <p>(2) Für sonstige Schäden haftet der Anbieter nur bei Vorsatz und grober Fahrlässigkeit (Art. 6:74 BW). Die Gesamthaftung ist begrenzt auf den Netto-Auftragswert des betreffenden Einzelauftrags, maximal jedoch auf 100.000 EUR.</p>
        <p>(3) Indirekte Schäden, Folgeschäden, entgangener Gewinn und Datenverlust sind ausgeschlossen, soweit gesetzlich zulässig.</p>
        <p>(4) Die vorstehenden Haftungsbeschränkungen gelten nicht, soweit der Anbieter den Schaden arglistig verschwiegen hat oder eine Garantie für die Beschaffenheit der Sache übernommen hat.</p>
        <p>(5) Für Verbraucher gelten die zwingenden Haftungsvorschriften des jeweiligen Wohnsitzstaates ergänzend.</p>
      </section>

      <section>
        <h2>§ 10 Geistiges Eigentum und Nutzungsrechte</h2>
        <p>(1) Der Auftraggeber erhält nach vollständiger Bezahlung ein nicht-exklusives, nicht übertragbares, zeitlich unbefristetes Nutzungsrecht an den individuell für ihn erstellten Werkleistungen.</p>
        <p>(2) Der Anbieter behält sämtliche Rechte an generischen Komponenten, Frameworks, Bibliotheken, Templates und Methoden, die er bei der Leistungserbringung einsetzt oder weiterentwickelt. Dies umfasst insbesondere wiederverwendbare Codebausteine und KI-Trainingspipelines.</p>
        <p>(3) Open-Source-Komponenten unterliegen ihren jeweiligen Lizenzbestimmungen (MIT, Apache 2.0, etc.). Der Anbieter stellt sicher, dass keine Copyleft-Lizenzen (GPL) ohne vorherige Zustimmung des Auftraggebers eingesetzt werden.</p>
        <p>(4) Bis zur vollständigen Bezahlung verbleiben alle Nutzungsrechte beim Anbieter (Eigentumsvorbehalt gemäß Art. 3:92 BW).</p>
      </section>

      <section>
        <h2>§ 11 Vertraulichkeit</h2>
        <p>(1) Beide Parteien verpflichten sich, alle im Rahmen der Zusammenarbeit erlangten vertraulichen Informationen der jeweils anderen Partei streng vertraulich zu behandeln und nicht an Dritte weiterzugeben.</p>
        <p>(2) Diese Verpflichtung gilt auch nach Beendigung des Vertragsverhältnisses für einen Zeitraum von 3 Jahren.</p>
        <p>(3) Ausgenommen sind Informationen, die: (a) öffentlich bekannt sind oder werden, (b) dem Empfänger bereits vorher bekannt waren, (c) von einem Dritten rechtmäßig offengelegt werden, (d) auf richterliche oder behördliche Anordnung offengelegt werden müssen.</p>
      </section>

      <section>
        <h2>§ 12 Datenschutz</h2>
        <p>(1) Der Anbieter verarbeitet personenbezogene Daten des Auftraggebers gemäß der DSGVO, der UAVG und der Datenschutzerklärung des Anbieters.</p>
        <p>(2) Soweit der Anbieter im Auftrag des Auftraggebers personenbezogene Daten verarbeitet, wird ein Auftragsverarbeitungsvertrag (AVV) gemäß Art. 28 DSGVO geschlossen.</p>
        <p>(3) Beide Parteien verpflichten sich zur Einhaltung der datenschutzrechtlichen Bestimmungen und zur gegenseitigen Unterstützung bei der Erfüllung der Betroffenenrechte.</p>
      </section>

      <section>
        <h2>§ 13 Vertragslaufzeit und Kündigung</h2>
        <p>(1) KI-Agenten-Verträge haben eine feste Laufzeit von 24 Monaten. Eine ordentliche Kündigung während der Mindestlaufzeit ist ausgeschlossen. Nach Ablauf der Mindestlaufzeit verlängert sich der Vertrag um jeweils 12 Monate, sofern er nicht mit einer Frist von 3 Monaten zum Laufzeitende gekündigt wird.</p>
        <p>(2) Projektbasierte Verträge enden mit Abnahme der Leistung oder durch ordentliche Kündigung mit einer Frist von 30 Tagen zum Monatsende.</p>
        <p>(3) Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt (Art. 6:265 BW, § 314 BGB). Ein wichtiger Grund liegt insbesondere vor bei: (a) Zahlungsverzug von mehr als 30 Tagen trotz Mahnung, (b) Insolvenzantrag oder Zahlungsunfähigkeit einer Partei, (c) wesentlicher Vertragsverletzung trotz Nachfristsetzung.</p>
        <p>(4) Im Falle der vorzeitigen Kündigung durch den Auftraggeber ohne wichtigen Grund sind die bis zum regulären Vertragsende fälligen Vergütungen als Schadensersatz geschuldet, abzüglich ersparter Aufwendungen des Anbieters.</p>
      </section>

      <section>
        <h2>§ 14 Höhere Gewalt (Force Majeure)</h2>
        <p>(1) Keine Partei haftet für die Nichterfüllung oder verspätete Erfüllung ihrer Pflichten, soweit dies auf Umstände zurückzuführen ist, die außerhalb ihres angemessenen Einflussbereichs liegen (Art. 6:75 BW, „overmacht").</p>
        <p>(2) Hierzu zählen insbesondere: Naturkatastrophen, Pandemien, Krieg, Terrorismus, behördliche Anordnungen, Streiks, Stromausfälle, Ausfall von Telekommunikationsnetzen, Cyberangriffe und wesentliche Änderungen der gesetzlichen Rahmenbedingungen.</p>
        <p>(3) Die betroffene Partei informiert die andere Partei unverzüglich und unternimmt zumutbare Anstrengungen zur Minimierung der Auswirkungen.</p>
        <p>(4) Dauert die Behinderung länger als 90 Tage, kann jede Partei den Vertrag ohne Schadensersatzpflicht kündigen.</p>
      </section>

      <section>
        <h2>§ 15 Referenzklausel</h2>
        <p>(1) Der Anbieter ist berechtigt, den Auftraggeber als Referenzkunden zu nennen und das Projekt in anonymisierter oder allgemeiner Form in seinem Portfolio zu verwenden, sofern keine vertraulichen Geschäftsinformationen offengelegt werden.</p>
        <p>(2) Der Auftraggeber kann dieser Nutzung jederzeit schriftlich widersprechen.</p>
      </section>

      <section>
        <h2>§ 16 Compliance und Anti-Korruption</h2>
        <p>(1) Beide Parteien verpflichten sich zur Einhaltung aller anwendbaren Gesetze, insbesondere im Bereich Anti-Korruption (UK Bribery Act, US FCPA soweit anwendbar), Geldwäschebekämpfung, Exportkontrolle und Sanktionsrecht.</p>
        <p>(2) Keine Partei wird der anderen Partei oder deren Mitarbeitern, Beauftragten oder Vertretern unangemessene Vorteile gewähren oder annehmen.</p>
      </section>

      <section>
        <h2>§ 17 Verfügbarkeit und Service Level (SaaS)</h2>
        <p>(1) Für SaaS-basierte KI-Agenten strebt der Anbieter eine Verfügbarkeit von 99,5 % pro Kalendermonat an (gemessen ohne geplante Wartungsfenster).</p>
        <p>(2) Geplante Wartungsarbeiten werden mindestens 48 Stunden im Voraus angekündigt und nach Möglichkeit in die Nachtstunden (22:00–06:00 Uhr MEZ) gelegt.</p>
        <p>(3) Der Anbieter haftet nicht für Nichtverfügbarkeit, die durch Drittanbieter-Dienste (Cloud-Infrastruktur, LLM-APIs, Zahlungsdienstleister) verursacht wird.</p>
      </section>

      <section>
        <h2>§ 18 Änderungen der AGB</h2>
        <p>(1) Der Anbieter behält sich vor, diese AGB mit einer Ankündigungsfrist von 30 Tagen zu ändern (Art. 6:236 BW, Abs. j).</p>
        <p>(2) Änderungen werden dem Auftraggeber per E-Mail mitgeteilt. Widerspricht der Auftraggeber nicht innerhalb von 30 Tagen nach Zugang der Mitteilung, gelten die geänderten AGB als genehmigt.</p>
        <p>(3) Bei wesentlichen Änderungen, die den Auftraggeber erheblich benachteiligen, hat dieser ein Sonderkündigungsrecht zum Zeitpunkt des Inkrafttretens der Änderung.</p>
      </section>

      <section>
        <h2>§ 19 Schlussbestimmungen</h2>
        <p>(1) Es gilt niederländisches Recht unter Ausschluss des UN-Kaufrechts (CISG) und der Verweisungsnormen des IPR.</p>
        <p>(2) Gerichtsstand für alle Streitigkeiten aus und im Zusammenhang mit diesem Vertrag ist Rechtbank Limburg, Maastricht (Niederlande). Verbraucher können alternativ den Gerichtsstand ihres Wohnsitzes wählen (Art. 18 Brüssel-Ia-VO).</p>
        <p>(3) Sollten einzelne Bestimmungen dieser AGB unwirksam oder undurchführbar sein oder werden, wird die Wirksamkeit der übrigen Bestimmungen nicht berührt. Die unwirksame Bestimmung wird durch eine Regelung ersetzt, die dem wirtschaftlichen Zweck der unwirksamen Bestimmung am nächsten kommt (Art. 3:41 BW).</p>
        <p>(4) Nebenabreden, Änderungen und Ergänzungen dieses Vertrages bedürfen der Textform (Art. 6:227a BW; § 126b BGB).</p>
        <p>(5) Die Übertragung von Rechten und Pflichten aus diesem Vertrag bedarf der vorherigen schriftlichen Zustimmung der anderen Partei (Art. 6:159 BW). Der Anbieter ist berechtigt, Forderungen abzutreten.</p>
      </section>

      <p className="legal-date">Stand: April 2026</p>
    </>
  ),
  nl: () => (
    <>
      <p>van {CO.legal}, ingeschreven bij de Kamer van Koophandel onder nr. {CO.kvk}</p>
      <section><h2>§ 1 Toepassingsgebied</h2><p>(1) Deze algemene voorwaarden gelden voor alle zakelijke relaties tussen {CO.legal} en de opdrachtgever. (2) Nederlands recht is van toepassing (Boek 6 en 7 BW). Dwingende consumentenbeschermingsregels voor DACH-consumenten blijven onverlet (Art. 6 lid 2 Rome I).</p></section>
      <section><h2>§ 2 Onderwerp</h2><p>AI-agenten, procesautomatisering, CRM/ERP, softwareontwikkeling, kennissystemen, IT-advies, webontwikkeling, SEO. Omvang per individueel contract.</p></section>
      <section><h2>§ 3 Totstandkoming</h2><p>Offertes vrijblijvend. Overeenkomst door schriftelijke/elektronische bevestiging of digitale acceptatie via Magic Link (Art. 6:227a BW). Eerste adviesgesprek kosteloos.</p></section>
      <section><h2>§ 4 Uitvoering</h2><p>Zorgvuldigheid goed opdrachtnemer (Art. 7:401 BW). Remote tenzij anders overeengekomen. Termijnen indicatief (Art. 6:83 BW). Deelleveringen toegestaan. Onderaannemers toegestaan.</p></section>
      <section><h2>§ 5 Vergoeding en betaling</h2><p>(1) Prijzen excl. BTW (21% NL / 19% DE / 20% AT / 8,1% CH). (2) AI-contracten: 24 maanden, 30% activeringsvooruitbetaling, rest in 24 gelijke maandtermijnen. (3) Betaling via Revolut of bankoverschrijving (IBAN: NL66 REVO 3601 4304 36). (4) Betalingstermijn: 14 dagen. (5) Verzuimrente: Art. 6:119a BW.</p></section>
      <section><h2>§ 6 Medewerkingsplicht</h2><p>Opdrachtgever levert informatie, toegang en contactpersonen tijdig. Projectleider als aanspreekpunt. Feedback binnen 5 werkdagen.</p></section>
      <section><h2>§ 7 Oplevering</h2><p>Oplevering binnen 10 werkdagen. Stilzwijgende acceptatie bij uitblijven van gemotiveerde klacht (Art. 7:758 lid 3 BW).</p></section>
      <section><h2>§ 8 Garantie</h2><p>Conformiteit met specificaties (Art. 7:17 BW). Gebreken binnen 14 dagen melden (Art. 7:23 BW). Recht op herstel. Garantietermijn: 12 maanden (ondernemers) / 24 maanden (consumenten).</p></section>
      <section><h2>§ 9 Aansprakelijkheid</h2><p>Onbeperkt bij opzet/grove schuld en letsel. Overigens beperkt tot netto opdrachtwaarde, max. 100.000 EUR. Indirecte schade uitgesloten.</p></section>
      <section><h2>§ 10 IE-rechten</h2><p>Niet-exclusief gebruiksrecht na volledige betaling. Opdrachtnemer behoudt generieke componenten. Eigendomsvoorbehoud (Art. 3:92 BW).</p></section>
      <section><h2>§ 11 Geheimhouding</h2><p>Wederzijdse geheimhouding, 3 jaar na beëindiging.</p></section>
      <section><h2>§ 12 Privacy</h2><p>AVG/UAVG-conform. Verwerkersovereenkomst bij opdracht (Art. 28 AVG).</p></section>
      <section><h2>§ 13 Looptijd en opzegging</h2><p>AI-contracten: 24 maanden vast, daarna 12 maanden stilzwijgend, 3 maanden opzegtermijn. Projecten: 30 dagen opzegtermijn. Buitengewone opzegging bij gewichtige reden (Art. 6:265 BW).</p></section>
      <section><h2>§ 14 Overmacht</h2><p>Geen aansprakelijkheid bij overmacht (Art. 6:75 BW). Na 90 dagen ontbindingsrecht.</p></section>
      <section><h2>§ 15-16 Referenties en Compliance</h2><p>Referentiegebruik met bezwaarmogelijkheid. Anti-corruptie en sanctienaleving.</p></section>
      <section><h2>§ 17 SLA (SaaS)</h2><p>99,5% beschikbaarheid per maand. Gepland onderhoud 48 uur vooraf aangekondigd.</p></section>
      <section><h2>§ 18-19 Wijzigingen en Slotbepalingen</h2><p>Wijzigingen met 30 dagen aankondiging. Nederlands recht, uitsluiting CISG. Bevoegde rechter: Rechtbank Limburg. Partiële nietigheid (Art. 3:41 BW). Schriftelijkheidsvereiste (Art. 6:227a BW).</p></section>
      <p className="legal-date">Status: april 2026</p>
    </>
  ),
  en: () => (
    <>
      <p>of {CO.legal}, registered with the Chamber of Commerce under no. {CO.kvk}</p>
      <section><h2>§ 1 Scope</h2><p>(1) These GTC apply to all business relationships between {CO.legal} and the client. (2) Dutch law applies (Books 6 and 7 BW). Mandatory consumer protection rules for DACH consumers remain unaffected (Art. 6(2) Rome I).</p></section>
      <section><h2>§ 2 Subject Matter</h2><p>AI agents, process automation, CRM/ERP integration, software development, knowledge systems, IT consulting, web development, SEO. Scope per individual contract.</p></section>
      <section><h2>§ 3 Contract Formation</h2><p>Offers non-binding. Contract through written/electronic confirmation or digital acceptance via Magic Link (Art. 6:227a BW). Initial consultation free.</p></section>
      <section><h2>§ 4 Service Delivery</h2><p>Care of proper contractor (Art. 7:401 BW). Remote unless agreed otherwise. Timelines indicative (Art. 6:83 BW). Partial deliveries and subcontractors permitted.</p></section>
      <section><h2>§ 5 Compensation and Payment</h2><p>(1) Prices net plus VAT (21% NL / 19% DE / 20% AT / 8.1% CH). (2) AI contracts: 24 months, 30% activation deposit, remainder in 24 equal monthly installments. (3) Payment via Revolut or bank transfer (IBAN: NL66 REVO 3601 4304 36). (4) Payment term: 14 days. (5) Late interest: Art. 6:119a BW.</p></section>
      <section><h2>§ 6 Client Obligations</h2><p>Timely provision of information, access, and contacts. Project manager as primary contact. Feedback within 5 business days.</p></section>
      <section><h2>§ 7 Acceptance</h2><p>Within 10 business days. Deemed accepted if no justified defects reported in writing (Art. 7:758(3) BW).</p></section>
      <section><h2>§ 8 Warranty</h2><p>Conformity with specifications (Art. 7:17 BW). Defects within 14 days (Art. 7:23 BW). Right to remedy. Warranty: 12 months (business) / 24 months (consumers).</p></section>
      <section><h2>§ 9 Liability</h2><p>Unlimited for intent/gross negligence and personal injury. Otherwise limited to net order value, max 100,000 EUR. Indirect damages excluded.</p></section>
      <section><h2>§ 10 IP Rights</h2><p>Non-exclusive license upon full payment. Provider retains generic components. Retention of title (Art. 3:92 BW).</p></section>
      <section><h2>§ 11 Confidentiality</h2><p>Mutual confidentiality, 3 years post-termination.</p></section>
      <section><h2>§ 12 Data Protection</h2><p>GDPR/UAVG compliant. DPA per Art. 28 GDPR as needed.</p></section>
      <section><h2>§ 13 Term and Termination</h2><p>AI contracts: 24 months fixed, then 12 months auto-renewal, 3 months notice. Projects: 30 days notice. Extraordinary termination for cause (Art. 6:265 BW).</p></section>
      <section><h2>§ 14 Force Majeure</h2><p>No liability for force majeure (Art. 6:75 BW). Termination right after 90 days.</p></section>
      <section><h2>§ 15-19 Final Provisions</h2><p>Reference clause with objection right. Anti-corruption compliance. SaaS SLA 99.5%. Changes with 30 days notice. Dutch law, CISG excluded. Jurisdiction: Rechtbank Limburg. Severability (Art. 3:41 BW). Text form required (Art. 6:227a BW).</p></section>
      <p className="legal-date">Last updated: April 2026</p>
    </>
  )
};

/* ═══════════════════════════════════════════════════════════
   KI-HINWEISE / AI TRANSPARENCY
   ═══════════════════════════════════════════════════════════ */
const KIContent = {
  de: () => (
    <>
      <p>gemäß Verordnung (EU) 2024/1689 (KI-Verordnung / EU AI Act), Art. 50 (Transparenzpflichten)</p>
      <section><h2>§ 1 Einsatz von KI-Systemen</h2><p>{CO.legal} setzt KI-gestützte Systeme als Bestandteil seiner Dienstleistungen ein. Diese Seite informiert Sie gemäß Art. 50 der KI-Verordnung (EU) 2024/1689 über den Einsatz, die Grenzen und Ihre Rechte.</p></section>
      <section><h2>§ 2 KI-Systeme auf dieser Website</h2>
        <h3>2.1 NeXifyAI Advisor (Live-Chat)</h3>
        <p><strong>Technologie:</strong> KI-Dialogsystem basierend auf Large Language Models (OpenAI GPT). API-Zugriff mit Zero Data Retention Policy — Ihre Eingaben werden nicht zum Training der KI-Modelle verwendet.</p>
        <p><strong>Funktionen:</strong> Automatisierte Erstberatung, Informationsbereitstellung über Dienstleistungen, Terminbuchung, Lead-Qualifizierung.</p>
        <p><strong>Grenzen:</strong> Der KI-Chat kann keine rechtsverbindlichen Zusagen, Preisgarantien oder verbindlichen Beratungen geben. KI-Modelle können halluzinieren (faktisch falsche Aussagen generieren). Der Chat ersetzt keine professionelle Fach-, Rechts- oder Steuerberatung.</p>
        <p><strong>Risikoklasse:</strong> Minimales Risiko gemäß Art. 6 Abs. 2 KI-Verordnung. Das System fällt nicht unter die Hochrisiko-KI-Systeme des Anhangs III.</p>
        <h3>2.2 Interne KI-Werkzeuge</h3>
        <p>Der Anbieter setzt intern KI-gestützte Werkzeuge für Textgenerierung, Datenanalyse und Prozessoptimierung ein. Diese Werkzeuge verarbeiten keine personenbezogenen Daten der Endnutzer ohne entsprechende Rechtsgrundlage.</p>
      </section>
      <section><h2>§ 3 Transparenz und Kennzeichnung</h2>
        <ul>
          <li>Alle KI-Interaktionen auf dieser Website sind als solche gekennzeichnet (Art. 50 Abs. 1 KI-Verordnung).</li>
          <li>KI-generierte Inhalte werden nicht als menschliche Äußerungen dargestellt.</li>
          <li>Human-in-the-Loop: Bei kritischen Geschäftsentscheidungen (Vertragsabschlüsse, Preisfestsetzung, Rechtsberatung) erfolgt stets eine menschliche Überprüfung und Freigabe.</li>
          <li>Audit-Trail: Alle KI-Interaktionen werden protokolliert (Art. 12 KI-Verordnung).</li>
        </ul>
      </section>
      <section><h2>§ 4 Ihre Rechte</h2>
        <ul>
          <li><strong>Recht auf menschliche Bearbeitung:</strong> Sie können jederzeit verlangen, dass Ihr Anliegen von einem menschlichen Mitarbeiter bearbeitet wird.</li>
          <li><strong>Recht auf Erklärung:</strong> Sie können eine Erklärung über die Funktionsweise der eingesetzten KI-Systeme verlangen.</li>
          <li><strong>Keine automatisierte Entscheidungsfindung:</strong> Es werden keine ausschließlich auf automatisierter Verarbeitung beruhenden Entscheidungen getroffen, die Ihnen gegenüber rechtliche Wirkung entfalten (Art. 22 DSGVO).</li>
        </ul>
      </section>
      <section><h2>§ 5 Verbotene Praktiken (Art. 5 KI-Verordnung)</h2>
        <p>Der Anbieter bestätigt, dass folgende Praktiken weder eingesetzt werden noch eingesetzt werden:</p>
        <ul>
          <li>Keine manipulativen oder täuschenden Techniken (Art. 5 Abs. 1 lit. a)</li>
          <li>Keine Ausnutzung von Schwächen (Art. 5 Abs. 1 lit. b)</li>
          <li>Kein Social Scoring (Art. 5 Abs. 1 lit. c)</li>
          <li>Keine biometrische Echtzeit-Identifikation (Art. 5 Abs. 1 lit. d)</li>
          <li>Keine Emotionserkennung am Arbeitsplatz oder in Bildungseinrichtungen (Art. 5 Abs. 1 lit. f)</li>
        </ul>
      </section>
      <section><h2>§ 6 Datenverarbeitung durch KI</h2>
        <p><strong>Keine Verwendung für KI-Training:</strong> Ihre Daten werden zu keinem Zeitpunkt zum Training oder Fine-Tuning von KI-Modellen verwendet.</p>
        <p><strong>Isolierte Verarbeitung:</strong> KI-Anfragen werden in isolierten, zustandslosen API-Aufrufen verarbeitet (kein Kontextübertrag zwischen verschiedenen Nutzersessions).</p>
        <p><strong>Zero Data Retention:</strong> OpenAI speichert keine Eingabe- oder Ausgabedaten bei API-Aufrufen mit aktivierter ZDR-Policy.</p>
        <p>Weiterführende Informationen zur Datenverarbeitung finden Sie in unserer <a href="/de/datenschutz">Datenschutzerklärung</a>.</p>
      </section>
      <section><h2>§ 7 Kontakt</h2><p>{CO.legal}<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a><br/>Telefon: {CO.phone}</p></section>
      <p className="legal-date">Stand: April 2026</p>
    </>
  ),
  nl: () => (
    <>
      <p>conform Verordening (EU) 2024/1689 (AI-verordening / EU AI Act), Art. 50</p>
      <section><h2>§ 1 Gebruik van AI</h2><p>{CO.legal} maakt gebruik van AI-systemen. Informatieverplichting conform Art. 50 AI-verordening.</p></section>
      <section><h2>§ 2 AI op deze website</h2><h3>2.1 NeXifyAI Advisor</h3><p>LLM-dialoogsysteem (OpenAI GPT). Zero Data Retention. Eerste advies, afspraken, leadkwalificatie.</p><p><strong>Beperkingen:</strong> Geen bindende toezeggingen, kan hallucineren, vervangt geen vakadvies. Risicoklasse: minimaal (Art. 6 lid 2).</p></section>
      <section><h2>§ 3 Transparantie</h2><ul><li>Alle AI-interacties gemarkeerd (Art. 50 lid 1).</li><li>Human-in-the-loop bij kritieke beslissingen.</li><li>Audittrail (Art. 12).</li></ul></section>
      <section><h2>§ 4 Uw rechten</h2><ul><li>Recht op menselijke verwerking.</li><li>Recht op uitleg.</li><li>Geen geautomatiseerde besluitvorming (Art. 22 AVG).</li></ul></section>
      <section><h2>§ 5 Verboden praktijken (Art. 5)</h2><p>Geen manipulatie, geen social scoring, geen biometrische identificatie, geen emotieherkenning.</p></section>
      <section><h2>§ 6 Gegevensverwerking</h2><p>Geen gebruik voor AI-training. Geïsoleerde verwerking. Zero Data Retention bij OpenAI.</p></section>
      <section><h2>§ 7 Contact</h2><p>{CO.legal}<br/>E-mail: <a href={`mailto:${CO.email}`}>{CO.email}</a></p></section>
      <p className="legal-date">Status: april 2026</p>
    </>
  ),
  en: () => (
    <>
      <p>pursuant to Regulation (EU) 2024/1689 (AI Act), Art. 50</p>
      <section><h2>§ 1 Use of AI</h2><p>{CO.legal} employs AI systems. This page informs you per Art. 50 AI Act.</p></section>
      <section><h2>§ 2 AI on this website</h2><h3>2.1 NeXifyAI Advisor</h3><p>LLM dialogue system (OpenAI GPT). Zero Data Retention. Initial consultation, bookings, lead qualification.</p><p><strong>Limitations:</strong> No binding commitments, may hallucinate, not professional advice. Risk class: minimal (Art. 6(2)).</p></section>
      <section><h2>§ 3 Transparency</h2><ul><li>All AI interactions labeled (Art. 50(1)).</li><li>Human-in-the-loop for critical decisions.</li><li>Audit trail (Art. 12).</li></ul></section>
      <section><h2>§ 4 Your Rights</h2><ul><li>Right to human processing.</li><li>Right to explanation.</li><li>No automated decision-making (Art. 22 GDPR).</li></ul></section>
      <section><h2>§ 5 Prohibited Practices (Art. 5)</h2><p>No manipulation, no social scoring, no biometric identification, no emotion recognition.</p></section>
      <section><h2>§ 6 Data Processing</h2><p>No use for AI training. Isolated processing. Zero Data Retention with OpenAI.</p></section>
      <section><h2>§ 7 Contact</h2><p>{CO.legal}<br/>Email: <a href={`mailto:${CO.email}`}>{CO.email}</a></p></section>
      <p className="legal-date">Last updated: April 2026</p>
    </>
  )
};

/* ═══════════════════════════════════════════════════════════
   WIDERRUFSBELEHRUNG
   ═══════════════════════════════════════════════════════════ */
const WiderrufContent = {
  de: () => (
    <>
      <p>gemäß Art. 6:230o Burgerlijk Wetboek (BW), §§ 312g, 355 BGB, § 11 FAGG (Österreich) und Art. 40 OR (Schweiz, soweit anwendbar)</p>
      <section>
        <h2>§ 1 Widerrufsrecht für Verbraucher</h2>
        <p>Wenn Sie als Verbraucher (Art. 6:230g BW; § 13 BGB) einen Vertrag über Dienstleistungen im Fernabsatz mit {CO.legal} geschlossen haben, steht Ihnen ein gesetzliches Widerrufsrecht zu.</p>
        <p><strong>Widerrufsfrist:</strong> Sie können Ihre Vertragserklärung innerhalb von 14 Tagen ohne Angabe von Gründen widerrufen. Die Frist beginnt am Tag des Vertragsschlusses (Art. 6:230o Abs. 1 BW; § 355 Abs. 2 BGB; § 11 FAGG).</p>
      </section>
      <section>
        <h2>§ 2 Ausübung des Widerrufs</h2>
        <p>Um Ihr Widerrufsrecht auszuüben, müssen Sie uns mittels einer eindeutigen Erklärung (z. B. per E-Mail oder Post) über Ihren Entschluss, diesen Vertrag zu widerrufen, informieren.</p>
        <p>{CO.legal}<br/>{CO.nl}<br/>E-Mail: <a href={`mailto:${CO.email}`}>{CO.email}</a></p>
        <p>Zur Wahrung der Widerrufsfrist reicht es aus, dass Sie die Mitteilung über die Ausübung des Widerrufsrechts vor Ablauf der Widerrufsfrist absenden.</p>
      </section>
      <section>
        <h2>§ 3 Folgen des Widerrufs</h2>
        <p>Wenn Sie diesen Vertrag widerrufen, haben wir Ihnen alle Zahlungen, die wir von Ihnen erhalten haben, einschließlich der Lieferkosten, unverzüglich und spätestens binnen 14 Tagen ab dem Tag zurückzuzahlen, an dem die Mitteilung über Ihren Widerruf bei uns eingegangen ist. Für diese Rückzahlung verwenden wir dasselbe Zahlungsmittel, das Sie bei der ursprünglichen Transaktion eingesetzt haben, es sei denn, mit Ihnen wurde ausdrücklich etwas anderes vereinbart.</p>
        <p>Haben Sie verlangt, dass die Dienstleistungen während der Widerrufsfrist beginnen sollen, so haben Sie uns einen angemessenen Betrag zu zahlen, der dem Anteil der bis zu dem Zeitpunkt, zu dem Sie uns von der Ausübung des Widerrufsrechts unterrichten, bereits erbrachten Dienstleistungen im Vergleich zum Gesamtumfang der im Vertrag vorgesehenen Dienstleistungen entspricht (Art. 6:230s BW; § 357 Abs. 8 BGB).</p>
      </section>
      <section>
        <h2>§ 4 Ausschluss und vorzeitiges Erlöschen des Widerrufsrechts</h2>
        <p>Das Widerrufsrecht erlischt vorzeitig, wenn:</p>
        <ul>
          <li>Der Anbieter die Dienstleistung vollständig erbracht hat und mit der Ausführung der Dienstleistung erst begonnen hat, nachdem der Verbraucher dazu seine ausdrückliche Zustimmung gegeben hat und gleichzeitig seine Kenntnis davon bestätigt hat, dass er sein Widerrufsrecht bei vollständiger Vertragserfüllung verliert (Art. 6:230p Abs. 1 lit. a BW; § 356 Abs. 4 BGB).</li>
          <li>Maßgeschneiderte digitale Inhalte geliefert wurden, die nicht vorgefertigt sind und deren Herstellung eine individuelle Auswahl oder Entscheidung des Verbrauchers voraussetzt.</li>
        </ul>
      </section>
      <section>
        <h2>§ 5 Kein Widerrufsrecht für Unternehmer (B2B)</h2>
        <p>Das gesetzliche Widerrufsrecht besteht ausschließlich für Verbraucher. Unternehmer im Sinne des Art. 7:5 BW / § 14 BGB haben kein gesetzliches Widerrufsrecht. Für Unternehmer gelten die Kündigungsregelungen in § 13 der AGB.</p>
      </section>
      <section>
        <h2>§ 6 Muster-Widerrufsformular</h2>
        <p>(Wenn Sie den Vertrag widerrufen wollen, füllen Sie bitte dieses Formular aus und senden Sie es zurück.)</p>
        <div style={{background:'rgba(14,20,28,0.5)',border:'1px solid rgba(255,255,255,0.06)',borderRadius:8,padding:'16px 20px',margin:'12px 0',fontSize:'.8125rem',lineHeight:1.7}}>
          <p>An: {CO.legal}, {CO.nl}<br/>E-Mail: {CO.email}</p>
          <p>Hiermit widerrufe(n) ich/wir (*) den von mir/uns (*) abgeschlossenen Vertrag über die Erbringung der folgenden Dienstleistung: _______________</p>
          <p>Bestellt am (*) / erhalten am (*): _______________</p>
          <p>Name des/der Verbraucher(s): _______________</p>
          <p>Anschrift des/der Verbraucher(s): _______________</p>
          <p>Unterschrift des/der Verbraucher(s) (nur bei Mitteilung auf Papier): _______________</p>
          <p>Datum: _______________</p>
          <p style={{fontSize:'.6875rem',color:'#6b7b8d'}}>(*) Unzutreffendes streichen.</p>
        </div>
      </section>
      <p className="legal-date">Stand: April 2026</p>
    </>
  ),
  nl: () => (
    <>
      <p>conform Art. 6:230o Burgerlijk Wetboek (BW)</p>
      <section><h2>§ 1 Herroepingsrecht</h2><p>Als consument (Art. 6:230g BW) kunt u binnen 14 dagen na contractsluiting zonder opgaaf van redenen herroepen.</p></section>
      <section><h2>§ 2 Uitoefening</h2><p>Stuur een ondubbelzinnige verklaring naar {CO.legal}, {CO.nl}, e-mail: <a href={`mailto:${CO.email}`}>{CO.email}</a>.</p></section>
      <section><h2>§ 3 Gevolgen</h2><p>Terugbetaling binnen 14 dagen via hetzelfde betaalmiddel. Bij reeds gestart werk: proportionele vergoeding (Art. 6:230s BW).</p></section>
      <section><h2>§ 4 Uitzonderingen</h2><p>Herroepingsrecht vervalt bij: volledig uitgevoerde dienst met uitdrukkelijke toestemming (Art. 6:230p lid 1 sub a BW), maatwerk digitale inhoud.</p></section>
      <section><h2>§ 5 B2B</h2><p>Ondernemers (Art. 7:5 BW) hebben geen wettelijk herroepingsrecht.</p></section>
      <p className="legal-date">Status: april 2026</p>
    </>
  ),
  en: () => (
    <>
      <p>pursuant to Art. 6:230o Dutch Civil Code (BW), §§ 312g, 355 German Civil Code (BGB)</p>
      <section><h2>§ 1 Right of Withdrawal</h2><p>Consumers (Art. 6:230g BW; § 13 BGB) may withdraw within 14 days of contract conclusion without reason.</p></section>
      <section><h2>§ 2 Exercise</h2><p>Send a clear declaration to {CO.legal}, {CO.nl}, email: <a href={`mailto:${CO.email}`}>{CO.email}</a>.</p></section>
      <section><h2>§ 3 Consequences</h2><p>Refund within 14 days via same payment method. For services already started: proportionate payment (Art. 6:230s BW; § 357(8) BGB).</p></section>
      <section><h2>§ 4 Exceptions</h2><p>Right of withdrawal expires: fully performed service with express consent (Art. 6:230p(1)(a) BW), custom digital content.</p></section>
      <section><h2>§ 5 B2B</h2><p>Businesses have no statutory right of withdrawal. See § 13 GTC for termination.</p></section>
      <p className="legal-date">Last updated: April 2026</p>
    </>
  )
};

/* ═══════════════════════════════════════════════════════════
   COOKIE-RICHTLINIE
   ═══════════════════════════════════════════════════════════ */
const CookieContent = {
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
