/**
 * NeXifyAI — Event Tracking Library
 * 
 * Zentrale track()-Funktion für alle DOS v2.0 Events.
 * Sendet Events an das Backend und optional an Plausible/PostHog.
 * 
 * Usage:
 *   import { track } from '../lib/track';
 *   track('cta_click', { id: 'hero-demo', label: 'Jetzt starten' });
 */

// ══════════════════════════════════════════════════════════════
// CONFIG
// ══════════════════════════════════════════════════════════════

const BACKEND_URL = process.env.REACT_APP_API_URL || 'https://nexifyai.nexifyai.cloud';
const TRACK_ENDPOINT = `${BACKEND_URL}/api/analytics/track`;

// ══════════════════════════════════════════════════════════════
// SESSION MANAGEMENT
// ══════════════════════════════════════════════════════════════

let sessionId: string | null = null;

function getSessionId(): string {
  if (!sessionId) {
    sessionId = sessionStorage.getItem('nx_session');
    if (!sessionId) {
      sessionId = `nx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('nx_session', sessionId);
    }
  }
  return sessionId;
}

// ══════════════════════════════════════════════════════════════
// MAIN TRACK FUNCTION
// ══════════════════════════════════════════════════════════════

type EventName = 
  | 'page_view'
  | 'cta_click'
  | 'scroll_depth'
  | 'pricing_view'
  | 'plan_select'
  | 'form_start'
  | 'form_submit'
  | 'form_error'
  | 'abandon_form'
  | 'add_to_cart'
  | 'begin_checkout'
  | 'purchase'
  | 'demo_request'
  | 'calendar_booked'
  | 'lead_scored'
  | 'returning_user'
  | 'email_subscribe'
  | 'search_internal';

interface TrackProperties {
  [key: string]: any;
}

const track = async (event: EventName, props: TrackProperties = {}): Promise<void> => {
  const payload = {
    event,
    properties: {
      ...props,
      url: window.location.pathname,
      referrer: document.referrer || '',
    },
    session_id: getSessionId(),
    timestamp: new Date().toISOString(),
  };

  // Fire-and-forget: Nicht auf Response warten
  try {
    fetch(TRACK_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    });
  } catch (_) {
    // Silent fail — Tracking darf UX nicht beeinträchtigen
    if (process.env.NODE_ENV === 'development') {
      console.debug('[track] Failed:', event, _);
    }
  }
};

// ══════════════════════════════════════════════════════════════
// AUTO-TRACKING: PAGE VIEWS
// ══════════════════════════════════════════════════════════════

const autoTrackPageView = (): void => {
  track('page_view', {
    url: window.location.pathname + window.location.search,
    title: document.title,
  });
};

// ══════════════════════════════════════════════════════════════
// AUTO-TRACKING: SCROLL DEPTH
// ══════════════════════════════════════════════════════════════

const trackedScrollDepths = new Set<number>();

const autoTrackScroll = (): void => {
  const thresholds = [25, 50, 75, 90];
  
  window.addEventListener('scroll', () => {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (docHeight <= 0) return;
    
    const percent = Math.round((window.scrollY / docHeight) * 100);
    const threshold = thresholds.find(t => percent >= t && !trackedScrollDepths.has(t));
    
    if (threshold) {
      trackedScrollDepths.add(threshold);
      track('scroll_depth', { percent: threshold });
    }
  }, { passive: true });
};

// ══════════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════════

const initTracking = (): void => {
  autoTrackPageView();
  autoTrackScroll();
};

export { track, initTracking, getSessionId };
export type { EventName, TrackProperties };
