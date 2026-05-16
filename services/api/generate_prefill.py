#!/usr/bin/env python3
"""
generate_prefill.py — Regeneriert backend/prefill.md aus Quellen.
Der ZWANGSBEFEHL-Header (zwischen @ZWANGSBEFEHL-START und @ZWANGSBEFEHL-ENDE)
wird durch preserve_zwangsbefehl_header() geschützt und nie überschrieben.
"""

import os
import re

PREFILL_PATH = os.path.join(os.path.dirname(__file__), "prefill.md")

ZWANGSBEFEHL_START = "<!-- @ZWANGSBEFEHL-START -->"
ZWANGSBEFEHL_ENDE = "<!-- @ZWANGSBEFEHL-ENDE -->"


def preserve_zwangsbefehl_header(new_content: str) -> str:
    """
    Stellt sicher, dass der ZWANGSBEFEHL-Header aus der bestehenden
    prefill.md erhalten bleibt. Falls die Datei noch keinen Header hat,
    wird der neue Content unverändert zurückgegeben.

    Args:
        new_content: Der neu generierte prefill.md-Inhalt

    Returns:
        Der Content mit erhaltenem ZWANGSBEFEHL-Header
    """
    if not os.path.exists(PREFILL_PATH):
        return new_content

    with open(PREFILL_PATH, "r") as f:
        existing = f.read()

    # Extrahiere den ZWANGSBEFEHL-Block aus der bestehenden Datei
    start_idx = existing.find(ZWANGSBEFEHL_START)
    end_idx = existing.find(ZWANGSBEFEHL_ENDE)

    if start_idx == -1 or end_idx == -1:
        # Kein Header vorhanden — neuen Content unverändert nutzen
        return new_content

    # Header-Block (inklusive Marker)
    header_block = existing[start_idx:end_idx + len(ZWANGSBEFEHL_ENDE)]

    # Falls neuer Content bereits einen Header hat, diesen ersetzen
    new_start = new_content.find(ZWANGSBEFEHL_START)
    new_end = new_content.find(ZWANGSBEFEHL_ENDE)

    if new_start != -1 and new_end != -1:
        # Ersetze neuen Header durch bewahrten Header
        new_content = (
            new_content[:new_start]
            + header_block
            + new_content[new_end + len(ZWANGSBEFEHL_ENDE):]
        )
    else:
        # Füge Header am Anfang ein
        new_content = header_block + "\n\n" + new_content

    return new_content


def generate_prefill() -> str:
    """
    Generiert den prefill.md-Inhalt aus Quellen.
    Überschreibt die Datei unter Erhalt des ZWANGSBEFEHL-Headers.
    """
    # Lade aktuelle prefill.md als Basis
    if os.path.exists(PREFILL_PATH):
        with open(PREFILL_PATH, "r") as f:
            content = f.read()
    else:
        content = "# NEXIFYAI - CHAT IT. AUTOMATE IT.\n\n## Prefill\n"

    # Stelle sicher, dass der ZWANGSBEFEHL-Header erhalten bleibt
    content = preserve_zwangsbefehl_header(content)

    return content


if __name__ == "__main__":
    content = generate_prefill()
    with open(PREFILL_PATH, "w") as f:
        f.write(content)
    print(f"prefill.md generated ({len(content)} bytes) — ZWANGSBEFEHL-Header preserved")
