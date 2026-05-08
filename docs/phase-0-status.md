# Phase 0 – Klärung rechtlicher/kommerzieller Rahmen

## Prüfmatrix: Leitfassung Abschnitt 7

| # | Punkt | Erfüllungsgrad | Quelle | Status |
|---|-------|---------------|--------|--------|
| 1 | **Preismodell** (Starter/Growth/Enterprise) | 100% | nexifyai-identity Skill + Website (nexify-automate.com) | ✅ Geklärt |
| 2 | **VAT / USt-ID** (NL865786276B01) | 100% | nexifyai-identity Skill, KvK 90483944 | ✅ Geklärt |
| 3 | **Dokumentenmatrix** (Quote→Invoice→Contract) | 100% | backend/routes/billing_routes.py, Offer-to-Cash Prozess im Identity Skill | ✅ Geklärt |
| 4 | **DSGVO / AVV** (DPA-Handling, Subprozessoren) | 75% | packages/config/legal.yaml (DPA-Template existiert, subprocessors dokumentiert) | ⚠️ Fehlende Unterschriften |
| 5 | **Cookie-Governance** (Consent-Taxonomie) | 75% | packages/config/legal.yaml (essential/functional/analytics/marketing definiert) | ⚠️ Cookie-Banner existiert, Consent-Log in Supabase fehlt |
| 6 | **Lizenz-Compliance** (Open-Source-Scan) | 50% | legal.yaml (allowed/blocked Lizenzen definiert), aber kein automatisierter Scan im CI | ⚠️ CI-Scan fehlt |
| 7 | **Data-Residency** (EU-Datenhaltung) | 75% | legal.yaml (primary_region: EU, Hostinger VPS in EU, Supabase Self-Hosted) | ⚠️ OpenRouter-DPA für US-Daten prüfen |

---

## Detailanalyse

### 1. Preismodell (100%)
- **Starter** (NXA-SAA-24-499): 499€/Monat, 24 Monate
- **Growth** (NXA-GAA-24-1299): 1.299€/Monat, 24 Monate
- **Enterprise:** Individuell ab 39.900€
- **Bundles:** Digital Starter 3.990€, Growth Digital 17.490€
- **Quelle:** nexifyai-identity Skill, Website Tarife-Sektion

### 2. VAT / USt-ID (100%)
- **KvK:** 90483944 (NL)
- **USt-ID:** NL865786276B01
- **Firmenname:** neXify - Chat it. Automat it.
- **Adresse:** Graaf van Loonstraat 1E, 5921 JA Venlo
- **Quelle:** nexifyai-identity Skill

### 3. Dokumentenmatrix (100%)
- **Quote-Status:** draft → sent → opened → accepted/declined/revision/expired
- **Invoice-Status:** draft → sent → paid/overdue/cancelled
- **Mahnstufen:** 21/35/49 Tage
- **Zahlungserinnerung:** 7/14 Tage
- **Offer-to-Cash:** Lead → Prequalify → Booking → Quote → Invoice → Contract → Project → Support
- **Quelle:** nexifyai-identity Skill, billing_routes.py

### 4. DSGVO / AVV (75%)
- ✅ DPA-Template-Pfad definiert in legal.yaml
- ✅ Subprozessoren dokumentiert (OpenRouter, Vercel, Resend, Hostinger, Supabase)
- ✅ AI-Disclosure Policy definiert
- ❌ Unterzeichnete AVV-Dokumente fehlen (keine PDFs im Repo)
- ❌ Verarbeitungsverzeichnis (VVT) nicht erstellt
- **Nächster Schritt:** AVV-Vorlage ausfüllen mit Pascal

### 5. Cookie-Governance (75%)
- ✅ Consent-Taxonomie in legal.yaml (essential, functional, analytics, marketing)
- ✅ Cookie-Banner in App.js (CookieConsent Component)
- ✅ DSGVO-konformes Opt-in
- ❌ Consent-Log speichert noch nicht in Supabase
- ❌ Cookie-Consent Präferenzen werden nur in sessionStorage gehalten
- **Nächster Schritt:** Consent-Log in Supabase Tabelle `user_consents`

### 6. Lizenz-Compliance (50%)
- ✅ Lizenz-Taxonomie (allowed: MIT, Apache 2.0, BSD, ISC; blocked: GPL, AGPL, SSPL)
- ✅ Lizenz-Scan-Frequenz definiert (per PR)
- ❌ Kein automatisierter Scan in CI (npm audit läuft, aber kein license-checker)
- ❌ Kein vollständiger Dependency-Lizenz-Report
- **Nächster Schritt:** license-checker in CI integrieren

### 7. Data-Residency (75%)
- ✅ Primäre Region: EU
- ✅ Hostinger VPS in EU (NL) — physische Datenhaltung
- ✅ Supabase Self-Hosted auf EU-VPS
- ⚠️ OpenRouter: US-basiert (DPA vorhanden, aber keine Data-Residency-Garantie)
- ⚠️ Vercel: US/EU Edge Network
- **Nächster Schritt:** OpenRouter-Subprozessor-Dokumentation prüfen

---

## Offene Punkte für Pascal (Freigabe erforderlich)

1. **AVV-Unterzeichnung:** DPA-Template vorhanden, muss mit Unternehmensdaten befüllt und unterschrieben werden.
2. **Cookie-Consent-Log:** Consent soll in Supabase `user_consents` Tabelle gespeichert werden — Freigabe für Schema-Design?
3. **Lizenz-Scan:** license-checker in CI aktivieren? (NPM + Python Dependencies)
4. **VVT (Verarbeitungsverzeichnis):** DSGVO-pflichtig, Basis kann aus legal.yaml generiert werden.
5. **OpenRouter Data-Residency:** Besteht Bedarf an EU-LLM-Alternative oder reicht DPA?
