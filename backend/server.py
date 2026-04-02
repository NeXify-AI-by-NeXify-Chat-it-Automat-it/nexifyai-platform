"""
NeXifyAI Backend - Complete Enterprise Landing Page API
Full-featured backend with:
- Contact form handling
- Email notifications via Resend
- Calendar booking system
- Admin CRM with authentication
- Lead management
- Analytics tracking
"""
import os
import asyncio
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import resend

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexifyai")

# Configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "nexifyai")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@send.nexify-automate.com")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "p.courbois@icloud.com")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
NOTIFICATION_EMAILS = ["support@nexify-automate.com", "nexifyai@nexifyai.de"]

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Company Data
COMPANY = {
    "name": "NeXifyAI by NeXify",
    "tagline": "Chat it. Automate it.",
    "legal_name": "NeXify Automate",
    "ceo": "Pascal Courbois, Geschäftsführer",
    "address_de": {
        "street": "Wallstraße 9",
        "city": "41334 Nettetal-Kaldenkirchen",
        "country": "Deutschland"
    },
    "address_nl": {
        "street": "Graaf van Loonstraat 1E",
        "city": "5921 JA Venlo",
        "country": "Niederlande"
    },
    "phone": "+31 6 133 188 56",
    "email": "support@nexify-automate.com",
    "website": "nexify-automate.com",
    "kvk": "90483944",
    "vat_id": "NL865786276B01"
}

# Database
db_client: Optional[AsyncIOMotorClient] = None
db = None

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
    await db.bookings.create_index("lead_id")
    await db.analytics.create_index("event")
    await db.analytics.create_index("timestamp")
    logger.info("Database connected and indexes created")
    yield
    db_client.close()

app = FastAPI(
    title="NeXifyAI API",
    version="2.0.0",
    description="Enterprise AI Landing Page Backend",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBasic()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if not ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="Admin not configured")
    
    password_hash = hash_password(credentials.password)
    if credentials.username != ADMIN_EMAIL or password_hash != ADMIN_PASSWORD_HASH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

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
    honeypot: Optional[str] = Field(None, alias="_hp")
    
    @validator('vorname', 'nachname')
    def clean_name(cls, v):
        return v.strip()

class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str
    timestamp: datetime = None

class ChatLead(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    qualification: Optional[dict] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None

class BookingRequest(BaseModel):
    lead_id: Optional[str] = None
    vorname: str = Field(..., min_length=2)
    nachname: str = Field(..., min_length=2)
    email: EmailStr
    telefon: Optional[str] = None
    unternehmen: Optional[str] = None
    date: str  # ISO date
    time: str  # HH:MM
    thema: Optional[str] = None
    notes: Optional[str] = None

class LeadStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class AnalyticsEvent(BaseModel):
    event: str
    properties: Optional[dict] = {}
    session_id: Optional[str] = None
    page: Optional[str] = None

# ============== EMAIL TEMPLATES ==============

def get_email_template(template_type: str, data: dict) -> str:
    """Generate branded HTML email templates"""
    
    base_style = """
    <style>
        body { font-family: 'Inter', Arial, sans-serif; margin: 0; padding: 0; background-color: #0e141b; }
        .container { max-width: 600px; margin: 0 auto; background-color: #1b2028; }
        .header { background-color: #0e141b; padding: 30px; text-align: center; border-bottom: 2px solid #ffb599; }
        .logo { color: #ffffff; font-size: 24px; font-weight: bold; }
        .logo-mark { display: inline-block; width: 8px; height: 24px; background-color: #ffb599; margin-right: 8px; vertical-align: middle; }
        .content { padding: 40px 30px; color: #dee3ed; }
        .content h1 { color: #ffffff; font-size: 24px; margin-bottom: 20px; }
        .content p { line-height: 1.7; margin-bottom: 15px; }
        .highlight { color: #ffb599; }
        .data-box { background-color: #252a32; padding: 20px; margin: 20px 0; border-left: 3px solid #ffb599; }
        .data-row { margin-bottom: 10px; }
        .data-label { color: #8f9095; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
        .data-value { color: #ffffff; font-size: 14px; margin-top: 4px; }
        .cta-button { display: inline-block; background-color: #ffb599; color: #5a1c00; padding: 15px 30px; text-decoration: none; font-weight: bold; margin: 20px 0; }
        .footer { background-color: #090f16; padding: 30px; text-align: center; color: #64748b; font-size: 12px; }
        .footer a { color: #ffb599; text-decoration: none; }
        .divider { height: 1px; background-color: #30353d; margin: 30px 0; }
    </style>
    """
    
    footer = f"""
    <div class="footer">
        <p><strong>{COMPANY['name']}</strong><br>{COMPANY['tagline']}</p>
        <p>Ein Produkt von {COMPANY['legal_name']}</p>
        <div class="divider"></div>
        <p>
            <strong>NL:</strong> {COMPANY['address_nl']['street']}, {COMPANY['address_nl']['city']}<br>
            <strong>DE:</strong> {COMPANY['address_de']['street']}, {COMPANY['address_de']['city']}
        </p>
        <p>
            Tel: <a href="tel:{COMPANY['phone'].replace(' ', '')}">{COMPANY['phone']}</a><br>
            E-Mail: <a href="mailto:{COMPANY['email']}">{COMPANY['email']}</a><br>
            Web: <a href="https://{COMPANY['website']}">{COMPANY['website']}</a>
        </p>
        <p style="margin-top: 20px;">KvK: {COMPANY['kvk']} | USt-ID: {COMPANY['vat_id']}</p>
    </div>
    """
    
    if template_type == "contact_confirmation":
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
        <div class="container">
            <div class="header">
                <span class="logo"><span class="logo-mark"></span>NeXifyAI</span>
            </div>
            <div class="content">
                <h1>Vielen Dank für Ihre Anfrage</h1>
                <p>Guten Tag {data.get('vorname', '')} {data.get('nachname', '')},</p>
                <p>wir haben Ihre Anfrage erhalten und werden uns <span class="highlight">innerhalb von 24 Stunden</span> bei Ihnen melden.</p>
                <div class="data-box">
                    <div class="data-row">
                        <div class="data-label">Ihre Nachricht</div>
                        <div class="data-value">{data.get('nachricht', '')[:200]}...</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">Referenz-Nr.</div>
                        <div class="data-value">{data.get('lead_id', '')}</div>
                    </div>
                </div>
                <p>Falls Sie in der Zwischenzeit Fragen haben, können Sie uns jederzeit kontaktieren.</p>
                <a href="https://nexify-automate.com" class="cta-button">Zur Website</a>
            </div>
            {footer}
        </div>
        </body>
        </html>
        """
    
    elif template_type == "internal_notification":
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
        <div class="container">
            <div class="header">
                <span class="logo"><span class="logo-mark"></span>NeXifyAI - Neue Anfrage</span>
            </div>
            <div class="content">
                <h1>Neue Kontaktanfrage eingegangen</h1>
                <div class="data-box">
                    <div class="data-row">
                        <div class="data-label">Name</div>
                        <div class="data-value">{data.get('vorname', '')} {data.get('nachname', '')}</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">E-Mail</div>
                        <div class="data-value"><a href="mailto:{data.get('email', '')}">{data.get('email', '')}</a></div>
                    </div>
                    {f'<div class="data-row"><div class="data-label">Telefon</div><div class="data-value"><a href="tel:{data.get("telefon", "")}">{data.get("telefon", "")}</a></div></div>' if data.get('telefon') else ''}
                    {f'<div class="data-row"><div class="data-label">Unternehmen</div><div class="data-value">{data.get("unternehmen", "")}</div></div>' if data.get('unternehmen') else ''}
                    <div class="data-row">
                        <div class="data-label">Quelle</div>
                        <div class="data-value">{data.get('source', 'Kontaktformular')}</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">Lead-ID</div>
                        <div class="data-value">{data.get('lead_id', '')}</div>
                    </div>
                </div>
                <h2 style="color: #ffffff; font-size: 18px;">Nachricht</h2>
                <div class="data-box">
                    <p style="white-space: pre-wrap;">{data.get('nachricht', '')}</p>
                </div>
                <a href="https://nexify-automate.com/admin" class="cta-button">Im Admin öffnen</a>
            </div>
            {footer}
        </div>
        </body>
        </html>
        """
    
    elif template_type == "booking_confirmation":
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
        <div class="container">
            <div class="header">
                <span class="logo"><span class="logo-mark"></span>NeXifyAI</span>
            </div>
            <div class="content">
                <h1>Ihr Beratungsgespräch ist bestätigt</h1>
                <p>Guten Tag {data.get('vorname', '')} {data.get('nachname', '')},</p>
                <p>vielen Dank für Ihre Terminbuchung. Wir freuen uns auf das Gespräch mit Ihnen.</p>
                <div class="data-box">
                    <div class="data-row">
                        <div class="data-label">Datum</div>
                        <div class="data-value" style="font-size: 18px; color: #ffb599;">{data.get('date', '')}</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">Uhrzeit</div>
                        <div class="data-value" style="font-size: 18px; color: #ffb599;">{data.get('time', '')} Uhr</div>
                    </div>
                    {f'<div class="data-row"><div class="data-label">Thema</div><div class="data-value">{data.get("thema", "")}</div></div>' if data.get('thema') else ''}
                    <div class="data-row">
                        <div class="data-label">Buchungs-Nr.</div>
                        <div class="data-value">{data.get('booking_id', '')}</div>
                    </div>
                </div>
                <p>Sie erhalten kurz vor dem Termin einen Link zum virtuellen Meetingraum. Bei Rückfragen stehen wir Ihnen gerne zur Verfügung.</p>
                <p><strong>Pascal Courbois</strong><br>Geschäftsführer, NeXify Automate</p>
            </div>
            {footer}
        </div>
        </body>
        </html>
        """
    
    elif template_type == "booking_notification":
        return f"""
        <!DOCTYPE html>
        <html>
        <head>{base_style}</head>
        <body>
        <div class="container">
            <div class="header">
                <span class="logo"><span class="logo-mark"></span>NeXifyAI - Neue Buchung</span>
            </div>
            <div class="content">
                <h1>Neues Beratungsgespräch gebucht</h1>
                <div class="data-box">
                    <div class="data-row">
                        <div class="data-label">Termin</div>
                        <div class="data-value" style="font-size: 18px; color: #ffb599;">{data.get('date', '')} um {data.get('time', '')} Uhr</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">Name</div>
                        <div class="data-value">{data.get('vorname', '')} {data.get('nachname', '')}</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">E-Mail</div>
                        <div class="data-value"><a href="mailto:{data.get('email', '')}">{data.get('email', '')}</a></div>
                    </div>
                    {f'<div class="data-row"><div class="data-label">Telefon</div><div class="data-value"><a href="tel:{data.get("telefon", "")}">{data.get("telefon", "")}</a></div></div>' if data.get('telefon') else ''}
                    {f'<div class="data-row"><div class="data-label">Unternehmen</div><div class="data-value">{data.get("unternehmen", "")}</div></div>' if data.get('unternehmen') else ''}
                    {f'<div class="data-row"><div class="data-label">Thema</div><div class="data-value">{data.get("thema", "")}</div></div>' if data.get('thema') else ''}
                    <div class="data-row">
                        <div class="data-label">Buchungs-Nr.</div>
                        <div class="data-value">{data.get('booking_id', '')}</div>
                    </div>
                </div>
                <a href="https://nexify-automate.com/admin" class="cta-button">Im Admin öffnen</a>
            </div>
            {footer}
        </div>
        </body>
        </html>
        """
    
    return ""

async def send_email_async(to: List[str], subject: str, html: str):
    """Send email asynchronously via Resend"""
    if not RESEND_API_KEY:
        logger.warning("Resend API key not configured, skipping email")
        return None
    
    try:
        params = {
            "from": f"NeXifyAI <{SENDER_EMAIL}>",
            "to": to,
            "subject": subject,
            "html": html
        }
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent successfully to {to}: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return None

# ============== API ENDPOINTS ==============

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "NeXifyAI API v2.0"
    }

@app.get("/api/company")
async def get_company():
    return COMPANY

# Contact Form
@app.post("/api/contact")
async def submit_contact(data: ContactForm):
    # Honeypot check
    if data.honeypot:
        logger.warning(f"Honeypot triggered from {data.email}")
        return {"success": True, "message": "Vielen Dank für Ihre Anfrage."}
    
    lead_id = f"LEAD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
    
    lead_doc = {
        "lead_id": lead_id,
        "vorname": data.vorname,
        "nachname": data.nachname,
        "email": data.email,
        "telefon": data.telefon,
        "unternehmen": data.unternehmen,
        "nachricht": data.nachricht,
        "source": data.source,
        "status": "neu",
        "notes": [],
        "consent": data.consent,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.leads.insert_one(lead_doc)
    logger.info(f"New lead created: {lead_id}")
    
    # Send emails
    email_data = {**lead_doc, "lead_id": lead_id}
    
    # Customer confirmation
    asyncio.create_task(send_email_async(
        [data.email],
        "Ihre Anfrage bei NeXifyAI – Bestätigung",
        get_email_template("contact_confirmation", email_data)
    ))
    
    # Internal notification
    asyncio.create_task(send_email_async(
        NOTIFICATION_EMAILS,
        f"[NeXifyAI] Neue Anfrage von {data.vorname} {data.nachname}",
        get_email_template("internal_notification", email_data)
    ))
    
    return {
        "success": True,
        "message": "Vielen Dank für Ihre Anfrage. Wir melden uns innerhalb von 24 Stunden bei Ihnen.",
        "lead_id": lead_id
    }

# Booking System
@app.get("/api/booking/slots")
async def get_available_slots(date: str):
    """Get available booking slots for a date"""
    # Business hours: 9:00 - 17:00, 30-min slots
    all_slots = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", 
                 "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
    
    # Get booked slots
    booked = await db.bookings.find(
        {"date": date, "status": {"$ne": "cancelled"}},
        {"time": 1, "_id": 0}
    ).to_list(100)
    booked_times = [b["time"] for b in booked]
    
    available = [s for s in all_slots if s not in booked_times]
    return {"date": date, "slots": available}

@app.post("/api/booking")
async def create_booking(data: BookingRequest):
    # Validate slot availability
    existing = await db.bookings.find_one({
        "date": data.date,
        "time": data.time,
        "status": {"$ne": "cancelled"}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Dieser Termin ist bereits vergeben")
    
    booking_id = f"BK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"
    
    # Create or link lead
    lead_id = data.lead_id
    if not lead_id:
        lead_id = f"LEAD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
        await db.leads.insert_one({
            "lead_id": lead_id,
            "vorname": data.vorname,
            "nachname": data.nachname,
            "email": data.email,
            "telefon": data.telefon,
            "unternehmen": data.unternehmen,
            "source": "booking",
            "status": "termin_gebucht",
            "notes": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
    else:
        await db.leads.update_one(
            {"lead_id": lead_id},
            {"$set": {"status": "termin_gebucht", "updated_at": datetime.now(timezone.utc)}}
        )
    
    booking_doc = {
        "booking_id": booking_id,
        "lead_id": lead_id,
        "vorname": data.vorname,
        "nachname": data.nachname,
        "email": data.email,
        "telefon": data.telefon,
        "unternehmen": data.unternehmen,
        "date": data.date,
        "time": data.time,
        "thema": data.thema,
        "notes": data.notes,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.bookings.insert_one(booking_doc)
    logger.info(f"New booking created: {booking_id}")
    
    email_data = {**booking_doc, "booking_id": booking_id}
    
    # Customer confirmation
    asyncio.create_task(send_email_async(
        [data.email],
        f"Ihr Beratungstermin am {data.date} – Bestätigung",
        get_email_template("booking_confirmation", email_data)
    ))
    
    # Internal notification
    asyncio.create_task(send_email_async(
        NOTIFICATION_EMAILS,
        f"[NeXifyAI] Neuer Termin: {data.date} {data.time} - {data.vorname} {data.nachname}",
        get_email_template("booking_notification", email_data)
    ))
    
    return {
        "success": True,
        "message": "Ihr Beratungstermin wurde bestätigt.",
        "booking_id": booking_id,
        "date": data.date,
        "time": data.time
    }

# Chat System
@app.post("/api/chat/message")
async def process_chat_message(session_id: str, message: str, context: Optional[dict] = None):
    """Process chat message and return AI response"""
    
    # Get or create chat session
    session = await db.chat_sessions.find_one({"session_id": session_id})
    if not session:
        session = {
            "session_id": session_id,
            "messages": [],
            "qualification": {},
            "created_at": datetime.now(timezone.utc)
        }
        await db.chat_sessions.insert_one(session)
    
    # Add user message
    user_msg = {
        "role": "user",
        "content": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Generate response based on context and qualification flow
    response = await generate_chat_response(message, session.get("messages", []), session.get("qualification", {}))
    
    assistant_msg = {
        "role": "assistant",
        "content": response["message"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Update session
    await db.chat_sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
            "$set": {
                "qualification": response.get("qualification", {}),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {
        "message": response["message"],
        "qualification": response.get("qualification", {}),
        "suggested_actions": response.get("actions", []),
        "should_escalate": response.get("should_escalate", False)
    }

async def generate_chat_response(message: str, history: list, qualification: dict) -> dict:
    """Generate contextual chat response for lead qualification"""
    
    msg_lower = message.lower()
    
    # Qualification keywords
    vertrieb_keywords = ["vertrieb", "sales", "lead", "anfragen", "kunden"]
    crm_keywords = ["crm", "erp", "sap", "hubspot", "salesforce", "integration"]
    wissen_keywords = ["wissen", "dokument", "rag", "knowledge", "faq", "support"]
    prozess_keywords = ["prozess", "automation", "workflow", "automatisieren"]
    datenschutz_keywords = ["dsgvo", "datenschutz", "sicherheit", "compliance", "governance"]
    
    # Update qualification based on message
    new_qual = {**qualification}
    
    if any(k in msg_lower for k in vertrieb_keywords):
        new_qual["interest"] = "vertrieb_automation"
        new_qual["use_case"] = "Sales & Lead-Qualifizierung"
    elif any(k in msg_lower for k in crm_keywords):
        new_qual["interest"] = "integration"
        new_qual["use_case"] = "CRM/ERP-Integration"
    elif any(k in msg_lower for k in wissen_keywords):
        new_qual["interest"] = "knowledge_system"
        new_qual["use_case"] = "Wissenssystem / RAG"
    elif any(k in msg_lower for k in prozess_keywords):
        new_qual["interest"] = "process_automation"
        new_qual["use_case"] = "Prozessautomation"
    elif any(k in msg_lower for k in datenschutz_keywords):
        new_qual["interest"] = "compliance"
        new_qual["use_case"] = "Governance & Compliance"
    
    # Check for booking intent
    booking_keywords = ["termin", "gespräch", "beraten", "anruf", "meeting", "buchen"]
    should_escalate = any(k in msg_lower for k in booking_keywords)
    
    # Generate contextual response
    responses = {
        "vertrieb_automation": "Vertriebsautomation ist ein starker Hebel. Unsere KI-Agenten können eingehende Anfragen automatisch qualifizieren, mit Ihrem CRM abgleichen und Termine koordinieren. Typische Ergebnisse: 40-60% weniger manuelle Arbeit im Vertriebsteam. Möchten Sie mehr über konkrete Implementierungsszenarien erfahren?",
        "integration": "CRM/ERP-Integrationen sind unser Kerngeschäft. Wir haben native Konnektoren für SAP, HubSpot und Salesforce. Die KI agiert dabei als intelligente Middleware, die Datenflüsse orchestriert und Aktionen auslöst. Welches System nutzen Sie aktuell?",
        "knowledge_system": "Interne Wissenssysteme mit RAG-Architektur sind ideal, um Mitarbeiterwissen sofort zugänglich zu machen. Stellen Sie sich vor: Ihre Service-Mitarbeiter finden in Sekunden die richtige Antwort aus Handbüchern, Tickets und Dokumenten. Wie groß ist Ihre aktuelle Wissensbasis?",
        "process_automation": "Prozessautomation ist der schnellste Weg zu messbarem ROI. Wir identifizieren wiederkehrende Abläufe und automatisieren sie mit KI-Agenten – ohne Medienbrüche. Welche Prozesse kosten Sie aktuell am meisten Zeit?",
        "compliance": "Datenschutz und Governance sind bei uns von Anfang an eingebaut. Wir arbeiten DSGVO-konform mit deutschen Rechenzentren, RBAC-Zugriffskontrolle und vollständigen Audit-Logs. Haben Sie spezifische Compliance-Anforderungen?"
    }
    
    interest = new_qual.get("interest", "")
    if interest and interest in responses:
        response_text = responses[interest]
    elif len(history) == 0:
        response_text = "Willkommen bei NeXifyAI! Ich helfe Ihnen, das richtige KI-Szenario für Ihr Unternehmen zu identifizieren. Erzählen Sie mir: Welche Herausforderung möchten Sie lösen?"
    else:
        response_text = "Verstanden. Um Ihnen konkret weiterzuhelfen: Wir könnten in einem kurzen Strategiegespräch Ihre Situation analysieren und erste Lösungsansätze skizzieren. Das Gespräch ist unverbindlich und dauert etwa 30 Minuten. Soll ich Ihnen einen Termin vorschlagen?"
        should_escalate = True
    
    actions = []
    if should_escalate:
        actions = [
            {"type": "booking", "label": "Beratungstermin buchen"},
            {"type": "contact", "label": "Kontaktformular öffnen"}
        ]
    
    return {
        "message": response_text,
        "qualification": new_qual,
        "actions": actions,
        "should_escalate": should_escalate
    }

# Analytics
@app.post("/api/analytics/track")
async def track_event(event: AnalyticsEvent):
    """Track analytics event"""
    doc = {
        "event": event.event,
        "properties": event.properties or {},
        "session_id": event.session_id,
        "page": event.page,
        "timestamp": datetime.now(timezone.utc)
    }
    await db.analytics.insert_one(doc)
    return {"success": True}

# ============== ADMIN ENDPOINTS ==============

@app.get("/api/admin/leads")
async def get_leads(
    admin: str = Depends(verify_admin),
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all leads with filtering"""
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
async def get_lead(lead_id: str, admin: str = Depends(verify_admin)):
    """Get single lead details"""
    lead = await db.leads.find_one({"lead_id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    
    # Get related bookings
    bookings = await db.bookings.find({"lead_id": lead_id}, {"_id": 0}).to_list(10)
    
    # Get chat sessions
    chat = await db.chat_sessions.find_one({"lead_id": lead_id}, {"_id": 0})
    
    return {"lead": lead, "bookings": bookings, "chat": chat}

@app.patch("/api/admin/leads/{lead_id}")
async def update_lead(lead_id: str, update: LeadStatusUpdate, admin: str = Depends(verify_admin)):
    """Update lead status and notes"""
    updates = {"status": update.status, "updated_at": datetime.now(timezone.utc)}
    
    if update.notes:
        await db.leads.update_one(
            {"lead_id": lead_id},
            {
                "$set": updates,
                "$push": {"notes": {"text": update.notes, "by": admin, "at": datetime.now(timezone.utc).isoformat()}}
            }
        )
    else:
        await db.leads.update_one({"lead_id": lead_id}, {"$set": updates})
    
    return {"success": True}

@app.get("/api/admin/bookings")
async def get_bookings(
    admin: str = Depends(verify_admin),
    date: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all bookings"""
    query = {}
    if date:
        query["date"] = date
    
    total = await db.bookings.count_documents(query)
    bookings = await db.bookings.find(query, {"_id": 0}).sort("date", -1).skip(skip).limit(limit).to_list(limit)
    
    return {"total": total, "bookings": bookings}

@app.get("/api/admin/stats")
async def get_stats(admin: str = Depends(verify_admin)):
    """Get dashboard statistics"""
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_leads = await db.leads.count_documents({})
    new_leads_today = await db.leads.count_documents({"created_at": {"$gte": today}})
    new_leads_week = await db.leads.count_documents({"created_at": {"$gte": week_ago}})
    
    upcoming_bookings = await db.bookings.count_documents({
        "date": {"$gte": today.strftime("%Y-%m-%d")},
        "status": "confirmed"
    })
    
    by_status = await db.leads.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(20)
    
    return {
        "total_leads": total_leads,
        "new_leads_today": new_leads_today,
        "new_leads_week": new_leads_week,
        "upcoming_bookings": upcoming_bookings,
        "by_status": {s["_id"]: s["count"] for s in by_status}
    }

# SEO/Meta endpoints
@app.get("/api/sitemap")
async def get_sitemap_data():
    """Return sitemap data for frontend generation"""
    return {
        "pages": [
            {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
            {"loc": "/#loesungen", "priority": "0.8", "changefreq": "monthly"},
            {"loc": "/#use-cases", "priority": "0.8", "changefreq": "monthly"},
            {"loc": "/#preise", "priority": "0.8", "changefreq": "monthly"},
            {"loc": "/#faq", "priority": "0.7", "changefreq": "monthly"},
            {"loc": "/#kontakt", "priority": "0.9", "changefreq": "monthly"},
            {"loc": "/impressum", "priority": "0.3", "changefreq": "yearly"},
            {"loc": "/datenschutz", "priority": "0.3", "changefreq": "yearly"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
