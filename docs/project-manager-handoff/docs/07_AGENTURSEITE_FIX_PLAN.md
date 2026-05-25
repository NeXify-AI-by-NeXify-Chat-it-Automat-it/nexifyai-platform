# 07 - Agenturseite Fix Plan

## Ziel

Die Agenturseite muss vor dem neuen Portal vollständig funktionsfähig und produktionsreif sein.

## Prioritäten (Business-First)

1. **Visuelle Integrität**
   - Logo/Header/Branding prüfen
   - Responsives Design validieren
   - Accessibility (WCAG 2.1 AA) sicherstellen

2. **Kontaktkanäle**
   - Kontaktformular funktionsfähig
   - Mailversand (SMTP) getestet
   - Beratungs-/Chatfunktion aktiv
   - Angebotsprozess automatisiert

3. **Leistungsportfolio vollständig**
   - Webseiten
   - Plattformen
   - Portale
   - Apps
   - Automatisierungen
   - KI-Lösungen
   - Betrieb/Wartung

4. **Technische Qualität**
   - Tracking (DSGVO-konform)
   - Datenschutz (Cookie-Banner, Privacy Policy)
   - SEO (Meta-Tags, Sitemap, Structured Data)
   - Performance (Lighthouse >90)
   - Build/Deployment Pipeline stabil

## Evidence Gates

Jede Agentur-Funktion muss nachgewiesen werden:

- [ ] Visuelle Regression Tests (Percy/Chromatic)
- [ ] Kontaktformular End-to-End Test
- [ ] Mailversand Log-Check
- [ ] Chat-Widget Integration Test
- [ ] SEO Audit (Lighthouse, PageSpeed)
- [ ] DSGVO Compliance Check
- [ ] Performance Baseline dokumentiert

## Definition of Done

- Alle Agentur-Funktionen produktiv und getestet
- Monitoring aktiv (Uptime, Errors, Performance)
- Documentation aktualisiert
- Stakeholder Review abgeschlossen

## Nächste Schritte

1. Audit durchführen (automatisiert + manuell)
2. Fixes priorisieren (P0 → P3)
3. Tests implementieren
4. Staging Deployment
5. Production Rollout

## Abhängigkeiten

- **Kein neues Portal** bevor Agenturseite stabil
- **Keine Features** die bestehende Funktionen brechen
- **Keine Deployments** ohne Evidence Gates
