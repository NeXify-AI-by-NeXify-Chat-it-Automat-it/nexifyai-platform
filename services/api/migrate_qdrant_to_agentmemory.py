#!/usr/bin/env python3
"""
Migrate all Qdrant points → AgentMemory.
AgentMemory auto-embeds via all-MiniLM-L6-v2 (384d).
Qdrant bleibt als Archiv erhalten.

Usage: python3 migrate_qdrant_to_agentmemory.py
"""
import json, logging, time, sys
from datetime import datetime, timezone
import requests
import agentmemory

log = logging.getLogger("migrate")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [migrate] %(levelname)s: %(message)s")

QDRANT_URL = "http://localhost:6333"

# Qdrant collections to migrate: (qdrant_collection, agentmemory_category_prefix)
SOURCES = [
    ("brain_agentmemory_4096_v1", "brain"),
    ("brain_knowledge_3072_v3", "knowledge"),
    ("nexifyai_brain_3072_v3", "legacy"),
]

def scroll_all_points(collection, limit=1000):
    """Scroll all points from a Qdrant collection."""
    points = []
    offset = None
    while True:
        body = {"limit": limit, "with_payload": True, "with_vector": False}
        if offset:
            body["offset"] = offset
        r = requests.post(f"{QDRANT_URL}/collections/{collection}/points/scroll",
                          json=body, timeout=30)
        if r.status_code != 200:
            log.error(f"Qdrant scroll error for {collection}: {r.text[:200]}")
            break
        result = r.json().get("result", {})
        batch = result.get("points", [])
        points.extend(batch)
        log.info(f"  Scrolled {len(points)} from {collection}...")
        if len(batch) < limit:
            break
        offset = result.get("next_page_offset")
    return points

def qdrant_to_agentmemory(points, cat_prefix):
    """Convert Qdrant points to AgentMemory format."""
    entries = []
    for p in points:
        pl = p.get("payload", {})
        content = pl.get("content") or pl.get("text") or pl.get("data") or ""
        category = pl.get("category", "unknown") or "unknown"
        source = pl.get("source", "migrated")
        timestamp = pl.get("timestamp") or datetime.now(timezone.utc).isoformat()
        tags = pl.get("tags", []) or []

        # Map content to text
        if isinstance(content, dict):
            text = json.dumps(content, ensure_ascii=False)
        else:
            text = str(content)

        # Build metadata
        metadata = {
            "category": category,
            "source": source,
            "timestamp": timestamp,
            "tags": json.dumps(tags) if tags else "",
            "qdrant_id": str(p["id"]),
            "qdrant_collection": cat_prefix,
        }
        if pl.get("title"):
            metadata["title"] = pl["title"]

        entries.append({
            "id": str(p["id"]),
            "document": text,
            "metadata": metadata,
        })
    return entries

def main():
    log.info("=" * 60)
    log.info("Qdrant → AgentMemory Migration")
    log.info("=" * 60)

    # 1. Check existing AgentMemory categories
    existing = agentmemory.export_memory_to_json(include_embeddings=False)
    log.info(f"Existing AgentMemory categories: {list(existing.keys())}")

    total_imported = 0
    for qdrant_col, cat_prefix in SOURCES:
        log.info(f"\n--- {qdrant_col} (→ {cat_prefix}_*) ---")

        # Scroll all points
        points = scroll_all_points(qdrant_col)
        log.info(f"  Total points in {qdrant_col}: {len(points)}")
        if not points:
            continue

        # Convert to AgentMemory format
        entries = qdrant_to_agentmemory(points, cat_prefix)
        log.info(f"  Converted {len(entries)} entries")

        # Group by category for import
        by_category = {}
        for e in entries:
            am_cat = f"{cat_prefix}_{e['metadata']['category']}"
            if am_cat not in by_category:
                by_category[am_cat] = []
            by_category[am_cat].append(e)

        log.info(f"  Target AgentMemory categories: {list(by_category.keys())}")

        # Import each category
        for am_cat, cat_entries in by_category.items():
            log.info(f"  Importing {len(cat_entries)} → {am_cat}...")
            t0 = time.time()
            agentmemory.import_json_to_memory(
                {am_cat: cat_entries},
                replace=False  # Don't replace, append
            )
            elapsed = time.time() - t0
            count = agentmemory.count_memories(am_cat)
            log.info(f"  Done: {count} in {am_cat} ({elapsed:.1f}s)")

        total_imported += len(entries)

    # 3. Summary
    log.info("\n" + "=" * 60)
    log.info(f"Migration complete: {total_imported} entries imported")
    final = agentmemory.export_memory_to_json(include_embeddings=False)
    log.info(f"Final AgentMemory categories:")
    for cat, mems in final.items():
        log.info(f"  {cat}: {len(mems)} entries")

    # Save mapping for reference
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_imported": total_imported,
        "categories": {cat: len(mems) for cat, mems in final.items()},
        "sources": [s[0] for s in SOURCES],
    }
    with open("/tmp/agentmemory_migration.json", "w") as f:
        json.dump(summary, f, indent=2)
    log.info(f"Summary saved to /tmp/agentmemory_migration.json")

if __name__ == "__main__":
    main()
