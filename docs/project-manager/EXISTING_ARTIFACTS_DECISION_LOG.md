# Existing Artifacts Decision Log

**Version:** 1.0  
**Stand:** 2026-05-25  
**Status:** active_managed  

---

## Übersicht

Dieses Log dokumentiert alle gefundenen Artefakte aus der Anton-Goose-Bridge / Project-Manager-Vorarbeiten und deren Entscheidungsstatus gemäß Resource Lifecycle Policy.

---

## Artefakt 1: /opt/nexify/anton-goose-bridge/

### Details

| Attribut | Wert |
|----------|------|
| Pfad | `/opt/nexify/anton-goose-bridge/` |
| Zweck | Anton-Goose Bridge API + Worker (vorheriger Auftrag) |
| Ersteller | Goose (vorheriger Lauf) |
| Produktiv relevant | UNKLAR |
| Service läuft | NEIN |
| Enthält Secrets | NEIN (Env nur Platzhalter) |
| Environment-Datei `/etc/nexify/anton-goose-bridge` (config) | NICHT VORHANDEN |
| Systemd Service aktiv | NEIN (Dateien existieren, nicht enabled) |

### Entscheidung

| Status | Grund |
|--------|-------|
| `quarantined` | Anton-spezifisch, nicht getestet, keine Env-Secrets, in Quarantäne verschoben. Generische Teile können später in Project Manager migriert werden. |

### Quarantäne-Details

- **Datum**: 2026-05-25
- **Ziel**: `/opt/nexify/_quarantine/anton-goose-bridge-20260525-1657/`
- **Manifest**: Siehe `MANIFEST.md` im Quarantäne-Ordner
- **Nicht aktivieren**
- **Nicht löschen** ohne Review

### Potentiell migrierbare Teile

| Datei | Migration möglich | Notizen |
|-------|-------------------|---------|
| `config/bridge.conf` | JA | Generische Konfig, muss umbenannt werden |
| `schemas/*.json` | JA | Generische JSON-Schemas |
| `systemd/*.service` | NEIN | Anton-spezifisch, muss für Project Manager neu |

---

## Artefakt 2: /opt/nexify/project-manager/

| Attribut | Wert |
|----------|------|
| Pfad | `/opt/nexify/project-manager/` |
| Existiert | NEIN |
| Entscheidung | `planned` |

### Nächste Schritte

1. Struktur anlegen (wenn nötig)
2. Migrierte Bridge-Teile integrieren
3. Env-Vorbereitung
4. Systemd erstellen

---

## Artefakt 3: /opt/nexify/goose-worker/

| Attribut | Wert |
|----------|------|
| Pfad | `/opt/nexify/goose-worker/` |
| Existiert | NEIN |
| Entscheidung | N/A |

---

## Artefakt 4: Anton-Goose-Bridge Systemd Services

### Dienst 1: nexify-anton-goose-bridge.service

| Attribut | Wert |
|----------|------|
| Datei existiert | JA (`/opt/nexify/anton-goose-bridge/systemd/nexify-anton-goose-bridge.service`) |
| In /etc/systemd/system/ | NEIN |
| Aktiv | NEIN |
| Entscheidung | `quarantined` (zusammen mit Bridge-Artefakten) |

### Dienst 2: nexify-goose-worker.service

| Attribut | Wert |
|----------|------|
| Datei existiert | JA (`/opt/nexify/anton-goose-bridge/systemd/nexify-goose-worker.service`) |
| In /etc/systemd/system/ | NEIN |
| Aktiv | NEIN |
| Entscheidung | `quarantined` (zusammen mit Bridge-Artefakten) |

---

## Artefakt 5: Environment-Konfiguration

| Attribut | Wert |
|----------|------|
| Existiert | NEIN |
| Notizen | Enthält keine Secrets, da nicht vorhanden. Muss bei Migration neu erstellt werden. |

---

## Artefakt 6: Log-Dateien

### /var/log/nexify/anton-goose-bridge/

| Attribut | Wert |
|----------|------|
| Existiert | JA (leer) |
| Entscheidung | `quarantined` |

### /var/log/nexify/goose-worker/

| Attribut | Wert |
|----------|------|
| Existiert | JA (leer) |
| Entscheidung | `quarantined` |

---

## Artefakt 7: Andere Systemd Services (Shadow Check)

| Service | Existiert | Aktiv | Notiz |
|---------|-----------|-------|-------|
| nexify-bridge.service | JA | ? | Bestehend, nicht Anton-spezifisch |
| goose-acp-server.service | JA | JA | Aktiv, separate Lösung |
| anton-cli-protect.service | JA | JA | Aktiv, separate Lösung |
| nexify-chat.service | JA (→/dev/null) | NEIN | Deaktiviert |

---

## Offene Blocker

1. **Project Manager Struktur**: Noch nicht angelegt. Sollte bewusst geplant werden, nicht überstürzt.
2. **Migrierte Teile**: Die JSON-Schemas aus der Bridge können in Project Manager übernommen werden, aber nicht jetzt.
3. **Shadow-Gefahr**: Keine Shadow-Systeme erkannt. Bestehende Services (goose-acp, bridge, anton-cli) sind separat und werden nicht berührt.

---

## Nächste Schritte

1. ✅ Anton-Goose-Bridge identifiziert und quarantänisiert
2. ⏳ Project Manager Struktur planen (nicht übereilt)
3. ⏳ Generische Bridge-Teile in Project Manager migrieren
4. ⏳ Env-Vorbereitung für Project Manager
5. ⏳ Systemd-Services für Project Manager erstellen
6. 🔄 Resource Catalog Update nach Abschluss

---

## Änderungshistorie

| Datum | Änderung | Autor |
|-------|----------|-------|
| 2026-05-25 | Initialer Entscheidungslog | Goose |
