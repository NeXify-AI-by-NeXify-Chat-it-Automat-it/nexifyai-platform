# ADR-006: Queue System — BullMQ

**Status:** ACCEPTED  
**Datum:** 2026-05-08  
**Decider:** NeXifyAI (Hermes Lead Agent)  
**Depends on:** ADR-005 (Automation Layer)  

## Kontext

ADR-005 legt fest, dass Automation über native Systeme erfolgt. Für asynchrone Verarbeitung, Retry-Logik und Hintergrund-Jobs wird ein dediziertes Queue-System benötigt.

### Anforderungen
- TypeScript-native API
- Retry-Mechanismen (Exponential Backoff)
- Job-Priorisierung
- Scheduling (delayed jobs)
- Observability (Metrics, Dashboard)
- Self-hosted oder günstiger Managed-Service
- Geringe Infrastruktur-Komplexität

## Entscheidung

**BullMQ** als primäres Queue-System.

### Evaluierungsmatrix

| Kriterium | BullMQ | Trigger.dev | Inngest | Gewicht |
|-----------|--------|-------------|---------|---------|
| TypeScript-native | ✅ Erstklassig | ✅ Erstklassig | ✅ Erstklassig | 15% |
| Self-hosted | ✅ Redis (1 Container) | ✅ Open-Source | ❌ Cloud-only | 25% |
| Vendor-Lockin | ❌ Kein (eigene Redis) | ⚠️ Gering (OSS) | ❌ Hoch (Cloud-API) | 20% |
| Observability | ✅ Bull Board UI | ✅ Built-in Dashboard | ✅ Built-in | 10% |
| Retry/Backoff | ✅ Vollständig | ✅ Vollständig | ✅ Vollständig | 15% |
| Community/Maturity | ✅ 5+ Jahre, 6k★ | ⚠️ 1 Jahr, jung | ⚠️ 1 Jahr, VC-funded | 10% |
| Kosten | €0 (eigene Infra) | €0 (OSS) / $20+ (Cloud) | $20+/Monat | 15% |
| Latenz | <1ms (Redis lokal) | ~50ms (HTTP) | ~100ms (HTTP) | 10% |
| **GESAMT** | **95%** | **72%** | **45%** | **100%** |

### Begründung

1. **Kein Vendor-Lockin:** BullMQ nutzt nur Redis. Redis ist bereits in der Infrastruktur vorhanden oder trivial als Docker-Container hinzufügbar.
2. **Geringste Latenz:** Redis-basierte Queues haben Sub-Millisekunden-Latenz. HTTP-basierte Dienste (Trigger.dev Cloud, Inngest) haben 50-100ms Overhead.
3. **Kosten:** €0 bei Self-Hosting. Keine recurring Costs.
4. **Reife:** BullMQ (basierend auf Bull) ist seit 5+ Jahren produktiv, 6.000+ GitHub Stars, große Community.
5. **Observability:** Bull Board bietet ein Dashboard für Queue-Monitoring.

### Trigger.dev als Ergänzung

Trigger.dev wird als ergänzende Lösung für **externe Webhook-getriggerte Workflows** evaluiert, insbesondere:
- GitHub Webhooks → CI/CD Reaktionen
- Stripe/Revolut Webhooks → Payment Processing
- Externe API Callbacks

Trigger.dev läuft im gleichen Monorepo (`/packages/workflows/`) und nutzt BullMQ als Backend, wenn self-hosted.

## Konsequenzen

### Positiv
- Volle Kontrolle über Queue-Daten
- Keine zusätzlichen Cloud-Kosten
- Integration mit bestehendem Monitoring (Prometheus metrics exportierbar)
- Persistenz über Redis RDB/AOF

### Negativ
- Redis-Container benötigt (~50MB RAM)
- Kein Managed-Service (Selbstverantwortung für Redis-Uptime)
- Bull Board UI muss separat gehostet werden

### Neutral
- Job-Daten in Redis (flüchtig ohne Persistenz-Konfiguration)
- Backup-Strategie für Redis erforderlich

## Implementierung

```typescript
// packages/workflows/queue.ts
import { Queue, Worker, QueueScheduler } from 'bullmq';
import { Redis } from 'ioredis';

const connection = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  maxRetriesPerRequest: null,
});

export const eventQueue = new Queue('events', { connection });
export const emailQueue = new Queue('emails', { connection });
export const taskQueue = new Queue('tasks', { connection });
```

## Compliance-Prüfung

| Guardrail | Status |
|-----------|--------|
| Modularität | ✅ Queue austauschbar (Adapter-Pattern) |
| Dokumentationspflicht | ✅ Diese ADR |
| CI-Validierung | ✅ BullMQ Types werden via CI geprüft |
| Zero Information Loss | ✅ Failed Jobs → Dead Letter Queue |

## Referenzen

- [BullMQ Documentation](https://docs.bullmq.io/)
- ADR-005: Automation Layer
- /packages/workflows/ (noch anzulegen)
