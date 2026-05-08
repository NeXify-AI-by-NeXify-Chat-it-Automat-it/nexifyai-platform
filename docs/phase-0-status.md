# Phase 0 – Klärung rechtlicher/kommerzieller Rahmen
# Status: 100% abgeschlossen (2026-05-08 02:45)

## Prüfmatrix: Leitfassung Abschnitt 7

| # | Punkt | Erfüllungsgrad | Quelle | Status |
|---|-------|---------------|--------|--------|
| 1 | **Preismodell** | 100% | Identity Skill + Website | ✅ |
| 2 | **VAT / USt-ID** | 100% | Identity Skill, KvK 90483944 | ✅ |
| 3 | **Dokumentenmatrix** | 100% | billing_routes.py + Identity Skill | ✅ |
| 4 | **DSGVO / AVV** | 100% | /docs/legal/dpa-nexifyai.md | ✅ Freigegeben & umgesetzt |
| 5 | **Cookie-Governance** | 100% | legal.yaml + user_consents Schema | ✅ Freigegeben & umgesetzt |
| 6 | **Lizenz-Compliance** | 100% | security-scan.yml (license-checker) | ✅ Freigegeben & umgesetzt |
| 7 | **Data-Residency** | 100% | legal.yaml + model-routing.yaml Vermerk | ✅ Freigegeben & umgesetzt |

---

## Umsetzungsdetails (alle freigegeben am 08.05.2026)

### 4. DSGVO / AVV (100%)
- ✅ DPA-Template → `/docs/legal/dpa-nexifyai.md`
- ✅ Vollständiger AVV gemäß Art. 28 DSGVO
- ✅ Subprozessoren dokumentiert mit DPA-Status
- ✅ TOM, Betroffenenrechte, Meldepflichten enthalten
- ⚠️ Unterschrift erfolgt extern durch Pascal

### 5. Cookie-Governance (100%)
- ✅ Consent-Taxonomie: essential, functional, analytics, marketing
- ✅ Cookie-Banner in App.js (CookieConsent Component)
- ✅ Opt-in Mechanismus (DSGVO-konform)
- ✅ Schema für `user_consents` Tabelle definiert (Phase 1 Migration)

### 6. Lizenz-Compliance (100%)
- ✅ license-checker Job in security-scan.yml
- ✅ NPM: `license-checker --production --onlyAllow`
- ✅ Python: `pip-licenses`
- ✅ Erlaubte Lizenzen: MIT, Apache 2.0, BSD, ISC, CC0, Unlicense
- ✅ Blockiert: GPL, AGPL, SSPL

### 7. Data-Residency (100%)
- ✅ Primäre Region: EU
- ✅ Hostinger VPS in EU (NL)
- ✅ Supabase Self-Hosted auf EU-VPS
- ✅ OpenRouter DPA reicht vorerst, EU-Alternative in model-routing.yaml vermerkt
- ✅ Vercel US/EU Edge Network akzeptiert

---

## Fazit

**Phase 0 ist vollständig abgeschlossen.** Alle 7 Punkte sind bei 100%.
Phase 1 (Supabase-Fundament) kann beginnen.
