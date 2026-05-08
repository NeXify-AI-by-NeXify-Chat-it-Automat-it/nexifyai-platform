# Incident Postmortem: INCID-002 — Build-Fehler blog.js/track.js Import

**Datum:** 2026-05-08
**Severity:** SEV2 (Teilausfall — Frontend-Build blockiert)
**Dauer:** 02:13 – 02:30 (17 Minuten)
**Autor:** NeXifyAI (Lead Agent)
**Incident-ID:** INC-20260508-002

---

## Zusammenfassung
Commit f47cc2d verursachte Build-Fehler im Vercel-Deployment. Das Frontend konnte nicht gebaut werden, weil `frontend/src/data/blog.js` fehlte und `frontend/src/lib/track.ts` CRA-inkompatibel war. Website war von diesem Build-Fehler nicht betroffen (letzter erfolgreicher Deploy lief weiter), aber alle neuen Änderungen blieben blockiert.

---

## Timeline (UTC)

| Zeit | Ereignis |
|------|----------|
| 02:05 | Commit f47cc2d (Phase-0-Status, Plausible-Doku) auf main gepusht |
| 02:10 | Vercel startet Auto-Deploy — Build schlägt fehl |
| 02:13 | Pascal meldet Build-Fehler |
| 02:14 | Analyse beginnt: `../data/blog` in BlogPage.js + BlogPostPage.js identifiziert |
| 02:15 | blog.js aus Git-History (1127642) wiederhergestellt |
| 02:17 | Erster Build-Versuch: `export default` doppelt in App.js → Syntax Error |
| 02:18 | Double-export gefixt |
| 02:20 | Zweiter Build: `./lib/track` not found → .ts-Datei nicht CRA-kompatibel |
| 02:22 | track.ts zu track.js konvertiert (TypeScript-Syntax entfernt) |
| 02:25 | Build erfolgreich |
| 02:27 | Commit 16e695c gepusht (blog.js + track.js + App.js-Fix) |
| ~02:28 | Vercel Auto-Deploy startet neu → erwartet erfolgreich |

---

## Root Cause

**Primär:** `frontend/src/data/blog.js` wurde beim Git-Stash-Pop auf dem VPS am 08.05.2026 01:25 gelöscht. Der Commit f47cc2d wurde vom Container aus gepusht (ohne blog.js), aber die BlogPage.js und BlogPostPage.js importierten weiterhin `../data/blog`.

**Sekundär:** `frontend/src/lib/track.ts` war in TypeScript geschrieben, aber das React-CRA-Projekt unterstützt keinen TypeScript-Import aus JavaScript-Dateien (`App.js` importierte `./lib/track`, was nur `.js` auflösen kann, nicht `.ts`).

**Tertiär:** In `App.js` wurde `function App()` fälschlich in `export default function App()` geändert, was mit dem bestehenden `export default App;` am Dateiende kollidierte (Syntax Error: Only one default export allowed).

**Kategorie:** Code-Fehler (Bug) — 3 Teilfehler

---

## Impact

| Metrik | Wert |
|--------|------|
| Betroffene Nutzer | 0 (letzter erfolgreicher Deploy lief weiter) |
| Blockierte Deployments | 1 (f47cc2d) |
| Ausfallzeit (Total) | 0 Minuten (kein Produktiv-Ausfall) |
| Finanzieller Schaden | 0 € |

---

## Resolution

1. **blog.js:** Aus Git-Commit 1127642 wiederhergestellt (`git checkout 1127642 -- frontend/src/data/blog.js`)
2. **track.ts→track.js:** TypeScript-Syntax entfernt (type/interface → var/function), CRA-kompatibel gemacht
3. **App.js Double-Export:** `export default function App()` → `function App()`, Original-Export am Ende bleibt
4. **Build-Verifikation:** `npm run build` erfolgreich → Commit + Push

---

## Prevention

- [x] **Prinzip C aktiv:** Vor jedem Git-Push `npm run build` ausführen und verifizieren. Verstoß = SEV1.
- [ ] **Git-Stash-Falle:** `git stash pop` birgt Risiko von gelöschten Dateien. Künftig: `git stash list` prüfen, bevor pop. Gelöschte Dateien via `git checkout {commit} -- {file}` wiederherstellen.
- [ ] **TypeScript im Frontend:** track.js bleibt als Plain-JS. Bei TypeScript-Migration: `tsconfig.json` anlegen und `npm install typescript`.
- [x] **Build vor Push:** Dieser Incident ist der Beleg, dass Prinzip B+C zwingend sind. Wurde sofort im Brain aktiviert.

---

## Lessons Learned

1. **Git-Stash-Pop ist gefährlich:** Bei Merge-Konflikten können Dateien verloren gehen. Immer `git status` nach `stash pop` prüfen.
2. **CRA + TypeScript:** Einfache .js-Dateien sind sicherer als .ts wenn das Projekt kein TypeScript-Migration hat. Bei Bedarf `tsconfig.json` einrichten.
3. **Double-Export-Check:** Bei Patches auf Export-Funktionen immer `grep -n "export default"` vor Commit prüfen.
4. **Build vor Push ist nicht optional:** Dieser SEV2 wäre durch einen lokalen Build vor Push vermeidbar gewesen.

---

**Postmortem erstellt:** 2026-05-08 02:35 UTC
**Review durch:** NeXifyAI (Lead Agent)
**Freigabe:** Automatisch (SEV2)
