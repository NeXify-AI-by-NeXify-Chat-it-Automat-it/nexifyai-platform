# DNS-Manuelle Schritte — ai-fabrik.nexifyai.cloud

**Status:** Automatische DNS-Erstellung derzeit blockiert (Hostinger API 530/1016).  
**Aktion:** Einmalig manuell im Hostinger hPanel durchführen (~2 Minuten).

---

## Schritt-für-Schritt

### 1. Hostinger hPanel öffnen
- URL: https://hpanel.hostinger.com/
- Login: `p.courbois@icloud.com`
- Passwort: Ihr Standard-Passwort

### 2. Domain auswählen
- Im Dashboard auf **"nexifyai.cloud"** klicken
- Oder: Links im Menü → **Domains** → nexifyai.cloud

### 3. DNS-Zone bearbeiten
- Tab **"DNS / Nameserver"** wählen
- Button **"Eintrag hinzufügen"** klicken

### 4. Neuen A-Record anlegen
| Feld | Wert |
|------|------|
| Typ | **A** |
| Name | **ai-fabrik** |
| Weist auf | **72.62.152.47** |
| TTL | 3600 (Standard) |

⚠ **Wichtig:** Name = `ai-fabrik`, NICHT `ai-farbrik` (die existierende Domain mit 'r' ist ein Tippfehler).

### 5. Speichern & prüfen
- Auf **"Hinzufügen"** klicken
- DNS-Propagation dauert 5–60 Minuten
- Verifikation: `host ai-fabrik.nexifyai.cloud` muss `72.62.152.47` zurückgeben

### 6. SSL-Zertifikat (automatisch)
- Traefik holt das Let's Encrypt-Zertifikat automatisch beim ersten HTTPS-Aufruf
- Keine manuelle Aktion nötig
- Test: `curl -I https://ai-fabrik.nexifyai.cloud` → HTTP 200

---

## Nach der DNS-Einrichtung

1. `curl -I https://ai-fabrik.nexifyai.cloud` muss HTTP 200 liefern
2. Paperclip ist dann unter der korrekten Domain erreichbar
3. Die alte `ai-farbrik`-Domain bleibt als Redirect erhalten

---

## Fallback

Falls hPanel nicht erreichbar: Hostinger Support kontaktieren (support@hostinger.com).  
Vertragsdetails: VPS srv1243952.hstgr.cloud, Abo läuft bis 09.05.2026.

---

Erstellt: 08.05.2026 | Hermes Agent | NeXifyAI
