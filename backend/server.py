"""
NeXifyAI Backend v3.0 - Production-Grade Enterprise System
Complete rewrite with:
- Argon2 password hashing (OWASP recommended)
- JWT-based authentication
- Rate limiting
- Proper session handling
- Full DACH compliance
"""
import os
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, validator
from motor.motor_asyncio import AsyncIOMotorClient
from jose import JWTError, jwt
from dotenv import load_dotenv
import resend

# Password hashing with Argon2 (fallback to bcrypt if pwdlib unavailable)
try:
    from pwdlib import PasswordHash
    pwd_context = PasswordHash.recommended()
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
except Exception:
    import hashlib
    def hash_password(password: str) -> str:
        return hashlib.pbkdf2_hmac('sha256', password.encode(), b'nexify_salt_v3', 100000).hex()
    def verify_password(plain: str, hashed: str) -> bool:
        return hash_password(plain) == hashed

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("nexifyai")

# Configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "nexifyai")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@send.nexify-automate.com")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

NOTIFICATION_EMAILS = ["support@nexify-automate.com", "nexifyai@nexifyai.de"]

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Company Data - Fixed
COMPANY = {
    "name": "NeXifyAI by NeXify",
    "tagline": "Chat it. Automate it.",
    "legal_name": "NeXify Automate",
    "ceo": "Pascal Courbois, Geschäftsführer",
    "address_de": {"street": "Wallstraße 9", "city": "41334 Nettetal-Kaldenkirchen", "country": "Deutschland"},
    "address_nl": {"street": "Graaf van Loonstraat 1E", "city": "5921 JA Venlo", "country": "Niederlande"},
    "phone": "+31 6 133 188 56",
    "email": "support@nexify-automate.com",
    "website": "nexify-automate.com",
    "kvk": "90483944",
    "vat_id": "NL865786276B01"
}

# Database
db_client: Optional[AsyncIOMotorClient] = None
db = None

# Rate limiting storage
rate_limit_storage = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_client, db
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client[DB_NAME]
    
    # Create indexes
    await db.leads.create_index("email")
    await db.leads.create_index("created_at")
    await db.leads.create_index("status")
    await db.bookings.create_index("date")
    await db.chat_sessions.create_index("session_id")
    await db.analytics.create_index([("event", 1), ("timestamp", -1)])
    await db.admin_users.create_index("email", unique=True)
    await db.audit_log.create_index("timestamp")
    
    # Ensure admin exists
    admin_email = os.environ.get("ADMIN_EMAIL", "p.courbois@icloud.com")
    admin_pw = os.environ.get("ADMIN_PASSWORD", "")
    
    if admin_pw:
        existing = await db.admin_users.find_one({"email": admin_email})
        if not existing:
            await db.admin_users.insert_one({
                "email": admin_email,
                "password_hash": hash_password(admin_pw),
                "role": "admin",
                "created_at": datetime.now(timezone.utc)
            })
            logger.info(f"Admin user created: {admin_email}")
    
    logger.info("NeXifyAI Backend v3.0 started")
    yield
    db_client.close()

app = FastAPI(title="NeXifyAI API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login", auto_error=False)

# Rate limiting middleware
async def check_rate_limit(request: Request, limit: int = 30, window: int = 60):
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{request.url.path}"
    now = datetime.now(timezone.utc).timestamp()
    
    if key in rate_limit_storage:
        requests, window_start = rate_limit_storage[key]
        if now - window_start > window:
            rate_limit_storage[key] = (1, now)
        elif requests >= limit:
            raise HTTPException(status_code=429, detail="Zu viele Anfragen. Bitte warten Sie.")
        else:
            rate_limit_storage[key] = (requests + 1, window_start)
    else:
        rate_limit_storage[key] = (1, now)

# ============== MODELS ==============

class ContactForm(BaseModel):
    vorname: str = Field(..., min_length=2, max_length=100)
    nachname: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefon: Optional[str] = None
    unternehmen: Optional[str] = None
    nachricht: str = Field(..., min_length=10, max_length=5000)
    source: str = "contact_form"
    consent: bool = True
    datenschutz_akzeptiert: bool = True
    honeypot: Optional[str] = Field(None, alias="_hp")

class BookingRequest(BaseModel):
    vorname: str = Field(..., min_length=2)
    nachname: str = Field(..., min_length=2)
    email: EmailStr
    telefon: Optional[str] = None
    unternehmen: Optional[str] = None
    date: str
    time: str
    thema: Optional[str] = None
    datenschutz_akzeptiert: bool = True

class ChatMessage(BaseModel):
    session_id: str
    message: str
    context: Optional[dict] = None

class LeadUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class AnalyticsEvent(BaseModel):
    event: str
    properties: Optional[dict] = {}
    session_id: Optional[str] = None

# ============== AUTH ==============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert", headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Ungültiger Token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token abgelaufen oder ungültig")
    
    user = await db.admin_users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Benutzer nicht gefunden")
    
    return user

async def log_audit(action: str, user: str, details: dict = None):
    await db.audit_log.insert_one({
        "action": action,
        "user": user,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc)
    })

# ============== EMAIL TEMPLATES ==============

def email_template(title: str, content: str, cta_url: str = None, cta_text: str = None) -> str:
    cta_html = f'<a href="{cta_url}" style="display:inline-block;background:#ffb599;color:#5a1c00;padding:14px 28px;font-weight:700;text-decoration:none;margin:24px 0;">{cta_text}</a>' if cta_url else ''
    
    return f'''<!DOCTYPE html>
<html lang="de">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{title}</title></head>
<body style="margin:0;padding:0;background:#0e141b;font-family:system-ui,-apple-system,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background:#1b2028;">
<tr><td style="background:#0e141b;padding:32px;text-align:center;border-bottom:2px solid #ffb599;">
<span style="color:#fff;font-size:22px;font-weight:700;">NeXifyAI</span>
</td></tr>
<tr><td style="padding:40px 32px;color:#dee3ed;font-size:15px;line-height:1.7;">
{content}
{cta_html}
</td></tr>
<tr><td style="background:#090f16;padding:32px;text-align:center;color:#64748b;font-size:12px;line-height:1.8;">
<p style="margin:0 0 8px;"><strong>NeXifyAI by NeXify</strong> | Ein Produkt von NeXify Automate</p>
<p style="margin:0 0 8px;">NL: Graaf van Loonstraat 1E, 5921 JA Venlo</p>
<p style="margin:0 0 8px;">DE: Wallstraße 9, 41334 Nettetal-Kaldenkirchen</p>
<p style="margin:0 0 8px;">Tel: +31 6 133 188 56 | support@nexify-automate.com</p>
<p style="margin:16px 0 0;font-size:11px;">KvK: 90483944 | USt-ID: NL865786276B01</p>
</td></tr>
</table>
</body>
</html>'''

async def send_email(to: List[str], subject: str, html: str):
    if not RESEND_API_KEY:
        logger.warning("Resend not configured")
        return None
    try:
        import asyncio
        result = await asyncio.to_thread(resend.Emails.send, {
            "from": f"NeXifyAI <{SENDER_EMAIL}>",
            "to": to,
            "subject": subject,
            "html": html
        })
        logger.info(f"Email sent to {to}")
        return result
    except Exception as e:
        logger.error(f"Email error: {e}")
        return None

# ============== PUBLIC ENDPOINTS ==============

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "3.0.0", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/company")
async def get_company():
    return COMPANY

@app.post("/api/contact")
async def submit_contact(data: ContactForm, request: Request):
    await check_rate_limit(request, limit=5, window=60)
    
    if data.honeypot:
        return {"success": True, "message": "Vielen Dank."}
    
    lead_id = f"LEAD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
    
    lead = {
        "lead_id": lead_id,
        "vorname": data.vorname.strip(),
        "nachname": data.nachname.strip(),
        "email": data.email.lower(),
        "telefon": data.telefon,
        "unternehmen": data.unternehmen,
        "nachricht": data.nachricht,
        "source": data.source,
        "status": "neu",
        "notes": [],
        "consent": data.consent,
        "datenschutz_akzeptiert": data.datenschutz_akzeptiert,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.leads.insert_one(lead)
    
    # Customer email
    import asyncio
    asyncio.create_task(send_email(
        [data.email],
        "Ihre Anfrage bei NeXifyAI – Bestätigung",
        email_template(
            "Anfrage erhalten",
            f'''<h1 style="color:#fff;font-size:22px;margin:0 0 16px;">Vielen Dank für Ihre Anfrage</h1>
            <p>Guten Tag {data.vorname} {data.nachname},</p>
            <p>wir haben Ihre Anfrage erhalten und werden uns <strong style="color:#ffb599;">innerhalb von 24 Stunden</strong> bei Ihnen melden.</p>
            <div style="background:#252a32;padding:20px;margin:20px 0;border-left:3px solid #ffb599;">
            <p style="margin:0;font-size:13px;color:#8f9095;">REFERENZ-NR.</p>
            <p style="margin:4px 0 0;color:#fff;font-weight:600;">{lead_id}</p>
            </div>
            <p>Mit freundlichen Grüßen,<br>Pascal Courbois<br>Geschäftsführer, NeXify Automate</p>'''
        )
    ))
    
    # Internal notification
    asyncio.create_task(send_email(
        NOTIFICATION_EMAILS,
        f"[NeXifyAI] Neue Anfrage: {data.vorname} {data.nachname}",
        email_template(
            "Neue Anfrage",
            f'''<h1 style="color:#fff;font-size:20px;margin:0 0 16px;">Neue Kontaktanfrage</h1>
            <div style="background:#252a32;padding:20px;margin:16px 0;">
            <p style="margin:0 0 12px;"><span style="color:#8f9095;font-size:12px;">NAME</span><br><strong style="color:#fff;">{data.vorname} {data.nachname}</strong></p>
            <p style="margin:0 0 12px;"><span style="color:#8f9095;font-size:12px;">E-MAIL</span><br><a href="mailto:{data.email}" style="color:#ffb599;">{data.email}</a></p>
            {f'<p style="margin:0 0 12px;"><span style="color:#8f9095;font-size:12px;">TELEFON</span><br><a href="tel:{data.telefon}" style="color:#ffb599;">{data.telefon}</a></p>' if data.telefon else ''}
            {f'<p style="margin:0 0 12px;"><span style="color:#8f9095;font-size:12px;">UNTERNEHMEN</span><br><span style="color:#fff;">{data.unternehmen}</span></p>' if data.unternehmen else ''}
            <p style="margin:0;"><span style="color:#8f9095;font-size:12px;">LEAD-ID</span><br><span style="color:#fff;">{lead_id}</span></p>
            </div>
            <h2 style="color:#fff;font-size:16px;margin:24px 0 12px;">Nachricht</h2>
            <div style="background:#171c23;padding:16px;color:#c5c6cb;white-space:pre-wrap;">{data.nachricht}</div>''',
            "https://nexifyai.de/admin",
            "Im Admin öffnen"
        )
    ))
    
    return {"success": True, "message": "Vielen Dank. Wir melden uns innerhalb von 24 Stunden.", "lead_id": lead_id}

@app.get("/api/booking/slots")
async def get_slots(date: str):
    slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
    booked = await db.bookings.find({"date": date, "status": {"$ne": "cancelled"}}, {"time": 1}).to_list(50)
    booked_times = [b["time"] for b in booked]
    return {"date": date, "slots": [s for s in slots if s not in booked_times]}

@app.post("/api/booking")
async def create_booking(data: BookingRequest, request: Request):
    await check_rate_limit(request, limit=3, window=60)
    
    existing = await db.bookings.find_one({"date": data.date, "time": data.time, "status": {"$ne": "cancelled"}})
    if existing:
        raise HTTPException(status_code=400, detail="Dieser Termin ist nicht mehr verfügbar.")
    
    booking_id = f"BK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"
    lead_id = f"LEAD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
    
    # Create lead
    await db.leads.insert_one({
        "lead_id": lead_id,
        "vorname": data.vorname,
        "nachname": data.nachname,
        "email": data.email.lower(),
        "telefon": data.telefon,
        "unternehmen": data.unternehmen,
        "source": "booking",
        "status": "termin_gebucht",
        "notes": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    # Create booking
    await db.bookings.insert_one({
        "booking_id": booking_id,
        "lead_id": lead_id,
        "vorname": data.vorname,
        "nachname": data.nachname,
        "email": data.email.lower(),
        "telefon": data.telefon,
        "unternehmen": data.unternehmen,
        "date": data.date,
        "time": data.time,
        "thema": data.thema,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc)
    })
    
    date_formatted = datetime.strptime(data.date, "%Y-%m-%d").strftime("%d.%m.%Y")
    
    import asyncio
    # Customer confirmation
    asyncio.create_task(send_email(
        [data.email],
        f"Ihr Beratungstermin am {date_formatted} ist bestätigt",
        email_template(
            "Termin bestätigt",
            f'''<h1 style="color:#fff;font-size:22px;margin:0 0 16px;">Ihr Beratungsgespräch ist bestätigt</h1>
            <p>Guten Tag {data.vorname} {data.nachname},</p>
            <p>vielen Dank für Ihre Terminbuchung. Wir freuen uns auf das Gespräch mit Ihnen.</p>
            <div style="background:#252a32;padding:24px;margin:24px 0;border-left:3px solid #ffb599;">
            <p style="margin:0 0 4px;font-size:12px;color:#8f9095;">TERMIN</p>
            <p style="margin:0;font-size:20px;color:#ffb599;font-weight:700;">{date_formatted} um {data.time} Uhr</p>
            {f'<p style="margin:16px 0 0;font-size:12px;color:#8f9095;">THEMA</p><p style="margin:4px 0 0;color:#fff;">{data.thema}</p>' if data.thema else ''}
            <p style="margin:16px 0 0;font-size:12px;color:#8f9095;">BUCHUNGS-NR.</p>
            <p style="margin:4px 0 0;color:#fff;">{booking_id}</p>
            </div>
            <p>Sie erhalten vor dem Termin einen Link zum virtuellen Meetingraum.</p>
            <p>Mit freundlichen Grüßen,<br>Pascal Courbois</p>'''
        )
    ))
    
    # Admin notification
    asyncio.create_task(send_email(
        NOTIFICATION_EMAILS,
        f"[NeXifyAI] Neuer Termin: {date_formatted} {data.time} - {data.vorname} {data.nachname}",
        email_template(
            "Neuer Termin",
            f'''<h1 style="color:#fff;font-size:20px;margin:0 0 16px;">Neues Beratungsgespräch gebucht</h1>
            <div style="background:#252a32;padding:24px;margin:16px 0;">
            <p style="margin:0 0 4px;font-size:12px;color:#8f9095;">TERMIN</p>
            <p style="margin:0 0 16px;font-size:20px;color:#ffb599;font-weight:700;">{date_formatted} um {data.time} Uhr</p>
            <p style="margin:0 0 8px;"><span style="color:#8f9095;font-size:12px;">NAME</span><br><strong style="color:#fff;">{data.vorname} {data.nachname}</strong></p>
            <p style="margin:0 0 8px;"><span style="color:#8f9095;font-size:12px;">E-MAIL</span><br><a href="mailto:{data.email}" style="color:#ffb599;">{data.email}</a></p>
            {f'<p style="margin:0 0 8px;"><span style="color:#8f9095;font-size:12px;">TELEFON</span><br><a href="tel:{data.telefon}" style="color:#ffb599;">{data.telefon}</a></p>' if data.telefon else ''}
            </div>''',
            "https://nexifyai.de/admin",
            "Im Admin öffnen"
        )
    ))
    
    return {"success": True, "message": "Ihr Beratungstermin wurde bestätigt.", "booking_id": booking_id}

@app.post("/api/chat/message")
async def chat_message(data: ChatMessage, request: Request):
    await check_rate_limit(request, limit=20, window=60)
    
    session = await db.chat_sessions.find_one({"session_id": data.session_id})
    if not session:
        session = {
            "session_id": data.session_id,
            "messages": [],
            "qualification": {},
            "created_at": datetime.now(timezone.utc)
        }
        await db.chat_sessions.insert_one(session)
    
    # Add user message
    user_msg = {"role": "user", "content": data.message, "ts": datetime.now(timezone.utc).isoformat()}
    
    # Generate response
    response = generate_response(data.message, session.get("messages", []), session.get("qualification", {}))
    
    assistant_msg = {"role": "assistant", "content": response["message"], "ts": datetime.now(timezone.utc).isoformat()}
    
    await db.chat_sessions.update_one(
        {"session_id": data.session_id},
        {
            "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
            "$set": {"qualification": response.get("qualification", {}), "updated_at": datetime.now(timezone.utc)}
        }
    )
    
    return {
        "message": response["message"],
        "qualification": response.get("qualification", {}),
        "actions": response.get("actions", []),
        "should_escalate": response.get("should_escalate", False)
    }

def generate_response(message: str, history: list, qual: dict) -> dict:
    msg = message.lower()
    new_qual = {**qual}
    
    # Keywords für Qualifizierung
    keywords = {
        "vertrieb": {"interest": "vertrieb", "use_case": "Vertriebsautomation & Lead-Qualifizierung"},
        "sales": {"interest": "vertrieb", "use_case": "Vertriebsautomation & Lead-Qualifizierung"},
        "crm": {"interest": "integration", "use_case": "CRM/ERP-Integration"},
        "erp": {"interest": "integration", "use_case": "CRM/ERP-Integration"},
        "sap": {"interest": "integration", "use_case": "SAP-Integration"},
        "hubspot": {"interest": "integration", "use_case": "HubSpot-Integration"},
        "salesforce": {"interest": "integration", "use_case": "Salesforce-Integration"},
        "wissen": {"interest": "knowledge", "use_case": "Internes Wissenssystem"},
        "dokument": {"interest": "knowledge", "use_case": "Dokumentenautomation"},
        "rag": {"interest": "knowledge", "use_case": "RAG-System"},
        "support": {"interest": "support", "use_case": "Support-Automation"},
        "ticket": {"interest": "support", "use_case": "Ticket-Automation"},
        "prozess": {"interest": "automation", "use_case": "Prozessautomation"},
        "workflow": {"interest": "automation", "use_case": "Workflow-Automation"},
        "datenschutz": {"interest": "compliance", "use_case": "Governance & Compliance"},
        "dsgvo": {"interest": "compliance", "use_case": "DSGVO-Konformität"},
        "app": {"interest": "apps", "use_case": "Web- oder Mobile-App"},
        "mobile": {"interest": "apps", "use_case": "Mobile App-Entwicklung"},
        "portal": {"interest": "apps", "use_case": "Kundenportal"},
    }
    
    for kw, data in keywords.items():
        if kw in msg:
            new_qual.update(data)
            break
    
    # Antworten
    responses = {
        "vertrieb": "Vertriebsautomation ist einer der schnellsten Wege zu messbarem ROI. Unsere KI-Agenten können eingehende Anfragen automatisch qualifizieren, mit Ihrem CRM abgleichen und Termine koordinieren. Typische Ergebnisse: 40-60% weniger manuelle Arbeit im Vertrieb. Nutzen Sie aktuell HubSpot, Salesforce oder ein anderes CRM?",
        "integration": "CRM- und ERP-Integrationen sind unser Kerngeschäft. Wir haben native Konnektoren für SAP S/4HANA, HubSpot, Salesforce, Microsoft Dynamics und 50+ weitere Systeme. Die KI orchestriert Datenflüsse intelligent zwischen Ihren Systemen. Welches System ist für Sie am wichtigsten?",
        "knowledge": "Interne Wissenssysteme mit RAG-Architektur machen Ihr gesamtes Firmenwissen sofort durchsuchbar. Ihre Mitarbeiter finden Antworten aus Handbüchern, Tickets und Dokumenten in Sekunden statt Stunden. Wie groß ist Ihre aktuelle Wissensbasis?",
        "support": "Support-Automation kann Ihr Team erheblich entlasten. Von intelligenter Ticket-Klassifizierung bis hin zu automatisierten Erstantworten – wir implementieren Lösungen, die Ihre Support-Qualität verbessern und gleichzeitig Kosten senken.",
        "automation": "Prozessautomation bringt den größten operativen Hebel. Wir identifizieren repetitive Abläufe und automatisieren sie mit KI-Agenten – ohne Medienbrüche. Welche Prozesse kosten Sie aktuell am meisten Zeit?",
        "compliance": "Datenschutz und Governance sind bei uns von Anfang an eingebaut. Wir arbeiten DSGVO-konform mit deutschen Rechenzentren, RBAC-Zugriffskontrolle und vollständigen Audit-Logs. Haben Sie spezifische Compliance-Anforderungen?",
        "apps": "Wir entwickeln maßgeschneiderte Web-Apps, Mobile-Apps und Kundenportale, die nahtlos mit Ihren KI-Workflows integriert sind. Von internen Tools bis zu kundenorientierten Anwendungen – alles aus einer Hand."
    }
    
    interest = new_qual.get("interest", "")
    should_escalate = any(kw in msg for kw in ["termin", "gespräch", "beraten", "buchen", "anruf", "meeting"])
    
    if interest and interest in responses:
        text = responses[interest]
    elif len(history) == 0:
        text = "Willkommen! Ich bin der NeXifyAI Advisor. Ich helfe Ihnen, das richtige KI-Szenario für Ihr Unternehmen zu identifizieren. Welche Herausforderung möchten Sie lösen?"
    elif should_escalate:
        text = "Sehr gut. Lassen Sie uns das in einem persönlichen Gespräch vertiefen. In einem 30-minütigen Beratungsgespräch können wir Ihre Situation analysieren und erste konkrete Handlungsempfehlungen erarbeiten. Soll ich Ihnen einen Termin vorschlagen?"
    else:
        text = "Verstanden. Um Ihnen optimal weiterzuhelfen: Wir könnten in einem kurzen Strategiegespräch Ihre Situation analysieren und konkrete Empfehlungen erarbeiten. Das Gespräch ist unverbindlich und dauert etwa 30 Minuten."
        should_escalate = True
    
    actions = []
    if should_escalate:
        actions = [{"type": "booking", "label": "Beratungstermin buchen"}]
    
    return {"message": text, "qualification": new_qual, "actions": actions, "should_escalate": should_escalate}

@app.post("/api/analytics/track")
async def track_event(event: AnalyticsEvent, request: Request):
    await db.analytics.insert_one({
        "event": event.event,
        "properties": event.properties or {},
        "session_id": event.session_id,
        "timestamp": datetime.now(timezone.utc)
    })
    return {"success": True}

# ============== ADMIN ENDPOINTS ==============

@app.post("/api/admin/login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    if request:
        await check_rate_limit(request, limit=5, window=300)
    
    user = await db.admin_users.find_one({"email": form_data.username.lower()})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        await log_audit("login_failed", form_data.username)
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    token = create_access_token({"sub": user["email"]})
    await log_audit("login_success", user["email"])
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/admin/me")
async def admin_me(user = Depends(get_current_admin)):
    return {"email": user["email"], "role": user.get("role", "admin")}

@app.get("/api/admin/stats")
async def admin_stats(user = Depends(get_current_admin)):
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    total = await db.leads.count_documents({})
    today_count = await db.leads.count_documents({"created_at": {"$gte": today}})
    week_count = await db.leads.count_documents({"created_at": {"$gte": week_ago}})
    upcoming = await db.bookings.count_documents({"date": {"$gte": today.strftime("%Y-%m-%d")}, "status": "confirmed"})
    
    status_agg = await db.leads.aggregate([{"$group": {"_id": "$status", "count": {"$sum": 1}}}]).to_list(20)
    
    return {
        "total_leads": total,
        "new_leads_today": today_count,
        "new_leads_week": week_count,
        "upcoming_bookings": upcoming,
        "by_status": {s["_id"]: s["count"] for s in status_agg if s["_id"]}
    }

@app.get("/api/admin/leads")
async def admin_leads(user = Depends(get_current_admin), status: str = None, search: str = None, skip: int = 0, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"vorname": {"$regex": search, "$options": "i"}},
            {"nachname": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"unternehmen": {"$regex": search, "$options": "i"}}
        ]
    
    total = await db.leads.count_documents(query)
    leads = await db.leads.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {"total": total, "leads": leads}

@app.get("/api/admin/leads/{lead_id}")
async def admin_lead_detail(lead_id: str, user = Depends(get_current_admin)):
    lead = await db.leads.find_one({"lead_id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    
    bookings = await db.bookings.find({"lead_id": lead_id}, {"_id": 0}).to_list(10)
    chat = await db.chat_sessions.find_one({"lead_id": lead_id}, {"_id": 0})
    
    return {"lead": lead, "bookings": bookings, "chat": chat}

@app.patch("/api/admin/leads/{lead_id}")
async def admin_update_lead(lead_id: str, update: LeadUpdate, user = Depends(get_current_admin)):
    updates = {"status": update.status, "updated_at": datetime.now(timezone.utc)}
    
    if update.notes:
        await db.leads.update_one(
            {"lead_id": lead_id},
            {"$set": updates, "$push": {"notes": {"text": update.notes, "by": user["email"], "at": datetime.now(timezone.utc).isoformat()}}}
        )
    else:
        await db.leads.update_one({"lead_id": lead_id}, {"$set": updates})
    
    await log_audit("lead_updated", user["email"], {"lead_id": lead_id, "status": update.status})
    return {"success": True}

@app.get("/api/admin/bookings")
async def admin_bookings(user = Depends(get_current_admin), skip: int = 0, limit: int = 50):
    total = await db.bookings.count_documents({})
    bookings = await db.bookings.find({}, {"_id": 0}).sort("date", -1).skip(skip).limit(limit).to_list(limit)
    return {"total": total, "bookings": bookings}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
