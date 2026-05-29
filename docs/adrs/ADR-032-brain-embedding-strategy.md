# ADR-032: Enterprise Brain v3 Embedding & Memory-Strategie
status: approved | date: 2026-05-29 | owner: goose

## Kontext
Das Enterprise Brain v3 verarbeitet 110.603 Wissenspunkte über 25 Qdrant-Collections.
Die Wahl des Embedding-Modells und der Speicherstrategie ist entscheidend für Retrieval-Qualität.

## Entscheidung

### Embedding Pipeline (Primary → Fallback → Fallback)
| Stufe | Modell | Provider | Status |
|-------|--------|----------|--------|
| Primary | Qwen3-8B | nScale (lokal) | ✅ Aktiv |
| Fallback 1 | text-embedding-3-large | OpenRouter | ✅ Konfiguriert |
| Fallback 2 | nomic-embed-text | Ollama (:11435) | ✅ Konfiguriert |

### Speicherstrategie
- **Collection:** `nexifyai_brain_4096_v1` (Haupt-Collection, 9.167 Points)
- **Chunking:** 4096 Token pro Embedding (Vorteil Qwen3-8B: 8K Kontext-Fenster)
- **Kategorisierung:** 25+ Kategorien (system_state, governance, wiki, brain, etc.)
- **Metadaten:** title, category, tags, source, confidence, timestamp

### Memory-Typen
1. **Semantisches Gedächtnis:** Faktisches Wissen (Tatsachen, Erkenntnisse, Regeln)
2. **Episodisches Gedächtnis:** Ereignisse mit Aktion/Ergebnis (Session-Logs)
3. **Prozedurales Gedächtnis:** Workflows/Lösungswege (Step-by-Step)

## Konsequenzen
- **Positiv:** 110.603 Points mit <500ms Query-Latenz
- **Positiv:** Embedding-Qualität durch Qwen3-8B (Enterprise-Grade)
- **Risiko:** nScale könnte ausfallen → Failover-Pipeline bereits konfiguriert

## Verweise
- ADR-014: Knowledge System Brain
- ADR-025: 9Router Integration (obsolet 2026-05-29, OpenRouter stattdessen)
- ADR-027: Brain API Architecture