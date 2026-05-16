# System 5 — MCP Infrastructure & Tool Registry
spec_id: SYS-005 | version: 1.0 | date: 2026-05-15 | owner: api-architect

## 1. SERVICE INVENTORY (13 Tools, 8 Services)
| Service | Tools | Status |
|---------|-------|--------|
| Qdrant | search, insert, scroll, count, delete | ✅ Active |
| GitHub | repo-action, repo-create | ✅ Active |
| Vercel | deploy, domain | ✅ Active |
| Supabase | query, migrate | ✅ Active |
| MongoDB | query, aggregate | ✅ Active |
| Resend | send-email | ✅ Active |
| Cloudflare | zone-manage, dns | ✅ Active |
| NeXifyAI | health, brain-status | ✅ Active |

### MCP Router
- Endpoint: POST /mcp/rpc (JSON-RPC 2.0)
- Discovery: GET /mcp/tools (all tools + schemas)
- Auth: X-Internal-Auth for internal, API key for external
- Proxy: Hermes Gateway (:8642) → MCP Router (:8001/mcp/rpc)

### Tool Schema Standard
```json
{
  "service": "qdrant",
  "tool": "search",
  "version": "1.0.0",
  "params": {"collection": "string", "query": "string", "limit": "int"},
  "returns": {"matches": "[{id, score, payload}]"},
  "rate_limit": "100/min",
  "timeout_ms": 5000
}
```

## 2. ROUTING ARCHITECTURE
- Hermes → MCP Router → Service Adapter → Backend Service
- Service Adapter handles: auth, retry, timeout, logging
- Router: matches tool name to service, validates params, returns result
- Circuit Breaker: 5 failures in 30s → service marked DEGRADED

## 3. MONITORING HOOKS
- Every MCP call: logged (service, tool, latency, status)
- Metrics: calls/sec, p95 latency, error rate per service
- Alert: error rate >5% → P1, service DEGRADED → P0

## 4. FAILOVER STRATEGY
- Retry: 3x with exponential backoff (1s, 2s, 4s)
- Timeout: per-tool configurable (default 5s)
- Circuit Breaker → fallback to cached result or error
- Dead service: removed from registry, CEO notified

## 5. CONSTRAINTS
- NEVER: MCP call without auth
- NEVER: Tool without version
- NEVER: Breaking change without migration path
- ALWAYS: Every tool documented + versioned
- ALWAYS: Every MCP call logged
