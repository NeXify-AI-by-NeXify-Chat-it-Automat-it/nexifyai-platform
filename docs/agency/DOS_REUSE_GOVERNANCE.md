# NeXifyAI DOS Clean Reuse Governance

**Version:** 1.0 | **Stand:** 2026-05-24
**Klassifikation:** INTERN – VERBINDLICH

---

## Grundregel

Warum neu erstellen, wenn es bereits existiert?

Vor jeder neuen Implementierung muss geprüft werden:

1. Gibt es diese Lösung bereits intern?
2. Gibt es diese Lösung bereits in einem Kundenprojekt?
3. Gibt es ein Portal, Dashboard, Authflow, Billingflow, Formular, KI-Widget, Angebotsgenerator, Adminbereich, Kundenportal, Landingpage-Modul oder API-Modul bereits?
4. Kann es sauber extrahiert, generalisiert und wiederverwendet werden?
5. Kann es als Package, Template, Component, Service, Hook, Workflow oder Blueprint zentralisiert werden?
6. Gibt es rechtliche/vertragliche Einschränkungen bei Kundenprojekt-Code?
7. Muss Code neu geschrieben, aber nach bewährtem Muster modelliert werden?
8. Muss ein vorhandenes Artefakt dokumentiert, abstrahiert oder bereinigt werden?

## Kundenprojekt-Code: Nur als Clean Pattern

Kundenprojekt-Code darf nicht ungeprüft kopiert werden.

### Erlaubt
- Architekturpattern übernehmen
- UI-/UX-Pattern abstrahieren
- generische Komponenten neu sauber aufbauen
- Workflows nachbauen
- Lessons Learned speichern
- wiederverwendbare Anforderungen ableiten

### Nicht erlaubt
- Kundendaten übernehmen
- Secrets übernehmen
- kundenspezifische Texte/Marke ungeprüft übernehmen
- Kundenrepo in Core kopieren
- Kundenprojekt als Core-Modul betreiben
- unklare Lizenz-/Eigentumsverhältnisse ignorieren

## Prüfung vor jeder Übernahme aus Kundenprojekt

1. Eigentum/Rechte prüfen
2. Secrets prüfen (keine übernehmen)
3. Kundendaten prüfen (keine übernehmen)
4. Mandantentrennung prüfen
5. Lizenz prüfen
6. Datenschutz prüfen
7. Branding prüfen (entfernen vor Wiederverwendung)
8. Technische Qualität prüfen
9. Abhängigkeiten prüfen

## Ziel

- wiederverwendbare Muster extrahieren
- saubere Clean-Room-Varianten erstellen, falls nötig
- zentrale Pakete/Blueprints bauen
- keine Kundenlogik im Core vermischen
- keine Secrets oder Kundendaten übernehmen

## Verantwortlich

- Jeder Entwickler/Agent vor jeder neuen Lösung
- Überprüfung durch Resource-Catalog-Abfrage
- Dokumentation im Reuse Catalog
