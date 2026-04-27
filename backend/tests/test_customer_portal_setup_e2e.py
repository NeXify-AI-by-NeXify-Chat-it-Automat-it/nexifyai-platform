"""E2E test: Admin creates quote → Customer sets password → Customer logs in."""
import asyncio
import os
import sys
import secrets
import httpx

API = "https://contract-os.preview.emergentagent.com"
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PW = "1def!xO2022!!"


async def main():
    test_email = f"e2e_test_{secrets.token_hex(4)}@example.com"
    test_password = "TestPassword123!"

    async with httpx.AsyncClient(timeout=30.0) as c:
        # 1. Admin login
        r = await c.post(f"{API}/api/admin/login",
                         data={"username": ADMIN_EMAIL, "password": ADMIN_PW})
        assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
        admin_token = r.json()["access_token"]
        H = {"Authorization": f"Bearer {admin_token}"}
        print("[OK] admin logged in")

        # 2. Create a quote for test customer
        quote_payload = {
            "customer_name": "E2E Test User",
            "customer_email": test_email,
            "customer_company": "Test GmbH",
            "customer_phone": "+49 123",
            "customer_country": "DE",
            "customer_industry": "SaaS",
            "tier": "starter",
            "use_case": "E2E test",
            "notes": "Automated E2E test",
        }
        r = await c.post(f"{API}/api/admin/quotes", json=quote_payload, headers=H)
        assert r.status_code in (200, 201), f"create quote failed: {r.status_code} {r.text}"
        quote_data = r.json()
        quote_id = quote_data.get("quote_id") or (quote_data.get("quote") or {}).get("quote_id")
        assert quote_id, f"no quote_id in response: {quote_data}"
        print(f"[OK] quote created: {quote_id}")

        # 3. Send the quote (triggers access_link creation)
        r = await c.post(f"{API}/api/admin/quotes/{quote_id}/send", headers=H)
        if r.status_code != 200:
            # Fallback: maybe endpoint is /api/quotes/{id}/send
            r = await c.post(f"{API}/api/quotes/{quote_id}/send", headers=H)
        print(f"[INFO] send quote: {r.status_code}")

        # 4. Fetch access token from DB via admin endpoint if available — otherwise use Mongo
        # We'll use direct Mongo access since admin access_links endpoint may not exist
        os.chdir("/app/backend")
        sys.path.insert(0, "/app/backend")
        from dotenv import load_dotenv
        load_dotenv()
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = mongo[os.environ["DB_NAME"]]
        link = await db.access_links.find_one({"customer_email": test_email, "quote_id": quote_id})
        if not link:
            # Try without quote_id filter
            link = await db.access_links.find_one({"customer_email": test_email})
        assert link, f"no access_link for {test_email}"
        # The plaintext token is not stored — we need to regenerate via admin API or mock
        # For testing, we'll insert a known token
        from commercial import generate_access_token
        tok = generate_access_token(test_email, "quote")
        await db.access_links.update_one(
            {"_id": link["_id"]},
            {"$set": {
                "token_hash": tok["token_hash"],
                "expires_at": tok["expires_at"],
                "quote_id": quote_id,
            }},
        )
        plaintext_token = tok["token"]
        print(f"[OK] access link patched with known token")

        # 5. Fetch quote with token (should show has_account=False)
        r = await c.get(f"{API}/api/portal/quote/{quote_id}?token={plaintext_token}")
        assert r.status_code == 200, f"get quote failed: {r.status_code} {r.text}"
        data = r.json()
        assert data["account_status"]["has_account"] is False, "should not have account yet"
        print("[OK] fetched quote, account not yet set up")

        # 6. Setup account with password
        r = await c.post(f"{API}/api/portal/setup-account", json={
            "token": plaintext_token,
            "quote_id": quote_id,
            "password": test_password,
        })
        assert r.status_code == 200, f"setup-account failed: {r.status_code} {r.text}"
        setup_data = r.json()
        assert setup_data.get("success") is True
        assert setup_data.get("access_token")
        print(f"[OK] account set up — JWT: {setup_data['access_token'][:20]}...")

        # 7. Customer login with new password
        r = await c.post(f"{API}/api/auth/customer-login", json={
            "email": test_email,
            "password": test_password,
        })
        assert r.status_code == 200, f"customer-login failed: {r.status_code} {r.text}"
        login_data = r.json()
        assert login_data.get("role") == "customer"
        customer_token = login_data["access_token"]
        print(f"[OK] customer logged in — JWT: {customer_token[:20]}...")

        # 8. Customer dashboard with JWT
        r = await c.get(f"{API}/api/customer/dashboard",
                        headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 200, f"dashboard failed: {r.status_code} {r.text}"
        print(f"[OK] dashboard accessible")

        # 9. Wrong password
        r = await c.post(f"{API}/api/auth/customer-login", json={
            "email": test_email, "password": "WrongPassword!",
        })
        assert r.status_code == 401
        print("[OK] wrong password rejected")

        # 10. check-email returns has_portal_password=True
        r = await c.post(f"{API}/api/auth/check-email", json={"email": test_email})
        assert r.status_code == 200
        ce = r.json()
        assert ce["has_portal_password"] is True, f"expected has_portal_password=True, got {ce}"
        print(f"[OK] check-email: {ce}")

        # 11. Password reset: request
        r = await c.post(f"{API}/api/auth/password-reset/request", json={"email": test_email})
        assert r.status_code == 200
        print("[OK] password-reset request ok (200)")

        # Non-existent account should still return 200 (no enumeration)
        r = await c.post(f"{API}/api/auth/password-reset/request", json={"email": "totally_unknown_9f@example.com"})
        assert r.status_code == 200
        print("[OK] password-reset request for unknown email also 200 (no enumeration)")

        # Grab the reset token from DB
        reset_entry = await db.password_resets.find_one({"email": test_email, "used": False}, sort=[("created_at", -1)])
        assert reset_entry, "no password_resets entry"
        # We can't retrieve plaintext token from hash — create a known one (unique per run)
        import hashlib as _h
        raw_reset = f"test_reset_{secrets.token_hex(8)}"
        known_hash = _h.sha256(raw_reset.encode()).hexdigest()
        await db.password_resets.update_one({"_id": reset_entry["_id"]}, {"$set": {"token_hash": known_hash}})

        # 12. Confirm with short password → 400
        r = await c.post(f"{API}/api/auth/password-reset/confirm", json={"token": raw_reset, "password": "short"})
        assert r.status_code == 400, f"expected 400, got {r.status_code}: {r.text}"
        print("[OK] short password rejected on reset")

        # 13. Confirm with valid token + new password
        new_password = "NewPassword456!"
        r = await c.post(f"{API}/api/auth/password-reset/confirm", json={"token": raw_reset, "password": new_password})
        assert r.status_code == 200, f"password-reset confirm failed: {r.status_code} {r.text}"
        assert r.json().get("success") is True
        print("[OK] password reset completed")

        # 14. Reuse same reset token → 403
        r = await c.post(f"{API}/api/auth/password-reset/confirm", json={"token": raw_reset, "password": "AnotherPass789!"})
        assert r.status_code == 403
        print("[OK] reset token cannot be reused")

        # 15. Old password fails, new password works
        r = await c.post(f"{API}/api/auth/customer-login", json={"email": test_email, "password": test_password})
        assert r.status_code == 401, f"old password should no longer work (got {r.status_code})"
        print("[OK] old password rejected after reset")

        r = await c.post(f"{API}/api/auth/customer-login", json={"email": test_email, "password": new_password})
        assert r.status_code == 200, f"new password should work: {r.status_code} {r.text}"
        print("[OK] new password works")

        # 16. Admin list customer accounts
        r = await c.get(f"{API}/api/admin/customer-accounts?search={test_email}", headers=H)
        assert r.status_code == 200
        accounts = r.json()["accounts"]
        assert any(a["email"] == test_email for a in accounts), f"test account not found in admin list"
        print(f"[OK] admin list customer-accounts: {len(accounts)} matching")

        # 17. Admin reset
        r = await c.post(f"{API}/api/admin/customer-accounts/{test_email}/reset", headers=H)
        assert r.status_code == 200
        print("[OK] admin-triggered password reset")

        # 18. Admin deactivate
        r = await c.delete(f"{API}/api/admin/customer-accounts/{test_email}", headers=H)
        assert r.status_code == 200
        print("[OK] admin deactivated customer account")

        # 19. Login now fails (account deactivated)
        r = await c.post(f"{API}/api/auth/customer-login", json={"email": test_email, "password": new_password})
        assert r.status_code == 401
        print("[OK] deactivated account cannot login")

        # Cleanup
        await db.customer_accounts.delete_one({"email": test_email})
        await db.contacts.delete_one({"email": test_email})
        await db.quotes.delete_one({"quote_id": quote_id})
        await db.access_links.delete_many({"customer_email": test_email})
        await db.password_resets.delete_many({"email": test_email})
        print("[OK] cleanup done")


if __name__ == "__main__":
    asyncio.run(main())
    print("\n✅ ALL E2E ASSERTIONS PASSED")
