# NeXifyAI Test Credentials

## Admin Panel
- URL: /admin
- Email: p.courbois@icloud.com
- Password: NxAi#Secure2026!

## Test Customer
- Email: max@testfirma.de
- Unternehmen: Testfirma GmbH
- Contact ID: ct_6df55ae162a34cd3

## Test Booking
- ID: BK-20260403091914-E729A9
- Date: 2026-04-10, Time: 10:00

## API Base URL
- https://ai-architecture-lab.preview.emergentagent.com

## Auth Flow
- Login: POST /api/admin/login (form-data: username=email, password=password)
- Returns: { access_token, token_type: "bearer" }
- Use: Authorization: Bearer {access_token}
