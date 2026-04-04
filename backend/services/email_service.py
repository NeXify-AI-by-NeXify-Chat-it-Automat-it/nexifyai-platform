"""
NeXifyAI — E-Mail-Service (SMTP via Hostinger)
Produktionsreifer, asynchroner E-Mail-Versand mit HTML-Templates.
"""
import os
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Optional

import aiosmtplib

logger = logging.getLogger("nexifyai.email")

# ══════════════════════════════════════════════════════════════
# KONFIGURATION
# ══════════════════════════════════════════════════════════════

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.hostinger.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "nexifyai@nexifyai.de")
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "NeXifyAI")


def utcnow():
    return datetime.now(timezone.utc)


# ══════════════════════════════════════════════════════════════
# HTML BASE TEMPLATE
# ══════════════════════════════════════════════════════════════

def _base_html(title: str, body: str, footer_extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{margin:0;padding:0;background:#0c1117;font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#c8d1dc;-webkit-text-size-adjust:100%}}
.wrap{{max-width:600px;margin:0 auto;padding:32px 24px}}
.header{{text-align:center;padding:24px 0 20px;border-bottom:1px solid rgba(255,255,255,.04)}}
.logo{{font-size:22px;font-weight:800;letter-spacing:-.02em;color:#fff}}
.logo .ai{{color:#ff9b7a}}
.content{{padding:28px 0}}
h1{{font-size:20px;font-weight:700;color:#fff;margin:0 0 16px;line-height:1.3}}
h2{{font-size:16px;font-weight:700;color:#ff9b7a;margin:0 0 12px}}
p{{font-size:14px;line-height:1.65;color:#c8d1dc;margin:0 0 14px}}
.card{{background:rgba(14,20,28,.8);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:20px;margin:16px 0}}
.card-row{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.03);font-size:13px}}
.card-row:last-child{{border:none}}
.card-label{{color:#6b7b8d;font-weight:600}}
.card-value{{color:#fff;font-weight:600;text-align:right}}
.btn{{display:inline-block;padding:14px 28px;background:#ff9b7a;color:#0c1117;font-size:14px;font-weight:700;text-decoration:none;border-radius:8px;margin:8px 0}}
.btn:hover{{background:#ffb59e}}
.footer{{padding:20px 0;border-top:1px solid rgba(255,255,255,.04);text-align:center;font-size:11px;color:#6b7b8d;line-height:1.6}}
.footer a{{color:#ff9b7a;text-decoration:none}}
.trust{{display:inline-block;padding:4px 10px;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.15);border-radius:12px;font-size:11px;color:#10b981;font-weight:600;margin:4px 2px}}
</style></head>
<body><div class="wrap">
<div class="header"><div class="logo">NeXify<span class="ai">AI</span></div></div>
<div class="content">{body}</div>
<div class="footer">
{footer_extra}
<p>NeXifyAI &middot; Starter/Growth AI Agenten AG<br>
KvK 96498099 &middot; BTW NL867282228B01<br>
<a href="https://nexifyai.de">nexifyai.de</a> &middot; <a href="mailto:nexifyai@nexifyai.de">nexifyai@nexifyai.de</a></p>
<p style="font-size:10px;color:#4a5568">Diese E-Mail wurde automatisch generiert. Bitte antworten Sie nicht auf diese Nachricht.</p>
</div>
</div></body></html>"""


# ══════════════════════════════════════════════════════════════
# SEND FUNCTION
# ══════════════════════════════════════════════════════════════

async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> dict:
    """E-Mail senden via SMTP (SSL). Gibt Ergebnis-Dict zurück."""
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP nicht konfiguriert — E-Mail an %s übersprungen", to_email)
        return {"sent": False, "reason": "smtp_not_configured"}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        if reply_to:
            msg["Reply-To"] = reply_to

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=True,
        )
        logger.info("E-Mail gesendet an %s: %s", to_email, subject)
        return {"sent": True, "to": to_email, "subject": subject, "timestamp": utcnow().isoformat()}

    except Exception as e:
        logger.error("E-Mail-Fehler an %s: %s", to_email, str(e))
        return {"sent": False, "to": to_email, "error": str(e), "timestamp": utcnow().isoformat()}


# ══════════════════════════════════════════════════════════════
# TEMPLATE: TERMINBESTÄTIGUNG
# ══════════════════════════════════════════════════════════════

async def send_booking_confirmation(booking: dict) -> dict:
    """Bestätigungs-E-Mail für Terminbuchung."""
    name = f"{booking.get('vorname', '')} {booking.get('nachname', '')}".strip()
    email = booking.get("email", "")
    date = booking.get("date", "")
    time_str = booking.get("time", "")
    thema = booking.get("thema", "Strategiegespräch")
    booking_id = booking.get("booking_id", "")

    body = f"""
<h1>Ihr Termin ist bestätigt</h1>
<p>Guten Tag {name},</p>
<p>vielen Dank für Ihre Terminbuchung. Wir freuen uns auf das Gespräch mit Ihnen.</p>

<div class="card">
<div class="card-row"><span class="card-label">Termin-ID</span><span class="card-value">{booking_id}</span></div>
<div class="card-row"><span class="card-label">Datum</span><span class="card-value">{date}</span></div>
<div class="card-row"><span class="card-label">Uhrzeit</span><span class="card-value">{time_str} Uhr</span></div>
<div class="card-row"><span class="card-label">Thema</span><span class="card-value">{thema}</span></div>
<div class="card-row"><span class="card-label">Format</span><span class="card-value">Videocall (30 Min.)</span></div>
</div>

<h2>Was als Nächstes passiert</h2>
<p>1. Sie erhalten eine Kalender-Einladung mit dem Videocall-Link.<br>
2. 24 Stunden vor dem Termin senden wir Ihnen eine Erinnerung.<br>
3. Unser KI-Stratege bereitet sich auf Basis Ihrer Angaben vor.</p>

<p>Falls Sie den Termin verschieben oder absagen möchten, antworten Sie einfach auf diese E-Mail oder kontaktieren Sie uns unter <a href="tel:+31681268033" style="color:#ff9b7a">+31 6 81268033</a>.</p>

<p><span class="trust">Kostenlos & unverbindlich</span> <span class="trust">DSGVO-konform</span></p>
"""
    return await send_email(
        to_email=email,
        subject=f"Terminbestätigung: {date} um {time_str} Uhr — NeXifyAI",
        html_body=_base_html("Terminbestätigung", body),
        text_body=f"Terminbestätigung für {name}\nDatum: {date}\nUhrzeit: {time_str} Uhr\nThema: {thema}\n\nIhr NeXifyAI-Team",
        reply_to="nexifyai@nexifyai.de",
    )


# ══════════════════════════════════════════════════════════════
# TEMPLATE: KONTAKTBESTÄTIGUNG
# ══════════════════════════════════════════════════════════════

async def send_contact_confirmation(contact: dict) -> dict:
    """Eingangsbestätigung für Kontaktformular."""
    name = f"{contact.get('vorname', '')} {contact.get('nachname', '')}".strip()
    email = contact.get("email", "")
    nachricht = contact.get("nachricht", "")

    body = f"""
<h1>Ihre Anfrage ist eingegangen</h1>
<p>Guten Tag {name},</p>
<p>vielen Dank für Ihre Nachricht. Wir haben Ihre Anfrage erhalten und werden uns innerhalb von 2 Stunden bei Ihnen melden.</p>

<div class="card">
<div class="card-row"><span class="card-label">Ihre Nachricht</span></div>
<p style="font-size:13px;color:#fff;padding:8px 0;margin:0;font-style:italic">"{nachricht[:300]}{"..." if len(nachricht) > 300 else ""}"</p>
</div>

<p>Möchten Sie in der Zwischenzeit direkt einen Termin buchen?</p>
<a href="https://nexifyai.de/termin" class="btn">Strategiegespräch buchen</a>
"""
    return await send_email(
        to_email=email,
        subject="Ihre Anfrage bei NeXifyAI — Eingangsbestätigung",
        html_body=_base_html("Anfrage eingegangen", body),
        text_body=f"Anfrage-Bestätigung für {name}\n\nIhre Nachricht: {nachricht[:300]}\n\nWir melden uns innerhalb von 2 Stunden.\n\nIhr NeXifyAI-Team",
        reply_to="nexifyai@nexifyai.de",
    )


# ══════════════════════════════════════════════════════════════
# TEMPLATE: REGISTRIERUNGSBESTÄTIGUNG
# ══════════════════════════════════════════════════════════════

async def send_registration_confirmation(customer: dict) -> dict:
    """Willkommens-E-Mail nach Konto-Erstellung."""
    name = f"{customer.get('vorname', '')} {customer.get('nachname', '')}".strip()
    email = customer.get("email", "")

    body = f"""
<h1>Willkommen bei NeXifyAI</h1>
<p>Guten Tag {name},</p>
<p>Ihr Konto wurde erfolgreich angelegt. Vielen Dank für Ihr Vertrauen.</p>

<div class="card">
<div class="card-row"><span class="card-label">E-Mail</span><span class="card-value">{email}</span></div>
<div class="card-row"><span class="card-label">Status</span><span class="card-value" style="color:#10b981">Registriert</span></div>
</div>

<h2>Nächste Schritte</h2>
<p>1. Ihr Konto wird innerhalb kurzer Zeit freigeschaltet.<br>
2. Sie erhalten einen persönlichen Zugangslink per E-Mail.<br>
3. Ab dann haben Sie Zugriff auf Angebote, Projekte und Rechnungen.</p>

<p>Buchen Sie jetzt Ihr kostenloses Strategiegespräch:</p>
<a href="https://nexifyai.de/termin" class="btn">Termin buchen</a>
"""
    return await send_email(
        to_email=email,
        subject="Willkommen bei NeXifyAI — Ihr Konto ist angelegt",
        html_body=_base_html("Willkommen", body),
        text_body=f"Willkommen bei NeXifyAI, {name}!\n\nIhr Konto wurde angelegt.\nWir melden uns in Kürze mit Ihren Zugangsdaten.\n\nIhr NeXifyAI-Team",
        reply_to="nexifyai@nexifyai.de",
    )


# ══════════════════════════════════════════════════════════════
# TEMPLATE: ANGEBOTSANFRAGE-BESTÄTIGUNG
# ══════════════════════════════════════════════════════════════

async def send_quote_request_confirmation(request: dict) -> dict:
    """Bestätigung für individuelle Angebotsanfrage."""
    name = f"{request.get('vorname', '')} {request.get('nachname', '')}".strip()
    email = request.get("email", "")
    tarif = request.get("tarif", "Individuell")
    interesse = request.get("interesse", "")
    qr_id = request.get("quote_request_id", "")

    body = f"""
<h1>Ihre Angebotsanfrage ist eingegangen</h1>
<p>Guten Tag {name},</p>
<p>vielen Dank für Ihr Interesse. Wir haben Ihre Anfrage erhalten und erstellen Ihnen ein individuelles Angebot.</p>

<div class="card">
<div class="card-row"><span class="card-label">Anfrage-ID</span><span class="card-value">{qr_id}</span></div>
<div class="card-row"><span class="card-label">Tarif</span><span class="card-value">{tarif}</span></div>
<div class="card-row"><span class="card-label">Interesse</span><span class="card-value" style="max-width:250px;text-align:right">{interesse[:120]}</span></div>
</div>

<h2>Wie geht es weiter?</h2>
<p>1. Unser Team prüft Ihre Anforderungen und erstellt ein maßgeschneidertes Angebot.<br>
2. Sie erhalten das Angebot innerhalb von 24 Stunden.<br>
3. Bei Rückfragen kontaktieren wir Sie direkt.</p>

<p><span class="trust">Kostenlos</span> <span class="trust">Unverbindlich</span> <span class="trust">Innerhalb 24h</span></p>
"""
    return await send_email(
        to_email=email,
        subject=f"Angebotsanfrage eingegangen — NeXifyAI [{qr_id}]",
        html_body=_base_html("Angebotsanfrage", body),
        text_body=f"Angebotsanfrage {qr_id}\n\n{name}, Ihre Anfrage für {tarif} ist eingegangen.\nWir erstellen Ihnen innerhalb von 24h ein Angebot.\n\nIhr NeXifyAI-Team",
        reply_to="nexifyai@nexifyai.de",
    )


# ══════════════════════════════════════════════════════════════
# TEMPLATE: ADMIN-BENACHRICHTIGUNG
# ══════════════════════════════════════════════════════════════

async def send_admin_notification(event_type: str, details: dict) -> dict:
    """Admin-Benachrichtigung bei neuen Leads, Buchungen, Anfragen."""
    admin_email = os.environ.get("ADMIN_EMAIL", "p.courbois@icloud.com")
    
    type_labels = {
        "new_lead": "Neuer Lead",
        "new_booking": "Neue Terminbuchung",
        "new_quote_request": "Neue Angebotsanfrage",
        "new_registration": "Neue Registrierung",
        "new_contact": "Neue Kontaktanfrage",
    }
    label = type_labels.get(event_type, event_type)

    rows = ""
    for k, v in details.items():
        if k not in ("_id",) and v:
            rows += f'<div class="card-row"><span class="card-label">{k}</span><span class="card-value">{str(v)[:100]}</span></div>\n'

    body = f"""
<h1>{label}</h1>
<p>Neues Ereignis im System:</p>
<div class="card">{rows}</div>
<a href="https://contract-os.preview.emergentagent.com/login" class="btn">Admin-Dashboard öffnen</a>
"""
    return await send_email(
        to_email=admin_email,
        subject=f"[NeXifyAI Admin] {label} — {details.get('email', details.get('vorname', ''))}",
        html_body=_base_html(f"Admin: {label}", body),
    )


# ══════════════════════════════════════════════════════════════
# TEMPLATE: ANGEBOTS-VERSAND
# ══════════════════════════════════════════════════════════════

async def send_quote_email(quote: dict, portal_url: str = "") -> dict:
    """Angebot per E-Mail an Kunden senden."""
    customer = quote.get("customer", {})
    name = customer.get("name", "")
    email = customer.get("email", "")
    calc = quote.get("calculation", {})
    quote_number = quote.get("quote_number", "")
    tier_name = calc.get("tier_name", "")
    total = calc.get("total_contract_eur", 0)

    body = f"""
<h1>Ihr Angebot von NeXifyAI</h1>
<p>Guten Tag {name},</p>
<p>anbei Ihr individuelles Angebot. Wir freuen uns, Ihnen folgende Lösung anbieten zu können:</p>

<div class="card">
<div class="card-row"><span class="card-label">Angebot-Nr.</span><span class="card-value">{quote_number}</span></div>
<div class="card-row"><span class="card-label">Tarif</span><span class="card-value">{tier_name}</span></div>
<div class="card-row"><span class="card-label">Gesamtwert</span><span class="card-value" style="font-size:16px;color:#ff9b7a">{total:,.2f} EUR</span></div>
<div class="card-row"><span class="card-label">Laufzeit</span><span class="card-value">{calc.get('contract_months', 24)} Monate</span></div>
<div class="card-row"><span class="card-label">Monatlich</span><span class="card-value">{calc.get('recurring_eur', 0):,.2f} EUR</span></div>
</div>

<p>Das Angebot ist 30 Tage gültig. Sie können es direkt in Ihrem Kundenportal einsehen und freigeben.</p>
{"<a href='" + portal_url + "' class='btn'>Angebot ansehen</a>" if portal_url else ""}

<p>Bei Fragen stehen wir Ihnen jederzeit zur Verfügung.</p>
"""
    return await send_email(
        to_email=email,
        subject=f"Ihr Angebot {quote_number} — NeXifyAI",
        html_body=_base_html("Angebot", body),
        text_body=f"Angebot {quote_number}\n\nGuten Tag {name},\n\nIhr Angebot über {tier_name} ({total:,.2f} EUR) ist bereit.\n\nIhr NeXifyAI-Team",
        reply_to="nexifyai@nexifyai.de",
    )


# ══════════════════════════════════════════════════════════════
# TEMPLATE: RECHNUNGS-VERSAND
# ══════════════════════════════════════════════════════════════

async def send_invoice_email(invoice: dict) -> dict:
    """Rechnung per E-Mail an Kunden senden."""
    customer = invoice.get("customer", {})
    name = customer.get("name", "")
    email = customer.get("email", "")
    inv_number = invoice.get("invoice_number", "")
    total = invoice.get("total_eur", 0)
    due_date = invoice.get("due_date", "")

    body = f"""
<h1>Ihre Rechnung von NeXifyAI</h1>
<p>Guten Tag {name},</p>
<p>anbei Ihre Rechnung. Bitte begleichen Sie den offenen Betrag bis zum Fälligkeitsdatum.</p>

<div class="card">
<div class="card-row"><span class="card-label">Rechnung-Nr.</span><span class="card-value">{inv_number}</span></div>
<div class="card-row"><span class="card-label">Betrag</span><span class="card-value" style="font-size:16px;color:#ff9b7a">{total:,.2f} EUR</span></div>
<div class="card-row"><span class="card-label">Fällig am</span><span class="card-value">{due_date}</span></div>
<div class="card-row"><span class="card-label">Status</span><span class="card-value">Offen</span></div>
</div>

<p>Die Zahlung können Sie bequem per Überweisung oder über unser Kundenportal vornehmen.</p>

<p>Bei Fragen zur Rechnung kontaktieren Sie uns unter <a href="mailto:nexifyai@nexifyai.de" style="color:#ff9b7a">nexifyai@nexifyai.de</a>.</p>
"""
    return await send_email(
        to_email=email,
        subject=f"Rechnung {inv_number} — NeXifyAI ({total:,.2f} EUR)",
        html_body=_base_html("Rechnung", body),
        text_body=f"Rechnung {inv_number}\n\nGuten Tag {name},\n\nBetrag: {total:,.2f} EUR\nFällig: {due_date}\n\nIhr NeXifyAI-Team",
        reply_to="nexifyai@nexifyai.de",
    )


# ══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════════════

async def check_smtp_health() -> dict:
    """SMTP-Verbindung testen."""
    if not SMTP_USER:
        return {"status": "not_configured", "host": SMTP_HOST}
    try:
        smtp = aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT, use_tls=True)
        await smtp.connect()
        await smtp.login(SMTP_USER, SMTP_PASSWORD)
        await smtp.quit()
        return {"status": "ok", "host": SMTP_HOST, "port": SMTP_PORT, "user": SMTP_USER}
    except Exception as e:
        return {"status": "error", "host": SMTP_HOST, "error": str(e)}
