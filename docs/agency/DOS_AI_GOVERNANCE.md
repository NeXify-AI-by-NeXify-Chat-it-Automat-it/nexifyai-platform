# NeXifyAI DOS AI Governance

## Brain-first
- Ohne Brain keine Arbeit
- Ein zentrales Brain (Qdrant + Brain API)
- Semantisches Gedächtnis: Fakten, Architektur, Regeln
- Episodisches Gedächtnis: Ereignisse, Incidents, Entscheidungen
- Prozedurales Gedächtnis: Workflows, Recovery, Vorgehensweisen

## Lernpflicht
- Lessons Learned sind Pflicht
- Prevention Rules sind Pflicht
- Fehler dürfen nicht zweimal passieren
- Jede AI-Lösung schreibt validierte Erkenntnisse ins Brain

## Resource-first
- Vor jeder neuen Lösung: existierende Ressourcen prüfen
- Brain, Tools, Skills, Infrastruktur, Code, Patterns, ADRs
- Wenn vorhanden: verwenden, verbinden, feinabstimmen
- Nicht: neubauen, duplizieren, lokal nachmodellieren, Shadow-System

## Runtime Evidence
- Sourcecode ist nicht Runtime
- Runtime muss gegen echte Systemzustände validiert werden
- Prozesse, Ports, Container, API-Responses, Logs, Netzwerke
- Keine Fertigmeldung ohne Runtime-Nachweis

## Secret-Governance
- Keine Secrets in Ausgaben
- Keine Umgebungsvariablen-Werte (environment)
- Keine systemd Environment-Werte
- Nur Secret-Namen und Fundorte redaktiert
