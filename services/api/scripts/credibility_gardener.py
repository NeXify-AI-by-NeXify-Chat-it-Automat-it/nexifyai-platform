#!/usr/bin/env python3
"""
NeXifyAI Credibility Gardener — Brain quality control system.
Runs as a dedicated agent (fact-checker) task.
Scans Brain entries for:
  - Missing credibility metadata (provenance, confidence, cross-review score)
  - Entries with low trust scores needing quarantine
  - Poisonous lessons (repeatedly failed in practice)
  - Stale entries that need re-evaluation

Think Tank Decision #2: "The Brain must enforce not just retrieval 
but reliability triage. Every stored entry should carry provenance, 
agent-confidence at time of writing, and a cross-review score."
"""
import os, json, sys, logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                   format="%(asctime)s [gardener] %(levelname)s: %(message)s")
logger = logging.getLogger("credibility_gardener")

BRAIN_URL = os.environ.get("HERMES_BRAIN_URL", "http://localhost:6333")
COLLECTION = "nexifyai_brain"

# === Credibility Schema ===
CREDIBILITY_FIELDS = {
    "provenance": "str — who/what created this entry (agent_id, system_process, human)",
    "confidence": "float 0.0-1.0 — agent confidence at time of writing",
    "cross_review_score": "float 0.0-1.0 — average score from other agents that reviewed this",
    "cross_review_count": "int — number of agents that reviewed this",
    "quarantine_score": "float 0.0-1.0 — starts at 0, increases as lessons fail in practice",
    "last_applied_context": "str — free-text note from last agent that applied this lesson",
    "applied_count": "int — how many times this lesson was applied",
    "applied_success_count": "int — how many times it held true",
    "applied_fail_count": "int — how many times it failed",
    "last_verified": "ISO8601 timestamp — when last cross-reviewed",
    "status": "str — active | quarantined | retired | under_review",
}

QUARANTINE_THRESHOLD = 0.7  # Quarantine score > 0.7 → quarantine
STALE_THRESHOLD_DAYS = 14     # Entries not verified in 14 days → under_review
POISON_THRESHOLD_FAILS = 3    # 3+ failures → poison flag


def scan_brain_entries() -> dict:
    """Scan all Brain entries and compute credibility stats."""
    import requests
    
    stats = {
        "total": 0,
        "with_provenance": 0,
        "with_confidence": 0,
        "with_cross_review": 0,
        "quarantined": 0,
        "poison_candidates": [],
        "stale_candidates": [],
        "missing_metadata": [],
    }
    
    try:
        # Scroll through all entries
        offset = None
        all_points = []
        
        while True:
            body = {"limit": 100, "with_payload": True}
            if offset:
                body["offset"] = offset
            
            r = requests.post(
                f"{BRAIN_URL}/collections/{COLLECTION}/points/scroll",
                json=body, timeout=15
            )
            
            if r.status_code != 200:
                break
            
            data = r.json().get("result", {})
            points = data.get("points", [])
            all_points.extend(points)
            
            next_offset = data.get("next_page_offset")
            if not next_offset or len(points) < 100:
                break
            offset = next_offset
        
        stats["total"] = len(all_points)
        logger.info(f"Scanned {stats['total']} Brain entries")
        
        for p in all_points:
            payload = p.get("payload", {})
            
            # Check credibility fields
            if "provenance" in payload:
                stats["with_provenance"] += 1
            if "confidence" in payload:
                stats["with_confidence"] += 1
            if "cross_review_score" in payload:
                stats["with_cross_review"] += 1
            
            # Check quarantine status
            quarantine = payload.get("quarantine_score", 0.0)
            status = payload.get("status", "active")
            
            if status == "quarantined":
                stats["quarantined"] += 1
            
            if quarantine > QUARANTINE_THRESHOLD:
                stats["poison_candidates"].append({
                    "id": p.get("id"),
                    "topic": payload.get("topic", "?"),
                    "quarantine_score": quarantine,
                    "fails": payload.get("applied_fail_count", 0),
                    "text": str(payload.get("text", ""))[:100],
                })
            
            # Check staleness
            last_verified = payload.get("last_verified", "")
            if last_verified:
                try:
                    last_dt = datetime.fromisoformat(last_verified.replace("Z", "+00:00"))
                    days_ago = (datetime.now(timezone.utc) - last_dt).days
                    if days_ago > STALE_THRESHOLD_DAYS:
                        stats["stale_candidates"].append({
                            "id": p.get("id"),
                            "topic": payload.get("topic", "?"),
                            "days_stale": days_ago,
                        })
                except:
                    pass
            
            # Missing metadata
            missing = []
            for field in ["provenance", "confidence", "cross_review_score"]:
                if field not in payload:
                    missing.append(field)
            if missing:
                stats["missing_metadata"].append({
                    "id": p.get("id"),
                    "missing": missing,
                    "category": payload.get("category", "?"),
                    "topic": payload.get("topic", "?"),
                })
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        stats["error"] = str(e)
    
    return stats


def enrich_entry(point_id, updates: dict):
    """Add credibility metadata to a Brain entry."""
    import requests
    
    try:
        r = requests.post(
            f"{BRAIN_URL}/collections/{COLLECTION}/points",
            json={"points": [{"id": point_id, "payload": updates}]},
            timeout=10
        )
        return r.status_code == 200
    except Exception as e:
        logger.warning(f"Enrich failed for {point_id}: {e}")
        return False


def generate_report(stats: dict) -> str:
    """Generate a human-readable credibility report."""
    
    report = []
    report.append("=" * 60)
    report.append("BRAIN CREDIBILITY GARDENING REPORT")
    report.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    report.append("=" * 60)
    report.append("")
    
    # Summary
    total = stats.get("total", 0)
    report.append(f"Total entries scanned: {total}")
    report.append(f"Entries with provenance: {stats.get('with_provenance', 0)} ({stats.get('with_provenance', 0)/max(total,1)*100:.0f}%)")
    report.append(f"Entries with confidence: {stats.get('with_confidence', 0)} ({stats.get('with_confidence', 0)/max(total,1)*100:.0f}%)")
    report.append(f"Entries with cross-review: {stats.get('with_cross_review', 0)} ({stats.get('with_cross_review', 0)/max(total,1)*100:.0f}%)")
    report.append(f"Currently quarantined: {stats.get('quarantined', 0)}")
    report.append("")
    
    # Poison candidates
    poisons = stats.get("poison_candidates", [])
    if poisons:
        report.append(f"⚠️  POISON CANDIDATES ({len(poisons)} entries above quarantine threshold):")
        for p in poisons[:10]:
            report.append(f"  [{p.get('topic', '?')}] quarantine={p.get('quarantine_score', 0):.2f} fails={p.get('fails', 0)} — {p.get('text', '')[:120]}")
        report.append("")
    
    # Stale candidates
    stales = stats.get("stale_candidates", [])
    if stales:
        report.append(f"⏰ STALE ENTRIES ({len(stales)} entries not verified in {STALE_THRESHOLD_DAYS}+ days):")
        for s in stales[:10]:
            report.append(f"  [{s.get('topic', '?')}] {s.get('days_stale', 0)} days stale")
        report.append("")
    
    # Missing metadata
    missing = stats.get("missing_metadata", [])
    if missing:
        report.append(f"📋 MISSING METADATA ({len(missing)} entries):")
        report.append(f"  Fields missing: provenance, confidence, cross_review_score")
        report.append(f"  Sample entries needing enrichment:")
        for m in missing[:5]:
            report.append(f"    [{m.get('category', '?')}] {m.get('topic', '?')} — missing: {', '.join(m.get('missing', []))}")
        report.append("")
    
    # Recommendations
    report.append("RECOMMENDATIONS:")
    if poisons:
        report.append(f"  1. Quarantine {len(poisons)} poison candidates immediately")
    if stales:
        report.append(f"  2. Dispatch cross-review agents to verify {len(stales)} stale entries")
    if missing:
        report.append(f"  3. Enrich {len(missing)} entries with provenance, confidence, and cross-review scores")
    if not poisons and not stales and not missing and total > 0:
        report.append("  ✓ Brain is healthy — all entries have credibility metadata")
    elif total == 0:
        report.append("  ⚠ Brain appears empty — this may indicate a connectivity issue")
    
    report.append("")
    report.append("=" * 60)
    return "\n".join(report)


if __name__ == "__main__":
    logger.info("Starting credibility garden scan...")
    stats = scan_brain_entries()
    report = generate_report(stats)
    print(report)
    
    # Store report in Brain
    import requests
    try:
        doc = {
            "category": "credibility_report",
            "source": "credibility_gardener",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": report,
            "stats": stats,
            "provenance": "credibility_gardener",
            "confidence": 0.95,
        }
        point_id = hash(f"cred-report-{datetime.now().isoformat()}") % (2**63)
        requests.put(
            f"{BRAIN_URL}/collections/{COLLECTION}/points?wait=true",
            json={"points": [{"id": point_id, "vector": [0.0] * 1024, "payload": doc}]},
            timeout=10
        )
        logger.info("Report stored in Brain")
    except Exception as e:
        logger.warning(f"Failed to store report: {e}")
    
    logger.info("Credibility gardening complete")
