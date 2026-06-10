# NeXify AI — Führungsregel V2: Heutige Vorgaben sind führend

**Stand:** 2026-06-09  
**Version:** 1.0  
**Status:** VERBINDLICH — OBERSTE BETRIEBSREGEL  
**Rang:** Überschreibt widersprüchliche ältere Vorgaben  
**Geltungsbereich:** Alle AI-Agenten, Teams, Worker, Skills, MCPs, Tools, Workflows, Repos, Dokumente, Konzepte, Automationen

---

## 1. Führungsregel

**Alle heute (2026-06-09) neu erteilten Vorgaben sind führend.**

Ältere Vorgaben bleiben nur insoweit gültig, wie sie den heutigen Vorgaben nicht widersprechen.

### Führende Dokumente (V2, Stand 2026-06-09)

| Rang | Dokument | Pfad |
|------|----------|------|
| 1 | **Agenten-Seele V2** | `docs/governance/NEXIFY_AI_AGENTEN_SEELE.md` |
| 2 | **Benutzerprofil V2** | `docs/governance/PASCAL_COURBOIS_BENUTZERPROFIL.md` |
| 3 | **Interaktionsanweisung V2** | `docs/governance/NEXIFY_AI_INTERAKTIONSANWEISUNG_V2.md` |
| 4 | **Fertigstellungsdefinition** | `docs/governance/NEXIFY_AI_FERTIGSTELLUNGSDEFINITION.md` |
| 5 | **Grundregelwerk Basis V1** (insoweit nicht widersprechend) | `00_.../01_.../11_NEXIFY_AI_GRUNDREGELWERK_BASIS_V1.md` |
| 6 | **Gesamtregelwerk konsolidiert** (insoweit nicht widersprechend) | `00_.../01_.../09_NEXIFY_AI_GESAMTREGELWERK_KONSOLIDIERT.md` |

### Führende Systementscheidungen (heute)

| Entscheidung | Status |
|-------------|--------|
| Kommunikation zielzustandsorientiert verstehen | ✅ Führend |
| 7 Ebenen Fertigstellungsdefinition | ✅ Führend |
| PARTIAL_DONE ≠ fertig | ✅ Führend |
| ToDo/auftragsfach/Automatik führen autonome Arbeit | ✅ Führend |
| Chat nicht für autonome Ausführung | ✅ Führend |
| NCCCE Chat-Fortsetzung als P0 | ✅ Führend |
| GitHub-Autonomie als P0 | ✅ Führend |
| 9Router als Workstation-Modul | ✅ Führend |
| nexifyai-standard-llm (v4-flash + reasoner) | ✅ Führend |
| v4-pro, v4-pro-max gesperrt | ✅ Führend |
| Graphite/Dark-Design als CI | ✅ Führend |
| Deutsche Oberfläche | ✅ Führend |
| Keine Fremdmarken im Kunden-UI | ✅ Führend |
| Projekttrennung in Spaces | ✅ Führend |
| Secrets nur als secret_ref | ✅ Führend |
| Policy Gate vor jedem Write | ✅ Führend |
| Evidence + Brain/Kanban/agentmemory bei jedem Task | ✅ Führend |
| DeepSeek API NUR über 9Router | ✅ Führend |
| Karpathy-Repos als Pflichtquelle | ✅ Führend |

---

## 2. Konfliktregel

Bei Konflikten zwischen heutigen und älteren Vorgaben:

```text
1. Heutige Vorgabe prüfen
2. Ältere Vorgabe vergleichen
3. Widerspruch dokumentieren
4. Neue führende Fassung erstellen
5. Alte Fassung archivieren
6. Betroffene Systeme anpassen
7. Brain/agentmemory/Kanban/Evidence aktualisieren
```

---

## 3. Schuldenfreiheitsregel

NeXify AI arbeitet ab sofort schuldenfrei:

- Keine ungeklärten Altdateien
- Keine doppelten Wahrheiten
- Keine widersprüchlichen Regeln
- Keine halbfertigen Konzepte ohne Folgeauftrag
- Keine nicht verankerten Dateien
- Keine nicht synchronisierten Brain-/Kanban-Einträge
- Keine Fake-Done-Meldungen

Jeder Schuldenpunkt erzeugt einen Task mit Priorität und Owner.

---

## 4. Archivregel

Nicht mehr benötigte Inhalte werden archiviert, nicht sofort gelöscht:

```text
1. Als veraltet/ersetzt/doppelt markieren
2. Abhängigkeiten prüfen
3. Wissen extrahieren
4. Neue führende Datei verlinken
5. In 99_archiv/ verschieben
6. Evidence schreiben
7. Löschung nur nach separater Freigabe
```

---

## 5. Konsolidierungspflicht

Jede neue Vorgabe prüft:

- Welche bestehenden Dateien/Regeln sind betroffen?
- Welche müssen ersetzt/archiviert werden?
- Ist die Arbeit schuldenfrei ausführbar?

---

## 6. Prüfpflicht für AI-Agenten

Vor jeder Arbeit:

```text
☐ Gilt eine heutige neuere Vorgabe?
☐ Gibt es ältere widersprüchliche Regeln?
☐ Muss etwas ersetzt oder archiviert werden?
☐ Ist der Zielzustand vollständig verstanden?
☐ Ist die Arbeit schuldenfrei ausführbar?
☐ Welche Evidence ist nötig?
☐ Welche Brain-/Kanban-Rückführung ist nötig?
```

