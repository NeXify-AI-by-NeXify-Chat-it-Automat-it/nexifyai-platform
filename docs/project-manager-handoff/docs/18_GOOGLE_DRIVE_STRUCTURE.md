# Google Drive Structure

## Zweck

Google Drive dient als Ablage für für Menschen lesbare Projektunterlagen. GitHub bleibt Source of Truth für Code, Governance und ausführbare Projektdateien.

## Empfohlene Struktur

- 00_Master
  - Projektauftrag
  - Masterplan
  - Entscheidungsprotokoll
- 01_Agenturseite
  - Audits
  - Fixpläne
  - Abnahmen
- 02_Kundenprojekte
  - je Kunde ein Ordner
  - Pflichtenheft
  - Statusberichte
  - Abnahme
  - Übergabe
- 03_Security_CI
  - Blocker
  - Findings
  - Maßnahmen
- 04_Runtime
  - Docker
  - Domains
  - Deployments
  - Monitoring
- 05_Project_Manager
  - Betriebsmodell
  - Runbooks
  - Reports
- 06_Archiv
  - alte Stände
  - abgelöste Konzepte

## Regel

Drive darf GitHub nicht ersetzen. Jede relevante Entscheidung muss im Repo oder Brain nachvollziehbar sein.
