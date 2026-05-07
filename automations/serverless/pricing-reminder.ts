/**
 * NeXifyAI — Serverless Automation: Pricing Reminder
 * 
 * Trigger: pricing_view Event ohne plan_select innerhalb 24h
 * Action: Sendet Erinnerungs-E-Mail via Resend
 * 
 * Endpoint: POST /api/automations/pricing-reminder
 * Deployment: FastAPI Route im Backend
 * 
 * Aufruf: Vercel Cron alle 30 Min → prüft pricing_views der letzten 24h
 */

// ══════════════════════════════════════════════════════════════
// TYPES
// ══════════════════════════════════════════════════════════════

interface PricingViewEvent {
  session_id: string;
  url: string;
  segment?: 'b2c' | 'b2b' | 'enterprise' | 'partner';
  timestamp: string;
  email?: string; // Falls bekannt
}

interface PlanSelectEvent {
  session_id: string;
  plan_id: string;
  plan_name: string;
  timestamp: string;
}

// ══════════════════════════════════════════════════════════════
// WORKFLOW LOGIC
// ══════════════════════════════════════════════════════════════

/**
 * Hauptfunktion: Findet pricing_views ohne nachfolgendes plan_select
 * und sendet eine Erinnerungs-E-Mail.
 */
async function pricingReminderWorkflow() {
  const now = new Date();
  const since = new Date(now.getTime() - 24 * 60 * 60 * 1000); // Letzte 24h

  // 1. Pricing-Views abrufen (aus Supabase analytics_events)
  const pricingViews: PricingViewEvent[] = await getEventsSince('pricing_view', since);
  
  // 2. Plan-Selects abrufen (gleicher Zeitraum)
  const planSelects: PlanSelectEvent[] = await getEventsSince('plan_select', since);
  
  // 3. Sessions finden, die Pricing gesehen aber keinen Plan gewählt haben
  const convertedSessions = new Set(planSelects.map(ps => ps.session_id));
  const unconverted = pricingViews.filter(pv => !convertedSessions.has(pv.session_id));
  
  // 4. E-Mail senden (wenn E-Mail bekannt)
  for (const view of unconverted) {
    if (view.email) {
      await sendPricingReminderEmail(view.email, view.segment || 'b2b');
    }
  }
  
  return {
    checked: pricingViews.length,
    converted: pricingViews.length - unconverted.length,
    reminders_sent: unconverted.length,
    timestamp: now.toISOString(),
  };
}

// ══════════════════════════════════════════════════════════════
// HELPERS (implementiert im Backend)
// ══════════════════════════════════════════════════════════════

async function getEventsSince(eventType: string, since: Date): Promise<any[]> {
  // Implementierung: Supabase Query
  // SELECT * FROM analytics_events WHERE event = $eventType AND timestamp > $since
  throw new Error('Backend-implementiert');
}

async function sendPricingReminderEmail(email: string, segment: string) {
  // Implementierung: Resend API
  // Template: pricing-reminder (enthält Vergleich + Case Study)
  throw new Error('Backend-implementiert');
}

export { pricingReminderWorkflow };
