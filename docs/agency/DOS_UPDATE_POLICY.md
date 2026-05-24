# NeXifyAI DOS Update Policy

## Wann DOS erweitert werden muss
- neue Lessons Learned
- wiederholte Fehler
- neue Architekturentscheidung
- neue Agenturleistung
- neue Tool-/Skill-/MCP-Erkenntnis
- neue Compliance-Anforderung
- neue Kundenprojekt-Erfahrung
- neue Security-/Runtime-Erkenntnis
- neue Best Practice

## Pflicht: Neue Erkenntnisse müssen immer übertragen werden

Neue Erkenntnisse sind keine Chatnotizen.
Jede neue Erkenntnis aus:
- Goose-Ausgaben
- User-Korrekturen
- Audits
- Runtime-Checks
- Security-Funden
- Kundenprojekten
- Repo-Analysen
- Vercel-/GitHub-/CI-Ergebnissen
- Brain-Abfragen
- Deployment-Fehlern
- Architekturentscheidungen
- wiederverwendbaren Artefakten
- bestehenden Kundenprojektlösungen

muss geprüft und übertragen werden in:
1. DOS, falls Regel/Standard/Prozess betroffen ist
2. Lessons Learned, falls Fehler/Erkenntnis entstanden ist
3. Prevention Rules, falls Wiederholungsfehler verhindert werden muss
4. Resource Catalog, falls vorhandene Ressource nutzbar ist
5. Reusable Capabilities, falls etwas wiederverwendet werden kann
6. Service Catalog, falls Service/System betroffen ist
7. ADR, falls Architekturentscheidung betroffen ist
8. Brain, falls agentenübergreifendes Wissen relevant ist

**Neue Erkenntnis ohne Governance-/Learning-/Resource-Abgleich gilt als nicht verarbeitet.**

## Prozess
1. Erkenntnis dokumentieren (lessons-learned.json)
2. Prevention Rule ableiten (prevention-rules.json)
3. DOS-Text erweitern (als v1.x)
4. Changelog aktualisieren
5. Brain-Eintrag erstellen
6. Resource Catalog aktualisieren (falls Ressource betroffen)
7. Reuse Catalog aktualisieren (falls Wiederverwendung möglich)
