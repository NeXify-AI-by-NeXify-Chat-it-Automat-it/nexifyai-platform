// Outbound Auto-Engine Trigger
// Läuft täglich 09:00 UTC, ruft Backend an, das die Pipeline autonom abarbeitet.

const BACKEND_URL = 'https://contract-os.preview.emergentagent.com';
const CRON_SECRET = process.env.CRON_SECRET || '';

export default async function handler(req) {
  if (req.headers.get('authorization') !== `Bearer ${CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    const r = await fetch(`${BACKEND_URL}/api/internal/cron/outbound-auto`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CRON_SECRET}`,
        'Content-Type': 'application/json',
      },
      body: '{}',
      signal: AbortSignal.timeout(120000), // 2 min — LLM calls dauern
    });
    const data = await r.json().catch(() => ({}));
    console.log('[CRON:outbound-auto] result:', JSON.stringify(data.totals || {}));
    return new Response(JSON.stringify(data), {
      status: r.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('[CRON:outbound-auto] failed:', e.message);
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

export const config = { runtime: 'edge' };
