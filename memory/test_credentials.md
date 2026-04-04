# Test Credentials

## Admin Account
- Email: p.courbois@icloud.com
- Password: 1def!xO2022!!
- Login Endpoint: POST /api/admin/login (OAuth2 form-encoded: username=email&password=pw)
- Login Flow: Email -> "Weiter" -> Role Selection ("Administration") -> Password -> "Anmelden"

## App URL
- Preview: https://contract-os.preview.emergentagent.com
- Admin Panel: https://contract-os.preview.emergentagent.com/admin
- Login Page: https://contract-os.preview.emergentagent.com/login

## API Testing
- Auth: curl -X POST "$URL/api/admin/login" -H "Content-Type: application/x-www-form-urlencoded" -d 'username=p.courbois@icloud.com&password=1def!xO2022!!'
- Outbound Pipeline: GET /api/admin/outbound/pipeline
- Outbound Leads: GET /api/admin/outbound/leads
- Discover Lead: POST /api/admin/outbound/discover
- Projects: GET /api/admin/projects
- Contracts: GET /api/admin/contracts
- Stats: GET /api/admin/stats
