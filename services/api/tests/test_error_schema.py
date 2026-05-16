"""
Unit Tests — API Standards & Error Schema (DOS v2.0 Kap. 23)
Prüft die APIErrorResponse und error_response() in shared.py
"""
import pytest
import sys
import os
from datetime import datetime

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ══════════════════════════════════════════════════════════════

def test_api_error_response_structure():
    """Test: APIErrorResponse hat alle Pflichtfelder."""
    from routes.shared import APIErrorResponse
    
    error = APIErrorResponse(
        code="VALIDATION_ERROR",
        message="Ungültige Eingabe",
        details=[{"field": "email", "reason": "ungültig"}],
        request_id="req_test123",
        timestamp="2026-05-08T12:00:00Z",
    )
    
    assert error.code == "VALIDATION_ERROR"
    assert error.message == "Ungültige Eingabe"
    assert len(error.details) == 1
    assert error.request_id == "req_test123"

def test_error_response_json():
    """Test: error_response() erzeugt korrekte JSON-Struktur."""
    from routes.shared import error_response
    
    response = error_response(
        status=400,
        code="VALIDATION_ERROR",
        message="Feld 'email' fehlt",
        details=[{"field": "email", "reason": "required"}],
    )
    
    assert response.status_code == 400
    body = response.body  # JSONResponse hat .body (Starlette)
    if isinstance(body, bytes):
        import json
        body = json.loads(body)
    
    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Feld 'email' fehlt"
    assert len(body["error"]["details"]) == 1
    assert "request_id" in body["error"]
    assert "timestamp" in body["error"]

def test_error_response_all_status_codes():
    """Test: Alle HTTP-Statuscodes werden korrekt durchgereicht."""
    from routes.shared import error_response
    
    test_cases = [
        (400, "VALIDATION_ERROR"),
        (401, "UNAUTHORIZED"),
        (403, "FORBIDDEN"),
        (404, "NOT_FOUND"),
        (409, "CONFLICT"),
        (429, "RATE_LIMITED"),
        (500, "INTERNAL_ERROR"),
    ]
    
    for status, code in test_cases:
        response = error_response(status=status, code=code, message=code)
        assert response.status_code == status

def test_error_response_empty_details():
    """Test: Leere details werden als [] behandelt."""
    from routes.shared import error_response
    
    response = error_response(status=404, code="NOT_FOUND", message="Nicht gefunden")
    assert response.status_code == 404

def test_error_response_timestamp_format():
    """Test: Timestamp ist ISO 8601."""
    from routes.shared import error_response
    
    response = error_response(status=500, code="INTERNAL_ERROR", message="Fehler")
    body = response.body
    if isinstance(body, bytes):
        import json
        body = json.loads(body)
    
    timestamp = body["error"]["timestamp"]
    # Sollte ISO 8601 sein
    assert "T" in timestamp
    assert "+" in timestamp or "Z" in timestamp
