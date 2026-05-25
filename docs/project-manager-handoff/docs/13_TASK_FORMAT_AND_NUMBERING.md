# Task Format and Numbering

## Task-ID

Format:

`NX-YYYYMMDD-HHMM-area-title`

Zeitzone:

`Europe/Berlin`

## Pflichtfelder

- task_id
- parent_task_id, falls vorhanden
- created_at
- timezone
- created_by
- assigned_to
- project
- repo
- branch
- priority
- mode
- allowed_actions
- denied_actions
- brain_context_required
- evidence_required
- acceptance_criteria
- abort_conditions

## Modi

- readonly: keine Datei- oder Serviceänderung
- plan: Plan- und Dokumentationsarbeit
- implement: Umsetzung auf Branch
- review: Prüfung, Kommentar, Evidence
- deploy: nur mit expliziter Freigabe

## Abschluss

Jeder Task endet mit Status, Evidence, offenen Blockern und nächstem sicheren Schritt.
