# Barrierefreiheits-Erklärung

**Stand:** 2026-05-30
**Geltungsbereich:** NeXifyAI Enterprise Brain v3 Plattform
**Anschrift:** NeXifyAI, Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande
**E-Mail:** support@nexify-automate.com

---

## 1. Erklärung zur Barrierefreiheit

Die NeXifyAI-Plattform (nexify-automate.com) ist bestrebt, ihre digitalen Angebote im Einklang mit den nationalen Rechtsvorschriften zur Umsetzung der Richtlinie (EU) 2016/2102 (Barrierefreiheitsstärkungsgesetz) barrierefrei zugänglich zu machen. Als Maßstab dienen die Web Content Accessibility Guidelines (WCAG) 2.2 auf Konformitätsstufe AA.

Diese Erklärung zur Barrierefreiheit gilt für die öffentlich zugänglichen Bereiche der Plattform (Website, Kundenportal und Admin-Oberfläche) sowie für die von NeXifyAI bereitgestellten Kommunikationsmittel.

---

## 2. Stand der Barrierefreiheit

Die NeXifyAI-Plattform ist **teilweise konform** mit WCAG 2.2 Level AA.

Ein automatisiertes Live-Audit (30.05.2026) hat Folgendes ergeben:

| Kategorie | Geprüft | Erfüllt | Nicht erfüllt | Nicht relevant |
|-----------|---------|---------|---------------|----------------|
| A-Kriterien | 28 | 20 | 0 | 8 |
| AA-Kriterien | 17 | 14 | **3** | 0 |
| **Gesamt** | **45** | **34** | **3** | **8** |

**Gesamtkonformität:** 34/37 = 91,9%

---

## 3. Nicht barrierefreie Inhalte

Die folgenden Inhalte sind aus folgenden Gründen nicht barrierefrei:

### 3.1 Unverhältnismäßige Belastung

| Bereich | Abweichung | Geplante Maßnahme | Frist |
|---------|-----------|-------------------|-------|
| **Icons in Sidebar** (2.5.8) | Icongröße 20px statt empfohlener 24px Mindest-Zielgröße | Icons auf 24x24 vergrößern, Abstände anpassen | **Q3 2026** |
| **ARIA-Live-Regionen** (4.1.3) | Chat-Bereich hat keine `aria-live="polite"`-Region für dynamische Aktualisierungen | Live-Region für Chat-Output ergänzen | **Q3 2026** |
| **Mobile Sidebar** (1.4.10) | Fixed-Sidebar kann bei < 320px Bildschirmbreite überlappen | Overlay-Mechanismus für Mobile implementieren | **Q3 2026** |

### 3.2 Derzeit nicht vorgesehen
- **Gebärdensprachvideos** (§ 4 BITV 2.0): Für die aktuelle Early-Access-Phase nicht vorgesehen
- **Leichte-Sprache-Versionen** (§ 4 BITV 2.0): Ebenfalls nicht vorgesehen

---

## 4. Bereits umgesetzte Barrierefreiheitsmaßnahmen

| Maßnahme | WCAG-Kriterium | Umsetzung |
|----------|---------------|-----------|
| Alt-Texte auf allen Bildern | 1.1.1 A | ✅ AdminCockpit, Admin, CustomerPortal |
| Skip-to-Content-Link | 2.4.1 A | ✅ Erster fokussierbarer Link |
| `role`-Attribute für Navigation | 1.3.1 A, 4.1.2 A | ✅ navigation, menubar, listitem |
| `aria-label` auf interaktiven Elementen | 4.1.2 A | ✅ Sidebar-Toggle, Buttons |
| `data-testid` auf Schlüsselelementen | — | ✅ 80+ Elemente |
| Fokus-Indikator (`:focus-visible`) | 2.4.7 AA, 2.4.13 AA | ✅ 2px #FE9B7B outline |
| Tastaturbedienung (Tabellen) | 2.1.1 A | ✅ tabindex + onKeyDown |
| Inline-Fehlermeldungen | 3.3.1 A, 3.3.3 AA | ✅ role="alert" auf Fehlerfeldern |
| Magic Link statt Passwort | 3.3.7 AA | ✅ Kein kognitiver Test |
| Konsistente Navigation | 3.2.3 AA | ✅ Sidebar + Topbar |
| Semantische H1-H3 Hierarchie | 2.4.6 AA | ✅ Map page/section/widget → h1/h2/h3 |
| Farbkontrast (Kernfarben) | 1.4.3 AA | ✅ 14.4:1 (Text) / 8.6:1 (Coral) / 4.1:1 (muted) |

---

## 5. Durchsetzungsverfahren

Bei Verstößen gegen die Barrierefreiheitsanforderungen können Nutzer die zuständige Durchsetzungsstelle einschalten.

### 5.1 Feedback und Kontakt
Sollten Ihnen Mängel zur Barrierefreiheit auffallen, bitten wir um Mitteilung:

**E-Mail:** support@nexify-automate.com  
**Betreff:** "Barrierefreiheit — [Beschreibung des Problems]"  

Wir bemühen uns, innerhalb von **14 Tagen** zu antworten.

### 5.2 Schlichtungsstelle
Sollte Ihre Rückmeldung nicht zufriedenstellend bearbeitet werden, können Sie die Schlichtungsstelle nach § 16 BGG einschalten:

**Schlichtungsstelle nach § 16 BGG**  
Mauerstraße 52, 10117 Berlin  
E-Mail: schlichtungsstelle@bmas.bund.de  
Web: https://www.schlichtungsstelle-bgg.de

---

## 6. Erstellungsgrundlage

Diese Erklärung wurde erstellt auf Grundlage eines automatisierten Live-Audits vom 30.05.2026 unter Verwendung von:
- WCAG 2.2 Erfolgskriterien (Level A + AA)
- Kontrast-Messungen mit laborgeprüften Farbwerten
- Live-Scan der Frontend-Quelldateien (JSX, CSS)
- BITV 2.0 (Barrierefreie-Informationstechnik-Verordnung)

**Letzte Überprüfung:** 30.05.2026  
**Nächste Überprüfung:** 30.08.2026 (quartalsweise)

---

## 7. Verweise

- [WCAG 2.2 Assessment](../policies/wcag-assessment.md)
- [Design Guidelines](../../design_guidelines.json)
- [Design Tokens (CSS)](../../packages/ui/tokens.css)
- Richtlinie (EU) 2016/2102: https://eur-lex.europa.eu/eli/dir/2016/2102
- WCAG 2.2: https://www.w3.org/TR/WCAG22/