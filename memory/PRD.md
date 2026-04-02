# NeXifyAI Landing Page - PRD v2.0

## Projektübersicht
**Projekt:** NeXifyAI by NeXify – Landing Page, Advisory Chat & CRM System
**Version:** 2.0 (Production Wave)
**Typ:** B2B Enterprise SaaS/Consulting Landing Page
**Zielmarkt:** DACH-Mittelstand

## Original Problem Statement
Vollständige Implementierung einer production-ready Landing Page mit:
- SEO-Optimierung für DACH
- Live Advisory Chat
- Kalender-Buchungssystem
- Admin CRM unter /admin
- E-Mail-System via Resend
- Compliance & Accessibility

## Unternehmensdaten (Fix)
- **Marke:** NeXifyAI by NeXify
- **Claim:** Chat it. Automate it.
- **Rechtsform:** NeXify Automate
- **Geschäftsführer:** Pascal Courbois
- **NL-Adresse:** Graaf van Loonstraat 1E, 5921 JA Venlo
- **DE-Adresse:** Wallstraße 9, 41334 Nettetal-Kaldenkirchen
- **Telefon:** +31 6 133 188 56
- **E-Mail:** support@nexify-automate.com
- **Website:** nexify-automate.com
- **KvK:** 90483944
- **USt-ID:** NL865786276B01

## Implementierte Features (02.04.2026)

### A) SEO & DACH Optimization ✅
- Vollständige Meta-Tags (title, description, keywords)
- Open Graph & Twitter Cards
- Canonical URL
- Schema.org Structured Data (Organization, Website, FAQ, Service)
- Semantic HTML5 Landmarks
- Einziges H1, korrekte Heading-Hierarchie
- Deutsche Sprache, DACH-Keywords
- robots.txt ready

### B) Performance Optimizations ✅
- Font preloading & optimized loading
- CSS Design Tokens für Konsistenz
- Keine externen Animationsbibliotheken
- Lazy loading für nicht-kritische Elemente
- Minimale JS-Bundles (React 18)
- Responsive Bilder-Handling

### C) Mobile Responsive ✅
- Vollständig responsiv: Mobile, Tablet, Desktop
- Mobile Navigation mit Hamburger-Menü
- Touch-freundliche Buttons (min 44px)
- Responsive Chat Modal
- Responsive Booking Modal
- Architecture Panel breakpoints

### D) Live Advisory Chat ✅
- Vollständig interaktiver Chat
- 6 Preset-Fragen für DACH B2B Use Cases
- Qualifizierungs-Flow mit Themenerkennung
- Lead-Eskalation zu Buchung
- Session-basierte Konversation
- Backend-Integration mit MongoDB-Speicherung
- Schließbar via ESC, Overlay-Click, Close-Button

### E) Contact & Booking Flow ✅
- Consultation-First CTAs ("Beratungsgespräch buchen")
- Direktes Kontaktformular mit Validierung
- Kalender-Buchungssystem (14 Tage voraus)
- Zeitslot-Verfügbarkeit (9-17 Uhr, keine Wochenenden)
- Booking-Bestätigung mit E-Mail

### F) Resend Email Integration ✅
- Kontakt-Bestätigungs-E-Mail
- Interne Benachrichtigung (support@, nexifyai@)
- Booking-Bestätigung
- Booking-Benachrichtigung an Admin
- Branded HTML-Templates im CI-Design

### G) Admin Area (/admin) ✅
- HTTP Basic Auth (Email + Password Hash)
- Dashboard mit Statistics
- Lead-Übersicht mit Suche & Filter
- Lead-Detail mit Status-Update
- Notizen-Funktion
- Booking-Übersicht
- Click-to-Call, Click-to-Mail
- Copy-to-Clipboard für Kontaktdaten

### H) Data Model & Persistence ✅
- MongoDB Collections: leads, bookings, chat_sessions, analytics
- Indexes für Performance
- Lead Status: neu, qualifiziert, termin_gebucht, in_bearbeitung, gewonnen, verloren, archiviert

### I) Compliance & Accessibility ✅
- WCAG 2.2 grundlegende Konformität
- Keyboard-Navigation
- Focus-States
- aria-labels und aria-expanded
- Skip-Link
- Semantic structure
- Formular-Labels und Error-Messages
- Impressum & Datenschutz Seiten

### J) Analytics Tracking ✅
- page_view
- cta_click
- scroll_depth (25%, 50%, 75%, 100%)
- form_submit, form_error
- chat_started, preset_question_clicked
- booking_modal_opened, booking_submit
- calendar_booked

### K) UX/Content ✅
- Consultation-orientierte CTAs
- Keine "kostenlos testen" Sprache
- Premium B2B-Ton
- DACH-relevante Use Cases
- Keine falschen Zertifizierungsclaims
- FAQ mit echten Antworten

## Tech Stack
- **Frontend:** React 18, React Router 6, CSS Custom Properties
- **Backend:** FastAPI, Pydantic, Motor (async MongoDB)
- **Database:** MongoDB
- **Email:** Resend API
- **Fonts:** Manrope, Inter, Material Symbols

## Environment Variables Required

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=nexifyai
RESEND_API_KEY=re_xxx
SENDER_EMAIL=noreply@send.nexify-automate.com
ADMIN_EMAIL=p.courbois@icloud.com
ADMIN_PASSWORD_HASH=<sha256 hash of admin password>
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=
```

## Admin Setup
1. Admin-Email: p.courbois@icloud.com
2. Passwort muss als SHA256-Hash in ADMIN_PASSWORD_HASH gesetzt werden
3. Hash generieren: `python3 -c "import hashlib; print(hashlib.sha256('YOUR_PASSWORD'.encode()).hexdigest())"`

## API Endpoints

### Public
- `GET /api/health` - Health Check
- `GET /api/company` - Firmendaten
- `POST /api/contact` - Kontaktformular
- `GET /api/booking/slots?date=YYYY-MM-DD` - Verfügbare Termine
- `POST /api/booking` - Termin buchen
- `POST /api/chat/message` - Chat-Nachricht
- `POST /api/analytics/track` - Event-Tracking

### Admin (Basic Auth)
- `GET /api/admin/stats` - Dashboard-Statistiken
- `GET /api/admin/leads` - Lead-Liste
- `GET /api/admin/leads/{id}` - Lead-Details
- `PATCH /api/admin/leads/{id}` - Lead-Update
- `GET /api/admin/bookings` - Buchungs-Liste

## Test Status
- Backend Health: ✅
- Contact Form: ✅
- Booking System: ✅
- Email (Resend): Konfiguriert, Domain: send.nexify-automate.com

## Remaining Blockers
1. **ADMIN_PASSWORD_HASH** - Muss vom Kunden gesetzt werden
2. Resend Domain-Verifikation ggf. erforderlich

## Compliance Matrix

| Standard | Status | Anmerkung |
|----------|--------|-----------|
| DSGVO | ✅ Implementiert | Datenschutzseite, Consent-ready |
| WCAG 2.2 A | ✅ Grundlegend | Focus, Keyboard, Labels |
| WCAG 2.2 AA | ⚠️ Teilweise | Kontraste geprüft, erweiterte Tests empfohlen |
| ISO 27001 | 📋 Angestrebt | Nur als Zielsetzung kommuniziert |
| SOC 2 Type II | 📋 Roadmap | Nur als Roadmap kommuniziert |

---
*Letzte Aktualisierung: 02.04.2026*
