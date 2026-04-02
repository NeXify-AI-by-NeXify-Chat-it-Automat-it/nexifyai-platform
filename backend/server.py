"""
NeXifyAI Landing Page Backend
Provides API endpoints for contact form submissions
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
import os
from datetime import datetime, timezone
import re

app = FastAPI(title="NeXifyAI API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Company data - fixed according to project brief
COMPANY_DATA = {
    "name": "NeXifyAI by NeXify",
    "legal_name": "NeXify Automate",
    "ceo": "Pascal Courbois",
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


class ContactFormSubmission(BaseModel):
    """Contact form data model with validation"""
    vorname: str
    nachname: str
    email: EmailStr
    nachricht: str
    
    @validator('vorname', 'nachname')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name muss mindestens 2 Zeichen haben')
        if len(v) > 100:
            raise ValueError('Name darf maximal 100 Zeichen haben')
        return v.strip()
    
    @validator('nachricht')
    def validate_message(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Nachricht muss mindestens 10 Zeichen haben')
        if len(v) > 5000:
            raise ValueError('Nachricht darf maximal 5000 Zeichen haben')
        return v.strip()


class NewsletterSubscription(BaseModel):
    """Newsletter subscription model"""
    email: EmailStr


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "NeXifyAI Landing API"
    }


@app.get("/api/company")
async def get_company_data():
    """Return company information"""
    return COMPANY_DATA


@app.post("/api/contact")
async def submit_contact_form(data: ContactFormSubmission):
    """
    Handle contact form submission.
    In production, this would integrate with CRM/email service.
    """
    # Log the submission (in production: send to CRM, email, etc.)
    submission = {
        "id": f"LEAD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "vorname": data.vorname,
        "nachname": data.nachname,
        "email": data.email,
        "nachricht": data.nachricht,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "status": "received"
    }
    
    print(f"[CONTACT FORM] New submission: {submission['id']} from {data.email}")
    
    return {
        "success": True,
        "message": "Vielen Dank für Ihre Anfrage. Wir melden uns innerhalb von 24 Stunden bei Ihnen.",
        "reference_id": submission["id"]
    }


@app.post("/api/newsletter")
async def subscribe_newsletter(data: NewsletterSubscription):
    """Handle newsletter subscription"""
    print(f"[NEWSLETTER] New subscription: {data.email}")
    
    return {
        "success": True,
        "message": "Erfolgreich angemeldet. Sie erhalten eine Bestätigungs-E-Mail."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
