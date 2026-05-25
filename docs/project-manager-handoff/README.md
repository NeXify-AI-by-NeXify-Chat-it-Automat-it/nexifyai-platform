# NeXifyAI Project Manager Handoff

Dieses Verzeichnis ist der kanonische Übergabepunkt für den neuen internen Projektleiter.

## Aktuelle Architekturentscheidung

Die externe Anton/MindsHub-Anbindung ist nicht mehr Pflichtbestandteil. Ziel ist eine interne **NeXify Project Manager Control Plane**, die Goose 24/7 sicher steuert. Externe Operatoren wie Anton können später optional angebunden werden, dürfen aber nicht Kernabhängigkeit sein.

## Priorität

Das neue Portal, Huginn/Temporal/Tool-MCP und die vollständige Agenten-Produktionsstraße werden nach hinten gestellt. Jetzt gilt Business-first:

1. Agenturseite verkaufsfähig machen.
2. KI-Berater, Angebotsgenerator, Kontakt/Mail und Leadprozess reparieren.
3. Bestehende Kundenprojekte nach Pflichtenheften fertigstellen und live bringen.
4. GitHub/Security/CI/Deployments stabilisieren.
5. Shadow-/Legacy-/halbe Artefakte kontrolliert erfassen, migrieren, quarantänisieren oder entfernen.

## Paket

Das vollständige von ChatGPT erzeugte Übergabepaket liegt hier als Base64-ZIP:

`docs/project-manager-handoff/package/nexify_projectleiter_uebergabe.zip.b64`

Die Integrität steht in:

`docs/project-manager-handoff/package/PACKAGE_MANIFEST.json`

Goose muss das Paket nach `docs/project-manager-handoff/extracted/` entpacken, validieren, die alten Anton-Pflichtbegriffe auf interne Project-Manager-Control-Plane umstellen und dann committen.

## Harte Regeln

- Ohne Brain keine Arbeit.
- GitHub ist Source of Truth.
- Goose ist Worker, nicht Projektleiter.
- Project Manager Control Plane ist Steuerungs-, Policy-, Queue- und Evidence-Schicht.
- Keine Secrets in Repo, Logs, Issues, Brain oder Goose-Ausgaben.
- Nichts halb gebaut liegen lassen.
- Jede von Goose erzeugte Ressource muss `active_managed`, `planned`, `migrated`, `quarantined`, `removed_with_evidence` oder `blocked` sein.
- Kundenprojekte niemals ungeprüft in den Core kopieren.
- Sourcecode ist nicht Runtime.
- Fertig heißt Evidence: Branch/Commit/PR, Tests/CI, Security, Brain-Update, Runtime-Nachweis falls relevant.

## Nächster Schritt

Goose muss zuerst `IMPORT_AND_EXPAND_RUNBOOK.md` ausführen. Danach erst darf die interne Project Manager Control Plane implementiert oder bereinigt werden.