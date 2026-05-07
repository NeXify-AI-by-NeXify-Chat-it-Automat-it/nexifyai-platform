"""NeXifyAI — Auth Routes"""
import os
import hashlib
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from routes.shared import S
from routes.shared import (
    create_access_token,
    get_current_admin,
    get_current_customer,
    verify_password,
    check_rate_limit,
    log_audit,
    send_email,
    email_template,
    logger,
)
from domain import create_contact, create_timeline_event, utcnow
from memory_service import AGENT_IDS
from commercial import generate_access_token, verify_access_token

router = APIRouter(tags=["auth"])

@router.post("/api/admin/login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    if request:
        await check_rate_limit(request, limit=20, window=300)
    
    user = await S.db.admin_users.find_one({"email": form_data.username.lower()})
    password_valid = user and verify_password(form_data.password, user["password_hash"])
    
    if not password_valid:
        # Fallback: try Supabase Auth
        try:
            anon_key = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzc3NzI0Njc2LCJleHAiOjE5MzU0MDQ2NzZ9.RT3idfOHPfYNves7nfO5xPVD2PlGHK05KgMx6m_hYQ8")
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"http://127.0.0.1:8002/auth/v1/token?grant_type=password",
                    headers={"apikey": anon_key, "Content-Type": "application/json"},
                    json={"email": form_data.username.lower(), "password": form_data.password}
                )
                if r.status_code == 200:
                    supabase_token = r.json().get("access_token", "")
                    if supabase_token:
                        return {"access_token": supabase_token, "token_type": "bearer"}
        except Exception:
            pass
    
    if not user or not password_valid:
        await log_audit("login_failed", form_data.username)
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    token = create_access_token({"sub": user["email"], "role": "admin"})
    await log_audit("login_success", user["email"])
    
    return {"access_token": token, "token_type": "bearer"}


# ============== UNIFIED AUTH (Admin + Kunde) ==============


@router.post("/api/auth/check-email")
async def auth_check_email(data: dict):
    """Prüfe ob E-Mail ein Admin oder Kunde ist."""
    email = data.get("email", "").strip().lower()
    if not email:
        raise HTTPException(400, "E-Mail ist Pflichtfeld")
    
    admin = await S.db.admin_users.find_one({"email": email})
    
    contact = await S.db.contacts.find_one({"email": email})
    lead = await S.db.leads.find_one({"email": email})
    is_customer = bool(contact or lead)
    
    # Check if customer has a password-based account
    customer_account = await S.db.customer_accounts.find_one({"email": email, "activated": True})
    has_password = bool(customer_account)
    
    if admin and is_customer:
        return {"role": "dual", "needs_password": True, "needs_magic_link": not has_password, "has_portal_password": has_password}
    
    if admin:
        return {"role": "admin", "needs_password": True, "needs_magic_link": False, "has_portal_password": False}
    
    if is_customer:
        return {"role": "customer", "needs_password": has_password, "needs_magic_link": not has_password, "has_portal_password": has_password}
    
    return {"role": "unknown", "needs_password": False, "needs_magic_link": False, "has_portal_password": False}



@router.post("/api/auth/request-magic-link")
async def auth_request_magic_link(data: dict, request: Request):
    """Magic Link per E-Mail an Kunden senden."""
    if request:
        await check_rate_limit(request, limit=5, window=300)
    
    email = data.get("email", "").strip().lower()
    if not email:
        raise HTTPException(400, "E-Mail ist Pflichtfeld")
    
    # Prüfe ob Kontakt/Lead existiert
    contact = await S.db.contacts.find_one({"email": email})
    lead = await S.db.leads.find_one({"email": email})
    if not contact and not lead:
        raise HTTPException(404, "Kein Konto für diese E-Mail gefunden")
    
    # Erstelle Portal-Zugangstoken
    token_data = generate_access_token(email, "portal")
    await S.db.access_links.insert_one({
        "token_hash": token_data["token_hash"],
        "customer_email": email,
        "customer_name": (contact or {}).get("first_name", (lead or {}).get("vorname", "")) + " " + (contact or {}).get("last_name", (lead or {}).get("nachname", "")),
        "document_type": "portal",
        "expires_at": token_data["expires_at"],
        "created_at": token_data["created_at"],
        "created_by": "system_magic_link",
    })
    
    base_url = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
    magic_link = f"{base_url}/login/verify?token={token_data['token']}"
    
    # E-Mail senden
    # E-Mail senden (SMTP + Resend Fallback)
    try:
        html = email_template(
            "Ihr Portalzugang — NeXifyAI",
            "<p>Hallo,</p>"
            "<p>Sie haben einen Zugangslink für Ihr NeXifyAI-Kundenportal angefordert.</p>"
            "<p>Klicken Sie auf den Button, um sich einzuloggen. Der Link ist 24 Stunden gültig.</p>",
            magic_link,
            "Zum Portal"
        )
        await send_email([email], "Ihr Portalzugang — NeXifyAI", html, category="portal_access", ref_id=email)
    except Exception as e:
        logger.error(f"Magic Link E-Mail Fehler: {e}")
    
    await log_audit("magic_link_requested", email)
    
    return {"status": "ok", "message": "Magic Link wurde per E-Mail gesendet"}



@router.post("/api/auth/verify-token")
async def auth_verify_token(data: dict):
    """Magic Link Token verifizieren → JWT mit role=customer zurückgeben."""
    token = data.get("token", "").strip()
    if not token:
        raise HTTPException(400, "Token fehlt")
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    link = await S.db.access_links.find_one({"token_hash": token_hash})
    if not link:
        raise HTTPException(403, "Zugangslink ungültig")
    
    expires = link.get("expires_at")
    if expires:
        if isinstance(expires, str):
            from dateutil.parser import parse as dateparse
            expires = dateparse(expires)
        if expires < datetime.now(timezone.utc):
            raise HTTPException(403, "Zugangslink abgelaufen")
    
    email = link.get("customer_email", "").lower()
    if not email:
        raise HTTPException(400, "Kein Kundenkonto verknüpft")
    
    # JWT mit role=customer erstellen
    jwt_token = create_access_token(
        {"sub": email, "role": "customer"},
        expires_delta=timedelta(hours=24)
    )
    
    await log_audit("customer_login_magic_link", email)
    
    # mem0 Memory Write
    if S.memory_svc:
        contact = await S.db.contacts.find_one({"email": email})
        if contact and contact.get("contact_id"):
            await S.memory_svc.write(contact["contact_id"], "Kunde hat sich über Magic Link eingeloggt",
                                   AGENT_IDS["system"], category="context", source="auth",
                                   verification_status="verifiziert")
    
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "role": "customer",
        "email": email,
        "customer_name": link.get("customer_name", "")
    }


# ============== CUSTOMER PORTAL JWT-AUTH ENDPOINTS ==============


@router.post("/api/auth/customer-login")
async def auth_customer_login(data: dict, request: Request):
    """Customer login with email + password (set via quote setup-account flow)."""
    if request:
        await check_rate_limit(request, limit=20, window=300)

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        raise HTTPException(400, "E-Mail und Passwort erforderlich")

    account = await S.db.customer_accounts.find_one({"email": email, "activated": True})
    if not account:
        await log_audit("customer_login_failed", email)
        raise HTTPException(401, "Kein aktives Kundenkonto gefunden")

    if not verify_password(password, account.get("password_hash", "")):
        await log_audit("customer_login_failed", email)
        raise HTTPException(401, "Ungültiges Passwort")

    jwt_token = create_access_token(
        {"sub": email, "role": "customer"},
        expires_delta=timedelta(hours=24)
    )

    await log_audit("customer_login_password", email)
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "role": "customer",
        "email": email,
        "customer_name": account.get("name", "")
    }


@router.post("/api/auth/password-reset/request")
async def auth_password_reset_request(data: dict, request: Request):
    """Customer requests a password reset — sends email with reset token."""
    if request:
        await check_rate_limit(request, limit=5, window=600)

    email = data.get("email", "").strip().lower()
    if not email:
        raise HTTPException(400, "E-Mail ist Pflichtfeld")

    account = await S.db.customer_accounts.find_one({"email": email, "activated": True})

    # Always return 200 to avoid user enumeration — only actually send if account exists
    if account:
        import secrets as _s
        raw_token = _s.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        await S.db.password_resets.insert_one({
            "email": email,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
            "used": False,
        })

        base_url = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
        reset_link = f"{base_url}/login?reset_token={raw_token}"

        try:
            html = email_template(
                "Passwort zurücksetzen — NeXifyAI",
                "<p>Hallo,</p>"
                "<p>Sie haben eine Passwort-Zurücksetzung für Ihr NeXifyAI-Kundenportal angefordert.</p>"
                "<p>Klicken Sie auf den Button, um ein neues Passwort zu vergeben. Der Link ist 1 Stunde gültig.</p>"
                "<p style='color:#8a9bb0;font-size:12px;'>Falls Sie die Zurücksetzung nicht angefordert haben, ignorieren Sie diese E-Mail.</p>",
                reset_link,
                "Neues Passwort vergeben",
            )
            await send_email([email], "Passwort zurücksetzen — NeXifyAI", html, category="password_reset", ref_id=email)
        except Exception as e:
            logger.error(f"Password-Reset E-Mail Fehler: {e}")

        await log_audit("password_reset_requested", email)

    return {"status": "ok", "message": "Falls ein Konto existiert, wurde eine E-Mail gesendet."}


@router.post("/api/auth/password-reset/confirm")
async def auth_password_reset_confirm(data: dict, request: Request):
    """Customer confirms password reset using token + new password."""
    if request:
        await check_rate_limit(request, limit=20, window=300)

    from routes.shared import hash_password

    token = data.get("token", "").strip()
    password = data.get("password", "")

    if not token or not password:
        raise HTTPException(400, "Token und Passwort erforderlich")
    if len(password) < 8:
        raise HTTPException(400, "Passwort muss mindestens 8 Zeichen haben")

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    entry = await S.db.password_resets.find_one({"token_hash": token_hash})
    if not entry:
        raise HTTPException(403, "Reset-Link ungültig")
    if entry.get("used"):
        raise HTTPException(403, "Reset-Link wurde bereits verwendet")

    expires = entry.get("expires_at")
    if isinstance(expires, str):
        from dateutil.parser import parse as dateparse
        expires = dateparse(expires)
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires and expires < datetime.now(timezone.utc):
        raise HTTPException(403, "Reset-Link abgelaufen")

    email = entry["email"].lower()
    now = datetime.now(timezone.utc).isoformat()

    await S.db.customer_accounts.update_one(
        {"email": email, "activated": True},
        {"$set": {"password_hash": hash_password(password), "updated_at": now}},
    )
    await S.db.password_resets.update_one(
        {"_id": entry["_id"]},
        {"$set": {"used": True, "used_at": now}},
    )

    jwt_token = create_access_token({"sub": email, "role": "customer"}, expires_delta=timedelta(hours=24))
    account = await S.db.customer_accounts.find_one({"email": email}, {"_id": 0})

    await log_audit("password_reset_completed", email)
    return {
        "success": True,
        "access_token": jwt_token,
        "token_type": "bearer",
        "role": "customer",
        "email": email,
        "customer_name": (account or {}).get("name", ""),
    }


@router.get("/api/customer/me")
async def customer_me(user = Depends(get_current_customer)):
    """Kundenprofil — JWT-authentifiziert."""
    return {
        "email": user["email"],
        "role": "customer",
        "contact": {k: v for k, v in user["contact"].items() if k not in ("_id",)}
    }



@router.get("/api/admin/me")
async def admin_me(user = Depends(get_current_admin)):
    return {"email": user["email"], "role": user.get("role", "admin")}


@router.get("/api/admin/memory/agents")
async def admin_memory_agents(current_user: dict = Depends(get_current_admin)):
    """Liste aller bekannten Agent-IDs für mem0."""
    return {"agents": AGENT_IDS}


@router.get("/api/admin/memory/by-agent/{agent_id}")
async def admin_memory_by_agent(agent_id: str, limit: int = 30, current_user: dict = Depends(get_current_admin)):
    """Alle Memory-Einträge eines bestimmten Agenten."""
    entries = await S.memory_svc.get_agent_history(agent_id, limit)
    for e in entries:
        for k, v in list(e.items()):
            if hasattr(v, 'isoformat'):
                e[k] = str(v)
    return {"agent_id": agent_id, "entries": entries, "count": len(entries)}


@router.get("/api/admin/memory/search")
async def admin_memory_search(q: str, contact_id: str = None, limit: int = 20, current_user: dict = Depends(get_current_admin)):
    """Text-Suche über alle Memory-Einträge."""
    results = await S.memory_svc.search(q, contact_id, limit)
    for r in results:
        for k, v in list(r.items()):
            if hasattr(v, 'isoformat'):
                r[k] = str(v)
    return {"query": q, "results": results, "count": len(results)}



# --- Admin: Chat Sessions ---

