# NeXifyAI DOS Skill Composition

## Skill-Kompositions-Pipeline (Pflicht-Reihenfolge)
1. Intent / Understanding / Research
2. Konzept / Anforderungen / Text / Preislogik
3. Architektur / Systemdesign
4. Design / UX / UI / Brand
5. Fullstack / Next.js / React / Supabase
6. Cloud / Network / Vercel / Hosting / Infra
7. Security / Compliance / ISO/DIN/Agenturvorgaben
8. QA / Tests / Review / Evidence
9. Dokumentation / Governance / Brain-Learning

## Master-Skill-Registry
- claude-code-templates ist einzige autorisierte Skill-Quelle
- Registry unter /opt/nexify/goose-skill-bridge/registry/skills.json
- Skills müssen aus Master-Pfad geladen werden (read-only)
- Keine lokalen Fake-Skills
- nearest-match suchen, wenn exakter Name fehlt

## Skill-Nutzung
- Prozess-Skills zuerst
- Architektur-Skills danach
- Domain-/Implementierungs-Skills danach
- QA/Security/Infra danach
- Skills müssen kombiniert werden, nicht isoliert
