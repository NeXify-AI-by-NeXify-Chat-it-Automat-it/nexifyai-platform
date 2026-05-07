/**
 * NeXifyAI — Serverless Automation: CRM Push
 * 
 * Trigger: form_submit Event (Type: demo, contact, booking)
 * Action: Schreibt Lead in Supabase → Webhook triggert CRM-Sync
 * 
 * Endpoint: POST /api/automations/crm-push
 * Deployment: FastAPI Route im Backend
 * 
 * Flow:
 *   1. form_submit Event empfangen
 *   2. Lead in Supabase-Tabelle 'leads' schreiben
 *   3. Supabase Database Webhook → POST /api/automations/crm-sync
 *   4. CRM-Sync Route → HubSpot/Pipedrive API
 */

// ══════════════════════════════════════════════════════════════
// TYPES
// ══════════════════════════════════════════════════════════════

interface FormSubmitEvent {
  form_id: string;
  form_type: 'contact' | 'demo' | 'newsletter' | 'booking' | 'support';
  success: boolean;
  data: {
    name?: string;
    email: string;
    company?: string;
    phone?: string;
    message?: string;
    product_interest?: string;
  };
  timestamp: string;
  source?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
}

interface LeadRecord {
  email: string;
  name?: string;
  company?: string;
  phone?: string;
  source?: string;
  form_type: string;
  product_interest?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  status: 'new';
  created_at: string;
}

// ══════════════════════════════════════════════════════════════
// WORKFLOW LOGIC
// ══════════════════════════════════════════════════════════════

/**
 * Verarbeitet form_submit Events und erstellt Lead-Records.
 * Der Supabase Database Webhook triggert dann den CRM-Sync.
 */
async function crmPushWorkflow(event: FormSubmitEvent): Promise<LeadRecord> {
  if (!event.success) {
    throw new Error('Nur erfolgreiche Formulare werden verarbeitet');
  }

  // Priorität basierend auf form_type
  const priority = 
    event.form_type === 'demo' ? 'hot' :
    event.form_type === 'booking' ? 'hot' :
    event.form_type === 'contact' ? 'warm' : 'cold';

  const lead: LeadRecord = {
    email: event.data.email,
    name: event.data.name,
    company: event.data.company,
    phone: event.data.phone,
    source: event.source || 'website',
    form_type: event.form_type,
    product_interest: event.data.product_interest,
    utm_source: event.utm_source,
    utm_medium: event.utm_medium,
    utm_campaign: event.utm_campaign,
    status: 'new',
    created_at: event.timestamp,
  };

  // In Supabase schreiben (via Backend)
  await createLeadInSupabase(lead);
  
  // Supabase Webhook triggert automatisch CRM-Sync:
  // INSERT INTO leads → Webhook → POST /api/automations/crm-sync → HubSpot API

  return lead;
}

// ══════════════════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════════════════

async function createLeadInSupabase(lead: LeadRecord): Promise<void> {
  // Implementierung: Supabase Client
  // INSERT INTO leads (email, name, ...) VALUES ($1, $2, ...)
  throw new Error('Backend-implementiert');
}

export { crmPushWorkflow };
export type { FormSubmitEvent, LeadRecord };
