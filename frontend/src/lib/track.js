/**
 * NeXifyAI — Event Tracking Library
 * Zentrale track()-Funktion für alle DOS v2.0 Events.
 * Sendet Events an das Backend und optional an Plausible/PostHog.
 * 
 * Usage:
 *   import { track, initTracking } from './lib/track';
 *   track('cta_click', { id: 'hero-demo', label: 'Jetzt starten' });
 */

const BACKEND_URL = process.env.REACT_APP_API_URL || 'https://nexifyai.nexifyai.cloud';
const TRACK_ENDPOINT = BACKEND_URL + '/api/analytics/track';

/* ═══════════════ SESSION ═══════════════ */
let sessionId = null;

function getSessionId() {
  if (!sessionId) {
    sessionId = sessionStorage.getItem('nx_session');
    if (!sessionId) {
      sessionId = 'nx_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('nx_session', sessionId);
    }
  }
  return sessionId;
}

/* ═══════════════ TRACK ═══════════════ */
async function track(event, props = {}) {
  var payload = {
    event: event,
    properties: Object.assign({}, props, {
      url: window.location.pathname,
      referrer: document.referrer || '',
    }),
    session_id: getSessionId(),
    timestamp: new Date().toISOString(),
  };

  try {
    fetch(TRACK_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    });
  } catch (e) {
    if (process.env.NODE_ENV === 'development') {
      console.debug('[track] Failed:', event, e);
    }
  }
}

/* ═══════════════ AUTO PAGE VIEW ═══════════════ */
function autoTrackPageView() {
  track('page_view', {
    url: window.location.pathname + window.location.search,
    title: document.title,
  });
}

/* ═══════════════ AUTO SCROLL ═══════════════ */
var trackedScrollDepths = {};

function autoTrackScroll() {
  var thresholds = [25, 50, 75, 90];
  
  window.addEventListener('scroll', function() {
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (docHeight <= 0) return;
    
    var percent = Math.round((window.scrollY / docHeight) * 100);
    for (var i = 0; i < thresholds.length; i++) {
      var t = thresholds[i];
      if (percent >= t && !trackedScrollDepths[t]) {
        trackedScrollDepths[t] = true;
        track('scroll_depth', { percent: t });
        break;
      }
    }
  }, { passive: true });
}

/* ═══════════════ INIT ═══════════════ */
function initTracking() {
  autoTrackPageView();
  autoTrackScroll();
}

export { track, initTracking, getSessionId };
