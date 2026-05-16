"""Audit-Script: Wo stehen wir bei Neukundenwerbung & Betriebsabläufen?"""
import asyncio
import os
from collections import Counter
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]

    print("=" * 60)
    print("BETRIEBSABLAUF-AUDIT — NeXifyAI")
    print("=" * 60)

    # ── OUTBOUND ──
    print("\n[1] OUTBOUND LEAD MACHINE")
    total = await db.outbound_leads.count_documents({})
    print(f"   Gesamt-Leads: {total}")
    if total > 0:
        statuses = Counter()
        sent_count = ai_drafts = 0
        async for l in db.outbound_leads.find({}, {"status": 1, "outreach_history": 1, "_id": 0}):
            statuses[l.get("status", "unknown")] += 1
            for o in l.get("outreach_history", []):
                if o.get("status") == "sent":
                    sent_count += 1
                if o.get("generated_by") == "ai":
                    ai_drafts += 1
        print(f"   Status: {dict(statuses)}")
        print(f"   Versendete Outreaches: {sent_count} | AI-Drafts: {ai_drafts}")

    # ── INBOUND LEADS ──
    print("\n[2] INBOUND LEADS (Web-Formular, Chat)")
    leads = await db.leads.count_documents({})
    new_leads = await db.leads.count_documents({"status": "neu"})
    print(f"   Total: {leads} | unbearbeitet ('neu'): {new_leads}")
    sources = Counter()
    async for l in db.leads.find({}, {"source": 1, "_id": 0}):
        sources[l.get("source", "unknown")] += 1
    print(f"   Quellen: {dict(sources)}")

    # ── KUNDENKONTEN ──
    print("\n[3] PORTAL-KONTEN")
    activated = await db.customer_accounts.count_documents({"activated": True})
    deactivated = await db.customer_accounts.count_documents({"activated": False})
    print(f"   Aktiv: {activated} | Deaktiviert: {deactivated}")

    # ── QUOTES ──
    print("\n[4] ANGEBOTE")
    qs = Counter()
    async for q in db.quotes.find({}, {"status": 1, "_id": 0}):
        qs[q.get("status", "draft")] += 1
    print(f"   Status: {dict(qs)}")

    # ── E-MAIL VERSAND ──
    print("\n[5] E-MAIL-VERSAND letzte 7 Tage")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    sent = await db.email_events.count_documents({"sent_at": {"$gte": cutoff}, "status": "sent"})
    failed = await db.email_events.count_documents({"sent_at": {"$gte": cutoff}, "status": "failed"})
    print(f"   Sent: {sent} | Failed: {failed}")
    cats = Counter()
    async for e in db.email_events.find({"sent_at": {"$gte": cutoff}}, {"category": 1, "_id": 0}):
        cats[e.get("category", "none")] += 1
    print(f"   By category: {dict(cats)}")

    # ── AGENT ZERO / NEXIFY-AI ──
    print("\n[6] NEXIFY-AI (Master-Brain)")
    if "nexify_conversations" in await db.list_collection_names():
        nx_convs = await db.nexify_conversations.count_documents({})
        print(f"   Conversations: {nx_convs}")

    # ── CHAT-SESSIONS ──
    print("\n[7] CHAT-SESSIONS (Web-Frontend)")
    sessions = await db.chat_sessions.count_documents({})
    recent_sessions = await db.chat_sessions.count_documents({"updated_at": {"$gte": cutoff}})
    print(f"   Total: {sessions} | letzte 7 Tage: {recent_sessions}")

    # ── PROAKTIVE TASKS / SCHEDULED ──
    print("\n[8] SCHEDULED TASKS / AUTONOMIE")
    if "scheduled_tasks" in await db.list_collection_names():
        tasks_active = await db.scheduled_tasks.count_documents({"is_active": True})
        tasks_total = await db.scheduled_tasks.count_documents({})
        print(f"   Aktiv: {tasks_active} / {tasks_total}")
    if "cron_runs" in await db.list_collection_names():
        runs = await db.cron_runs.count_documents({"executed_at": {"$gte": cutoff}})
        print(f"   Cron-Runs letzte 7 Tage: {runs}")

    # ── TIMELINE EVENTS ──
    print("\n[9] TIMELINE EVENTS letzte 7 Tage")
    if "timeline_events" in await db.list_collection_names():
        timeline = await db.timeline_events.count_documents({"timestamp": {"$gte": cutoff}})
        print(f"   Total events: {timeline}")
        et = Counter()
        async for e in db.timeline_events.find({"timestamp": {"$gte": cutoff}}, {"action": 1, "_id": 0}).limit(500):
            et[e.get("action", "?")] += 1
        for action, count in et.most_common(10):
            print(f"     {action}: {count}")

    # ── HEALTH ALERTS ──
    print("\n[10] HEALTH-ALERTS letzte 7 Tage")
    if "health_alerts" in await db.list_collection_names():
        ha = await db.health_alerts.count_documents({"timestamp": {"$gte": cutoff}})
        print(f"   Total runs: {ha}")
        active_inc = await db.health_alert_state.find_one({"_id": "current"})
        if active_inc:
            active = active_inc.get("active", {})
            print(f"   Aktive Incidents: {list(active.keys()) or 'keine'}")


if __name__ == "__main__":
    asyncio.run(main())
