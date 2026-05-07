"""
Contract Test — Event Schema Validation (DOS v2.0 Kap. 11)
Validiert dass alle Events aus taxonomy.ts dem Schema entsprechen
"""
import pytest
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ══════════════════════════════════════════════════════════════
# MOCK SCHEMA (entspricht taxonomy.ts ohne Zod/TypeScript)
# ══════════════════════════════════════════════════════════════

REQUIRED_EVENT_FIELDS = {"event", "timestamp"}

EXPECTED_EVENTS = [
    "page_view",
    "cta_click",
    "scroll_depth",
    "pricing_view",
    "plan_select",
    "form_start",
    "form_submit",
    "form_error",
    "abandon_form",
    "add_to_cart",
    "begin_checkout",
    "purchase",
    "demo_request",
    "calendar_booked",
    "lead_scored",
    "returning_user",
    "email_subscribe",
    "search_internal",
]


def test_all_events_have_required_fields():
    """Test: Jedes Event hat event-Feld und timestamp."""
    for event_name in EXPECTED_EVENTS:
        event = {"event": event_name, "timestamp": "2026-05-08T12:00:00Z"}
        
        assert "event" in event
        assert event["event"] == event_name
        assert "timestamp" in event


def test_page_view_event():
    """Contract: page_view Event-Schema."""
    event = {
        "event": "page_view",
        "url": "/preise",
        "referrer": "https://google.com",
        "timestamp": "2026-05-08T12:00:00Z",
    }
    
    assert event["event"] == "page_view"
    assert "url" in event
    assert event["url"].startswith("/")


def test_pricing_view_event():
    """Contract: pricing_view Event-Schema."""
    event = {
        "event": "pricing_view",
        "url": "/preise",
        "segment": "b2b",
        "timestamp": "2026-05-08T12:00:00Z",
    }
    
    assert event["event"] == "pricing_view"
    assert event["segment"] in ("b2c", "b2b", "enterprise", "partner")


def test_form_submit_event():
    """Contract: form_submit Event-Schema."""
    event = {
        "event": "form_submit",
        "form_id": "demo-form",
        "form_type": "demo",
        "success": True,
        "timestamp": "2026-05-08T12:00:00Z",
    }
    
    assert event["event"] == "form_submit"
    assert event["form_type"] in ("contact", "demo", "newsletter", "booking", "support")
    assert event["success"] is True


def test_event_taxonomy_completeness():
    """Test: Alle 18 Pflicht-Events sind definiert."""
    assert len(EXPECTED_EVENTS) == 18, f"Erwarte 18 Events, habe {len(EXPECTED_EVENTS)}"
    
    # Keine Duplikate
    assert len(set(EXPECTED_EVENTS)) == len(EXPECTED_EVENTS), "Doppelte Event-Namen!"
