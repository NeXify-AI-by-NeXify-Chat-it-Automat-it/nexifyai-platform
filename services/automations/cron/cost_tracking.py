#!/usr/bin/env python3
"""
NeXifyAI — AI Cost Tracking Middleware
Loggt Token-Verbrauch und OpenRouter-Kosten in MongoDB.
Datenquelle fuer Grafana AI Cost Tracking Dashboard.
"""
import os, time, logging
from datetime import datetime, timezone
from pymongo import MongoClient

logger = logging.getLogger("nexifyai.cost_tracking")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "nexifyai")

# OpenRouter Pricing (per 1M tokens, USD, Stand 2026-05)
MODEL_PRICING = {
    "deepseek/deepseek-v4-flash": {"input": 0.14, "output": 0.28},
    "deepseek/deepseek-v4-pro": {"input": 0.435, "output": 0.87},
    "deepseek/deepseek-r1": {"input": 0.55, "output": 2.19},
    "qwen/qwen3-embedding-8b": {"input": 0.025, "output": 0.025},
}


def track_usage(model: str, input_tokens: int, output_tokens: int,
                endpoint: str = "chat", session_id: str = None) -> dict:
    """Track AI usage and cost in MongoDB."""
    pricing = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
    cost = (input_tokens / 1_000_000 * pricing["input"]) + \
           (output_tokens / 1_000_000 * pricing["output"])

    record = {
        "model": model,
        "endpoint": endpoint,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(cost, 8),
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc),
        "day": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        db.ai_usage.insert_one(record)
        db.ai_usage_daily.update_one(
            {"day": record["day"], "model": model},
            {"$inc": {
                "total_input_tokens": input_tokens,
                "total_output_tokens": output_tokens,
                "total_cost_usd": round(cost, 6),
                "request_count": 1,
            }},
            upsert=True,
        )
        client.close()
        logger.info(f"Tracked {model}: {input_tokens}+{output_tokens} tokens, ${cost:.6f}")
        return {"status": "tracked", "cost": cost}
    except Exception as e:
        logger.error(f"Cost tracking error: {e}")
        return {"status": "error", "error": str(e)}


def get_daily_costs(days: int = 30, model: str = None) -> list:
    """Get daily cost aggregation for Grafana."""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    match = {
        "day": {"$gte": (datetime.now(timezone.utc).strftime("%Y-%m-%d"))}
    }
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": {"day": "$day", "model": "$model"},
            "total_cost": {"$sum": "$cost_usd"},
            "total_tokens": {"$sum": "$total_tokens"},
            "requests": {"$sum": 1},
        }},
        {"$sort": {"_id.day": 1}},
        {"$limit": 100},
    ]
    if model:
        pipeline[0]["$match"]["model"] = model

    results = list(db.ai_usage.aggregate(pipeline, allowDiskUse=True))
    client.close()
    return results


def get_model_costs(limit: int = 20) -> list:
    """Get aggregated costs per model."""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    results = list(db.ai_usage_daily.find(
        {},
        {"_id": 0, "model": 1, "total_cost_usd": 1, "total_input_tokens": 1,
         "total_output_tokens": 1, "request_count": 1, "day": 1}
    ).sort("day", -1).limit(limit))
    client.close()
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(f"Daily costs (30d):")
        for r in get_daily_costs():
            print(f"  {r['_id']['day']} | {r['_id']['model']}: ${r['total_cost']:.4f} ({r['total_tokens']} tok, {r['requests']} req)")
    elif len(sys.argv) > 1 and sys.argv[1] == "track":
        track_usage(
            model=sys.argv[2] if len(sys.argv) > 2 else "deepseek/deepseek-v4-flash",
            input_tokens=int(sys.argv[3]) if len(sys.argv) > 3 else 500,
            output_tokens=int(sys.argv[4]) if len(sys.argv) > 4 else 200,
        )
    else:
        print(f"Usage: {sys.argv[0]} [report|track [model input_tokens output_tokens]]")