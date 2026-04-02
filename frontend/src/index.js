import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import App from './App';
import Admin from './pages/Admin';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/impressum" element={<Impressum />} />
        <Route path="/datenschutz" element={<Datenschutz />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);

// Legal Pages
function Impressum() {
  return (
    <div className="legal-page">
      <nav className="legal-nav">
        <a href="/" className="legal-back">← Zurück zur Startseite</a>
      </nav>
      <main className="legal-content">
        <h1>Impressum</h1>
        <section>
          <h2>Angaben gemäß § 5 TMG / Art. 5 E-Commerce-Gesetz</h2>
          <p><strong>NeXify Automate</strong></p>
          <p>Graaf van Loonstraat 1E<br/>5921 JA Venlo<br/>Niederlande</p>
          <p>Wallstraße 9<br/>41334 Nettetal-Kaldenkirchen<br/>Deutschland</p>
        </section>
        <section>
          <h2>Vertreten durch</h2>
          <p>Pascal Courbois, Geschäftsführer</p>
        </section>
        <section>
          <h2>Kontakt</h2>
          <p>Telefon: +31 6 133 188 56<br/>E-Mail: support@nexify-automate.com</p>
        </section>
        <section>
          <h2>Registereintrag</h2>
          <p>Kamer van Koophandel (KvK): 90483944<br/>USt-IdNr.: NL865786276B01</p>
        </section>
        <section>
          <h2>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
          <p>Pascal Courbois<br/>Graaf van Loonstraat 1E<br/>5921 JA Venlo, Niederlande</p>
        </section>
        <section>
          <h2>EU-Streitschlichtung</h2>
          <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a></p>
          <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
        </section>
      </main>
    </div>
  );
}

function Datenschutz() {
  return (
    <div className="legal-page">
      <nav className="legal-nav">
        <a href="/" className="legal-back">← Zurück zur Startseite</a>
      </nav>
      <main className="legal-content">
        <h1>Datenschutzerklärung</h1>
        <section>
          <h2>1. Verantwortlicher</h2>
          <p>Verantwortlich für die Datenverarbeitung auf dieser Website ist:</p>
          <p>NeXify Automate<br/>Pascal Courbois<br/>Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande<br/>E-Mail: support@nexify-automate.com</p>
        </section>
        <section>
          <h2>2. Erhebung und Speicherung personenbezogener Daten</h2>
          <p>Wenn Sie uns per Kontaktformular Anfragen zukommen lassen, werden Ihre Angaben (Name, E-Mail, Nachricht) zwecks Bearbeitung der Anfrage und für den Fall von Anschlussfragen bei uns gespeichert.</p>
        </section>
        <section>
          <h2>3. Ihre Rechte</h2>
          <p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch. Kontaktieren Sie uns unter support@nexify-automate.com.</p>
        </section>
        <section>
          <h2>4. Cookies</h2>
          <p>Diese Website verwendet technisch notwendige Session-Cookies. Es werden keine Tracking-Cookies ohne Ihre Einwilligung gesetzt.</p>
        </section>
        <section>
          <h2>5. Hosting</h2>
          <p>Unsere Website wird in Rechenzentren in Deutschland/EU gehostet. Eine Übermittlung in Drittländer findet nicht statt.</p>
        </section>
        <section>
          <h2>6. SSL-Verschlüsselung</h2>
          <p>Diese Seite nutzt aus Sicherheitsgründen SSL-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie an "https://" in der Adresszeile.</p>
        </section>
        <section>
          <h2>7. Änderungen</h2>
          <p>Wir behalten uns vor, diese Datenschutzerklärung anzupassen, damit sie stets den aktuellen rechtlichen Anforderungen entspricht.</p>
        </section>
        <p className="legal-date">Stand: April 2026</p>
      </main>
    </div>
  );
}
