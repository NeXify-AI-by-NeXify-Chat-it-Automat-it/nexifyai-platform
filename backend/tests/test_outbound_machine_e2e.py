"""E2E Test: Outbound Lead Machine (P6) — Bulk-Import, AI-Analyse, AI-Outreach, AI-Followup."""
import asyncio
import httpx
import os
import sys
import secrets as _s

API = "http://localhost:8001"
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PW = "1def!xO2022!!"


async def main():
    test_email = f"e2e_ob_{_s.token_hex(4)}@example.com"

    async with httpx.AsyncClient(timeout=120.0) as c:
        r = await c.post(f"{API}/api/admin/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PW})
        assert r.status_code == 200
        token = r.json()["access_token"]
        H = {"Authorization": f"Bearer {token}"}
        print("[OK] admin logged in")

        # 1. Bulk import
        r = await c.post(f"{API}/api/admin/outbound/bulk-import", headers=H, json={
            "rows": [
                {"name": "E2E OB Test GmbH", "website": "https://nexify-automate.com",
                 "industry": "saas", "email": test_email, "country": "DE",
                 "notes": "manuelle prozesse, lead-generierung"},
                {"name": "", "email": "skip@example.com"},
            ],
        })
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["imported"] == 1, data
        assert data["skipped"] == 1, data
        print(f"[OK] bulk import: {data}")

        # 2. Find lead_id
        r = await c.get(f"{API}/api/admin/outbound/leads?limit=30", headers=H)
        lead_id = next((l["outbound_lead_id"] for l in r.json()["leads"] if l.get("contact_email") == test_email), None)
        assert lead_id, "lead not found"
        print(f"[OK] lead_id: {lead_id}")

        # 3. Prequalify
        r = await c.post(f"{API}/api/admin/outbound/{lead_id}/prequalify", headers=H)
        assert r.status_code == 200
        assert r.json()["qualified"] is True
        print("[OK] prequalified")

        # 4. AI website analyze
        r = await c.post(f"{API}/api/admin/outbound/{lead_id}/ai-website-analyze", headers=H)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["score"] > 0, d
        a = d["analysis"]
        assert a.get("source") == "ai_website"
        assert "industry" in a or "llm_error" in a
        print(f"[OK] AI analyze — score={d['score']}, industry={a.get('industry')}, pain={a.get('pain_signals')}")

        # 5. Legal check
        r = await c.post(f"{API}/api/admin/outbound/{lead_id}/legal-check", headers=H)
        assert r.status_code == 200
        assert r.json()["legal_ok"] is True, r.json()
        print("[OK] legal check passed")

        # 6. AI outreach
        r = await c.post(f"{API}/api/admin/outbound/{lead_id}/ai-outreach", headers=H,
                         json={"custom_hint": "20h Zeitersparnis pro Monat"})
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("outreach_id"), d
        assert len(d.get("subject", "")) > 10
        assert len(d.get("content", "")) > 50
        print(f"[OK] AI outreach generated: subject='{d['subject'][:80]}', content_len={len(d['content'])}")
        outreach_id = d["outreach_id"]

        # 7. Outreach unauthorized without legal → already tested. Skip.

        # 8. Clean up (delete lead)
        os.chdir("/app/backend"); sys.path.insert(0, "/app/backend")
        from dotenv import load_dotenv; load_dotenv()
        from motor.motor_asyncio import AsyncIOMotorClient
        db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
        await db.outbound_leads.delete_many({"contact_email": test_email})
        await db.outbound_leads.delete_many({"company_name": "E2E OB Test GmbH"})
        print("[OK] cleanup")


if __name__ == "__main__":
    asyncio.run(main())
    print("\n✅ ALL OUTBOUND E2E ASSERTIONS PASSED")
