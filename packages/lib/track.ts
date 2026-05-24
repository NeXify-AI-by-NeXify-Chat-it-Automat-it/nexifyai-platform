/**
 * NeXifyAI — Universal Event Tracker
 * 
 * Client-side tracking utility. Validates events against taxonomy.ts
 * and sends them to the analytics backend.
 * 
 * Usage:
 *   import { track } from '@/lib/track';
 *   track({ event: 'page_view', url: '/pricing', timestamp: Date.now() });
 */

import { AnyEvent, AnyEventType, EVENT_VERSION } from '@nexifyai/events';

// ══════════════════════════════════════════════
// CONFIGURATION
// ══════════════════════════════════════════════

const ANALYTICS_ENDPOINT = process.env.NEXT_PUBLIC_ANALYTICS_URL || '/api/analytics/event';
const BATCH_SIZE = 10;
const FLUSH_INTERVAL_MS = 5000;
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

// ══════════════════════════════════════════════
// EVENT QUEUE (Client-side Buffer)
// ══════════════════════════════════════════════

interface QueuedEvent {
  event: AnyEventType;
  timestamp: number;
  retries: number;
  session_id?: string;
  user_id?: string;
}

let eventQueue: QueuedEvent[] = [];
let flushTimer: ReturnType<typeof setInterval> | null = null;
let sessionId: string | null = null;

// ══════════════════════════════════════════════
// SESSION MANAGEMENT
// ══════════════════════════════════════════════

function getSessionId(): string {
  if (!sessionId) {
    sessionId = localStorage.getItem('nx_session_id');
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      localStorage.setItem('nx_session_id', sessionId);
    }
  }
  return sessionId;
}

function getUserId(): string | undefined {
  try {
    const token = localStorage.getItem('nx_token');
    if (!token) return undefined;
    // Decode JWT payload (no verification — just extract user_id)
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub || payload.user_id;
  } catch {
    return undefined;
  }
}

// ══════════════════════════════════════════════
// TRACK FUNCTION
// ══════════════════════════════════════════════

/**
 * Track an event. Validates against taxonomy, enqueues for batch sending.
 * 
 * @param event - The event to track, must match taxonomy.ts schemas
 * @returns true if event was queued successfully
 */
export function track(event: Partial<AnyEventType> & { event: string }): boolean {
  try {
    // Validate event type exists
    const validated = AnyEvent.parse({
      ...event,
      timestamp: event.timestamp || Date.now(),
    }) as AnyEventType;

    // Add session context
    const queued: QueuedEvent = {
      event: validated,
      timestamp: Date.now(),
      retries: 0,
      session_id: getSessionId(),
      user_id: getUserId(),
    };

    eventQueue.push(queued);

    // Auto-flush if batch size reached
    if (eventQueue.length >= BATCH_SIZE) {
      flush();
    }

    // Start flush timer if not running
    if (!flushTimer) {
      flushTimer = setInterval(flush, FLUSH_INTERVAL_MS);
    }

    return true;
  } catch (err) {
    console.warn('[track] Invalid event:', event, err);
    return false;
  }
}

// ══════════════════════════════════════════════
// BATCH FLUSH
// ══════════════════════════════════════════════

async function flush(): Promise<void> {
  if (eventQueue.length === 0) return;

  const batch = eventQueue.splice(0, BATCH_SIZE);
  
  try {
    const response = await fetch(ANALYTICS_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Event-Version': EVENT_VERSION,
      },
      body: JSON.stringify({
        events: batch.map(({ event, session_id, user_id }) => ({
          ...event,
          session_id,
          user_id,
        })),
        sent_at: new Date().toISOString(),
      }),
      keepalive: true, // Works even during page unload
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (err) {
    console.warn('[track] Flush failed, re-queueing:', err);
    
    // Re-queue with retry count
    for (const item of batch) {
      if (item.retries < MAX_RETRIES) {
        eventQueue.push({ ...item, retries: item.retries + 1 });
      } else {
        console.warn('[track] Event dropped after max retries:', item.event.event);
      }
    }
  }
}

// ══════════════════════════════════════════════
// PAGE UNLOAD HANDLER
// ══════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    flush();
  });

  // Visibility change — flush when tab becomes hidden
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      flush();
    }
  });
}

// ══════════════════════════════════════════════
// UTILITY: IDENTIFY USER
// ══════════════════════════════════════════════

export function identify(userId: string, traits?: Record<string, unknown>): void {
  track({
    event: 'user_identified' as any,
    timestamp: Date.now(),
  } as any);
  
  // Can be extended to send traits to analytics
}

export function pageView(url?: string, referrer?: string): void {
  track({
    event: 'page_view',
    url: url || window.location.pathname,
    referrer: referrer || document.referrer || undefined,
    timestamp: Date.now(),
  } as any);
}
