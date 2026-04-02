# NeXifyAI Test Credentials

## Admin Account
- **Email**: p.courbois@icloud.com
- **Password**: NxAi#Secure2026!
- **Login Endpoint**: POST /api/admin/login (form-urlencoded: username=email&password=pw)
- **Returns**: JWT access_token

## API Base URL
- Preview: https://ai-architecture-lab.preview.emergentagent.com

## Routes
- Landing Page: /de (or /nl, /en)
- Admin Panel: /admin
- Customer Offer Portal: /angebot?token={magic_link_token}&qid={quote_id}

## Database
- MongoDB via MONGO_URL in backend/.env
- DB: DB_NAME from backend/.env
- Collections: leads, bookings, blocked_slots, inquiries, chat_sessions, admin_users, analytics, quotes, invoices, documents, access_links, audit_log, webhook_events, commercial_events, counters
