"""Regression tests for chat resilience.

Ensures:
- /api/chat/message NEVER returns empty/null message field
- Backend has fallback when LLM returns empty
- Multiple sequential messages in same session keep working
"""
import asyncio
import httpx
import secrets

API = "http://localhost:8001"


async def main():
    sid = f"regression_{secrets.token_hex(6)}"
    questions = [
        "Hallo",
        "Was kann KI in meiner Branche leisten?",
        "Wie integriert ihr euch in unsere Systeme?",
        "Welche Ergebnisse erzielen eure Kunden?",
        "Ich möchte meine Prozesse analysieren lassen",
        "Was unterscheidet euch von anderen Anbietern?",
    ]
    async with httpx.AsyncClient(timeout=90.0) as c:
        for q in questions:
            r = await c.post(
                f"{API}/api/chat/message",
                json={"session_id": sid, "message": q, "language": "de"},
            )
            assert r.status_code == 200, f"q={q!r} status={r.status_code} body={r.text[:200]}"
            d = r.json()
            msg = d.get("message", "")
            # Hard regression assertions:
            assert msg, f"EMPTY message for q={q!r} -> response={d}"
            assert isinstance(msg, str), f"message is not str: {type(msg)}"
            assert msg.strip(), f"WHITESPACE-ONLY message for q={q!r}"
            assert len(msg) >= 10, f"TOO_SHORT message ({len(msg)} chars) for q={q!r}: {msg!r}"
            print(f"  ✓ {q[:40]:40s} -> {len(msg)} chars OK")
    print("\n✅ CHAT REGRESSION PASSED — never empty, always non-trivial response")


if __name__ == "__main__":
    asyncio.run(main())
