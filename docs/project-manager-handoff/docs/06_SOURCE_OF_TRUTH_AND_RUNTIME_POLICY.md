# Source of Truth and Runtime Policy

## Source of Truth

Das zentrale Repository ist `NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform`.

Lokale Ordner, Docker-Stacks, Compose-Projekte, alte Mirrors und Runtime-Dateien sind keine automatische Wahrheit.

## Runtime Evidence

Eine Komponente gilt nur dann als aktiv oder produktiv relevant, wenn Evidence vorliegt:

- Prozess oder Container läuft
- Port oder Domain ist erreichbar
- Routing über Traefik, Cloudflare oder Vercel ist nachgewiesen
- Logs oder Healthchecks zeigen Nutzung
- Git-Remote und Commit sind zugeordnet
- Deployment-Pfad ist dokumentiert

## Sourcecode ist nicht Runtime

Code im Repo beweist nicht, dass etwas produktiv läuft. Umgekehrt beweist ein laufender Container nicht, dass er zum aktuellen Source-of-Truth-Repo gehört.

## Docker und Shadow-Systeme

Docker-Projekte wie `agentur-repo` müssen gegen GitHub, Compose-Pfad, Traefik-Routing, Images und Logs abgeglichen werden, bevor sie bewertet oder geändert werden.

## Pflicht vor Änderung

Vor jeder Änderung an Runtime-Systemen muss geklärt sein:

- was läuft
- wofür es genutzt wird
- welche Domain darauf zeigt
- welches Repo dazu gehört
- wer es benötigt
- wie Rollback funktioniert
