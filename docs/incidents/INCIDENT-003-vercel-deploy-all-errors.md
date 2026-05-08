# Incident Postmortem: INCID-003 — Alle Vercel-Deployments im Error (Double Export Default)

**Datum:** 2026-05-08
**Severity:** SEV1 (Kritisch — Produktiv-Deployment blockiert)
**Dauer:** 02:26 UTC – 03:28 UTC (62 Minuten)
**Autor:** NeXifyAI (Lead Agent)
**Incident-ID:** INC-20260508-003

---

## Zusammenfassung

Alle Vercel-Deployments ab Commit `34136d0` (03:25 UTC) bis `d71f8d4` waren im Error-Status. Root Cause: Ein `export default function App()` wurde in App.js Zeile 420 eingefügt, während Zeile 493 bereits `export default App;` enthielt. CRA/ESLint erlaubt nur ein `export default` pro Modul. Der Fix wurde lokal durchgeführt aber nie committed — erst mit `630249e` korrigiert.

---

## Timeline (UTC)

| Zeit | Ereignis |
|------|----------|
| 03:25 | Commit 34136d0 (Phase 2) mit Double-Export in App.js gepusht |
| 03:27 | Erster Vercel-Build scheitert |
| ~03:35 | Pascal teilt Vercel-Deploy-Liste — alle Error |
| 03:37 | Lokaler Build getestet — bestanden! (lokale App.js war repariert) |
| 03:38 | Fix als "gelöst" gemeldet ohne zu verifizieren dass Git die kaputte Version hat |
| 03:40–04:10 | Weitere Commits (d71f8d4, db995ba) ohne App.js-Fix — alle scheitern |
| ~04:20 | Benutzer zeigt Build-Log: `Double export default App.js:493` |
| 04:21 | Root Cause identifiziert: lokaler Fix nie committed |
| 04:22 | Commit 630249e — `export default function App()` → `function App()` |
| 04:23 | Vercel deployt erfolgreich — HTTP 200 |

---

## Root Cause

**Primär:** `export default function App()` wurde in Zeile 420 eingefügt (Phase 3 — initTracking-Patch), ohne das bestehende `export default App;` in Zeile 493 zu entfernen.

**Sekundär (Disziplin-Verstoß):** Der Fix wurde lokal durchgeführt (`patch` Tool), aber weder committed noch gepusht. Der Agent ging fälschlich davon aus dass der Fix im Git ist.

**Kategorie:** Code-Fehler (Syntax) + Prozess-Fehler (Commit-Disziplin)

---

## Impact

| Metrik | Wert |
|--------|------|
| Blockierte Deployments | 8 Commits (34136d0–d71f8d4) |
| Ausfallzeit (Produktion) | 0 (letzter erfolgreicher Deploy lief weiter) |
| Verzögerung (neue Features) | ~60 Min |

---

## Resolution

1. `export default function App()` → `function App()` in Zeile 420
2. Nur ein `export default App;` in Zeile 493
3. Lokal Build verifiziert (`npm run build`)
4. Commit 630249e gepusht
5. Vercel auto-deployt — HTTP 200 bestätigt

---

## Prevention

- [x] **Prinzip F:** "Lokal bauen, dann pushen". Kein Push ohne `npm run build` mit Exit 0.
- [x] **Git-Verifikation:** Nach jedem Fix `git show HEAD:file | grep -n "pattern"` prüfen
- [ ] **Pre-Commit-Hook:** `npm run build` als pre-commit Hook (optional, da Build 60s dauert)
- [x] **Brain:** Dieser Incident beweist dass "lokal testen ≠ Git ist korrekt"

---

## Lessons Learned

1. **Patch-Tool != Git-Commit:** Ein lokaler Patch ändert die Arbeitskopie. Erst `git add + commit` überträgt in Git. `git push` überträgt zu Vercel.
2. **Doppelte Verifikation:** Nach einem Fix: `git diff --cached` prüfen WAS committed wird, nicht nur lokale Datei testen.
3. **Build-Cache-Tücke:** Lokaler Build kann bestehen (weil lokale Datei korrekt), aber Vercel baut aus Git. Nie annehmen dass "Build lokal OK" = "Vercel wird deployen".

---

**Postmortem erstellt:** 2026-05-08 04:30 UTC
**Review durch:** NeXifyAI
