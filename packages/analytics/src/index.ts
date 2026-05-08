/**
 * NeXifyAI Analytics — Event ingestion, aggregation, and metrics.
 * 
 * Processes raw events from /lib/track.ts and produces:
 * - Session analytics
 * - Funnel metrics
 * - Conversion tracking
 * - Real-time dashboards
 * 
 * @package @nexifyai/analytics
 * @version 1.0.0
 */

import { AnyEventType } from '@nexifyai/events';

export interface AnalyticsEvent {
  event: AnyEventType;
  session_id?: string;
  user_id?: string;
  received_at: string;
  ip_hash?: string;
  user_agent?: string;
  geo_country?: string;
}

export interface SessionMetrics {
  session_id: string;
  start_time: string;
  end_time?: string;
  page_views: number;
  events_fired: number;
  conversion_events: string[];
  duration_seconds?: number;
  bounce: boolean;
}

export function aggregateSessionEvents(events: AnalyticsEvent[]): SessionMetrics {
  const first = events[0];
  const last = events[events.length - 1];
  
  return {
    session_id: first?.session_id || 'unknown',
    start_time: first?.received_at || new Date().toISOString(),
    end_time: last?.received_at,
    page_views: events.filter(e => e.event.event === 'page_view').length,
    events_fired: events.length,
    conversion_events: events
      .filter(e => ['purchase', 'demo_request', 'form_submit', 'plan_select'].includes(e.event.event))
      .map(e => e.event.event),
    duration_seconds: first && last 
      ? (new Date(last.received_at).getTime() - new Date(first.received_at).getTime()) / 1000
      : undefined,
    bounce: events.length === 1 && events[0].event.event === 'page_view',
  };
}

export { track } from '../../../lib/track';
