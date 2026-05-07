/**
 * NeXifyAI — Event Taxonomy v1.0
 * Zentrale Definition aller Tracking-Events mit Zod-Validierung.
 * 
 * Usage:
 *   import { pageViewEvent } from '@nexifyai/events';
 *   const event = pageViewEvent.parse({ url: '/', referrer: 'google.com', timestamp: Date.now() });
 */

import { z } from 'zod';

// ══════════════════════════════════════════════
// BASELINE EVENTS (Pflicht für alle Projekte)
// ══════════════════════════════════════════════

export const PageViewSchema = z.object({
  event: z.literal('page_view'),
  url: z.string().min(1),
  referrer: z.string().optional(),
  timestamp: z.number(),
  session_id: z.string().optional(),
  user_id: z.string().optional(), // hashed
});
export type PageViewEvent = z.infer<typeof PageViewSchema>;

export const CtaClickSchema = z.object({
  event: z.literal('cta_click'),
  id: z.string(),
  location: z.enum(['header', 'hero', 'body', 'footer', 'pricing', 'sidebar']),
  label: z.string(),
  destination: z.string().optional(),
  timestamp: z.number(),
  session_id: z.string().optional(),
});
export type CtaClickEvent = z.infer<typeof CtaClickSchema>;

export const ScrollDepthSchema = z.object({
  event: z.literal('scroll_depth'),
  percent: z.union([z.literal(25), z.literal(50), z.literal(75), z.literal(90)]),
  url: z.string(),
  timestamp: z.number(),
  session_id: z.string().optional(),
});
export type ScrollDepthEvent = z.infer<typeof ScrollDepthSchema>;

export const PricingViewSchema = z.object({
  event: z.literal('pricing_view'),
  url: z.string(),
  segment: z.enum(['b2c', 'b2b', 'enterprise', 'partner']).optional(),
  timestamp: z.number(),
});
export type PricingViewEvent = z.infer<typeof PricingViewSchema>;

export const PlanSelectSchema = z.object({
  event: z.literal('plan_select'),
  plan_id: z.string(),
  plan_name: z.string(),
  price: z.number().optional(),
  billing_cycle: z.enum(['monthly', 'yearly']).optional(),
  timestamp: z.number(),
});
export type PlanSelectEvent = z.infer<typeof PlanSelectSchema>;

export const FormStartSchema = z.object({
  event: z.literal('form_start'),
  form_id: z.string(),
  form_type: z.enum(['contact', 'demo', 'newsletter', 'booking', 'support']),
  timestamp: z.number(),
});
export type FormStartEvent = z.infer<typeof FormStartSchema>;

export const FormSubmitSchema = z.object({
  event: z.literal('form_submit'),
  form_id: z.string(),
  form_type: z.enum(['contact', 'demo', 'newsletter', 'booking', 'support']),
  success: z.boolean(),
  timestamp: z.number(),
});
export type FormSubmitEvent = z.infer<typeof FormSubmitSchema>;

export const FormErrorSchema = z.object({
  event: z.literal('form_error'),
  form_id: z.string(),
  field: z.string(),
  error_type: z.string(),
  timestamp: z.number(),
});
export type FormErrorEvent = z.infer<typeof FormErrorSchema>;

export const AbandonFormSchema = z.object({
  event: z.literal('abandon_form'),
  form_id: z.string(),
  last_field: z.string(),
  timestamp: z.number(),
});
export type AbandonFormEvent = z.infer<typeof AbandonFormSchema>;

// ══════════════════════════════════════════════
// EXTENDED EVENTS (je Geschäftsmodell)
// ══════════════════════════════════════════════

export const AddToCartSchema = z.object({
  event: z.literal('add_to_cart'),
  product_id: z.string(),
  product_name: z.string(),
  price: z.number(),
  quantity: z.number().default(1),
  timestamp: z.number(),
});

export const BeginCheckoutSchema = z.object({
  event: z.literal('begin_checkout'),
  cart_value: z.number(),
  item_count: z.number(),
  timestamp: z.number(),
});

export const PurchaseSchema = z.object({
  event: z.literal('purchase'),
  order_id: z.string(),
  total: z.number(),
  currency: z.string().default('EUR'),
  items: z.number(),
  timestamp: z.number(),
});

export const DemoRequestSchema = z.object({
  event: z.literal('demo_request'),
  source: z.enum(['website', 'email', 'referral', 'social', 'other']),
  product_interest: z.string().optional(),
  timestamp: z.number(),
});

export const CalendarBookedSchema = z.object({
  event: z.literal('calendar_booked'),
  meeting_type: z.string(),
  date: z.string(), // ISO date
  timestamp: z.number(),
});

export const LeadScoredSchema = z.object({
  event: z.literal('lead_scored'),
  score: z.number().min(0).max(100),
  qualification: z.enum(['cold', 'warm', 'hot']),
  timestamp: z.number(),
});

export const ReturningUserSchema = z.object({
  event: z.literal('returning_user'),
  days_since_last_visit: z.number(),
  visit_count: z.number(),
  timestamp: z.number(),
});

export const EmailSubscribeSchema = z.object({
  event: z.literal('email_subscribe'),
  source: z.string(),
  list: z.string().optional(),
  timestamp: z.number(),
});

export const InternalSearchSchema = z.object({
  event: z.literal('search_internal'),
  query: z.string(),
  result_count: z.number().optional(),
  timestamp: z.number(),
});

// ══════════════════════════════════════════════
// UNION TYPES
// ══════════════════════════════════════════════

export const AnyEvent = z.discriminatedUnion('event', [
  PageViewSchema, CtaClickSchema, ScrollDepthSchema,
  PricingViewSchema, PlanSelectSchema,
  FormStartSchema, FormSubmitSchema, FormErrorSchema, AbandonFormSchema,
  AddToCartSchema, BeginCheckoutSchema, PurchaseSchema,
  DemoRequestSchema, CalendarBookedSchema, LeadScoredSchema,
  ReturningUserSchema, EmailSubscribeSchema, InternalSearchSchema,
]);

export type AnyEventType = z.infer<typeof AnyEvent>;

// ══════════════════════════════════════════════
// EVENT TRANSPORT POLICY
// ══════════════════════════════════════════════
// - Events are append-only (immutable after firing)
// - No PII in plaintext (email/user IDs hashed)
// - Events sent to BOTH analytics provider AND serverless automation endpoint (FastAPI route)
// - Schema validated with Zod before firing
// - Breaking changes require new version (events/v2/)

export const EVENT_VERSION = '1.0.0';
