# NeXifyAI Test Credentials

## Admin Login
- **URL:** /admin
- **Email:** p.courbois@icloud.com
- **Password:** MUSS IN ENVIRONMENT VARIABLE GESETZT WERDEN

### Password Setup
Der Admin-Password-Hash muss in `/app/backend/.env` als `ADMIN_PASSWORD_HASH` gesetzt werden.

Beispiel zur Hash-Generierung:
```bash
python3 -c "import hashlib; print(hashlib.sha256('IHR_PASSWORT'.encode()).hexdigest())"
```

## API Testing
- Health: `curl http://localhost:8001/api/health`
- Admin (mit Auth): `curl -u "p.courbois@icloud.com:PASSWORD" http://localhost:8001/api/admin/stats`

## Resend Email Configuration
- Domain: send.nexify-automate.com
- API Key: In .env konfiguriert
- Sender: noreply@send.nexify-automate.com

## Notification Recipients
- support@nexify-automate.com
- nexifyai@nexifyai.de
